# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "pydantic", "pypdf", "python-dotenv"]
# ///
"""Turn a messy folder of documents into one clean, structured action queue.

THE core pattern of this course: unstructured multimodal mess in -> typed structure out.
An invoice, a meeting note, a renewal notice, a receipt, a screenshot — all different
shapes on the way in, all the same tidy row on the way out.

Input   -> a folder of mixed documents (.pdf .txt .md, and images .png/.jpg/.jpeg)
Process -> ask the AI to fill ONE Pydantic schema per document (type, summary,
           priority, dates, people, action items); the schema FORCES typed output
Output  -> a table printed to the terminal; with --apply, an inbox.csv (or --format md)

Run it like:
    uv run demos/01-document-inbox/document_inbox.py inbox
    uv run demos/01-document-inbox/document_inbox.py inbox --apply
    uv run demos/01-document-inbox/document_inbox.py inbox --format md --apply

Needs: OPENAI_API_KEY in the repo-root .env file.
"""

import argparse
import base64
import csv
import os
import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[2]
TEXT_TYPES = (".pdf", ".txt", ".md")
IMAGE_TYPES = (".png", ".jpg", ".jpeg")


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


# The schema IS the spec: field names, types, and descriptions the model must fill.
# This is how you turn any document into the same boring, reliable row.
class DocumentCard(BaseModel):
    document_type: str = Field(description="Kind of document, e.g. invoice, receipt, "
                                           "meeting note, letter, contract, screenshot")
    summary: str = Field(description="One-sentence summary of what this document is")
    priority: Literal["high", "medium", "low"] = Field(
        description="How urgently a human must act: high if money or a deadline is at stake")
    key_dates: list[str] = Field(description="Important dates as written, e.g. due dates, "
                                             "deadlines, meeting dates (empty if none)")
    people: list[str] = Field(description="Names of people or organizations mentioned")
    action_items: list[str] = Field(description="Concrete things a human should do next "
                                                 "(empty if the document needs no action)")


def read_text(path: Path) -> str:
    """PDFs need extraction; .txt/.md files are already text."""
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="replace")


def build_content(path: Path) -> list:
    """Text docs go in as text; images go in as a base64 data URL for the vision model."""
    instruction = "Analyze this document and fill in the requested fields."
    if path.suffix.lower() in IMAGE_TYPES:
        data = base64.b64encode(path.read_bytes()).decode()
        suffix = path.suffix.lower().lstrip(".").replace("jpg", "jpeg")
        return [
            {"type": "text", "text": instruction},
            {"type": "image_url",
             "image_url": {"url": f"data:image/{suffix};base64,{data}"}},
        ]
    return [{"type": "text", "text": f"{instruction}\n\n{read_text(path)}"}]


def analyze(client: OpenAI, path: Path, model: str) -> DocumentCard:
    # .parse() + response_format=<Pydantic model> = structured output: the API
    # guarantees the reply matches the schema (or refuses) — no regex, no hoping.
    completion = client.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system",
             "content": "You triage documents into a structured action queue."},
            {"role": "user", "content": build_content(path)},
        ],
        response_format=DocumentCard,
    )
    return completion.choices[0].message.parsed


def to_row(path: Path, card: DocumentCard) -> dict:
    """Flatten one card into a single spreadsheet row (lists become '; ' text)."""
    data = card.model_dump()
    for field in ("key_dates", "people", "action_items"):
        data[field] = "; ".join(data[field])
    return {"file": path.name, **data}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Triage a folder of documents into one structured action queue.")
    parser.add_argument("folder", help="Folder of documents, e.g. inbox")
    parser.add_argument("--model", default="gpt-5.6-luna",
                        help="Model to use (default: gpt-5.6-luna)")
    parser.add_argument("--format", choices=("csv", "md"), default="csv",
                        help="Output format written with --apply (default: csv)")
    parser.add_argument("--output", default=None,
                        help="Output file for --apply (default: inbox.csv / inbox.md)")
    parser.add_argument("--apply", action="store_true",
                        help="Write the file (default: print the table only)")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    files = sorted(p for p in folder.glob("*")
                   if p.suffix.lower() in TEXT_TYPES + IMAGE_TYPES)
    if not files:
        print(f"No documents (.pdf .txt .md .png .jpg) found in: {folder}")
        sys.exit(1)

    require_key("OPENAI_API_KEY", "https://platform.openai.com/api-keys")
    client = OpenAI()

    rows = []
    for path in files:
        print(f"Reading {path.name} ...")
        rows.append(to_row(path, analyze(client, path, args.model)))

    # Show the result as a small table either way — that's the proof step.
    columns = list(rows[0].keys())
    print()
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(row[c]) for c in columns))

    if not args.apply:
        print("\nDry run: no file written. Re-run with --apply to save the queue.")
        return

    out = Path(args.output) if args.output else Path(f"inbox.{args.format}")
    if args.format == "md":
        lines = ["| " + " | ".join(columns) + " |",
                 "| " + " | ".join("---" for _ in columns) + " |"]
        lines += ["| " + " | ".join(str(r[c]) for c in columns) + " |" for r in rows]
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
