# /// script
# requires-python = ">=3.12"
# dependencies = ["openpyxl", "pandas", "rich"]
# ///
"""Compare two Excel files and highlight every changed cell.

Input   -> two .xlsx files (an old version and a new version)
Process -> match rows by the first column, then diff every cell
Output  -> a console report: rows added/removed, and old vs new for each change

Run it like:
    uv run demos/reserve/spreadsheet-diff/diff_excel.py employee_roster_january.xlsx employee_roster_february.xlsx

Needs: nothing (no API key). Read-only: it never modifies either file.
"""

import argparse
import sys

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


def load_excel(path: str) -> pd.DataFrame:
    # The FIRST column becomes the row key (like a primary key in a database),
    # so we can match "the same row" across files even if the order changed.
    df = pd.read_excel(path, engine="openpyxl")
    return df.set_index(df.columns[0])


def compare(df_old: pd.DataFrame, df_new: pd.DataFrame) -> None:
    old_keys, new_keys = set(df_old.index), set(df_new.index)
    added = sorted(new_keys - old_keys, key=str)
    removed = sorted(old_keys - new_keys, key=str)

    if added:
        console.print(f"\n[green bold]Rows added ({len(added)}):[/] "
                      + ", ".join(str(k) for k in added))
    if removed:
        console.print(f"\n[red bold]Rows removed ({len(removed)}):[/] "
                      + ", ".join(str(k) for k in removed))

    # Cell-by-cell comparison only makes sense for rows present in BOTH files.
    common = sorted(old_keys & new_keys, key=str)
    df_old_c, df_new_c = df_old.loc[common], df_new.loc[common]

    total_diffs = 0
    rows_changed: set = set()

    for col in df_old_c.columns:
        old_vals, new_vals = df_old_c[col], df_new_c[col]

        # Two cells are "equal" if the values match OR both are empty (NaN).
        # Without the both-NaN check, every pair of blanks is a false alarm.
        equal = (old_vals == new_vals) | (old_vals.isna() & new_vals.isna())

        # Type-mismatch rescue: 100 (number) vs "100" (text) should NOT count
        # as a change, so compare the string forms before flagging a cell.
        for key in old_vals[~equal].index:
            if str(old_vals[key]).strip() == str(new_vals[key]).strip():
                equal[key] = True

        diff_keys = equal[~equal].index
        if len(diff_keys) == 0:
            continue

        total_diffs += len(diff_keys)
        rows_changed.update(diff_keys)

        table = Table(title=f"Column: [bold]{col}[/bold]", show_lines=True)
        table.add_column("Row Key", style="cyan")
        table.add_column("Old Value", style="red")
        table.add_column("New Value", style="green")
        for key in sorted(diff_keys, key=str):
            table.add_row(str(key),
                          "" if pd.isna(old_vals[key]) else str(old_vals[key]),
                          "" if pd.isna(new_vals[key]) else str(new_vals[key]))
        console.print()
        console.print(table)

    summary = Table(title="Summary", show_lines=True)
    summary.add_column("Metric", style="bold")
    summary.add_column("Value", justify="right")
    summary.add_row("Cell differences", str(total_diffs))
    summary.add_row("Rows with changes", str(len(rows_changed)))
    summary.add_row("Rows added", str(len(added)))
    summary.add_row("Rows removed", str(len(removed)))
    console.print()
    console.print(summary)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two Excel files cell by cell.")
    parser.add_argument("file_old", help="Path to the original .xlsx file")
    parser.add_argument("file_new", help="Path to the updated .xlsx file")
    args = parser.parse_args()

    try:
        df_old = load_excel(args.file_old)
        df_new = load_excel(args.file_new)
    except FileNotFoundError as error:
        print(f"File not found: {error.filename}")
        sys.exit(1)

    # Guard: if the headers differ, a cell-by-cell diff would be meaningless.
    if list(df_old.columns) != list(df_new.columns):
        console.print("[red bold]Error:[/] column headers do not match between files.")
        console.print(f"  Old: {list(df_old.columns)}")
        console.print(f"  New: {list(df_new.columns)}")
        sys.exit(1)

    console.print(f"[bold]Comparing:[/] {args.file_old} -> {args.file_new}")
    console.print(f"Key column: [cyan]{df_old.index.name}[/] | "
                  f"{len(df_old)} vs {len(df_new)} rows")
    compare(df_old, df_new)


if __name__ == "__main__":
    main()
