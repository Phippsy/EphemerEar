"""Hazel entrypoint.

Usage from Hazel rule:
python /path/to/EphemerEar/ephemerear/hazel-transcription.py "$1"

Set EPHEMEREAR_CONFIG to point at your config file.
"""

from __future__ import annotations

import datetime
import os
import sys

from ephemerear.EphemerEar import EphemerEar
from ephemerear.transcribe import handle_audio


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: hazel-transcription.py <audio-file>")

    audio_filename = sys.argv[1]
    config_path = os.environ.get("EPHEMEREAR_CONFIG", "config.yaml")

    print(f"Running at {datetime.datetime.now()} on filename {audio_filename}")
    ee = EphemerEar(config_path)

    if ee.notify:
        ee.send_pushover(
            "ephemerear transcription started",
            f"Running transcription on {audio_filename}",
            ee.pushover_user,
            ee.pushover_key,
        )

    handle_audio(
        audio_filepath=audio_filename,
        api_key=ee.api_key,
        custom_prompt="",
        transcript_output_dir=ee.config["stores"]["transcripts"],
        cache_dir=ee.config["bot"]["cache"],
        config_file=config_path,
    )

    if ee.notify:
        ee.send_pushover(
            "Transcription complete",
            f"Transcription of {audio_filename} is complete",
            ee.pushover_user,
            ee.pushover_key,
        )


if __name__ == "__main__":
    main()
