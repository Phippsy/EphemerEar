import pytest
import sys
from pathlib import Path

# Ensure the package root is on the path so that ``ephemerear`` can be imported
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import ephemerear
from ephemerear import functions as Functions

@pytest.fixture
def setup_todo_environment(tmp_path):
    todo_file = tmp_path / "todos.md"
    return str(todo_file)

def test_add_todo_creates_file_if_not_exists(setup_todo_environment):
    todo_file = setup_todo_environment
    task_description = "- [ ] Read Pytest Documentation"
    Functions.add_todo(text=task_description, todo_file=todo_file)
    with open(todo_file, 'r') as file:
        content = file.read()
    assert "- [ ] Read Pytest Documentation" in content

def test_add_todo_appends_to_file(setup_todo_environment):
    todo_file = setup_todo_environment
    task_description = "- [ ] Review PR #42"
    # Adding a task to ensure the file is already created
    Functions.add_todo(text="- [ ] Initial task", todo_file=todo_file)
    Functions.add_todo(text=task_description, todo_file=todo_file)
    with open(todo_file, 'r') as file:
        content = file.readlines()
    assert "- [ ] Review PR #42\n" in content


### 2. Testing `ephemerear.py` File

#### Testing `load_yaml_to_dict` Function

from ephemerear.EphemerEar import EphemerEar

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
    yaml_file.write_text(yaml_content)
    ee = EphemerEar(str(yaml_file))
    loaded_config = ee.load_yaml_to_dict(str(yaml_file))  # Pass the file path to the method
    assert loaded_config['bot']['name'] == "TestBot"
    assert loaded_config['bot']['model'] == "gpt-3.5-turbo"
    assert 'openai' in loaded_config['auth_tokens']

def test_load_yaml_to_dict_raises_error_on_invalid_path(tmp_path):
    # Create a valid config file so that the EphemerEar instance initialises
    yaml_content = "bot:\n  name: Test\n"
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content)
    ee = EphemerEar(str(yaml_file))
    with pytest.raises(FileNotFoundError):
        ee.load_yaml_to_dict("invalid_path.yaml")
        


