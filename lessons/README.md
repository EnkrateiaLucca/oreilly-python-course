# lessons/ — Day 1: your Python reading vocabulary

Nine small scripts, meant to be **read first, then run**, in order — plus a
puzzle set. Each lesson follows the same beats: **Predict** (guess before the
output appears) → **Explain** (say in one sentence what the script is for) →
**Run** → **Puzzle** (reassemble shuffled scripts in `puzzles.py`) →
**Modify** (the `✏️ TRY IT` edits at the end). Together they build toward one
recurring project: a script that tidies a messy Downloads folder.

No setup beyond [uv](https://docs.astral.sh/uv/). From the repo root:

```bash
uv run lessons/01_first_run.py
```

...then `02`, `03`, and so on. Any needed packages install themselves.

| Lesson | Run | What you'll be able to read |
|---|---|---|
| 01 | `uv run lessons/01_first_run.py` | `print`, variables, f-strings — and proof your setup works |
| 02 | `uv run lessons/02_lists_and_loops.py` | lists, indexing & slicing, for-loops, `.strip()/.split()/.join()`, and tallying files by type |
| 03 | `uv run lessons/03_decisions.py` | if/elif/else and functions — the organizer's brain |
| 04 | `uv run lessons/04_files_and_folders.py` | pathlib: looking at your real disk, read-only (plus recognizing `with open(...)`) |
| 05 | `uv run lessons/05_packages.py` | imports, the PEP 723 header, and the hallucinated-package check |
| 06 | `uv run lessons/06_when_it_breaks.py` | tracebacks (last line first!), try/except, and the three red-flag lines |
| 07 | `uv run lessons/07_talking_to_apis.py` | `requests` + a real keyless weather API (needs internet) |
| 08 | `uv run lessons/08_talking_to_ai.py` | the same `ask()` at three counters: OpenAI, Anthropic, local Ollama (keys optional — degrades gracefully) |
| 09 | `uv run lessons/09_capstone_organizer.py` | the full Downloads organizer: dry-run by default, `--apply` to move, sandbox included |
| — | `uv run lessons/puzzles.py` | Parsons puzzles: rebuild three shuffled scripts and see the skeleton (setup → loop → decision → output) |

Lesson 08 wants API keys in a `.env` file at the repo root (copy
`.env.example`) — but runs fine without them, showing you what *would* happen.
