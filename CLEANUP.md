# Post-approval cleanup checklist

The 2026 redesign is **additive**: everything new lives in `lessons/`, `demos/`,
`prompts/`, `slides/`, plus the rewritten `README.md` and new `SETUP.md`. Nothing
old was moved or deleted. Once the redesign is approved, this is the deliberate
archive/delete pass — **do not run it before approval** (and per house rules, ask
before deleting multiple files).

## Move to `archive/` (keep for reference)

- [ ] `notebooks/` — all Jupyter content (day-1, day-2). Replaced by `lessons/` + `demos/`.
      Contains some material worth mining later: the ReportLab PDF tutorial
      (`day-2/04-exercises/05-tutorial_learning_python_with_pdfs.ipynb`) and the solveit
      notebook (potential standalone product).
- [ ] `presentation/` — remark.js deck + PDF. Replaced by `slides/`.
- [ ] `scripts/` — old demos, lib, and archive tree. The keepers were ported into `demos/`
      (with `scripts/lib/solveit.py` possibly worth extracting as its own project).
- [ ] `assets/media/` — ~50 screenshots that fed the old deck. Keep only images the new
      deck references.
- [ ] Old setup docs superseded by `SETUP.md`: `QUICK_START_WINDOWS.md`,
      `WINDOWS_SETUP.md`, `setup.sh`, `requirements/` (three dependency systems → PEP 723
      per-script now), `index-scripts.md`.

## ⚠️ Privacy — handle first

- [ ] `assets/fake-invoices/invoice1.txt` is a **real payslip** containing Lucas's full
      name and tax/ID numbers — it's tracked in the public repo's history. Remove it
      (and consider scrubbing git history / rotating any exposed identifiers). The new
      `demos/02` uses clearly-fake invoices instead.

## Delete outright

- [ ] `notebooks/day-1/.ipynb_checkpoints/`, `notebooks/day-1/archive/live-*` duplicates
- [ ] Stray artifacts: `notebooks/day-1/2026-06-16-*.png`, `notebooks/day-1/new_file.md`,
      `__pycache__/`
- [ ] `scripts/.env` — untracked and contains only a placeholder (verified), but shouldn't
      exist in the tree at all; the root `.env` is the one true location.
- [ ] `scripts/script_placeholder_template.py` (typos, superseded by `prompts/generate-a-tool.md`)

## Update after archiving

- [ ] `pyproject.toml` — the project env is only needed for Codespaces convenience now;
      slim the 70 pinned deps to what `lessons/` + `demos/` actually use (or drop
      `uv sync` from the flow entirely and lean fully on PEP 723).
- [ ] `.devcontainer/post-create.sh` — remove kernel install + playwright steps; keep uv.
- [ ] `CLAUDE.md` — rewrite for the new layout (script-first, no Jupyter/kernel/playwright).
- [ ] README "legacy" footnote — remove once the dirs are archived.
- [ ] Delete this file.

## Pre-existing bugs that become moot (noted for the record)

- README (old) step 2 used a Windows-style path `"$PWD\.venv"` in the macOS kernel command.
- `playwright install` was required by setup but no active notebook used Playwright.
- Model IDs were inconsistent across notebooks/scripts (mix of 2024-2026 era IDs);
  the new content standardizes on `gpt-5.6-luna` / `claude-opus-4-8` / `gemma4`.
