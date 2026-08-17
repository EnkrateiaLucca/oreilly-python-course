# 06 — Spreadsheet diff

## The problem

"Which cells did Finance change in this month's roster?" You put January and
February side by side and play spot-the-difference across 200 cells. You WILL
miss one, and it will be the salary column.

## The ticket

- **Trigger:** I run it manually with two versions of the same spreadsheet.
- **Touches:** reads TWO .xlsx files I name. No network, no credentials, no
  files written — pure read-and-report.
- **Must never:** modify either file, or compare files whose column headers
  don't match (that diff would be garbage — refuse loudly instead).
- **Done means:** every changed cell is listed with its row key, old value and
  new value; added/removed rows are called out; blank-vs-blank and 100-vs-"100"
  are NOT flagged as changes; a summary counts the total.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that compares two Excel files with pandas +
> openpyxl. Use the first column as the row key. Report rows added and removed,
> then for each column print a rich table of changed cells with row key, old
> value, new value, plus a summary table of counts. Treat two NaN cells as equal
> and ignore pure type mismatches like 100 vs "100". If the column headers of
> the two files differ, print a clear error and exit 1. Read-only — never write
> or modify files. argparse with two positional file arguments, no classes,
> friendly errors, under 150 lines.

## Run it

```bash
cd demos/reserve/spreadsheet-diff

# Read-only, so no dry run needed — just run it:
uv run diff_excel.py employee_roster_january.xlsx employee_roster_february.xlsx
```

## Prove it

- The summary table's "Cell differences" count matches the number of old/new
  pairs printed above it.
- Open both files and hand-check ONE reported change — the old and new values
  match reality. (Trust, but verify one.)
- Swap the argument order: every "old" and "new" value flips — the tool reads
  the files, it doesn't guess.
- Both .xlsx files keep their original modification time: read-only confirmed.

## ✏️ Your turn (5 minutes)

The row key is silently hard-coded: `load_excel()` always keys on the FIRST
column (`df.columns[0]`). Add a `--key` flag to choose the key column by name.
Two parts must change together: `load_excel()` needs to accept a column name
(falling back to the first column when none is given), and `main()` needs the
argparse flag plus BOTH `load_excel()` calls updated to pass it through.

- **Done means:** adding `--key "Email"` prints `Key column: Email` and the diff
  still runs; with no flag, the output is unchanged (key stays `Employee ID`).
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Ship it

```bash
# macOS/Linux (~/.zshrc):
alias xldiff='uv run ~/oreilly-python-course/demos/reserve/spreadsheet-diff/diff_excel.py'
# then:  xldiff budget_v1.xlsx budget_v2.xlsx
```
