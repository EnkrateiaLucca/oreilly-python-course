---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Automate Tasks with Python + AI'
footer: 'O\'Reilly Live Training'
style: |
  section {
    font-size: 26px;
  }
  h1 {
    color: #1a1a1a;
  }
  h2 {
    color: #2c3e50;
  }
  table {
    font-size: 22px;
  }
  .zone-green { color: #2e7d32; font-weight: bold; }
  .zone-yellow { color: #f57f17; font-weight: bold; }
  .zone-red { color: #c62828; font-weight: bold; }
  .lead {
    text-align: center;
    font-size: 38px;
  }
---

<!-- _class: lead -->

# What Can — and Can't — Be Automated with Python?

### Building intuition before writing code

---

## Where we're going

**Part 1 — What Python _can_ do for you**
A framework for spotting automations in your own work.

**Part 2 — What Python _can't_ do for you**
A framework for avoiding expensive dead ends.

> The hard part of automation isn't the code.
> AI can write the code.
> The hard part is **seeing the automation**.

---

<!-- _class: lead -->

# Part 1
## What can you automate?

---

## The core mental model

Every automation is three things:

# `INPUT → PROCESS → OUTPUT`

Before writing any code, fill in three blanks.

| Blank        | Example                                        |
| ------------ | ---------------------------------------------- |
| **Input?**   | A folder, CSV, URL, PDF, clipboard, API call   |
| **Process?** | Rename, filter, extract, summarize, convert    |
| **Output?**  | A new file, a report, an email, a sheet row    |

---

## Example — filled in

**Task:** "Rename all photos in a folder by the date they were taken."

- **Input:** a folder of photos
- **Process:** read each photo's EXIF date
- **Output:** renamed files in the same folder

If you can say it in one sentence like this, **you have a script**.

---

## The sniff test — is it worth automating?

Four yes/no questions:

1. Do I do this **more than once**?
2. Are the steps **predictable**?
3. Does the input live somewhere a computer can **reach**?
4. Is the output something a computer can **produce**?

**4 yeses** → strong candidate
**2 or fewer** → not worth automating yet

> Twice is a coincidence. Three times is a script.

---

## The five categories

Most beginner-friendly automations fall into one of these buckets.

| # | Category             | What it touches              |
| - | -------------------- | ---------------------------- |
| 1 | Files & folders      | Your filesystem              |
| 2 | Text & data          | Documents, tables, PDFs      |
| 3 | The web              | URLs, pages, public data     |
| 4 | App integrations     | Gmail, Slack, Notion, etc.   |
| 5 | AI-powered           | Language & judgment tasks    |

_[Inference] A teaching shortcut, not an official taxonomy._

---

## Category examples (1–3)

**1. Files & folders**
Rename 300 photos by date • Sort Downloads by file type • Zip-backup a folder every Friday

**2. Text & data**
Clean a CSV • Extract emails from a folder of PDFs • Convert `.docx` → Markdown

**3. The web**
Track a stock price daily • Scrape public headlines • Call a public API, save as spreadsheet

---

## Category examples (4–5)

**4. App integrations**
Read unread Gmail and log subjects • Post a daily Slack summary • Sync calendar events into Notion

**5. AI-powered**
Summarize a folder of meeting notes • Classify incoming support emails • Turn voice memo transcripts into clean drafts

> Common thread in green-zone work: data is **reachable**, rules are **describable**, errors are **cheap**.

---

## From idea to runnable script — 4 steps

1. **Write the one-sentence spec**
  _"Take `<input>`, do `<process>`, produce `<output>`."_

2. **Ask an AI to draft it** (template on next slide)

3. **Run it**
  `uv run python scripts/my_tool.py --input ./folder`

4. **Turn it into a CLI tool**
  `argparse` + save to `scripts/` + a `--help` description

---

## Reusable AI prompt template

```
Write a Python script that:
- Takes <input> as input
- Does <process>
- Produces <output>

Make it runnable from the command line with argparse.
Use only the standard library unless you need <library>.
```

Paste your one-sentence spec into the blanks. That's it.

---

## Script → CLI tool

The jump students underestimate is **not** writing the code.
It's turning a one-off script into a reusable tool.

Three moves:

1. Replace hardcoded paths with `argparse` arguments
2. Save it to `scripts/` with a clear name
3. Add a one-line `--help` description

**That's the whole difference** between a script and a tool.

---

<!-- _class: lead -->

# Part 2
## What Python _can't_ do for you

---

## The core frame: the four R's

Before committing to automate something, ask:

| Question          | What it's really asking                                     |
| ----------------- | ----------------------------------------------------------- |
| **Reach?**        | Can my code get to the data and act on the system?          |
| **Rules?**        | Can I describe the logic in plain steps?                    |
| **Reliability?**  | Am I OK with occasional mistakes?                           |
| **Risk?**         | If it misfires, is the worst case recoverable?              |

The four answers sort every task into a zone.

---

## Three zones

<span class="zone-green">■ GREEN</span> — Build it. Python is great at this.

<span class="zone-yellow">■ YELLOW</span> — Possible, but fragile. Build it small. Babysit it.

<span class="zone-red">■ RED</span> — Don't aim Python here. Keep a human in the loop.

---

## <span class="zone-green">Green zone</span> — Python shines

- Moving data between files and formats (CSV ↔ JSON ↔ Excel, PDFs, logs)
- Talking to documented APIs (OpenAI, Anthropic, GitHub, Notion, Gmail)
- Scraping **public, static** web pages
- Running things on a schedule (backups, daily reports)
- LLM language tasks: summarize, classify, extract, rewrite
- Gluing tools together — "when X happens in A, write to B"

Common thread: **reachable, describable, cheap to get wrong.**

---

## <span class="zone-yellow">Yellow zone</span> — possible, but fragile

- Scraping sites with logins, captchas, or heavy JavaScript
- Automating desktop apps by clicking buttons (breaks on every update)
- Parsing messy/inconsistent documents (scanned PDFs, wild emails)
- Anything that "mostly works" 90% of the time — when the other 10% matters
- Long chains of AI calls without verification steps

> Rule of thumb: **build it small, watch it run, expect to babysit.**

---

## <span class="zone-red">Red zone</span> — wrong shape of problem

**Reach:** closed systems, 2FA/SSO with no API, mobile-only apps, physical tasks
**Rules:** tasks that need genuine human judgment every time
**Reliability:** near-perfect is required (medical, legal, safety)
**Risk:** irreversible or expensive failure (moving money, mass email, bulk delete)

> If any of the four R's lands in red, **keep the human in the loop** — or pick a smaller version of the task.

---

## The AI-specific trap

Because this course uses AI heavily, two failure modes matter:

**1. Silent wrongness**
LLMs produce confident, fluent output even when it's wrong.
_[Inference] Based on observed patterns, this is the #1 source of broken student automations._

**2. Drift**
The same prompt can give different outputs on different days or model versions.

**Habit:** print the AI's output before you act on it — for the first dozen runs at least.

---

## 30-second "which zone?" checklist

Before you build:

- [ ] I can **reach** the input without manual steps
- [ ] I can **describe the rules** in a paragraph
- [ ] I'm OK with occasional errors, or I have a way to catch them
- [ ] If the script misfires, the worst case is **easy to undo**

**4 checks** → build it
**3 checks** → build small, watch it run
**2 or fewer** → don't automate yet. Do it by hand and learn the shape first.

---

## 5-minute exercise

1. Write down **three repetitive tasks** from your week
2. For each: fill in **Input → Process → Output**
3. For each: answer the **four R's** (reach, rules, reliability, risk)
4. Sort them: <span class="zone-green">green</span> / <span class="zone-yellow">yellow</span> / <span class="zone-red">red</span>
5. Build only the **green** ones this week
6. Write one sentence for each **red** one explaining _why_ it's red

That last sentence is often the most valuable thing you'll learn.

---

<!-- _class: lead -->

## The real skill isn't Python.

### It's instantly recognizing
### what's automatable and what isn't —
### and not wasting a weekend on a task
### that was always in the red zone.

---

<!-- _class: lead -->

# Thank you

### Questions?
