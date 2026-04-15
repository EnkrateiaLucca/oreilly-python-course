# What Can You Automate with Python? A Simple Framework

The hard part of automation isn't writing the code — AI can do that for you.
The hard part is **seeing** the automation in your daily work.

This guide gives you a repeatable way to spot those opportunities and turn them into small, runnable scripts.

---

## 1. The core mental model: Input → Process → Output

Every automation, no matter how fancy, is three things:

```
  INPUT  ──►  PROCESS  ──►  OUTPUT
(data in)   (what to do)    (result)
```

Before you write a single line, answer three questions:

| Question     | Examples                                                              |
| ------------ | --------------------------------------------------------------------- |
| **Input?**   | A folder, a CSV, a URL, a PDF, text on your clipboard, an API response |
| **Process?** | Rename, filter, extract, summarize, convert, merge, call an AI model  |
| **Output?**  | A new file, a printed report, an email, a row added to a sheet        |

If you can fill these three blanks in one sentence, you almost certainly have a script on your hands.

---

## 2. The sniff test — is this worth automating?

Ask yourself:

1. **Do I do this more than once?** (Twice is a coincidence. Three times is a script.)
2. **Are the steps predictable?** Could you describe them to a friend in under a minute?
3. **Does the input live somewhere a computer can reach?** (A file, a URL, an API, the clipboard.)
4. **Is the output something a computer can produce?** (A file, a message, a printed value.)

Four yeses → strong candidate. Two or fewer → probably not worth it yet.

---

## 3. The five categories (and what each one looks like)

Most beginner-friendly automations fall into one of these buckets. [Inference] These categories are a teaching shortcut, not an official taxonomy — they're meant to jog intuition.

### a) Files & folders
Anything involving your filesystem.
- Rename 300 photos by the date they were taken
- Sort a messy Downloads folder by file type
- Back up a folder to a dated zip file every Friday

### b) Text & structured data
Anything where the input is a document or a table.
- Clean a CSV and drop duplicate rows
- Extract all email addresses from a folder of PDFs
- Convert a `.docx` report to Markdown

### c) The web
Anything that talks to a URL.
- Download the latest price of a stock once a day
- Scrape a page and save the headlines to a file
- Call a public API and turn the JSON into a spreadsheet

### d) App integrations
Anything that glues two tools together.
- Read unread Gmail messages and log their subjects
- Post a daily summary to Slack
- Add today's calendar events into a Notion page

### e) AI-powered
Anything that needs judgment or language understanding.
- Summarize a folder of meeting notes
- Classify incoming support emails by topic
- Turn a rough voice memo transcript into a clean blog draft

---

## 4. From vague idea to runnable script, in four steps

### Step 1 — Write the one-sentence spec
> "Take **\<input\>**, do **\<process\>**, and produce **\<output\>**."

Example: *"Take a folder of PDFs, extract every email address, and write them to `emails.csv`."*

### Step 2 — Ask an AI to draft the script
A template you can reuse:

```
Write a Python script that:
- Takes <input> as input
- Does <process>
- Produces <output>
Make it runnable from the command line with argparse.
Use only the standard library unless you need <library>.
```

### Step 3 — Run it
```bash
uv run python scripts/my_tool.py --input ./folder --output emails.csv
```

### Step 4 — Turn it into a CLI tool
This is the part most students underestimate. The jump from "a script I run once" to "a tool I can reuse" is mostly just:

- Put it in `scripts/`
- Accept inputs via `argparse` instead of hardcoding them
- Add a short `--help` description so future-you remembers what it does

That's it. You now have a real tool.

---

## 5. Red flags — when Python is probably the wrong hammer

[Inference] Based on common patterns, these tend to be poor fits for a beginner script:

- The "rules" change every time you do the task (requires human judgment per case).
- The input isn't reachable by a program (it only lives in your head, or behind a login with 2FA and no API).
- The task is faster to just do by hand once and never again.
- The consequences of a bug are expensive or irreversible (money transfers, mass email sends).

When in doubt, start with something small, boring, and repetitive. Those are the best first automations.

---

## 6. A 5-minute exercise for students

1. Write down **three things you did this week that felt repetitive**.
2. For each one, fill in: Input → Process → Output.
3. Pick the smallest one.
4. Paste its one-sentence spec into the AI prompt template above.
5. Run the script. If it works, wrap it in `argparse` and save it to `scripts/`.

By the end of the course, the goal isn't to have memorized Python syntax — it's to instinctively see your own workflow as a series of Input → Process → Output blocks.
