---
name: script-loop
description: >-
  Run the SCRIPT loop — the six-step formula from Lucas Soares' O'Reilly
  "Automate Tasks with Python + AI" course — to turn a repetitive chore into a
  safe, single-file Python tool: Spot it, Compose the ticket, Request the code,
  Inspect before you run, Prove it, Turn it into a tool. Use this whenever
  someone wants to automate a task, asks for a script for a chore, says
  "automate X", "build me a python automation", "make a script that…",
  "turn this into a tool", "is this worth automating?", "/script-loop", or
  hands over a repetitive manual process. Also use to resume mid-loop ("run the
  Run Gate on this script", "write me an automation ticket", "wrap this script
  as a skill") and to audit an existing AI-generated script before running it.
---

# The SCRIPT loop

Six steps, every time. Your job is to do the mechanical work at each step and
make the human do the judgment at each gate. **Never skip a gate to be helpful** —
the gates are the entire safety story of AI-generated automation.

The student-facing one-pager is `references/script-loop.md`. Read a reference
file when you reach its step; they are short and you must not paraphrase them
from memory.

Announce which letter you're on as you go (`**S — Spot it**`), so the person
learns the loop and not just the answer.

---

## S — Spot it

Before anything else, ask whether this should be built at all.

1. Get the chore in one sentence. If it's vague ("automate my emails"), offer
   2–4 concrete narrowings with `AskUserQuestion` rather than guessing.
2. Check: does it happen more than once a week, the same way every time? Could
   the steps be written down for an intern? If the rules genuinely change per
   case, say so and stop — that's a judgment task, not an automation.
3. Run the does-this-exist check (`references/does-this-exist.md`). Name real
   existing tools, free first, Mac and Windows. Give a one-line verdict:
   **BUY / USE BUILT-IN / BUILD**.

**Gate:** if the verdict isn't BUILD, say so plainly and stop. Saving them an
afternoon is a better outcome than a script.

## C — Compose the ticket

Write the ticket **before** any code. Five fields, from
`references/automation-ticket.md`:

```
TASK:       one sentence — what should happen
TRIGGER:    manual / every morning at 8 / when a file appears
TOUCHES:    exact folders, files, sites, accounts it may read or write
MUST NEVER: hard limits — never delete, never send, never leave folder X
DONE MEANS: the concrete result you will check by hand
```

Draft it yourself from what they told you, then show it and ask them to correct
it. Push back on two things specifically:

- a TOUCHES that isn't bounded to specific paths
- a DONE MEANS that isn't checkable by hand ("it works" is not a DONE MEANS)

**Gate:** all five fields filled, and the person has agreed to them. Save the
ticket next to where the tool will live — it becomes the tool's usage contract
in step T.

## R — Request the code

Generate one single-file Python script following every constraint in
`references/generate-a-tool.md`. Non-negotiable:

- PEP 723 inline metadata (`# /// script` … `# ///`), runnable with `uv run script.py`
- only packages that actually exist on PyPI, all listed in the header
- small functions, no classes, no cleverness — the person must be able to *read* it
- anything that moves/changes/deletes/sends: **dry-run by default**, acts only with `--apply`
- `argparse` so `--help` explains it
- friendly plain-English errors, never a raw traceback
- every MUST NEVER line enforced in code, not in a comment
- final line prints a one-line summary matching DONE MEANS

If it calls an AI API, use the current SDK snippet from the reference rather
than writing the call from memory.

**Gate:** do not run the script yet. Go to I.

## I — Inspect before you run (the Run Gate)

AI-generated code is untrusted input. Walk `references/run-gate.md` out loud
against the actual script and report each finding:

1. **Blast radius** — files written/moved/deleted? network? secrets? installs?
   `subprocess`/`os.system`/`eval`/`exec` (red flag — stop and justify or rewrite)?
   Unattended trigger makes all of this stricter.
2. **Package check** — every dependency in the header: real on PyPI, plausible,
   maintained? A near-miss name is a different package, not a typo.
3. **Follow the story** — state the script's plot in three lines:
   input → process → output. If you can't, the script is too clever; regenerate.
4. Confirm the code actually honours every MUST NEVER line.

**Gate:** report the gate as passed or failed. Any red — regenerate, don't
patch around it. Ask the person to confirm before the first run.

## P — Prove it

In order, never skipping ahead:

1. `uv run <script>.py --help` — does it describe the ticket?
2. Dry run. Show them what it *would* do, in full.
3. `--apply` on a **practice copy** of the data, never the real folder first.
4. Check DONE MEANS by hand and say explicitly whether it passed.

Red → Green: it is not done until the ticket's own check passes on the real
thing. If it fails, improve the **ticket** and regenerate rather than patching
the script through many turns.

**Gate:** DONE MEANS verified, stated plainly. If it didn't pass, say that.

## T — Turn it into a tool

The script is cheap; the reusable capability is the asset. From
`references/tool-to-skill.md`, confirm all four:

- **Clear inputs** — args, files, env vars, visible in `--help`
- **Clear outputs** — what it writes or returns, and where
- **Safe defaults** — dry-run default, bounded scope, friendly failures
- **Usage contract** — the ticket, saved next to the tool

Then offer the ladder, and recommend the rung the chore actually needs:

- **Alias it** — `alias briefing='uv run ~/tools/briefing.py'`
- **Schedule it** — launchd (Mac) / Task Scheduler (Windows); working example in
  `demos/03-intelligence-briefing/`
- **Skill it** — only if an agent will call it. Write the wrapper from the
  template in `references/tool-to-skill.md`; the Python does not change.

Most tools stop at "reusable" or "scheduled". That's fine — name the rung and
say why.

---

## Entering mid-loop

People often arrive holding a script or a half-finished idea. Jump straight to
the right letter, say which one, and finish the remaining steps:

| They say | Start at |
|---|---|
| "should I automate this?" / "does this already exist?" | **S** |
| "write me a ticket / spec for this" | **C** |
| "here's my ticket, write the script" | **R** |
| "is this script safe to run?" / "run the Run Gate" | **I** |
| "it ran, did it work?" | **P** |
| "make this reusable" / "wrap this as a skill" | **T** |

## Rules

- One task, one file. Disposable is fine — this is a tool, not software.
- Never run a generated script before the Run Gate, and never on real data
  before a dry run and a practice copy.
- Wrong result → fix the **ticket**, then regenerate. If a fix drags past 2–3
  turns, start fresh with the improved ticket and the current script.
- Keep scripts readable over clever. The person has to inspect it without you.
