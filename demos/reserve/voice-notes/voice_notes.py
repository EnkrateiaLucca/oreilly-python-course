# /// script
# requires-python = ">=3.12"
# dependencies = ["faster-whisper", "anthropic", "python-dotenv"]
# ///
"""Turn a voice note into a transcript plus an AI summary with action items.

Input   -> an audio file (mp3, wav, m4a, ...)
Process -> transcribe LOCALLY with faster-whisper (free, private, no key),
           then ask Claude for a short summary and action items
Output  -> transcript + summary printed; with --apply, saved next to the audio

Run it like:
    uv run demos/reserve/voice-notes/voice_notes.py audio-sample.mp3
    uv run demos/reserve/voice-notes/voice_notes.py audio-sample.mp3 --apply
    uv run demos/reserve/voice-notes/voice_notes.py audio-sample.mp3 --no-summary

Needs: ANTHROPIC_API_KEY in the repo-root .env (skip it with --no-summary).
The first run downloads the Whisper model (~250 MB), then it's cached.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]


def require_key(name: str, where: str) -> str:
    """Load .env from the repo root, fall back to the environment, or explain the fix."""
    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get(name)
    if not key:
        print(f"No {name} found.")
        print(f"1) Get a key at {where}")
        print(f"2) Add this line to {REPO_ROOT / '.env'}:  {name}=your-key-here")
        sys.exit(1)
    return key


def transcribe(audio: Path, model_size: str) -> str:
    """Speech -> text, entirely on your machine. The audio never leaves it."""
    from faster_whisper import WhisperModel  # imported here: it's a heavy import

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(audio), vad_filter=True)
    print(f"Detected language: {info.language} "
          f"(confidence {info.language_probability:.0%})\n")
    return "\n".join(segment.text.strip() for segment in segments)


def summarize(transcript: str) -> str:
    """Ask Claude for a summary + action items. Only the TEXT is sent, not audio."""
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": ("Summarize this voice note in 2-3 sentences, then list "
                        "any action items as '- [ ]' checkboxes. If there are "
                        f"none, say so.\n\nTranscript:\n{transcript}"),
        }],
    )
    # Claude replies with a list of content blocks; we keep only the text ones.
    return "".join(block.text for block in response.content if block.type == "text")


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe a voice note and summarize it with AI.")
    parser.add_argument("audio", help="Path to the audio file, e.g. audio-sample.mp3")
    parser.add_argument("--model", default="small",
                        help="Whisper size: tiny, base, small, medium (default: small)")
    parser.add_argument("--no-summary", action="store_true",
                        help="Transcribe only — fully local, no API key needed")
    parser.add_argument("--apply", action="store_true",
                        help="Save .transcript.txt / .summary.md next to the audio")
    args = parser.parse_args()

    audio = Path(args.audio).expanduser()
    if not audio.exists():
        print(f"Audio file not found: {audio}")
        sys.exit(1)

    # Fail fast: check the key BEFORE the slow transcription step.
    if not args.no_summary:
        require_key("ANTHROPIC_API_KEY", "https://console.anthropic.com/settings/keys")

    transcript = transcribe(audio, args.model)
    print("--- Transcript ---")
    print(transcript)

    summary = ""
    if not args.no_summary:
        summary = summarize(transcript)
        print("\n--- Summary ---")
        print(summary)

    if not args.apply:
        print("\nDry run: nothing saved. Re-run with --apply to write the files.")
        return

    transcript_file = audio.with_suffix(".transcript.txt")
    transcript_file.write_text(transcript + "\n", encoding="utf-8")
    print(f"\nSaved {transcript_file}")
    if summary:
        summary_file = audio.with_suffix(".summary.md")
        summary_file.write_text(summary + "\n", encoding="utf-8")
        print(f"Saved {summary_file}")


if __name__ == "__main__":
    main()
