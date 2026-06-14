# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "faster-whisper",
# ]
# ///
"""Transcribe an audio file to text locally with Whisper (no API key).

Automation category: Media + AI (local).

Input   -> an audio file (mp3, wav, m4a, ...)
Process -> run faster-whisper on the CPU to transcribe speech to text
Output  -> the transcript printed to the console and saved to a text file

Run it like:
    uv run scripts/demos/media/transcribe_audio.py audio.mp3
    uv run scripts/demos/media/transcribe_audio.py audio.mp3 --model base --output out.txt

Needs: nothing (runs locally; the first run downloads the chosen Whisper model).
"""

from pathlib import Path
import argparse

from faster_whisper import WhisperModel


def transcribe_audio(
    audio_path: str,
    model_size: str = "small",
    output_path: str | None = None,
):
    audio_file = Path(audio_path)

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # Good beginner default:
    # - device="cpu" works almost everywhere
    # - compute_type="int8" uses less memory
    model = WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",
    )

    segments, info = model.transcribe(
        str(audio_file),
        beam_size=5,
        vad_filter=True,  # skips long silent parts
    )

    print(f"Detected language: {info.language}")
    print(f"Language probability: {info.language_probability:.2f}")
    print()

    transcript_lines = []

    for segment in segments:
        line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text.strip()}"
        print(line)
        transcript_lines.append(line)

    if output_path:
        Path(output_path).write_text("\n".join(transcript_lines), encoding="utf-8")
        print(f"\nSaved transcript to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Free local audio transcription with Whisper.")
    parser.add_argument("audio", help="Path to audio file, e.g. audio.mp3")
    parser.add_argument("--model", default="small", help="tiny, base, small, medium, large-v3")
    parser.add_argument("--output", default="transcript.txt", help="Output text file")

    args = parser.parse_args()

    transcribe_audio(
        audio_path=args.audio,
        model_size=args.model,
        output_path=args.output,
    )
