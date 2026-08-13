# Archived legacy materials (pre-2026 redesign)

These are the **old course materials**, superseded by the 2026 redesign. They're
parked here for reference during the transition.

**🗓 Safe to delete after ~2026-09-13** (kept ~1 month from 2026-08-13). Nothing
in the active course (`lessons/`, `demos/`, `prompts/`, `slides/`, `extras/`)
depends on anything in this folder — the keepers were ported over and the deck's
images live in `slides/img/`.

## What's here and what replaced it

| Archived | Replaced by |
|---|---|
| `notebooks/` (Jupyter, day-1 & day-2) | `lessons/` (Day 1) + `demos/` (Day 2) |
| `presentation/` (remark.js deck + PDF) | `slides/` (Marp deck) |
| `scripts/` (old demos, `lib/`, `archive/`) | `demos/` (keepers ported) + `prompts/` |
| `assets/` (old sample data, media, docs) | per-demo sample data; `slides/img/` |
| `requirements/`, `setup.sh` | `SETUP.md` (single `uv`-based setup) |
| `QUICK_START_WINDOWS.md`, `WINDOWS_SETUP.md` | `SETUP.md` (Mac + Windows in one) |
| `index-scripts.md` | `demos/README.md` |

## ⚠️ Before deleting — two things

1. **Privacy (payslip):** a **real payslip** (full name + tax/ID numbers) lived in
   the old materials at several paths (`assets/fake-invoices/invoice1.txt`,
   `assets/documents/receipt_data.txt`, and pasted inline in an old script/README).
   All copies were **purged from git history** on 2026-08-13 via `git filter-repo`
   (stripped by content/blob id) and force-pushed. History + tree verified clean.
   ‼️ Remaining: GitHub still holds it in PR refs (`refs/pull/*`) and cached commit
   views — a **GitHub Support request** is needed to purge those (see repo `CLEANUP.md`).
2. **Possible keepers worth rescuing** before deletion: the ReportLab PDF tutorial
   (`notebooks/day-2/04-exercises/05-tutorial_learning_python_with_pdfs.ipynb`) and
   the `solveit` toolkit (`scripts/lib/solveit.py`, a ~1,600-line standalone AI
   tutor) — neither made the cut but both could become their own thing.

When the month is up: delete this whole `archive-legacy-2026-08/` folder.
