# The Automation Ticket

One paragraph. Four fields. Fill it in *before* you ask an AI for code —
a vague ask produces a vague (and riskier) script. This is the "C" in the SCRIPT loop.

## Template

```
TASK: <one sentence — what should happen>
TRIGGER: <when it runs: manual / every morning at 8 / when I drop a file in X>
TOUCHES: <exact folders, files, sites, accounts it may read or write>
MUST NEVER: <hard limits: never delete, never send, never leave folder X, never spend money>
DONE MEANS: <the checkable result you will verify — be concrete>
```

## Example 1 — invoices

```
TASK: Pull the company, date, and total out of each PDF invoice into one spreadsheet.
TRIGGER: Manual — I run it after downloading the month's invoices.
TOUCHES: Reads PDFs in ~/Documents/invoices-2026-08/ only. Writes one new CSV next to them.
MUST NEVER: Modify or move the PDFs. Touch any other folder. Upload the PDFs anywhere
            except the AI API I choose.
DONE MEANS: invoices.csv exists with one row per PDF and columns company, date, total —
            and the totals for 3 invoices I spot-check by hand are correct.
```

## Example 2 — morning briefing

```
TASK: Fetch the top 10 Hacker News stories and write me a 5-bullet AI summary.
TRIGGER: Every weekday at 7:30am, unattended.
TOUCHES: Reads the public Hacker News API. Writes one markdown file to ~/briefings/.
MUST NEVER: Send email, post anything, or touch any other folder.
DONE MEANS: A dated file like ~/briefings/2026-08-12.md exists each weekday morning
            with 5 bullets and links.
```

## Why this works

- **Trigger** decides how careful you must be — anything unattended gets a stricter Run Gate.
- **Touches** defines the blast radius *before* the AI does.
- **Must never** goes verbatim into your prompt; AIs follow explicit constraints well.
- **Done means** is your Red→Green check — if you can't describe done, you can't verify it,
  and a script you can't verify is a script you shouldn't schedule.
