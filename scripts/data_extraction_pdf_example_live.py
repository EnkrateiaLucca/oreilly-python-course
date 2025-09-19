# extraction.py
# /// script
# requires-python = ">=3.10"
# dependencies = ["pdfplumber>=0.11", "pandas>=2.0"]
# ///
#
# How to run (example):
#   uv run extraction.py "/path/to/input.pdf"            # writes alongside the PDF
#   uv run extraction.py "/path/to/input.pdf" output.csv # optional explicit output
#
# What it does:
#   1) Opens the PDF.
#   2) Scans pages for tables.
#   3) Finds the table with headers like: Month | Due Date | Amount ($).
#   4) Normalizes rows and writes a CSV.

from __future__ import annotations
import sys
import os
import re
from typing import List, Optional
import pandas as pd
import pdfplumber

REQUIRED_COLS = {"month", "due date", "amount"}  # relaxed match (case/spacing)

def usage_and_exit() -> None:
    print("Usage:\n  uv run extraction.py <input.pdf> [output.csv]")
    sys.exit(1)

# --- Parse CLI args (keep it simple) ---
if len(sys.argv) < 2:
    usage_and_exit()
in_path = sys.argv[1]
if not os.path.isfile(in_path) or not in_path.lower().endswith(".pdf"):
    print("Error: first argument must be a valid PDF file path.")
    sys.exit(1)
out_path = (
    sys.argv[2]
    if len(sys.argv) >= 3
    else os.path.splitext(in_path)[0] + ".csv"
)

# --- Helpers to lightly normalize headers/cells ---
def norm_head(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    s = s.replace("( $ )", "$")  # just in case weird spacing
    s = s.lower()
    s = s.replace("amount ($)", "amount").replace("amount($)", "amount")
    return s

def looks_like_header(row: List[str]) -> bool:
    heads = {norm_head(c) for c in row if c and str(c).strip()}
    # allow supersets (e.g., extra blank columns)
    return REQUIRED_COLS.issubset({h.replace(":", "") for h in heads})

def clean_money(val: str) -> str:
    # keep as text in CSV; strip currency formatting like "$5,000"
    s = (val or "").strip()
    s = s.replace("$", "").replace(",", "")
    return s

# --- Extract tables and pick the one matching required headers ---
rows: List[List[str]] = []
with pdfplumber.open(in_path) as pdf:
    for page in pdf.pages:
        # Try a "lines" strategy first (works for bordered tables),
        # then a gentler "text" fallback.
        for settings in (
            {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
            {"vertical_strategy": "text", "horizontal_strategy": "text"},
        ):
            try:
                tables = page.extract_tables(table_settings=settings)
            except Exception:
                continue
            for tbl in tables or []:
                # find header row index
                header_idx: Optional[int] = None
                for i, r in enumerate(tbl):
                    if r and looks_like_header([str(c) if c is not None else "" for c in r]):
                        header_idx = i
                        break
                if header_idx is None:
                    continue

                header = [norm_head(str(c) if c is not None else "") for c in tbl[header_idx]]
                # map indices of columns we care about
                def col_idx(key: str) -> Optional[int]:
                    for j, h in enumerate(header):
                        if key == h or key in h:
                            return j
                    return None

                m_i = col_idx("month")
                d_i = col_idx("due date")
                a_i = col_idx("amount")
                if None in (m_i, d_i, a_i):
                    continue

                # collect body rows after header
                for r in tbl[header_idx + 1 :]:
                    if not any(x for x in r):
                        continue
                    month = (r[m_i] or "").strip()
                    due   = (r[d_i] or "").strip()
                    amt   = clean_money(r[a_i] or "")
                    # simple guard to skip junk lines
                    if not month or not due:
                        continue
                    rows.append([month, due, amt])

        if rows:
            break  # stop after first matching table found

# --- If nothing found, fail clearly (don’t guess) ---
if not rows:
    print("I cannot verify a matching table in this PDF (headers not found).")
    sys.exit(2)

# --- Write CSV (Month, Due Date, Amount) ---
df = pd.DataFrame(rows, columns=["Month", "Due Date", "Amount"])
df.to_csv(out_path, index=False)
print(f"Saved: {out_path}")