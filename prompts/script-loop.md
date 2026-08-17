# The SCRIPT Loop — the course on one page

Every automation in this course is built the same way. Six steps, every time.
You don't need to memorize Python. You need to memorize this.

## S — Spot it
Is this task worth automating?
- Do I do it more than once a week, the same way every time?
- Could I write the steps down for an intern? (Rule-based = automatable.)
- **Does a tool for this already exist?** (Ask first — see `does-this-exist.md`.)

## C — Compose the ticket
One paragraph, four fields. This is the spec you'll hand the AI.
- **Trigger:** when does this run? (me, manually / every morning / when a file appears)
- **Touches:** which files, folders, websites, accounts?
- **Must never:** delete anything, send anything, touch files outside folder X…
- **Done means:** the concrete, checkable result. ("A CSV with one row per invoice.")

Template + examples: `automation-ticket.md`

## R — Request the code
Paste the ticket into the generation prompt (`generate-a-tool.md`).
Ask for: a single-file Python script, uv inline metadata, dry-run by default.
One task, one file. Disposable is fine — this is a tool, not software.

## I — Inspect before you run
The **Run Gate** (`run-gate.md`). AI-generated code is untrusted input.
- Blast radius: does it write/delete files? hit the network? read your keys? install things?
- Do all the packages in the header actually exist on pypi.org?
- Can you follow the story of the script? (You learned the reading vocabulary for exactly this.)
- Still unsure? Ask the AI: "Explain this script line-by-line in plain English."

## P — Prove it
- Run the **dry run** first. Read what it *would* do.
- Then `--apply` on a practice folder, then on the real thing.
- Check the ticket's "done means" — you told the AI what done means; now verify it.
  (Red → Green: it's only done when your own check passes.)

## T — Turn it into a (reusable) tool
The script is cheap. The reusable **capability** is the asset. Finish every tool
so a human *or* an AI agent could use it reliably — four things:
- **Clear inputs** — arguments, files, environment variables.
- **Clear outputs** — exactly what it returns or changes.
- **Safe defaults** — dry-run by default, bounded scope, friendly failures.
- **Usage contract** — when to use it, how to call it, what it must never do (that's your ticket).

Then ship it up the ladder as far as the task needs:
- **Alias it** ("ship it"): `alias briefing='uv run ~/tools/briefing.py'`
- **Schedule it**: launchd (Mac) / Task Scheduler (Windows) — see `demos/03-intelligence-briefing/`.
- **Skill it** (optional): describe the tool in one markdown file so an agent can
  invoke it — see `demos/04-tool-to-skill/` and `tool-to-skill.md`.
- Save the script + ticket + prompt in your personal tools folder. That's your hoard.

The continuum: **one-off automation → reusable tool → scheduled tool → agent-callable skill.**

---
*Read it. Bound it. Run it. Prove it.* — the four-word version.
