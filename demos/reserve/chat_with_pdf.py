# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "pypdf", "python-dotenv"]
# ///
"""Chat with a PDF in your terminal: ask questions, get answers from ITS text.

Input   -> a PDF file (its text is loaded into the conversation once)
Process -> an interactive loop; each question goes to the AI with the PDF text
Output  -> answers in the terminal, grounded in the document (read-only)

Run it like:
    uv run demos/reserve/chat_with_pdf.py report.pdf

Type your questions at the prompt; 'exit' (or Ctrl+C) quits.
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
MAX_CHARS = 120_000  # keep very large PDFs within the model's context window


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


def load_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if len(text) > MAX_CHARS:
        # Keep the start and the end; the middle is usually the most skippable.
        text = text[: MAX_CHARS // 2] + "\n\n[... TRUNCATED ...]\n\n" + text[-MAX_CHARS // 2:]
    return text


def chat_loop(client: OpenAI, pdf_name: str, pdf_text: str) -> None:
    # The whole document rides along as the system message; every question is
    # then answered "with the PDF open" rather than from the model's memory.
    messages = [{
        "role": "system",
        "content": ("Answer using ONLY this document. If the answer is not in it, "
                    f"say so plainly.\n\n--- {pdf_name} ---\n{pdf_text}\n--- END ---"),
    }]

    print("PDF loaded. Ask a question, or type 'exit' to quit.\n")
    while True:
        try:
            question = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        messages.append({"role": "user", "content": question})
        response = client.chat.completions.create(model="gpt-5.6-luna", messages=messages)
        answer = response.choices[0].message.content
        # Remembering the assistant's answers is what makes it a conversation.
        messages.append({"role": "assistant", "content": answer})
        print(f"\nai  > {answer}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive Q&A with a PDF in your terminal.")
    parser.add_argument("pdf", help="Path to the PDF file")
    args = parser.parse_args()

    path = Path(args.pdf).expanduser()
    if not path.exists():
        print(f"PDF not found: {path}")
        sys.exit(1)

    require_key("OPENAI_API_KEY", "https://platform.openai.com/api-keys")

    text = load_pdf_text(path)
    if not text.strip():
        print("No text could be extracted. A scanned PDF needs OCR first.")
        sys.exit(1)

    print(f"Loaded {path.name} ({len(text)} characters).")
    chat_loop(OpenAI(), path.name, text)


if __name__ == "__main__":
    main()
