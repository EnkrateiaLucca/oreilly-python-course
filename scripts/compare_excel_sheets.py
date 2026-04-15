# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openpyxl",
#     "pandas",
#     "rich",
# ]
# ///

import argparse
import sys

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


# Load an Excel file and use its first column as the row key (index).
# This lets us match rows between files by key rather than by position.
def load_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    df = df.set_index(df.columns[0])
    return df


def compare(df_old: pd.DataFrame, df_new: pd.DataFrame) -> None:
    # --- Detect added/removed rows ---
    # Set difference on index keys tells us 
    # which rows exist in one file but not the other.
    old_keys = set(df_old.index)
    new_keys = set(df_new.index)

    added = sorted(new_keys - old_keys, key=str)
    removed = sorted(old_keys - new_keys, key=str)

    if added:
        console.print(f"\n[green bold]Rows added ({len(added)}):[/] {', '.join(str(k) for k in added)}")
    if removed:
        console.print(f"\n[red bold]Rows removed ({len(removed)}):[/] {', '.join(str(k) for k in removed)}")

    # --- Narrow both DataFrames to only the rows 
    # they share ---
    # We can only do cell-by-cell 
    # comparison on rows present in both files.
    common = sorted(old_keys & new_keys, key=str)
    df_old_c = df_old.loc[common]
    df_new_c = df_new.loc[common]

    total_diffs = 0
    cols_affected = 0
    rows_with_changes: set = set()

    # --- Column-by-column comparison loop ---
    for col in df_old_c.columns:
        old_vals = df_old_c[col]
        new_vals = df_new_c[col]

        # Two cells are "equal" if their values 
        # match OR both are NaN.
        # Without the both_nan check, 
        # every pair of empty cells would be a 
        # false positive.
        both_nan = old_vals.isna() & new_vals.isna()
        equal = (old_vals == new_vals) | both_nan

        # Type-mismatch fallback: if a cell holds 
        # 100 (int) and the other holds "100" (str),
        # pandas says they differ. Casting both 
        # to string catches these false positives.
        still_diff = ~equal
        for key in old_vals[still_diff].index:
            try:
                if str(old_vals[key]).strip() == str(new_vals[key]).strip():
                    equal[key] = True
            except Exception:
                pass

        # Skip this column entirely if there are no real differences
        diff_keys = equal[~equal].index
        if len(diff_keys) == 0:
            continue

        # --- Build a rich table showing old vs new for every changed cell in this column ---
        cols_affected += 1
        total_diffs += len(diff_keys)
        rows_with_changes.update(diff_keys)

        table = Table(title=f"Column: [bold]{col}[/bold]", show_lines=True)
        table.add_column("Row Key", style="cyan")
        table.add_column("Old Value", style="red")
        table.add_column("New Value", style="green")

        for key in sorted(diff_keys, key=str):
            old_display = "" if pd.isna(old_vals[key]) else str(old_vals[key])
            new_display = "" if pd.isna(new_vals[key]) else str(new_vals[key])
            table.add_row(str(key), old_display, new_display)

        console.print()
        console.print(table)

    # --- Final stats summary ---
    console.print()
    summary = Table(title="Summary", show_lines=True)
    summary.add_column("Metric", style="bold")
    summary.add_column("Value", justify="right")
    summary.add_row("Total cell differences", str(total_diffs))
    summary.add_row("Columns affected", str(cols_affected))
    summary.add_row("Rows with changes", str(len(rows_with_changes)))
    summary.add_row("Rows added", str(len(added)))
    summary.add_row("Rows removed", str(len(removed)))
    console.print(summary)


def main() -> None:
    # --- Parse CLI arguments: two Excel file paths ---
    parser = argparse.ArgumentParser(description="Compare two Excel files column by column.")
    parser.add_argument("file_old", help="Path to the original .xlsx file")
    parser.add_argument("file_new", help="Path to the updated .xlsx file")
    args = parser.parse_args()

    # --- Load both files, using the first column as row key ---
    df_old = load_excel(args.file_old)
    df_new = load_excel(args.file_new)

    # --- Guard: columns must match exactly or comparison is meaningless ---
    if list(df_old.columns) != list(df_new.columns):
        console.print("[red bold]Error:[/red bold] Column headers do not match between files.")
        console.print(f"  Old: {list(df_old.columns)}")
        console.print(f"  New: {list(df_new.columns)}")
        sys.exit(1)

    console.print(Text(f"\nComparing: {args.file_old} → {args.file_new}", style="bold"))
    console.print(f"Key column: [cyan]{df_old.index.name}[/cyan]  |  {len(df_old)} vs {len(df_new)} rows\n")

    compare(df_old, df_new)


if __name__ == "__main__":
    main()