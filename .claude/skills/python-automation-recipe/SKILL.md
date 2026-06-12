---
name: python-automation-recipe
description: Interactively guide a student from a vague "I want to automate X" idea to a runnable, course-style Python script (or a clear "don't build this" recommendation). Grills the user through Lucas's O'Reilly "Automate Tasks with Python + AI" pedagogy — the Input→Process→Output mental model, the 5 automation categories, and the Reach/Rules/Reliability/Risk green/yellow/red audit — then generates a single-file `uv`-runnable script following the course's exact conventions (inline script metadata, argparse CLI, `ai_tools` pattern, dry-run flags for destructive ops, AI verification step). Use this skill whenever a student says any of: "build me a python automation", "automate this task", "make a script for X", "I want to automate X", "turn this into a script", "/python-automation-recipe", "help me write a script that does Y", "is this worth automating?", "should I script this?", or shows up with a repetitive task they want to offload. Also trigger when a student references the oreilly-python-course repo and wants to scaffold a new automation, or when they're stuck on the "what should I build?" step of a course exercise.
---

# Python Automation Recipe

Help a student in Lucas Soares' O'Reilly "Automate Tasks with Python + AI" course turn a vague repetitive-task idea into either:
- a runnable, course-style Python script, OR
- a clear recommendation explaining why scripting is the wrong tool here and what to do instead.

The skill's job is **not** to write code immediately. The job is to **interview the student first** using the course's mental models, then either build the right thing or say "don't build this." Skipping the interview produces brittle scripts aimed at the wrong problem — which is the #1 failure mode the course is designed to prevent.

## The course frame this skill encodes

Two short reference files in this skill capture the teaching:

- `references/automation-intuition.md` — Input→Process→Output, the sniff test, the 5 categories, the "vague idea → runnable script" 4-step flow.
- `references/four-rs-audit.md` — Reach / Rules / Reliability / Risk → green/yellow/red zones. This is the audit that decides whether to build at all.

Read these references when you reach the relevant step. They're short. Don't paraphrase them from memory.

A third file gives you ready-to-adapt code:

- `references/script-templates.md` — Per-category skeletons (file-management, pdf-documents, data-dashboards, browser-automation, email-comms, ai-text) with the exact conventions Lucas teaches: uv inline metadata, argparse, `ai_tools.ask_ai`, dry-run flags, structured LLM output, idempotency notes.

## Interactive workflow

Work through these steps **in order**. Use the `AskUserQuestion` tool for each branching question — do not infer the student's intent silently. The grilling is the value: it's how the student internalizes the course's mental model.

### Step 1 — Get the one-sentence spec

Ask the student to describe the repetitive task in plain language. If they offer something vague ("I want to automate my emails"), push back with a single AskUserQuestion that offers 2–4 concrete narrowings (e.g., "Classify incoming emails by urgency", "Auto-reply to newsletter subscriptions", "Daily digest of unread mail"). Don't move on until you can write **one sentence** of the form:

> "Take **\<input\>**, do **\<process\>**, produce **\<output\>**."

Echo that sentence back and confirm.

### Step 2 — Fill the I→P→O blanks explicitly

Ask the student to name each blank concretely:

- **Input**: what kind of thing, where does it live (path / URL / API / clipboard), how often does it arrive?
- **Process**: the transformation in one short paragraph. Flag if it needs human judgment per case — that's a yellow/red signal.
- **Output**: file / printed report / email / DB row / etc., and where it goes.

If any blank is vague after one round of clarification, name the gap out loud and ask again. The point is for the student to feel the difference between "I want to automate emails" and "I want to read unread Gmail messages from the last 24h and write a CSV of subject + sender to ~/daily-mail.csv".

### Step 3 — Run the 4 R's audit

Read `references/four-rs-audit.md` now. Walk the student through Reach / Rules / Reliability / Risk **using their specific task**. Use one AskUserQuestion per R with concrete option labels tailored to their scenario (e.g., for Reach: "Yes, plain HTTP endpoint", "Behind login but has API", "Behind SSO/2FA, no API"). Score each as green / yellow / red and announce the overall zone:

- **Green** (all 4 green, or 3 green + 1 yellow) → proceed to Step 4a.
- **Yellow** (any yellow without reds) → proceed to Step 4b with the explicit warning template.
- **Red** (any single red) → go to Step 4c and **refuse to build**. The course's whole point is that recognizing red-zone tasks is the most valuable skill a student can learn.

State the zone *and the reason* — not "this is red" but "this is red because the rules genuinely change per case (Rules → red)".

### Step 4a — GREEN ZONE: build the script

1. Confirm the **category** with the student (`AskUserQuestion`, 4 options drawn from the 5 categories): files & folders / text & docs / web & APIs / app integrations / AI-powered. Pick the closest fit.
2. Ask a single consolidated `AskUserQuestion` (multiSelect=true) for the build choices the student would otherwise forget:
   - Needs API keys? (OpenAI, Anthropic, none)
   - Destructive op? (moves/deletes/sends — if yes, the script gets `--dry-run` defaulted to **on**)
   - Run on a schedule? (one-shot vs cron/launchd suggestion at the end)
   - Output format? (stdout, CSV, JSON, Markdown report)
