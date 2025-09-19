# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pdfplumber>=0.11",
#   "pydantic>=2.7",
#   "openai>=1.51",
#   "tqdm>=4.66",
#   "python-slugify>=8.0",
#   "docling>=2.5"  # optional; if unavailable, we fall back to pdfplumber
# ]
# ///
"""
Usage
-----
uv run extract_tables_llm.py input1.pdf [input2.pdf ...] \
  --out out_dir --engine [auto|docling|pdfplumber] --model gpt-4o-mini --per-table

What it does
------------
- Extracts per-page text from each PDF (Docling if available/selected; else pdfplumber).
- Sends text chunks to OpenAI with Pydantic Structured Outputs to detect & normalize tables.
- Writes each detected table as CSV (default), plus a summary JSONL of provenance.

Notes
-----
[Unverified] LLM parsing of tables from plain text can be imperfect (merged cells, wrapped lines).
Prefer for quick prototyping / weakly-structured docs. For production-grade table extraction,
use lattice/stream parsers (Camelot/Tabula) or Docling’s native table objects directly.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

import pdfplumber
from pydantic import BaseModel, Field, ValidationError
from slugify import slugify
from tqdm import tqdm

# OpenAI (new SDK style)
from openai import OpenAI

# -----------------------------
# Pydantic schemas (Structured Outputs)
# -----------------------------

class TableCell(BaseModel):
    value: str = Field(..., description="Raw cell text without surrounding quotes.")


class TableRow(BaseModel):
    cells: List[TableCell] = Field(..., description="Row cells, keep column order.")


class DetectedTable(BaseModel):
    title: Optional[str] = Field(None, description="Optional short title or caption if present nearby.")
    page: int = Field(..., description="1-based page number where this table appears.")
    columns: List[str] = Field(..., description="Header names; if missing, synthesize short, neutral headers.")
    rows: List[TableRow] = Field(..., description="Body rows; each row length should match columns length.")
    source_span: Optional[str] = Field(
        None, description="Short snippet of the text region used to infer this table."
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Heuristic confidence (0-1) that this is a correct table parse."
    )


class TablesBundle(BaseModel):
    tables: List[DetectedTable] = Field(default_factory=list)
    notes: Optional[str] = Field(
        None, description="Any caveats or formatting decisions made during parsing."
    )


# -----------------------------
# Prompt for the model
# -----------------------------
SYSTEM_PROMPT = """You extract tables from noisy plain text.
Rules:
- Only return actual tabular data (records with consistent columns).
- If headers are unclear, infer short neutral headers (e.g., col_1, col_2, ...).
- Keep rows aligned with headers; trim whitespace; do not invent values.
- If a number is split across lines, join it.
- If you cannot reliably reconstruct a table from the text, omit it.
- Provide a confidence score per table (0..1).
"""

USER_PROMPT_TEMPLATE = """Extract all reliable tables from the following text (page {page_num} of a PDF). 
Return nothing if no table can be confidently reconstructed.

