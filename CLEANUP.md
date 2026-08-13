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

## ⚠️ Privacy — payslip deleted from tree; HISTORY still open

- [x] Deleted the old `assets/fake-invoices/` folder (held a real payslip with
      full name + tax/ID numbers) from the working tree — it was never archived.
- [ ] **Still in public git history.** The delete only affects HEAD going forward;
      the payslip remains in older commits already pushed. To fully remediate:
      scrub history (`git filter-repo` / BFG) + force-push, and rotate any exposed
      identifiers. Decide whether that's worth doing.

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
