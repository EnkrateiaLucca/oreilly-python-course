# 05 — Morning briefing

## The problem

You start every workday doom-scrolling tech news for 25 minutes to feel caught
up, and still miss the one story that matters. What you actually want is five
bullets waiting for you at 8am — without you doing anything at all.

## The ticket

- **Trigger:** every morning at 08:00, automatically (that's the whole point) —
  or manually whenever I want a briefing.
- **Touches:** reads the public Hacker News API; sends headlines to the OpenAI
  API; with `--apply` writes one markdown file per day into
  `~/morning-briefings/`. Needs `OPENAI_API_KEY` and internet.
- **Must never:** overwrite anything outside `~/morning-briefings/`, send email
  or messages, or fail silently when scheduled — errors must land in a log file
  I can read.
- **Done means:** `~/morning-briefings/2026-08-12.md` exists before I sit down,
  with today's date and a themed 5-bullet briefing with links.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that fetches the top N stories from the
> public Hacker News API (topstories.json, then item/{id}.json for titles and
> urls), sends the headlines to the OpenAI API (model "gpt-5.6-luna") asking for
> a themed 5-bullet morning briefing in markdown, and prints it. With --apply it
> also saves the briefing to ~/morning-briefings/YYYY-MM-DD.md, creating the
> folder if needed. argparse with a --limit flag. Load OPENAI_API_KEY with
> python-dotenv from the repo-root .env and exit with a friendly 3-line fix
> message if it's missing — check the key FIRST so scheduled runs fail loudly
> and early. No classes, friendly errors, under 150 lines.

## Run it

```bash
cd demos/05-morning-briefing

# Dry run — print the briefing, save nothing:
uv run briefing.py

# Save today's briefing file (this is what the scheduler runs):
uv run briefing.py --apply
cat ~/morning-briefings/$(date +%F).md
```

## Prove it

- The briefing prints with today's date as the title and ~5 themed bullets.
- After `--apply`, `ls ~/morning-briefings/` shows today's `YYYY-MM-DD.md`.
- Scheduled proof: the file appears tomorrow at 08:00 **without you running
  anything** — and if it doesn't, `cat /tmp/morning-briefing.err` tells you why.

## ✏️ Your turn (5 minutes)

Two changes that live in two different functions: (1) make the briefing **3
bullets instead of 5** — that's the prompt text inside `write_briefing()`; (2)
put the **weekday name in the filename**, e.g. `2026-08-12-Wednesday.md` —
that's the `out_file` line in `main()`. Keep the ISO date first so the folder
still sorts by day; `date.today().strftime("%A")` gives you the weekday name.

- **Done means:** `uv run briefing.py --apply` prints exactly 3 bullets and
  `ls ~/morning-briefings/` shows a new file ending in today's weekday name.
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Ship it

```bash
# macOS/Linux (~/.zshrc):
alias briefing='uv run ~/oreilly-python-course/demos/05-morning-briefing/briefing.py'
```

**Schedule it on macOS (launchd).** Edit `com.user.morning-briefing.plist` (in
this folder): replace `YOUR-USERNAME` and the repo path. The pattern is that the
plist calls uv by absolute path: `/Users/<you>/.local/bin/uv run <absolute
path>/briefing.py --apply`. Then:

```bash
cp com.user.morning-briefing.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.morning-briefing.plist
launchctl start com.user.morning-briefing        # test it right now
cat /tmp/morning-briefing.log                    # see what happened
```

**Schedule it on Windows (Task Scheduler):**

```powershell
schtasks /Create /SC DAILY /ST 08:00 /TN "MorningBriefing" /TR "C:\Users\YOUR-USERNAME\.local\bin\uv.exe run C:\Users\YOUR-USERNAME\oreilly-python-course\demos\05-morning-briefing\briefing.py --apply"
```
