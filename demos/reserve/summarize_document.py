# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "pypdf", "python-dotenv"]
# ///
"""Summarize a PDF, text or Markdown file into bullet points with AI.

Input   -> a path to a .pdf, .txt or .md file
Process -> extract the text, ask the AI to compress it into bullet points
Output  -> the summary printed to the console (read-only: writes nothing)

Run it like:
    uv run demos/reserve/summarize_document.py report.pdf
    uv run demos/reserve/summarize_document.py notes.md

Needs: OPENAI_API_KEY in the repo-root .env file.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

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


def load_text(path: Path) -> str:
    """Route by extension: PDFs need extraction, txt/md are already text."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="replace")
    print(f"Unsupported file type: '{suffix}' (use .pdf, .txt or .md)")
    sys.exit(1)


def summarize(text: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[{
            "role": "user",
            "content": ("Summarize the following document into compressed, "
                        f"instructive bullet points:\n\n{text}"),
        }],
    )
    return response.choices[0].message.content


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a document into bullet points with AI.")
    parser.add_argument("file", help="Path to a .pdf, .txt or .md file")
    args = parser.parse_args()

    path = Path(args.file).expanduser()
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    require_key("OPENAI_API_KEY", "https://platform.openai.com/api-keys")

    text = load_text(path)
    if not text.strip():
        print("No text could be extracted. A scanned PDF needs OCR first.")
        sys.exit(1)

    print(f"Summarizing {path.name} ({len(text)} characters)...\n")
    print(summarize(text))


if __name__ == "__main__":
    main()
