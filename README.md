## EphemerEar

<img src="img/logo.svg" width="100" alt="EphemerEar logo" />

EphemerEar transcribes voice recordings and can optionally pass transcript prompts into an LLM workflow.

## What changed in this refresh

- Updated to modern OpenAI Python SDK usage (`OpenAI(...)` client).
- Default cloud transcription model is now `gpt-4o-mini-transcribe` (recommended for quality/cost balance).
- Added a simple CLI entrypoint so teammates can run transcription with one command.
- Removed hard-coded local machine paths from the Hazel helper script.
- Dependency spec now uses modern minimum versions instead of a legacy `openai==0.28` pin.

## Table of Contents

- [Quick start (team-friendly)](#quick-start-team-friendly)
- [Configuration reference](#configuration-reference)
- [Recommended transcription mode](#recommended-transcription-mode)
- [Hazel automation](#hazel-automation)
- [Application workflow](#application-workflow)
- [Demonstration notebook](#demonstration-notebook)
- [Function calling (optional)](#function-calling-optional)
- [Using a chat UI with Chainlit (optional)](#using-a-chat-ui-with-chainlit-optional)
- [Notes](#notes)

## Quick start (team-friendly)

### 1) Prerequisites

- Python 3.10+
- `ffmpeg` (required by `pydub` for audio chunking/conversion)
- OpenAI API key
- (Optional) [Hazel for macOS](https://www.noodlesoft.com/) if you want fully automatic transcription from Voice Memos

### 2) Install

```bash
git clone <your-repo-url>
cd EphemerEar
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Configure

```bash
cp config-template.yaml config.yaml
```

Then edit `config.yaml`:

- `auth_tokens.openai`
- `bot.model` (chat model)
- `bot.stt_engine` (`openai` recommended; `whisper` for local offline)
- `bot.stt_model` for cloud transcription (default `gpt-4o-mini-transcribe`)
- `bot.local_whisper_model` for local transcription mode
- all output paths under `stores`

### 4) Run transcription manually

```bash
python -m ephemerear.transcribe /path/to/recording.m4a --config config.yaml
```

That command will:

- read config,
- transcribe the recording,
- write markdown transcript output to your configured transcript store,
- optionally trigger LLM handling when transcript contains a prompt marker.

## Configuration reference

The default `config-template.yaml` gives a full working structure. Useful keys:

- `bot.name`: display name used in response files.
- `bot.root_dir`: repository root for your local installation.
- `bot.history_file`: JSON conversation history file.
- `bot.system_prompt`: path to your system prompt text.
- `bot.max_message_window`: context window budget for carried chat history.
- `bot.cache`: directory used for temporary chunked audio files.
- `bot.model`: OpenAI chat model for prompt handling.
- `bot.stt_engine`: `openai` or `whisper`.
- `bot.stt_model`: OpenAI transcription model (when `stt_engine: openai`).
- `bot.local_whisper_model`: local Whisper size (when `stt_engine: whisper`).
- `bot.use_pushover`: set `true` to enable mobile notifications.
- `auth_tokens.openai`: OpenAI API key.
- `auth_tokens.pushover_key` + `auth_tokens.pushover_user`: optional Pushover notification credentials.
- `stores.*`: output locations for transcripts, responses, notes, achievements, and other bot artifacts.

## Recommended transcription mode

### Option A (recommended for most teams): OpenAI hosted STT

Use in `config.yaml`:

```yaml
bot:
  stt_engine: openai
  stt_model: gpt-4o-mini-transcribe
```

Why this is the easiest:

- No local model downloads.
- Better consistency across teammates.
- Least machine-specific setup burden.

### Option B: Local Whisper (offline)

```yaml
bot:
  stt_engine: whisper
  local_whisper_model: base
```

Use this when offline transcription or local-only processing is required.

## Hazel automation

`ephemerear/hazel-transcription.py` no longer has hard-coded machine paths.

Set an environment variable (or pass a default config in your shell profile):

```bash
export EPHEMEREAR_CONFIG=/absolute/path/to/config.yaml
```

Then Hazel can run:

```bash
python /absolute/path/to/EphemerEar/ephemerear/hazel-transcription.py "$1"
```

Tip: when debugging Hazel rules, redirect stdout/stderr to files so you can inspect failures.

Typical macOS Voice Memos sync location (may vary by system setup):

`/Users/{your_user_name}/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings`

## Application workflow

1. **Capture audio** in Voice Memos (or any recorder that writes supported audio files).
2. **Trigger transcription** either manually (`python -m ephemerear.transcribe`) or automatically through Hazel.
3. **Save transcript** into the configured `stores.transcripts` location (organized by year/month).
4. **Optional prompt handling**: if "prompt" appears early in the transcript, EphemerEar sends the trailing text to the configured chat model and writes the response markdown to `stores.responses`.

## Demonstration notebook

See [`ephemerear-demo.ipynb`](./ephemerear-demo.ipynb) for a walkthrough of the project flow and sample behavior.

## Function calling (optional)

EphemerEar can expose Python functions to the chat model using OpenAI function-calling-style metadata.

- Functions are defined in [`ephemerear/functions.py`](./ephemerear/functions.py).
- A function is eligible when it has a corresponding schema dictionary named `<function_name>_definition`.
- Current defaults include helper functions for adding to-do items and committing memories.

If you add your own functions and matching schema definitions, they are loaded automatically at runtime and can be invoked by the model.

## Using a chat UI with Chainlit (optional)

There is a basic Chainlit entrypoint in [`app.py`](./app.py).

```bash
source .venv/bin/activate
chainlit run app.py -w
```

Before using it, update `app.py` to point to your own config path and environment (it is currently a local developer scaffold).

## Notes

- OpenAI and transcription APIs evolve frequently. Pinning very old SDK versions is brittle; this repo now tracks modern versions with minimum constraints.
- If team reproducibility is critical, freeze exact versions with `pip freeze > requirements-lock.txt` after your team verifies a known-good environment.
- For viewing transcript/response markdown files, tools like Obsidian can be convenient but are optional.
