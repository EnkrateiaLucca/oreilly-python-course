# Prompt

The "I" in the SCRIPT loop. AI-generated code is **untrusted input** — treat it the
way a bank treats a form someone mailed in. You can debug a wrong *output*; you can't
un-delete a folder. Two minutes here beats an afternoon of recovery.

## 1. Blast radius — what can this script touch?

Scan the script (or its --help, or ask the AI) and answer five questions:

| Question | Look for | If yes… |
|---|---|---|
| Does it **write, move, or delete files**? | `shutil`, `os.remove`, `.unlink()`, `.rename()`, `open(..., "w")` | Demand dry-run + `--apply`. Test on a practice folder. |
| Does it **touch the network**? | `requests`, `httpx`, `urllib`, any SDK | Know *which* sites, and what data leaves your machine. |
| Does it **read secrets**? | `os.environ`, `.env`, `API_KEY` | Keys should come from `.env` — never pasted into the code. |
| Does it **install or run other software**? | `subprocess`, `pip install`, `os.system` | Understand exactly what, or don't run it. |
| Will it **run unattended** (scheduled)? | your own ticket's TRIGGER | Everything above gets stricter — nobody's watching. |
| Does it **run other code**? ← red flags | `subprocess.run`, `os.system`, `eval(`, `exec(` | **Stop.** These lines execute arbitrary programs or turn text into code. Ask the AI exactly what gets executed and why — often there's a safer way. |

## 2. The package check

AI models suggest packages that **don't exist** roughly 1 in 5 times — and attackers
register those made-up names with malicious code ("slopsquatting").

- Read the `dependencies = [...]` list in the PEP 723 header.
- Anything you don't recognize: check it on **pypi.org** — real page, real downloads,
  recent releases, plausible author?
- A typo'd package name is not a "close enough" — it's a different (possibly hostile) package.

## 3. Can you follow the story?

You don't need to understand every line. You need the plot:
input → process → output. Where does data come in, what happens to it, where does it go?

If you can't follow it: **"Explain this script step by step in plain English,
including everything it reads, writes, or sends."** Then re-read with the map.
If the explanation and the code seem to disagree — stop. Regenerate.

## 4. Then prove it (the "P" step)

1. `uv run script.py --help` — does it describe what you asked for?
2. Dry run. Read every line of what it *would* do.
3. `--apply` on a **practice copy**, never the real folder first.
4. Check your ticket's DONE MEANS by hand. Green? Now it's a tool.

---
**Read it. Bound it. Run it. Prove it.**

## How to read the verdict

_(Placeholder — the four checks above ARE the verdict. Green only when the blast
radius is bounded, every package is real, you can follow the story, and DONE MEANS
passes by hand. Any red — stop and regenerate.)_
