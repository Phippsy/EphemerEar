import pytest
import sys
import types
import json
import textwrap

try:
    import tiktoken  # noqa: F401
except ModuleNotFoundError:
    dummy_tiktoken = types.ModuleType("tiktoken")

    class DummyEncoding:
        def encode(self, text):
            return []

    def get_encoding(name):
        return DummyEncoding()

    dummy_tiktoken.get_encoding = get_encoding
    sys.modules["tiktoken"] = dummy_tiktoken

if "openai" not in sys.modules:
    sys.modules["openai"] = types.ModuleType("openai")

if "requests" not in sys.modules:
    dummy_requests = types.ModuleType("requests")
    exceptions_mod = types.ModuleType("requests.exceptions")

    class RequestException(Exception):
        pass

    class Response:
        status_code = 200

    exceptions_mod.RequestException = RequestException
    dummy_requests.post = lambda *a, **k: None
    dummy_requests.Response = Response
    dummy_requests.exceptions = exceptions_mod
    sys.modules["requests"] = dummy_requests
    sys.modules["requests.exceptions"] = exceptions_mod

if "yaml" not in sys.modules:
    dummy_yaml = types.ModuleType("yaml")
    def safe_load(stream):
        if hasattr(stream, "read"):
            stream = stream.read()
        try:
            return json.loads(stream)
        except Exception:
            result = {}
            current = None
            for line in stream.splitlines():
                if not line.strip():
                    continue
                if not line.startswith("  "):
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip().strip('"')
                    if value == "":
                        current = key
                        result[current] = {}
                    else:
                        val = {
                            "true": True,
                            "false": False
                        }.get(value.lower(), value)
                        result[key] = val
                        current = None
                else:
                    subkey, _, value = line.strip().partition(":")
                    value = value.strip().strip('"')
                    val = {
                        "true": True,
                        "false": False
                    }.get(value.lower(), value)
                    if current is not None:
                        result[current][subkey] = val
            return result
    class YAMLError(Exception):
        pass
    dummy_yaml.safe_load = safe_load
    dummy_yaml.YAMLError = YAMLError
    sys.modules["yaml"] = dummy_yaml

import importlib.util
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1] / "ephemerear"

ephemerear_pkg = types.ModuleType("ephemerear")
ephemerear_pkg.__path__ = [str(MODULE_DIR)]
sys.modules["ephemerear"] = ephemerear_pkg

spec_functions = importlib.util.spec_from_file_location(
    "ephemerear.functions", MODULE_DIR / "functions.py"
)
functions = importlib.util.module_from_spec(spec_functions)
spec_functions.loader.exec_module(functions)
ephemerear_pkg.functions = functions
sys.modules["ephemerear.functions"] = functions

spec_ephemer = importlib.util.spec_from_file_location(
    "ephemerear.EphemerEar", MODULE_DIR / "EphemerEar.py"
)
ephemer_module = importlib.util.module_from_spec(spec_ephemer)
spec_ephemer.loader.exec_module(ephemer_module)
EphemerEar = ephemer_module.EphemerEar
ephemerear_pkg.EphemerEar = ephemer_module
sys.modules["ephemerear.EphemerEar"] = ephemer_module

from ephemerear import functions


@pytest.fixture
def setup_todo_environment(tmp_path):
    todo_file = tmp_path / "todos.md"
    return str(todo_file)

def test_add_todo_creates_file_if_not_exists(setup_todo_environment):
    todo_file = setup_todo_environment
    task_description = "- [ ] Read Pytest Documentation"
    functions.add_todo(text=task_description, todo_file=todo_file)
    with open(todo_file, 'r') as file:
        content = file.read()
    assert "- [ ] Read Pytest Documentation" in content

def test_add_todo_appends_to_file(setup_todo_environment):
    todo_file = setup_todo_environment
    task_description = "- [ ] Review PR #42"
    # Adding a task to ensure the file is already created
    functions.add_todo(text="- [ ] Initial task", todo_file=todo_file)
    functions.add_todo(text=task_description, todo_file=todo_file)
    with open(todo_file, 'r') as file:
        content = file.readlines()
    assert "- [ ] Review PR #42\n" in content


### 2. Testing `ephemerear.py` File

#### Testing `load_yaml_to_dict` Function



@pytest.mark.skipif(EphemerEar is None, reason="tiktoken not installed")
def test_load_yaml_to_dict_returns_correct_structure(tmp_path):
    yaml_content = """
    bot:
      name: TestBot
      model: gpt-3.5-turbo
      cache: tests
      history_file: tests/history.json
      system_prompt: tests/prompt.md
      use_pushover: true
    user:
      name: TestUser
      user_details: tests/user_details.txt
    auth_tokens:
      openai: "test-openai-token"
      pushover_key: "test-pushover-key"
      pushover_user: "test-pushover-user"

    """
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(textwrap.dedent(yaml_content))
    ee = EphemerEar(str(yaml_file))
    loaded_config = ee.load_yaml_to_dict(str(yaml_file))
    assert loaded_config['bot']['name'] == "TestBot"
    assert loaded_config['bot']['model'] == "gpt-3.5-turbo"
    assert 'openai' in loaded_config['auth_tokens']

@pytest.mark.skipif(EphemerEar is None, reason="tiktoken not installed")
def test_load_yaml_to_dict_raises_error_on_invalid_path():
    with pytest.raises(FileNotFoundError):
        EphemerEar("invalid_path.yaml")
        