--- BEGIN TEXT ---
{page_text}
--- END TEXT ---
"""


# -----------------------------
# Text extraction engines
# -----------------------------
def extract_text_pdfplumber(path: Path) -> List[str]:
    """Return list of page texts (1 string per page)."""
    pages: List[str] = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            txt = p.extract_text() or ""
            pages.append(txt)
    return pages


def extract_text_docling(path: Path) -> List[str]:
    """
    [Unverified] Minimal Docling text extraction.
    If docling is not installed or fails, raise ImportError to let caller fallback.
    """
    try:
        from docling.document_converter import DocumentConverter  # type: ignore
    except Exception as e:  # pragma: no cover
        raise ImportError("docling not available") from e

    converter = DocumentConverter()
    result = converter.convert(str(path))
    # Concatenate text blocks per page if available; fallback to whole text split.
    # [Unverified] API surfaces may differ across versions.
    if hasattr(result, "document") and hasattr(result.document, "pages"):
        pages = []
        for i, page in enumerate(result.document.pages, start=1):
            blocks = []
            for b in getattr(page, "blocks", []):
                t = getattr(b, "text", "")
                if t:
                    blocks.append(t)
            pages.append("\n".join(blocks))
        return pages
    # Fallback: split by form-feed if present
    text_all = getattr(result, "text", "") or ""
    return text_all.split("\f") if "\f" in text_all else [text_all]


# -----------------------------
# Chunking (simple: page-by-page)
# -----------------------------
def iter_page_chunks(pages: List[str]) -> List[Dict[str, Any]]:
    """Yield dicts: {'page_num': int, 'text': str} for non-empty pages."""
    out: List[Dict[str, Any]] = []
    for i, t in enumerate(pages, start=1):
        clean = (t or "").strip()
        if clean:
            out.append({"page_num": i, "text": clean})
    return out


# -----------------------------
# LLM call (Structured Outputs)
# -----------------------------
def extract_tables_from_text(
    client: OpenAI, model: str, page_num: int, text: str
) -> TablesBundle:
    user_prompt = USER_PROMPT_TEMPLATE.format(page_num=page_num, page_text=text[:120000])  # crude safety cap
    # Use structured outputs with Pydantic parsing
    try:
        resp = client.responses.parse(
            model=model,
            temperature=0,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=TablesBundle,
        )
        parsed: TablesBundle = resp.parsed  # type: ignore
        # Backfill page numbers in case model omitted them
        for tbl in parsed.tables:
            if not getattr(tbl, "page", None):
                tbl.page = page_num
        return parsed
    except ValidationError as ve:
        # Model returned wrong shape; return empty bundle with note
        return TablesBundle(tables=[], notes=f"ValidationError: {ve}")
    except Exception as e:
        return TablesBundle(tables=[], notes=f"LLM error: {e}")


# -----------------------------
# Write outputs
# -----------------------------
def write_table_csv(out_dir: Path, base: str, idx: int, table: DetectedTable) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{base}_p{table.page:03d}_t{idx:02d}.csv"
    fpath = out_dir / fname
    # CSV write
    with fpath.open("w", encoding="utf-8") as f:
        f.write(",".join(table.columns) + "\n")
        for row in table.rows:
            cells = [c.value.replace("\n", " ").replace(",", " ").strip() for c in row.cells]
            # pad/truncate to columns length
            if len(cells) < len(table.columns):
                cells = cells + [""] * (len(table.columns) - len(cells))
            elif len(cells) > len(table.columns):
                cells = cells[: len(table.columns)]
            f.write(",".join(cells) + "\n")
    return fpath


def write_summary_jsonl(summary_path: Path, records: List[Dict[str, Any]]) -> None:
    with summary_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# -----------------------------
# Main
# -----------------------------
def main():
    ap = argparse.ArgumentParser(description="Extract tables from PDFs via LLM-structured outputs on extracted text.")
    ap.add_argument("inputs", nargs="+", help="One or more PDF files (or directories to scan).")
    ap.add_argument("--out", default="tables_out", help="Output directory (default: tables_out).")
    ap.add_argument("--engine", choices=["auto", "docling", "pdfplumber"], default="auto",
                    help="Text extraction engine (default: auto).")
    ap.add_argument("--model", default="gpt-4o-mini", help="OpenAI model name (default: gpt-4o-mini).")
    ap.add_argument("--per-table", action="store_true", help="Write each table to its own CSV file (default).")
    ap.add_argument("--merge", action="store_true", help="Also write one merged CSV per PDF (union of all tables).")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect PDF files
    pdfs: List[Path] = []
    for inp in args.inputs:
        p = Path(inp)
        if p.is_file() and p.suffix.lower() == ".pdf":
            pdfs.append(p)
        elif p.is_dir():
            pdfs.extend([q for q in p.rglob("*.pdf") if q.is_file()])
        else:
            print(f"[warn] Skipping non-PDF input: {p}")

    if not pdfs:
        print("[error] No PDF files found.")
        raise SystemExit(2)

    # OpenAI client (requires OPENAI_API_KEY in env)
    client = OpenAI()

    summary_records: List[Dict[str, Any]] = []

    for pdf_path in tqdm(pdfs, desc="Processing PDFs"):
        base = slugify(pdf_path.stem) or "document"
        print(f"\n=== {pdf_path.name} ===")

        # Choose engine
        pages: List[str] = []
        use_engine = args.engine
        if use_engine == "auto":
            # Try docling first if installed; else pdfplumber
            try:
                pages = extract_text_docling(pdf_path)
                use_engine = "docling"
            except Exception:
                pages = extract_text_pdfplumber(pdf_path)
                use_engine = "pdfplumber"
        elif use_engine == "docling":
            try:
                pages = extract_text_docling(pdf_path)
            except Exception as e:
                print(f"[warn] Docling failed ({e}); falling back to pdfplumber.")
                pages = extract_text_pdfplumber(pdf_path)
                use_engine = "pdfplumber"
        else:
            pages = extract_text_pdfplumber(pdf_path)

        # Iterate pages -> LLM
        all_tables: List[DetectedTable] = []
        for chunk in iter_page_chunks(pages):
            bundle = extract_tables_from_text(
                client=client, model=args.model, page_num=chunk["page_num"], text=chunk["text"]
            )
            if bundle.notes:
                print(f"[note] {bundle.notes}")
            if bundle.tables:
                all_tables.extend(bundle.tables)

        # Write per-table CSVs
        emitted_files: List[str] = []
        for i, tbl in enumerate(all_tables, start=1):
            path_csv = write_table_csv(out_dir, base, i, tbl)
            emitted_files.append(str(path_csv))

        # Optional merge (simple vertical concat with column union)
        if args.merge and all_tables:
            # Build unioned header
            all_cols = []
            for t in all_tables:
                for c in t.columns:
                    if c not in all_cols:
                        all_cols.append(c)
            merged_path = out_dir / f"{base}__merged.csv"
            with merged_path.open("w", encoding="utf-8") as f:
                # add provenance columns
                header = all_cols + ["__page", "__table_index", "__title", "__engine"]
                f.write(",".join(header) + "\n")
                for idx, t in enumerate(all_tables, start=1):
                    col_index = {c: k for k, c in enumerate(t.columns)}
                    for row in t.rows:
                        row_vals = [""] * len(all_cols)
                        for c_idx, c_name in enumerate(t.columns):
                            v = row.cells[c_idx].value if c_idx < len(row.cells) else ""
                            row_vals[col_index[c_name]] = v.replace("\n", " ").replace(",", " ").strip()
                        meta = [str(t.page), str(idx), (t.title or "").replace(",", " "), "LLM"]
                        f.write(",".join(row_vals + meta) + "\n")
            emitted_files.append(str(merged_path))

        summary_records.append(
            {
                "pdf": str(pdf_path),
                "engine_used": use_engine,
                "pages": len(pages),
                "tables_found": len(all_tables),
                "outputs": emitted_files,
            }
        )

    # Write summary JSONL
    write_summary_jsonl(out_dir / "_summary.jsonl", summary_records)
    print(f"\nDone. Summary written to: {out_dir / '_summary.jsonl'}")
    print("[Reminder] This LLM-based method is a prototype; validate outputs before relying on them.")
    

if __name__ == "__main__":
    main()
