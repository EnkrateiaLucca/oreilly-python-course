# 02 — Messy data → interactive decision dashboard

## The problem

Someone emails you a CSV and asks "what's going on with sales?" You open it,
stare at 100 rows of numbers, and start hand-building the same three Excel charts
you built last month — then still have to write the "here's what I'm seeing" note.
Twenty minutes later the meeting already started.

This demo does both jobs, and it teaches the line that runs through the whole
course: **deterministic Python** cleans the data and draws the charts (exact,
repeatable), while **AI judgement** reads the result and tells you what's
interesting (fuzzy, useful). You trust the charts to the cell; you treat the AI's
read as a lead to verify — never as gospel.

## The ticket

- **Trigger:** I run it manually whenever someone hands me a CSV.
- **Touches:** reads ONE CSV file I name; serves a web page on my machine only
  (127.0.0.1); no files written. With `--explain` it also sends a small
  *profile* of the data (shape + summary stats, never the raw rows) to the
  OpenAI API. `--explain` needs `OPENAI_API_KEY`.
- **Must never:** modify the CSV, upload the raw rows anywhere, or crash on a CSV
  that has no date column — it should just draw fewer charts.
- **Done means:** a browser page with up to three interactive charts picked
  automatically from the columns, and — with `--explain` — a short AI summary of
  notable patterns pinned above them that I can check against the charts.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that takes a CSV path as a CLI argument and
> serves an interactive dashboard with pandas, plotly and dash at
> http://127.0.0.1:8050. Auto-detect columns: parse any column containing "date"
> as datetimes, take the first numeric and first text column, and build a
> time-series line, a histogram, and an average-by-category bar chart — skipping
> any chart whose columns are missing. Add a --explain flag that builds a small
> text PROFILE of the data (row count, column list, df.describe()) — never the raw
> rows — sends it to the OpenAI API (model "gpt-5.6-luna") asking for 4-5 plain
> bullets on notable patterns, and shows the result in a card above the charts.
> Read-only: never write or modify files. argparse with --port, load
> OPENAI_API_KEY with python-dotenv only when --explain is used, no classes,
> friendly errors, under 170 lines.

## Run it

```bash
cd demos/02-data-to-dashboard

# Charts only — no API key, no dry run needed (it writes nothing):
uv run dashboard.py SALES.csv

# Charts + an AI read of the patterns (needs OPENAI_API_KEY):
uv run dashboard.py SALES.csv --explain

# then open http://127.0.0.1:8050 in your browser; Ctrl+C stops it.
# Try it on YOUR data:  uv run dashboard.py ~/Desktop/any-file.csv --explain
```

## Prove it

- The terminal prints `Loaded 100 rows, 14 columns.` for SALES.csv.
- The browser shows three charts; hover any bar or point and a tooltip appears
  with the exact numbers — that's "interactive", not a screenshot.
- With `--explain`, a green card sits above the charts with 4-5 bullets. **Verify
  one:** if it claims a region leads on profit, find that in the category chart.
  The habit — treat the AI's read as a claim to check — is the whole point.
- Feed it a CSV with no date column: the time-series chart is skipped, the app
  still works. That's the "must never crash" line of the ticket holding.

## ✏️ Your turn (5 minutes)

The AI only ever sees a *profile* of your data (`profile_data()` builds it from
`df.describe()`), never the rows — that's a deliberate privacy boundary. Tighten
the prompt: edit the instruction string in `explain_data()` so the summary ends
with one line — **"Recommended next question to investigate: …"**. One sentence,
one function, re-run with `--explain`.

- **Done means:** the AI card now ends with a "Recommended next question"
  line, and the charts are unchanged.
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Turn it into a tool

```bash
# macOS/Linux (~/.zshrc):
alias dashboard='uv run ~/oreilly-python-course/demos/02-data-to-dashboard/dashboard.py'
# then:  dashboard quarterly-report.csv --explain
```
