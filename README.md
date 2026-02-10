## EphemerEar

<img src="img/logo.svg" width="100" alt="EphemerEar logo" />

EphemerEar transcribes voice recordings and can optionally pass transcript prompts into an LLM workflow.

## What changed in this refresh

- Updated to modern OpenAI Python SDK usage (`OpenAI(...)` client).
- Default cloud transcription model is now `gpt-4o-mini-transcribe` (recommended for quality/cost balance).
- Added a simple CLI entrypoint so teammates can run transcription with one command.
- Removed hard-coded local machine paths from the Hazel helper script.
- Dependency spec now uses modern minimum versions instead of a legacy `openai==0.28` pin.

## Quick start (team-friendly)

### 1) Prerequisites

- Python 3.10+
- `ffmpeg` (required by `pydub` for audio chunking/conversion)
- OpenAI API key

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
- `bot.model` (chat model, default modern value suggested below)
- `bot.stt_engine` (`openai` recommended; `whisper` for local offline)
- `bot.stt_model` for cloud transcription (default `gpt-4o-mini-transcribe`)
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

## Notes

- OpenAI and transcription APIs evolve frequently. Pinning very old SDK versions is brittle; this repo now tracks modern versions with minimum constraints.
- If team reproducibility is critical, freeze exact versions with `pip freeze > requirements-lock.txt` after your team verifies a known-good environment.
