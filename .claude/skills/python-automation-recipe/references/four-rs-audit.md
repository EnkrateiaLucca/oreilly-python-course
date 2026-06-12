# The 4 R's Audit — Reach / Rules / Reliability / Risk

Source: `oreilly-python-course/notebooks/03-automation-projects/00b-automation-limits.md`.
Read this before Step 3 of the skill workflow. The audit decides whether to build at all.

## The four questions

| Question            | What it's really asking                                                  |
|---------------------|--------------------------------------------------------------------------|
| **Reach?**          | Can my code actually *get to* the data and *act on* the system?          |
| **Rules?**          | Can I describe the logic in plain steps, or does it need real judgment?  |
| **Reliability?**    | Am I OK with occasional mistakes, or does it have to be perfect?         |
| **Risk?**           | If the script misbehaves, is the worst case recoverable or a disaster?   |

Score each green / yellow / red, then take the worst color as the overall zone.

## Green zone — Python is great at this

- Moving data between files and formats (CSV↔JSON↔Excel, PDF text extraction).
- Talking to documented APIs (OpenAI, Anthropic, GitHub, Notion, Gmail, Slack).
- Scraping public, static, JS-free pages.
- Scheduled jobs (nightly backups, daily reports).
- LLM language tasks **with spot-checks**.
- Gluing tools together with a clear "when X, do Y."

Common thread: data is **reachable**, rules are **describable**, errors are **cheap**.

## Yellow zone — possible but fragile (build small, watch it run)

- Scraping logged-in / captcha-protected / heavily JS-rendered sites.
- Automating desktop apps without an API (coordinate-based clicking).
- Parsing wildly inconsistent documents (scanned PDFs, messy hand-written notes).
- Anything that "mostly works 90% of the time" *when the other 10% matters*.
- Long chains of unverified AI calls — errors compound.

Generated script must: warn loudly, include a verification step, **not** be scheduled until human-watched for ≥10 runs.

## Red zone — refuse, recommend an alternative

### Reach problems
- Systems behind strict SSO / 2FA / enterprise auth without an API.
- Content inside closed mobile apps, DRM files.
- Anything requiring physical presence.

### Rules problems
- "Decide whether this needs a human reply." (Rules differ every time.)
- Legal, medical, hiring decisions where accountability matters.
- Creative work where the value *is* the judgment.

### Reliability problems
- Anything financial where a mistaken transaction is unrecoverable.
- Mass communications without a human in the loop.
- Safety-critical calculations.

### Risk problems
- Executing trades / moving money automatically.
- Bulk-deleting files with no backup.
- Auto-responding to customers with unreviewed AI content.

## The specific trap of AI automations

Two failure modes worth naming to the student:

1. **Silent wrongness** — LLMs produce confident, fluent, wrong output. **Always** add a verification step (human spot-check, rule-based sanity check, or second-model cross-check). This is the #1 source of broken automations in the course.
2. **Drift** — same prompt, different output across days or model versions. Re-tune.

Habit to teach: **print the AI's output before acting on it**, for the first dozen runs minimum.

## 30-second checklist (use as the AskUserQuestion options)

- I can reach the input without manual steps. *(no → yellow/red)*
- I can describe the processing rules in a paragraph. *(no → yellow/red)*
- I'm OK with occasional errors, or I have a way to catch them. *(no → yellow)*
- If the script misfires, the worst case is easy to undo. *(no → red)*

4 → build it. 3 → build small + watch it. 2 or fewer → don't automate yet.

## Red-zone recommendations to offer

When you refuse to build, propose one of:

- **"Do it by hand 3 more times and notice the rules."** The rules will either crystallize (now green) or you'll see why they can't (confirmed red).
- **"Keep a human in the loop."** Build the script that *prepares* the action — drafts the email to a Drafts folder, organizes candidates into a sortable sheet, builds a transaction request as JSON for review — but does not *execute*.
- **"Use a tool that already solves this safely"** (Zapier / Make / native email rules / Notion automations / IFTTT). Often the right answer for app-integration tasks that need enterprise auth.
- **"Scope it down to a green subset."** Offer a concrete narrower task you *can* build right now.