3. Ask where to save it. Default suggestion: `/Users/greatmaster/Desktop/projects/oreilly-live-trainings/oreilly-python-course/scripts/student/<verb_noun>.py` — but **always confirm the path with the student** rather than assuming.
4. Read the matching section of `references/script-templates.md` and adapt it. Always include, regardless of category:
   - `# /// script` uv inline metadata with `requires-python = ">=3.12"` and minimal `dependencies = [...]`.
   - `argparse` with a real `--help` description.
   - Small typed functions, `print(...)` progress lines.
   - For **any destructive op**: `--dry-run` flag, defaulted true if the student hasn't already used the script, and a final printed summary of what *would* change.
   - For **any AI call**: print the model's raw output before acting on it, and add either a `--review` flag that pauses for human confirmation, or a rule-based sanity check (length bounds, schema validation, regex match). The course's #1 teaching is "silent wrongness" from LLMs — this is non-negotiable.
   - For **LLM output that downstream code consumes**: ask for JSON via prompt + parse with a try/except, do not parse free text.
   - For **file writes/moves**: make it idempotent (e.g., suffix on name conflict, skip if dest exists, or explicit overwrite flag).
5. Write the file with the `Write` tool. Then print:
   - The exact `uv run python <path> --help` command.
   - A 1-line dry-run command.
   - If the student said "run on a schedule," a short, OS-appropriate cron/launchd/Task Scheduler snippet (macOS → launchd plist or `crontab -e` line; explicitly mention which one is which).

### Step 4b — YELLOW ZONE: build it, but warn loudly

Same as Step 4a, but the script header gets a `# WARNING:` comment block naming the fragility (e.g., "Scrapes a JS-rendered page — selectors may break when the site updates"), and the student-facing summary explicitly says:

> "This is in the **yellow zone** because [reason]. Run it manually a few times, watch the output, and expect to babysit it. Don't put it on a schedule yet."

Always include a verification step (printed diff, sample of rows, human-in-the-loop prompt) and explicitly tell the student where the script is likely to rot first.

### Step 4c — RED ZONE: refuse, and recommend

Do **not** generate a script. Instead respond with:

1. One sentence naming which R landed red and why.
2. A short concrete alternative — usually one of:
   - "Do this by hand 3 more times and notice the rules. Then automate a smaller scoped version."
   - "Keep a human in the loop: write a script that prepares the action but doesn't execute it (drafts the email, builds the transaction request, organizes the candidate list)."
   - "Use a tool that already solves this safely (Zapier/Make/Notion automations/email rules)."
3. Offer to scope down: ask the student if they want to redefine the task as a green-zone subset (e.g., not "auto-reply to support emails" but "classify the inbox and draft replies to a labeled folder for human review").

This is **not** a failure mode of the skill — it's the most valuable lesson the course teaches. Frame it that way.

## Style guarantees for generated scripts

Every script this skill writes must follow these conventions, which match Lucas's `scripts/demos/` patterns:

- **Single file**. No package layout, no nested modules.
- **uv inline metadata** at the top so `uv run python script.py` Just Works:
  ```python
  # /// script
  # requires-python = ">=3.12"
  # dependencies = ["openai", "anthropic"]
  # ///
  ```
- **Type hints** on function signatures.
- **`argparse`** with a descriptive `prog` and `description`. No `sys.argv[1]` positional hacks.
- **Imports** at top, **`main()` function**, **`if __name__ == "__main__": main()`** at bottom.
- **AI calls** follow the `ai_tools.ask_ai` pattern: short helper function, model name as an argument with a sane default, raw output printed before downstream parsing.
- **No emojis** in code output, no decorative banners. Print plain, scannable progress lines.
- **Defensive only at the I/O boundary** — validate the input path exists, the URL is reachable, the API key is set. Trust internal code.
- **Idempotency**: a second run with the same input doesn't corrupt state.
- **Tiny docstrings** — one line max per function, the *why* not the *what*.

## What this skill should NOT do

- Don't skip the interview to look fast. The interview is the deliverable.
- Don't generate a script for a red-zone task even if the student insists. Offer the scoped-down green version instead.
- Don't add testing infrastructure, CI, logging frameworks, retry decorators, or other production scaffolding — this is a learning-grade script.
- Don't write multi-paragraph docstrings or explanatory comments. The course style is terse.
- Don't invent fake `ai_tools` or course modules — if the script needs the course's `ask_ai`, inline a 10-line copy of the function rather than importing from a sibling path the student may not have.

## When the student already has a draft

If the student arrives with a script and asks "is this OK?", skip Steps 1–2 (the spec is the script), run Step 3 (the 4 R's audit) against what the code actually does, then propose targeted fixes — don't rewrite from scratch unless they ask.
