# Automate Tasks with Python + AI

**You don't need to learn to write Python. You need to learn to read it, run it,
and steer the AI that writes it.** This 2-day live course teaches a single
repeatable formula for turning everyday chores — messy folders, PDF invoices,
spreadsheets, voice notes, morning news — into small, safe, scheduled Python
tools generated with AI.

## The formula: the SCRIPT loop

Every automation in this course is built the same six-step way:

**S**pot it → **C**ompose the ticket → **R**equest the code → **I**nspect before
you run → **P**rove it → **T**urn it into a tool.

The one-page version lives in [`prompts/script-loop.md`](prompts/script-loop.md) —
it's the take-home artifact the whole course orbits.

## Start here (5 minutes)

1. Install `uv` (one command — no Python install, no environments):
   see **[SETUP.md](SETUP.md)** for Mac and Windows.
2. Download this folder (green **Code** button → Download ZIP, or `git clone`).
3. Run your first script:

```bash
uv run lessons/01_first_run.py
```

That's the entire setup. API keys only become relevant at lesson 07 — SETUP.md
covers them when you get there.

> **No-install fallback:** [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/EnkrateiaLucca/oreilly-python-course)

## What's in this repo

| Folder | What it is |
|---|---|
| [`lessons/`](lessons/) | **Day 1** — 8 short scripts that build your Python *reading vocabulary*: just enough to inspect any script an AI hands you. Run them in order. |
| [`demos/`](demos/) | **Day 2** — 3 real automations, each a full rep of the SCRIPT loop: document inbox → structured queue, messy data → interactive dashboard, personal intelligence briefing (scheduled) — then an endpoint that upgrades one tool into an agent-callable skill. |
| [`prompts/`](prompts/) | The take-home artifacts: the SCRIPT loop card, the automation-ticket template, the generate-a-tool prompt, the Run Gate checklist, the "does this already exist?" prompt, the tool-to-skill wrapper. |
| [`slides/`](slides/) | The course slide deck (Marp). |
| [`skills/`](skills/) | The SCRIPT loop packaged as a **Claude skill** — copy it into your own project and Claude walks you through the six steps, gates included. See [`skills/script-loop/README.md`](skills/script-loop/README.md). |
| [`extras/`](extras/) | Optional bonuses, outside the course flow. Currently: the **Maze Lab** — an animated maze game where your Python drives a robot (open `extras/maze/maze-lab.html`, zero setup). |

## The two days

**Day 1 — Read Python, run scripts.** A cold-open demo in the first ten minutes,
then the reading vocabulary (variables → loops → decisions → files → packages →
APIs → AI APIs), taught prediction-first: guess what the code prints, then run it.
Capstone: a downloads organizer you can read every line of.

**Day 2 — The loop at full power.** Three worked automations, each following the
same Spot→Compose→Request→Inspect→Prove→Turn beats, with real time to modify and
inspect each one: a document inbox that turns a messy pile into a structured
action queue, messy data into an interactive dashboard with an AI read of the
patterns, and a personal intelligence briefing that runs **unattended on a
schedule** — with the safety habits (dry-runs, blast-radius checks,
verify-what-done-means) that make that responsible. The day ends by upgrading one
tool you already understand into an **agent-callable skill**: the script is cheap,
the reusable capability is the asset.

## Who this is for

Knowledge workers, analysts, ops folks, founders — people who will never write
code from scratch but want the automations code makes possible. If you can write
a clear paragraph describing a task, this course teaches you to turn it into a
tool and to *know it's safe before you run it*.

---

*Legacy course material (Jupyter notebooks, previous slide deck, older demo
scripts) has been moved to [`archive-legacy-2026-08/`](archive-legacy-2026-08/)
and will be deleted around 2026-09-13. New students: ignore it — you only need
the folders in the table above.*
