# Cleanup / follow-ups

The 2026 redesign is live (`lessons/`, `demos/`, `prompts/`, `slides/`, `extras/`,
rewritten `README.md`, new `SETUP.md`). The old materials were **archived on
2026-08-13** into [`archive-legacy-2026-08/`](archive-legacy-2026-08/) via
`git mv` (history preserved) — see that folder's README. It's scheduled for
deletion around **2026-09-13**.

## ✅ Done

- [x] Archived `notebooks/`, `presentation/`, `scripts/`, `assets/`,
      `requirements/`, `setup.sh`, `index-scripts.md`, `QUICK_START_WINDOWS.md`,
      `WINDOWS_SETUP.md` → `archive-legacy-2026-08/`.
- [x] Updated the README footnote to point at the archive.

## ⚠️ Privacy — payslip scrubbed from history (2026-08-13)

- [x] Deleted the fake-invoices payslip and purged **all copies of the payslip
      content** from git history via `git filter-repo` (stripped by blob id, so it
      caught every filename): the file `assets/fake-invoices/invoice1.txt`, a
      second copy at `assets/documents/receipt_data.txt`, and the same payslip
      pasted inline into an old demo script and an old README. Force-pushed to
      `main` + both side branches. History + working tree verified clean.
- [ ] **GitHub still retains it in two places I can't reach by push:**
      (1) pull-request refs `refs/pull/1..7/head` still point at pre-scrub commits;
      (2) the old commit SHAs stay accessible by direct URL until GitHub garbage-
      collects. **Action:** open a GitHub Support request to purge cached views /
      stale refs for this repo (their documented step after a history rewrite).
- [ ] The exposed identifiers (Portuguese NIF/NISS tax numbers, employer, salary)
      were public for a while — worth noting for your own records; tax numbers
      can't be rotated like a password.

## When the month is up

- [ ] Delete `archive-legacy-2026-08/` entirely (rescue the ReportLab tutorial
      and `scripts/lib/solveit.py` first if you want them — noted in its README).

## Update whenever convenient (stale but harmless)

- [ ] `pyproject.toml` — 70 pinned deps; only Codespaces/devcontainer needs the
      synced env now (the course runs on per-script PEP 723). Slim it, or drop
      `uv sync` from the flow entirely.
- [ ] `.devcontainer/post-create.sh` — still does kernel install + `playwright
      install` (unused now); keep only the uv step. README still shows a Codespaces
      button, so this path should work.
- [ ] `CLAUDE.md` — describes the old layout (notebooks/kernel/playwright);
      rewrite for the script-first structure.

## Pre-existing bugs, now moot (for the record)

- Old README step 2 used a Windows path `"$PWD\.venv"` in the macOS kernel command.
- `playwright install` was required by setup but no active notebook used Playwright.
- Model IDs were inconsistent across the old notebooks/scripts; the new content
  standardizes on `gpt-5.6-luna` / `claude-opus-4-8` / `gemma4`.
