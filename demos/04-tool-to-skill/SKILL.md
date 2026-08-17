---
name: document-inbox
description: >-
  Triage a folder of mixed documents (PDFs, notes, receipts, screenshots) into
  one structured action queue — document type, summary, priority, dates, people,
  and action items — as a CSV or Markdown table.
---

# Skill: document-inbox

A minimal example of the last rung on the ladder: the SAME `document_inbox.py`
tool from [`../01-document-inbox/`](../01-document-inbox/), described so an AI
agent knows *when* and *how* to invoke it. Nothing about the Python changed — this
file is just its usage contract, written for a machine to read.

## When to use

Use this when the user has a **folder of unsorted documents** and wants them
triaged into a structured, sortable queue — e.g. "sort out my downloads",
"what's in this pile of invoices and notes", "pull the action items and deadlines
out of these files". Do **not** use it for a single document (just read that one)
or for data that is already a clean spreadsheet.

## Inputs

- **`folder`** (required): path to a folder containing `.pdf`, `.txt`, `.md`, or
  image (`.png`/`.jpg`) documents.
- **`--format csv|md`** (optional, default `csv`): output table format.
- **`--apply`** (optional): actually write the file. Without it, nothing is
  written — the queue is only printed.
- **Environment:** `OPENAI_API_KEY` must be set (read from the repo-root `.env`).

## Command to run

```bash
# Preview only (safe — writes nothing):
uv run demos/01-document-inbox/document_inbox.py <folder>

# Write the action queue:
uv run demos/01-document-inbox/document_inbox.py <folder> --apply
```

## Expected output

- A table (one row per document) printed to stdout with columns: `file`,
  `document_type`, `summary`, `priority`, `key_dates`, `people`, `action_items`.
- With `--apply`: an `inbox.csv` (or `inbox.md`) written in the working directory,
  and a final `Wrote N rows to inbox.csv` line.

## Safety constraints

- **Never** modify, move, or delete the source documents — the tool is read-only
  over the input folder.
- **Never** write any output file unless `--apply` was passed. Preview first, let
  the user confirm the table, then re-run with `--apply`.
- Only the document text (or, for images, the image) is sent to the OpenAI API;
  do not point this at folders containing secrets the user hasn't agreed to send.
- If `OPENAI_API_KEY` is missing, report the printed fix message — do not attempt
  to work around it.
