# 01 — Tame your Downloads

## The problem

Your Downloads folder is a landfill: months of PDFs, screenshots, CSVs and stray
notes you scroll past every day. Finding anything takes minutes, and "I'll clean
it up this weekend" has been true for a year.

## The ticket

- **Trigger:** I run it manually whenever a folder gets messy.
- **Touches:** ONE folder that I name on the command line — its direct files only,
  no subfolders, no network, no credentials.
- **Must never:** delete a file, rename a file, touch anything outside the named
  folder, or move a single byte without me passing `--apply`.
- **Done means:** every known file type sits in a subfolder (`documents/`, `PDFs/`,
  `images/`, `data/`, ...), unknown types are left in place and listed as skipped,
  and a dry run first showed me the exact plan.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that organizes one folder I pass as a CLI
> argument: move each file into a subfolder based on its extension (txt/md →
> documents, pdf → PDFs, png/jpg → images, csv/xlsx → data). Use argparse. It must
> be dry-run by default, printing "would move X -> Y", and only move files when I
> pass --apply. Never delete anything, never recurse into subfolders, skip unknown
> extensions with a message. No classes, small functions, friendly error messages,
> standard library only.

## Run it

```bash
# 1. Build a SAFE sandbox first (never practice on your real Downloads):
uv run demos/01-tame-your-downloads/make_mess.py
uv run demos/01-tame-your-downloads/make_mess.py --apply

# 2. Dry run — read the plan before anything moves:
uv run demos/01-tame-your-downloads/organize.py practice-mess

# 3. Happy with the plan? Execute it:
uv run demos/01-tame-your-downloads/organize.py practice-mess --apply

# Bonus — sort images by CONTENT with local AI (needs: ollama pull gemma4):
uv run demos/01-tame-your-downloads/classify_images.py practice-mess
uv run demos/01-tame-your-downloads/classify_images.py practice-mess --apply
```

## Prove it

- Dry run prints one `would move` / `skip` line per file and ends with
  "This was a DRY RUN — nothing changed."
- After `--apply`, `ls practice-mess` shows only subfolders plus the skipped
  files; every file is still findable (moved, never deleted).
- Run `organize.py practice-mess` again: it should find nothing left to move.

## ✏️ Your turn (5 minutes)

Give spreadsheets their own home: add a `Spreadsheets/` category so `.xlsx` and
`.csv` stop landing in `data/`. Two parts of the script have to agree: the
`EXTENSION_FOLDERS` table at the top (both extensions currently point at
`"data"`), and the lookup in `organize_files()` where files with no rule fall
through to `skip` — read that branch to confirm a brand-new folder name needs
zero extra code, and find who actually creates the destination folder.

- **Done means:** a fresh dry run on `practice-mess` prints
  `would move  budget-draft.xlsx  ->  Spreadsheets/`, both `.csv` files follow
  it, and nothing is headed to `data/` anymore.
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Ship it

```bash
# macOS/Linux (~/.zshrc):
alias tidy='uv run ~/oreilly-python-course/demos/01-tame-your-downloads/organize.py'
# then:  tidy ~/Downloads          (dry run)
#        tidy ~/Downloads --apply  (for real — after you read the plan!)
```
