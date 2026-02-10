"""Audio transcription helpers and CLI for EphemerEar.

This module supports two speech-to-text engines:
- ``openai`` (default): OpenAI's hosted transcription models.
- ``whisper``: local ``openai-whisper`` model execution.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import math
import os
from pathlib import Path
from typing import Iterable, List

from pydub import AudioSegment
import yaml

from .EphemerEar import EphemerEar, testforword

DEFAULT_OPENAI_TRANSCRIBE_MODEL = "gpt-4o-mini-transcribe"


def whisper_local_transcribe(
    file_path: str,
    model: str = "base",
    custom_prompt: str = "Here is the full text, in English:",
) -> str:
    """Run local whisper transcription for a single audio file."""
    try:
        import whisper
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Local whisper transcription requires the 'openai-whisper' package"
        ) from exc

    local_model = whisper.load_model(model)
    result = local_model.transcribe(file_path, language="en", initial_prompt=custom_prompt)
    return result["text"]


def split_audio(file_path: str, target_length_ms: int = 10 * 60 * 1000, cache_dir: str = "./cache") -> List[str]:
    """Split audio into fixed-size MP3 chunks and return created chunk paths."""
    audio = AudioSegment.from_file(file_path)
    chunks: List[str] = []
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)

    total_chunks = max(1, math.ceil(len(audio) / target_length_ms))
    stem = Path(file_path).stem

    for i in range(total_chunks):
        start = i * target_length_ms
        end = min((i + 1) * target_length_ms, len(audio))
        chunk = audio[start:end]
        chunk_name = cache_path / f"{stem}_chunk{i:03}.mp3"
        chunk.export(chunk_name, format="mp3")
        chunks.append(str(chunk_name))

    return chunks


def whisper_api_transcribe(
    chunks: Iterable[str],
    api_key: str,
    custom_prompt: str = "Here is the full text, in English:",
    model: str = DEFAULT_OPENAI_TRANSCRIBE_MODEL,
) -> str:
    """Transcribe one or more chunks with OpenAI's speech-to-text API."""
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "OpenAI transcription requires the 'openai' package"
        ) from exc

    client = OpenAI(api_key=api_key)
    transcriptions = []

    for chunk in chunks:
        print(f"Transcribing {chunk}")
        with open(chunk, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                prompt=custom_prompt,
            )
        transcriptions.append(response.text)

    return " ".join(transcriptions).strip()


def transcribe_audio(
    file_path: str,
    api_key: str,
    custom_prompt: str = "Here is the full text, in English:",
    cache_dir: str = "./cache",
    model: str = DEFAULT_OPENAI_TRANSCRIBE_MODEL,
) -> str:
    """Transcribe audio and transparently chunk files over OpenAI's size limit."""
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    chunks = split_audio(file_path, cache_dir=cache_dir) if file_size_mb > 25 else [file_path]
    return whisper_api_transcribe(chunks, api_key, custom_prompt=custom_prompt, model=model)


def handle_audio(
    audio_filepath: str,
    api_key: str,
    custom_prompt: str,
    transcript_output_dir: str,
    cache_dir: str = "./cache",
    config_file: str = "config.yaml",
) -> None:
    """Transcribe an audio file and persist the transcript to markdown."""
    with open(config_file, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    stt_engine = config.get("bot", {}).get("stt_engine", "openai")
    openai_model = config.get("bot", {}).get("stt_model", DEFAULT_OPENAI_TRANSCRIBE_MODEL)

    audio_filename = os.path.basename(audio_filepath)
    simplified_filename = audio_filename.split("-")[0]

    print(f"Handling file: {audio_filename}")

    now = datetime.now()
    year_month_path = os.path.join(transcript_output_dir, now.strftime("%Y"), now.strftime("%m"))
    os.makedirs(year_month_path, exist_ok=True)

    transcript_path = os.path.join(year_month_path, f"{simplified_filename}.md")
    if os.path.exists(transcript_path):
        print(f"Skipping duplicate file: {audio_filename}")
        return

    if stt_engine == "whisper":
        whisper_model = config.get("bot", {}).get("local_whisper_model", "base")
        transcription_result = whisper_local_transcribe(
            audio_filepath,
            model=whisper_model,
            custom_prompt=custom_prompt,
        )
    else:
        transcription_result = transcribe_audio(
            audio_filepath,
            api_key,
            custom_prompt=custom_prompt,
            cache_dir=cache_dir,
            model=openai_model,
        )

    handle_transcript(
        transcription_result,
        transcript_output_dir,
        simplified_filename,
        config_file=config_file,
    )
    print(f"Processed and handled file: {audio_filename}")


def handle_transcript(
    transcript_text: str,
    transcript_output_dir: str,
    simplified_filename: str,
    year_month_folders: bool = True,
    config_file: str = "config.yaml",
) -> str:
    """Write transcript text to markdown and optionally trigger GPT follow-up."""
    if year_month_folders:
        now = datetime.now()
        transcript_output_dir = os.path.join(transcript_output_dir, now.strftime("%Y"), now.strftime("%m"))
        os.makedirs(transcript_output_dir, exist_ok=True)

    transcript_path = os.path.join(transcript_output_dir, f"{simplified_filename}.md")
    with open(transcript_path, "w", encoding="utf-8") as transcript_file:
        transcript_file.write(transcript_text)

    print(f"Transcript written to {transcript_path}")

    if testforword(transcript_text, "prompt|from|prom"):
        print("Transcript contains prompt")
        prompt = transcript_text.lower().split("prompt", 1)[1]
        prompt = prompt.replace(".", "").replace(",", "").strip()
        ee = EphemerEar(config_file)
        ee.gpt_chat(prompt)

    return transcript_text


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcribe an audio file with EphemerEar")
    parser.add_argument("audio_file", help="Path to the recording to transcribe")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML")
    parser.add_argument("--prompt", default="", help="Optional transcription prompt")
    return parser


def main() -> None:
    args = _build_arg_parser().parse_args()
    ee = EphemerEar(args.config)
    handle_audio(
        audio_filepath=args.audio_file,
        api_key=ee.api_key,
        custom_prompt=args.prompt,
        transcript_output_dir=ee.config["stores"]["transcripts"],
        cache_dir=ee.config["bot"]["cache"],
        config_file=args.config,
    )


if __name__ == "__main__":
    main()
