# 07 — Your first tool (capstone)

There is no script in this folder. That's the point.

Every demo so far was a rep of the SCRIPT loop with the instructor driving.
This is the Make stage: **30-40 minutes, you build, instructor circulates.**
You leave the course with a tool that exists because you built it.

## The assignment

Build ONE small tool of your own, live, using the full SCRIPT loop.
Pick whichever option you can describe in one sentence right now:

- **(a) Combine two of today's demos.** Examples: after saving the morning
  briefing, also diff it against yesterday's briefing file (05 + 06 thinking);
  or transcribe a voice note and auto-file it into a topic folder (04 + 01).
- **(b) Automate the ticket you brought from your Day-1 homework.** You already
  spotted it — today you build it.
- **(c) Extend a demo beyond its ✏️ Your-turn.** Examples: demo 01 with a
  `--undo` log of every move; demo 02 pointed at a folder of YOUR documents;
  demo 06 writing its report to a markdown file with `--apply`.

Scope check: if the ticket's TASK line needs the word "and" twice, it's two
tools. Build the first one.

## The required path

The same loop as every demo — no skipping steps just because it's yours:

1. **Fill the ticket** — [automation-ticket.md](../../prompts/automation-ticket.md).
   Five fields, especially MUST NEVER and DONE MEANS.
2. **Generate** — paste your ticket into
   [build-automation-mac.md](../../prompts/build-automation-mac.md) or
   [build-automation-windows.md](../../prompts/build-automation-windows.md).
3. **Run Gate** — [run-gate.md](../../prompts/run-gate.md) BEFORE the first run:
   blast radius, package check, can you follow the story?
4. **Dry-run first** — on practice data if the tool moves or writes anything.
5. **Prove your done-means** — run the exact check you wrote in the ticket.

## It counts as DONE when

You can do the plain-English "code walk" — no jargon required:

1. Explain **in one sentence** what the script is for.
2. **Point at the line(s)** that write, move, or send anything.
3. Show your **done-means check passing.**

If you can do those three things, you didn't just get code from an AI —
you have a tool you can vouch for.

## If you finish early

- **Ship it:** give it an alias so it's one word from any terminal.
- **Schedule it** (if its trigger is time-based) — steal the launchd /
  Task Scheduler recipe from [demo 05](../05-morning-briefing/).
- **Run your own ✏️ Your-turn:** change one behavior of your tool and re-prove it.
- **Point it at real data** — after one more dry run.
- **Write tomorrow's ticket:** the next annoyance you'd automate. Filling the
  ticket is the skill; the code is the cheap part.

## A note on ugly

Disposable and ugly is fine — this is a tool, not software. No tests, no repo,
no design review. If it saves you ten minutes a week and you can pass the code
walk above, it's a success. Delete it without guilt when it stops being useful;
you now know how to make another.
