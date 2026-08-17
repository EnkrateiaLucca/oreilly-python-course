# 03 — Personal intelligence briefing → scheduled tool

## The problem

You start every workday doom-scrolling news across five sites for 25 minutes to
feel caught up, and still miss the one story that matters. What you actually want
is a short briefing — pulled from *your* sources — waiting for you at 8am, without
you doing anything at all.

This is the climax of the course, and it teaches the parts nothing before it
could: pulling from APIs and RSS feeds, AI summarization, and — the real prize —
**unattended execution on a schedule**. Scheduling materially changes the risk
profile: nobody is watching when it runs, so it earns the strictest Run Gate of
the two days.

## The ticket

- **Trigger:** every morning at 08:00, automatically (that's the whole point) —
  or manually whenever I want a briefing.
- **Touches:** reads the public Hacker News API and any RSS/Atom feeds I choose;
  sends the headlines (titles + links only) to the OpenAI API; with `--apply`
  writes one markdown file per day into `~/briefings/`. Needs `OPENAI_API_KEY`
  and internet.
- **Must never:** overwrite anything outside `~/briefings/`, send email or post
  anything, or fail silently when scheduled — errors must land in a log file I
  can read.
- **Done means:** `~/briefings/2026-08-17.md` exists before I sit down, with
  today's date and a themed 5-bullet briefing with links.

## The prompt that generated this

> Write a full runnable single-file Python script with uv inline metadata
> (PEP 723, requires-python >=3.12) that builds a morning briefing from multiple
> sources. By default fetch the top N stories from the public Hacker News API
> (topstories.json, then item/{id}.json). Add a repeatable --rss URL flag that
> pulls the top N entries from any RSS/Atom feed with feedparser, and a --no-hn
> flag to use only the feeds. Tag each headline with its source, send them all to
> the OpenAI API (model "gpt-5.6-luna") asking for a themed 5-bullet briefing in
> markdown, and print it. With --apply also save it to ~/briefings/YYYY-MM-DD.md,
> creating the folder if needed. Load OPENAI_API_KEY with python-dotenv from the
> repo-root .env and check it FIRST so scheduled runs fail loudly and early; one
> bad feed must not kill the run. No classes, friendly errors, under 170 lines.

## Run it

```bash
cd demos/03-intelligence-briefing

# Dry run — Hacker News only, print the briefing, save nothing:
uv run briefing.py

# Add your own sources (repeat --rss for more):
uv run briefing.py --rss https://hnrss.org/frontpage --rss https://www.theverge.com/rss/index.xml

# Save today's briefing file (this is what the scheduler runs):
uv run briefing.py --apply
cat ~/briefings/$(date +%F).md
```

## Prove it

- The briefing prints with today's date as the title and ~5 themed bullets, each
  traceable to a headline from one of your sources.
- Add a `--rss` feed and its stories show up tagged with that source's name.
- After `--apply`, `ls ~/briefings/` shows today's `YYYY-MM-DD.md`.
- Scheduled proof: the file appears tomorrow at 08:00 **without you running
  anything** — and if it doesn't, `cat /tmp/briefing.err` tells you why.

## ✏️ Your turn (5 minutes)

Make the briefing yours: (1) change it to **3 themed bullets** — that's the prompt
text inside `write_briefing()`; (2) add **one RSS feed you actually read** to the
default so a plain `uv run briefing.py` includes it — set argparse's `--rss`
`default=["<your-feed-url>"]` in `main()`.

- **Done means:** a plain `uv run briefing.py` prints exactly 3 bullets and
  includes at least one story from your feed.
- Stuck? Paste the script + this task into your AI — then
  [Run-Gate](../../prompts/run-gate.md) the diff.

## Turn it into a tool (then schedule it)

```bash
# macOS/Linux (~/.zshrc):
alias briefing='uv run ~/oreilly-python-course/demos/03-intelligence-briefing/briefing.py'
```

**Schedule it on macOS (launchd).** Edit `com.user.briefing.plist` (in this
folder): replace `YOUR-USERNAME` and the repo path. The pattern is that the plist
calls uv by absolute path: `/Users/<you>/.local/bin/uv run <absolute
path>/briefing.py --apply`. Then:

```bash
cp com.user.briefing.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.briefing.plist
launchctl start com.user.briefing        # test it right now
cat /tmp/briefing.log                     # see what happened
```

**Schedule it on Windows (Task Scheduler):**

```powershell
schtasks /Create /SC DAILY /ST 08:00 /TN "Briefing" /TR "C:\Users\YOUR-USERNAME\.local\bin\uv.exe run C:\Users\YOUR-USERNAME\oreilly-python-course\demos\03-intelligence-briefing\briefing.py --apply"
```

An unattended tool is one step from an agent-callable one — see
[`04-tool-to-skill/`](../04-tool-to-skill/) for the final upgrade.
