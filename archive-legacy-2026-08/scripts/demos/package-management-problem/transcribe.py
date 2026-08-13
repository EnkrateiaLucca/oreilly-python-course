#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["faster-whisper>=1.1.0", "rich>=13.7.0"]
# ///

DESCRIPTION = """
Free local audio/video transcription using Faster Whisper.
Run with: uv run transcribe.py path/to/audio_or_video_file.mp4
"""

import argparse
from pathlib import Path
from datetime import timedelta

from faster_whisper import WhisperModel
from rich.console import Console
from rich.progress import track


console = Console()


def format_timestamp(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    ms = int((seconds - int(seconds)) * 1000)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def write_txt(segments, output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as f:
        for segment in segments:
            f.write(segment.text.strip() + "\n")


def write_srt(segments, output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(
                f"{format_timestamp(segment.start)} --> "
                f"{format_timestamp(segment.end)}\n"
            )
            f.write(segment.text.strip() + "\n\n")


def transcribe(
    input_file: Path,
    model_size: str,
    language: str | None,
    output_dir: Path,
) -> None:
    if not input_file.exists():
        raise FileNotFoundError(f"File not found: {input_file}")

    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold]Loading model:[/bold] {model_size}")

    model = WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",
    )

    console.print(f"[bold]Transcribing:[/bold] {input_file}")

    segments_iter, info = model.transcribe(
        str(input_file),
        language=language,
        beam_size=5,
        vad_filter=True,
    )

    segments = list(track(segments_iter, description="Processing..."))

    base_name = input_file.stem
    txt_path = output_dir / f"{base_name}.txt"
    srt_path = output_dir / f"{base_name}.srt"

    write_txt(segments, txt_path)
    write_srt(segments, srt_path)

    console.print()
    console.print(f"[green]Done.[/green] Detected language: {info.language}")
    console.print(f"TXT: {txt_path}")
    console.print(f"SRT: {srt_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe audio/video files locally for free using Faster Whisper."
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to an audio or video file.",
    )

    parser.add_argument(
        "--model",
        default="small",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size. Default: small.",
    )

    parser.add_argument(
        "--language",
        default=None,
        help="Optional language code, e.g. en, pt, fr. If omitted, auto-detects.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("transcripts"),
        help="Directory where transcript files are saved. Default: transcripts/",
    )

    args = parser.parse_args()

    console.print(DESCRIPTION.strip())
    transcribe(
        input_file=args.file,
        model_size=args.model,
        language=args.language,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()