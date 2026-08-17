# 01 — Document inbox → structured action queue

## The problem

Real work doesn't arrive as a tidy spreadsheet. It arrives as a *pile*: PDF
invoices, a screenshot someone Slacked you, a messy meeting note, a renewal
notice, a receipt. Each one hides a date, a name, or a "you need to do something"
buried in the noise — and triaging the pile by hand is exactly the boring,
error-prone chore nobody has time for.

This is the automation knowledge workers actually need, and it teaches the single
most valuable pattern in AI automation: **messy multimodal information → AI + a
schema → clean structured data** you can sort, filter, and act on.

## The ticket

- **Trigger:** I run it manually against a folder of mixed documents
  (`.pdf` / `.txt` / `.md` / images).
- **Touches:** reads the files in one folder I name; sends their text (or, for
  images, the picture) to the OpenAI API; writes one new `inbox.csv` (or
  `inbox.md`) in the current folder. Needs `OPENAI_API_KEY`.
- **Must never:** modify, move, or delete the source documents; write the file
  without `--apply`; invent facts — the schema forces typed fields and I eyeball
  the printed table against a source document before trusting it.
- **Done means:** one row per document with document type, a one-line summary,
  a priority, key dates, people, and action items — and the three rows I
  spot-check match what the documents actually say.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that takes a folder of documents as a CLI
> argument and turns each one into a structured record using the OpenAI
> structured-output API. Support .pdf/.txt/.md as text (use pypdf for PDFs) and
> .png/.jpg/.jpeg as images sent to the vision model as a base64 data URL.
> Define ONE Pydantic model with document_type (str), summary (str), priority
> (Literal high/medium/low), key_dates (list[str]), people (list[str]) and
> action_items (list[str]); pass it as response_format to
> client.chat.completions.parse with model "gpt-5.6-luna". Print the results as a
> table; only write inbox.csv (or inbox.md with --format md) when I pass --apply.
> Never modify the source files. Load OPENAI_API_KEY with python-dotenv from the
> repo-root .env and exit with a friendly 3-line fix message if it's missing.
> argparse, no classes besides the Pydantic model, friendly errors, under 170 lines.

## Run it

```bash
cd demos/01-document-inbox

# Dry run — triage every document and print the table, write nothing:
uv run document_inbox.py inbox

# Looks right? Save the action queue:
uv run document_inbox.py inbox --apply

# Prefer a Markdown table you can paste into notes?
uv run document_inbox.py inbox --format md --apply
```

## Prove it

- The printed table has exactly one row per file in `inbox/` (6 samples here:
  three invoices, a meeting note, a renewal notice, a receipt).
- `priority` is only ever `high` / `medium` / `low` — the `Literal` in the schema
  did that, not luck. The renewal notice (a deadline + money) should read `high`.
- Open `inbox/meeting-note.txt` and compare its row: the `action_items` column
  should list booking the offsite venue and following up on invoice GX-2026-0217.
- After `--apply`, `inbox.csv` opens cleanly in Excel/Numbers, one tidy row per
  document — a mixed pile is now a sortable queue.

## ✏️ Your turn (5 minutes)

Add a `--min-priority` flag (default `low`) that filters the output to rows at or
above a priority — so a busy morning shows only `high` items. The value starts in
one place and is used in another: add the flag in `main()`'s argparse block, then
filter `rows` before the table is printed. A tiny rank map
(`{"low": 0, "medium": 1, "high": 2}`) turns the three words into numbers you can
compare.

- **Done means:** `uv run document_inbox.py inbox --min-priority high` prints only
  the high-priority rows (the renewal notice is one of them), and a plain run still
  prints all six.
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Turn it into a tool

Give it a one-word nickname, then read [`04-tool-to-skill/`](../04-tool-to-skill/)
— this is the exact tool we upgrade into an agent-callable **skill** at the end of
Day 2.

```bash
# macOS/Linux (~/.zshrc):
alias inbox='uv run ~/oreilly-python-course/demos/01-document-inbox/document_inbox.py'
# then:  inbox ~/Downloads/to-triage --apply
```
