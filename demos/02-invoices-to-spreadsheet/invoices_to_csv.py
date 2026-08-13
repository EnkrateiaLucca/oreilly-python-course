# /// script
# requires-python = ">=3.12"
# dependencies = ["openai", "pydantic", "pypdf", "python-dotenv"]
# ///
"""Turn a folder of invoices (PDF or text) into one clean CSV.

THE core pattern of this course: unstructured mess in -> typed structure out.

Input   -> a folder of invoice files (.pdf or .txt)
Process -> ask the AI to fill a Pydantic schema (vendor, number, date, total...)
           for each file; the schema FORCES valid, typed output
Output  -> a table printed to the terminal; with --apply, an invoices.csv file

Run it like:
    uv run demos/02-invoices-to-spreadsheet/invoices_to_csv.py invoices
    uv run demos/02-invoices-to-spreadsheet/invoices_to_csv.py invoices --apply

Needs: OPENAI_API_KEY in the repo-root .env file.
"""

import argparse
import csv
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
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


# The schema IS the spec: field names, types, and descriptions the model must fill.
# This is how you make AI output boring and reliable instead of chatty.
class InvoiceFields(BaseModel):
    vendor: str = Field(description="Company that issued the invoice")
    invoice_number: str = Field(description="Invoice number or ID")
    invoice_date: str = Field(description="Issue date, as printed on the invoice")
    total_amount: float = Field(description="Final total including tax")
    currency: str = Field(description="Currency code or symbol, e.g. USD or EUR")


def read_invoice_text(path: Path) -> str:
    """PDFs need extraction; .txt files are already text."""
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="replace")


def extract_fields(client: OpenAI, text: str) -> InvoiceFields:
    # .parse() + response_format=<Pydantic model> = structured output: the API
    # guarantees the reply matches the schema (or refuses) — no regex, no hoping.
    completion = client.chat.completions.parse(
        model="gpt-5.6-luna",
        messages=[
            {"role": "system",
             "content": "Extract the requested fields from this invoice text."},
            {"role": "user", "content": text},
        ],
        response_format=InvoiceFields,
    )
    return completion.choices[0].message.parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract invoice fields from a folder into CSV.")
    parser.add_argument("folder", help="Folder containing .pdf/.txt invoices, e.g. invoices")
    parser.add_argument("--output", default="invoices.csv",
                        help="CSV file to write with --apply (default: invoices.csv)")
    parser.add_argument("--apply", action="store_true",
                        help="Write the CSV file (default: print the table only)")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    files = sorted(p for p in folder.glob("*") if p.suffix.lower() in (".pdf", ".txt"))
    if not files:
        print(f"No .pdf or .txt invoices found in: {folder}")
        sys.exit(1)

    require_key("OPENAI_API_KEY", "https://platform.openai.com/api-keys")
    client = OpenAI()

    rows = []
    for path in files:
        print(f"Reading {path.name} ...")
        fields = extract_fields(client, read_invoice_text(path))
        rows.append({"file": path.name, **fields.model_dump()})

    # Show the result as a small table either way — that's the proof step.
    columns = list(rows[0].keys())
    print()
    print(" | ".join(columns))
    for row in rows:
        print(" | ".join(str(row[c]) for c in columns))

    if not args.apply:
        print(f"\nDry run: no file written. Re-run with --apply to save {args.output}")
        return

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
