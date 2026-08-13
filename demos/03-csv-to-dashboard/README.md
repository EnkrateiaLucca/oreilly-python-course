# 03 — CSV to dashboard

## The problem

Someone emails you a CSV and asks "what's going on with sales?" You open it,
stare at 100 rows of numbers, and start hand-building the same three Excel charts
you built last month. Twenty minutes later the meeting already started.

## The ticket

- **Trigger:** I run it manually whenever someone hands me a CSV.
- **Touches:** reads ONE CSV file I name; serves a web page on my machine only
  (127.0.0.1). No network calls out, no credentials, no files written.
- **Must never:** modify the CSV, upload the data anywhere, or crash on a CSV
  that has no date column — it should just draw fewer charts.
- **Done means:** a browser page with up to three interactive charts (trend over
  time, distribution, category breakdown) picked automatically from the columns,
  and hovering a data point shows its exact values.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that takes a CSV path as a CLI argument and
> serves an interactive dashboard with pandas, plotly and dash at
> http://127.0.0.1:8050. Auto-detect columns: parse any column containing "date"
> as datetimes, take the first numeric column and the first text column, and
> build a time-series line, a histogram, and an average-by-category bar chart —
> skipping any chart whose columns are missing. Use argparse with a --port flag.
> Read-only: never write or modify files. No classes, small functions, friendly
> errors, under 150 lines.

## Run it

```bash
cd demos/03-csv-to-dashboard

# Serve the dashboard (read-only — no dry run needed):
uv run dashboard.py SALES.csv

# then open http://127.0.0.1:8050 in your browser; Ctrl+C stops it.
# Try it on YOUR data:  uv run dashboard.py ~/Desktop/any-file.csv
```

## Prove it

- The terminal prints `Loaded 100 rows, 14 columns.` for SALES.csv.
- The browser shows three charts; hover any bar or point and a tooltip appears
  with the exact numbers — that's "interactive", not a screenshot.
- Feed it a CSV with no date column: the time-series chart is skipped, the app
  still works. That's the "must never crash" line of the ticket holding.

## ✏️ Your turn (5 minutes)

Chart the column YOU care about: add a `--column` flag that picks which numeric
column all three charts use. Trace the value across two parts:
`build_figures()` silently charts `numeric_cols[0]` — for SALES.csv that's
`Order ID`, a meaningless number (check the chart titles!) — while argparse
lives in `main()`, so you'll have to pass your choice through `build_app()` to
connect the two. With no flag, today's behavior must not change.

- **Done means:** `uv run dashboard.py SALES.csv --column "Total Profit"`
  retitles all three charts to Total Profit.
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Ship it

```bash
# macOS/Linux (~/.zshrc):
alias dashboard='uv run ~/oreilly-python-course/demos/03-csv-to-dashboard/dashboard.py'
# then:  dashboard quarterly-report.csv
```
