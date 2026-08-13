# 02 — Invoices to spreadsheet

## The problem

Every month you copy-paste vendor, number, date and total from a pile of invoice
PDFs into a spreadsheet, one squinting file at a time. It takes an hour, and a
mistyped total is exactly the kind of error nobody catches until the audit.

## The ticket

- **Trigger:** I run it manually against a folder of invoice files (`.pdf` / `.txt`).
- **Touches:** reads files in one folder I name; sends their TEXT to the OpenAI
  API; writes one new CSV in the current folder. Needs `OPENAI_API_KEY`.
- **Must never:** modify or delete the invoice files, write the CSV without
  `--apply`, invent values — the schema forces typed fields, and I eyeball the
  printed table against a source invoice before trusting it.
- **Done means:** one CSV row per invoice with vendor, invoice number, date,
  total (a real number, not text) and currency, matching what's printed on the
  invoices.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that takes a folder of invoices (.pdf and
> .txt) as a CLI argument and extracts structured fields from each one using the
> OpenAI structured-output API. Define a Pydantic model with vendor,
> invoice_number, invoice_date, total_amount (float) and currency, and pass it as
> response_format to client.chat.completions.parse with model "gpt-5.6-luna".
> Use pypdf for PDF text. Print the results as a table; only write invoices.csv
> when I pass --apply. Load OPENAI_API_KEY with python-dotenv from the repo-root
> .env and exit with a friendly 3-line fix message if it's missing. argparse, no
> classes besides the Pydantic model, friendly errors, under 150 lines.

## Run it

```bash
cd demos/02-invoices-to-spreadsheet

# Dry run — extract and print the table, write nothing:
uv run invoices_to_csv.py invoices

# Looks right? Save the spreadsheet:
uv run invoices_to_csv.py invoices --apply
```

## Prove it

- The printed table has exactly one row per file in `invoices/` (3 samples here).
- Open a sample invoice and compare: ACME's total is 18900.00 USD — the row must
  match the paper, including the currency.
- `total_amount` is a number (no `$`, no commas) — the schema did that, not luck.
- After `--apply`, `invoices.csv` opens cleanly in Excel/Numbers.

## ✏️ Your turn (5 minutes)

Un-hard-code the model: add a `--model` flag (default `gpt-5.6-luna`) so you can
swap models without editing code. The value starts in one place and is used in
another: the argparse block in `main()` needs the new flag, and
`extract_fields()` has the model name baked into the API call — give it a
`model` parameter and thread your flag's value through the call inside the
`for path in files` loop.

- **Done means:** `uv run invoices_to_csv.py invoices --help` lists `--model`, and
  a run with no flag still prints the same 3-row table (ACME total 18900.0 USD).
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Ship it

```bash
# macOS/Linux (~/.zshrc):
alias invoices2csv='uv run ~/oreilly-python-course/demos/02-invoices-to-spreadsheet/invoices_to_csv.py'
# then:  invoices2csv ~/Documents/invoices-march --apply
```
