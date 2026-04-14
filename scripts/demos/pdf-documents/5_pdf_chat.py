# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.99.2",
#   "prompt_toolkit>=3.0.52",
#   "pdfplumber>=0.11.0",
#   "pandas>=2.2.0",
#   "rich>=13.7.0",
#   "tabulate>=0.9.0",
# ]
# ///
"""
chat_with_pdfs_extract.py

A standalone terminal chat app that:

1) Loads a PDF into memory (raw text + detected tables).
2) Asks the user what to extract.
3) Confirms the extraction request.
4) Uses GPT-5 via the OpenAI Responses API to produce a CSV.
5) Previews the CSV and saves it locally on approval.

Run:
  uv run chat_with_pdfs_extract.py /path/to/file.pdf

Requires:
  export OPENAI_API_KEY="sk-..."
"""
from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Any

import pandas as pd
import pdfplumber
from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel

console = Console()


# ---------------------------
# PDF loading / preprocessing
# ---------------------------

@dataclass
class PDFContext:
    path: Path
    raw_text: str
    tables: List[pd.DataFrame]
    tables_markdown: str


def load_pdf(path: Path, max_chars: int = 120_000) -> PDFContext:
    """
    Load a PDF and return:
      - raw_text: concatenated text per page (possibly truncated)
      - tables: list of DataFrames extracted by pdfplumber
      - tables_markdown: markdown previews of those tables

    Table extraction is best-effort: some PDFs won't yield tables.
    """
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    raw_parts: List[str] = []
    tables: List[pd.DataFrame] = []

    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if text.strip():
                raw_parts.append(f"\n\n--- Page {i+1} ---\n{text}")

            # Best-effort table extraction per page.
            try:
                page_tables = page.extract_tables() or []
                for t in page_tables:
                    if not t or len(t) < 2:
                        continue
                    header = t[0]
                    body = t[1:]
                    df = pd.DataFrame(body, columns=header).dropna(axis=1, how="all")
                    if df.shape[1] > 0:
                        tables.append(df)
            except Exception:
                continue

    raw_text = "".join(raw_parts).strip()

    if len(raw_text) > max_chars:
        head = raw_text[: max_chars // 2]
        tail = raw_text[-max_chars // 2 :]
        raw_text = head + "\n\n[TRUNCATED ...]\n\n" + tail

    tables_md = tables_to_markdown(tables)

    return PDFContext(path=path, raw_text=raw_text, tables=tables, tables_markdown=tables_md)


def tables_to_markdown(tables: List[pd.DataFrame], max_rows: int = 15) -> str:
    """
    Convert extracted tables to markdown previews.

    Uses DataFrame.to_markdown if tabulate is available.
    Falls back to a simple pipe-table renderer if not.
    """
    md_parts = []
    for idx, df in enumerate(tables, start=1):
        preview = df.head(max_rows)

        try:
            md_table = preview.to_markdown(index=False)
        except ImportError:
            # Fallback renderer without tabulate.
            cols = [str(c) for c in preview.columns]
            rows = preview.fillna("").astype(str).values.tolist()

            header = "| " + " | ".join(cols) + " |"
            sep = "| " + " | ".join(["---"] * len(cols)) + " |"
            body = "\n".join("| " + " | ".join(r) + " |" for r in rows)

            md_table = "\n".join([header, sep, body])

        md_parts.append(f"\n\n### Table {idx}\n{md_table}")
    return "".join(md_parts).strip()


# ---------------------------
# OpenAI helpers
# ---------------------------

def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set. Please export it before running.")
    return OpenAI(api_key=api_key)


def response_text(resp: Any) -> str:
    """Extract concatenated text from a Responses API response."""
    out: List[str] = []
    for item in getattr(resp, "output", []):
        content = getattr(item, "content", None)
        if content:
            for c in content:
                txt = getattr(c, "text", None)
                if txt:
                    out.append(txt)
    return "".join(out).strip()


def ask_model(
    client: OpenAI,
    model: str,
    messages: List[dict],
    previous_response_id: Optional[str] = None,
    reasoning_effort: str = "minimal",
    text_format: str = "text",
) -> Tuple[str, str]:
    """
    Call the Responses API with a list of message items.
    Returns (text, response_id).
    """
    kwargs: dict = {
        "model": model,
        "input": messages,
        "text": {"format": {"type": text_format}},
        "reasoning": {"effort": reasoning_effort},
    }
    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id

    resp = client.responses.create(**kwargs)
    return response_text(resp), resp.id


# ---------------------------
# Chat UI + workflow
# ---------------------------

STYLE = Style.from_dict({"user": "#00aa00 bold", "assistant": "#0088ff bold"})

YES_RE = re.compile(r"^(y|yes|ok|okay|sure|go ahead|approve)\b", re.I)
NO_RE = re.compile(r"^(n|no|nope|cancel|stop)\b", re.I)


def print_assistant(msg: str) -> None:
    console.print(Panel(msg, title="Assistant", border_style="blue"))


def print_user(msg: str) -> None:
    console.print(Panel(msg, title="You", border_style="green"))


def preview_csv(csv_text: str, max_rows: int = 20) -> pd.DataFrame:
    """
    Parse CSV text into a DataFrame and print a short preview.
    Raises if the CSV is invalid.
    """
    from io import StringIO

    df = pd.read_csv(StringIO(csv_text.strip()))
    console.print("\n[bold]Preview (first rows):[/bold]")
    console.print(df.head(max_rows))
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with GPT-5 to extract CSV from a PDF.")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file.")
    parser.add_argument("--model", default="gpt-5", help="OpenAI model to use (default: gpt-5).")
    parser.add_argument("--max-chars", type=int, default=120_000, help="Max PDF chars to send to model.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path).expanduser().resolve()
    console.print(f"[bold]Loading PDF:[/bold] {pdf_path}")
    ctx = load_pdf(pdf_path, max_chars=args.max_chars)
    console.print(f"[bold]Loaded PDF.[/bold] Extracted {len(ctx.tables)} tables.")

    client = get_client()
    session = PromptSession(history=InMemoryHistory(), style=STYLE)

    # Step 1: Ask user what to extract.
    print_assistant(
        "PDF loaded! What would you like to extract?\n"
        "Describe the table(s) or fields you want, and any filters.\n"
        "Example: Extract all invoice line items with columns Date, Vendor, Amount."
    )
    user_request = session.prompt(HTML("<user>You > </user> "))
    print_user(user_request)

    # Step 2: Model confirms requirement.
    confirm_messages = [
        {
            "role": "developer",
            "content": (
                "You are a careful data-extraction assistant. "
                "Restate the user's extraction request clearly, "
                "ask any missing questions, and end by asking for confirmation. "
                "Keep it short."
            ),
        },
        {"role": "user", "content": user_request},
    ]
    confirm_text, _ = ask_model(client, args.model, confirm_messages)
    print_assistant(confirm_text)

    approval = session.prompt(HTML("<user>Approve? (y/n) > </user> "))
    print_user(approval)
    if NO_RE.match(approval):
        print_assistant("Okay — cancelled. Re-run the script to try a different request.")
        return

    # Step 3: Extraction.
    extraction_messages = [
        {
            "role": "developer",
            "content": (
                "You extract structured data from PDFs. "
                "You will be given raw text and markdown previews of detected tables. "
                "Return ONLY a CSV (comma-separated) with a header row. "
                "Do not include commentary or code fences. "
                "If you are unsure, still produce your best CSV with empty cells where needed."
            ),
        },
        {
            "role": "user",
            "content": (
                f"The user wants:\n{user_request}\n\n"
                f"PDF raw text:\n{ctx.raw_text}\n\n"
                f"Detected tables (markdown previews):\n{ctx.tables_markdown or '[none detected]'}"
            ),
        },
    ]
    csv_text, _ = ask_model(client, args.model, extraction_messages, reasoning_effort="minimal")

    print_assistant("Here is the extracted CSV. I'll preview it below:")
    try:
        df = preview_csv(csv_text)
    except Exception as e:
        print_assistant(
            "I couldn't parse the model output as CSV.\n"
            f"Error: {e}\n\nRaw output:\n{csv_text}"
        )
        return

    # Step 4: Save on approval.
    save_ans = session.prompt(HTML("<user>Save this as CSV? (y/n) > </user> "))
    print_user(save_ans)
    if not YES_RE.match(save_ans):
        print_assistant("No problem — not saved.")
        return

    out_name = f"{pdf_path.stem}_extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    out_path = pdf_path.parent / out_name
    df.to_csv(out_path, index=False)
    print_assistant(f"Saved CSV to: {out_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")