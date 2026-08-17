# 04 — From script to reusable tool → to an agent skill

The last 20 minutes of the course. No new Python — a change in **mental model**.

Every demo so far ended at **T — Turn it into a tool**. Until now "tool" meant
*a script with an alias*. We're going to make that word mean more, because the
script was never the valuable part:

> **The script is cheap. The reusable *capability* is the asset.**

You leave understanding one continuum — and where you are on it:

**one-off automation → reusable tool → scheduled tool → agent-callable skill**

You already built the first three today. The fourth is almost free once the third
is done right.

---

## Step 1 — Make it a *reusable* tool (not just a script)

A script you can run is not yet a tool someone else — a teammate, future-you, or
an AI agent — can use reliably. Before you call any finished automation "done",
give it these four things:

1. **Clear inputs** — exactly what it takes: arguments, files, environment
   variables. (`document_inbox.py` takes one positional `folder`, an optional
   `--model` / `--format`, and reads `OPENAI_API_KEY` from `.env`.)
2. **Clear outputs** — exactly what it returns or changes. (Prints a table
   always; writes `inbox.csv` **only** with `--apply`; never touches the source
   files.)
3. **Safe defaults** — dry-run by default, bounded scope, friendly failures.
   (No `--apply` = nothing written. Missing key = a 3-line fix message, not a
   traceback.)
4. **Usage contract** — a short description of *when to use it*, *how to call it*,
   and *what it must never do*. This is your automation ticket, kept next to the
   tool.

If `uv run yourtool.py --help` and a one-paragraph note answer all four, it's a
reusable tool. That's the bar — and it's the same bar whether the caller is a
human or a model.

---

## Step 2 — The conceptual upgrade: describe it so an *agent* can call it

Here's the punchline: **nothing about the Python needs to change.** A tool that
already has clear inputs, clear outputs, safe defaults, and a usage contract is
already agent-ready — we just have to *write the contract down in a form an agent
reads*. That form is a **skill**: a short markdown file that tells an AI agent
when and how to invoke your tool.

Open [`SKILL.md`](SKILL.md) in this folder. It wraps demo 01's `document_inbox.py`
— the tool you already understand — with six fields:

- **Name** — what the capability is called
- **When to use** — the trigger, so the agent knows *whether* to reach for it
- **Inputs** — the arguments and files it needs
- **Command to run** — the exact `uv run …` line
- **Expected output** — what a successful run produces
- **Safety constraints** — the MUST NEVER lines, so the agent stays in its lane

That's the whole upgrade. The agent doesn't need to see your code; it needs your
usage contract in a shape it can act on. Same Run Gate, same blast radius
thinking — the agent just has a bigger reach, so the safety constraints matter
*more*, not less.

---

## ✏️ You build — 30 minutes: your first reusable tool

Build ONE small tool of your own, live, using the full SCRIPT loop — and finish
it to the **reusable-tool bar** above. Pick whatever you can describe in one
sentence right now:

- **Point demo 01 at your own documents** — a real folder you triage by hand.
- **Automate the ticket you brought from Day 1.** You spotted it; today you build it.
- **Extend a demo past its ✏️ Your-turn** — e.g. demo 03 with a second scheduled feed.

The path is the loop, no skipping steps just because it's yours:

1. **Fill the ticket** — [automation-ticket.md](../../prompts/automation-ticket.md).
2. **Generate** — [build-automation-mac.md](../../prompts/build-automation-mac.md) /
   [build-automation-windows.md](../../prompts/build-automation-windows.md).
3. **Run Gate** — [run-gate.md](../../prompts/run-gate.md) BEFORE the first run.
4. **Dry-run first**, then prove your DONE MEANS.
5. **Make it reusable** — the four requirements above.

### It counts as DONE when you can

1. Say **in one sentence** what the tool is for.
2. **Point at the line(s)** that write, move, or send anything.
3. Show your **done-means check passing**.
4. Answer all **four reusable-tool requirements** for it.

### If you finish early

Write a `SKILL.md` for *your* tool — copy the six fields from this folder's
example and fill them in. You now have an agent-callable capability, not just a
script. That's the take-home: the habit of turning a chore into a capability you
(or an agent) can reach for again.

---

## A note on scope

This is not a course on building agents — it's a course on building tools *good
enough that an agent could use them*. The skill wrapper is one page of markdown,
not a new framework. Most of your automations will live happily at "reusable
tool" or "scheduled tool" and never need the fourth rung. But now you can see the
whole ladder, and you know the rungs are all the same safety habits, one reach
further each time.
