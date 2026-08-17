# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "feedparser", "openai", "python-dotenv"]
# ///
"""Pull from your chosen sources and turn them into an AI intelligence briefing.

This is the demo that ends in UNATTENDED automation: alias it, then schedule it
(launchd on macOS, Task Scheduler on Windows) so a personalized briefing waits for
you at 8am. Scheduling is the climax of the course because nobody is watching when
it runs — which is exactly why it earns the strictest Run Gate.

Input   -> the public Hacker News API, plus any RSS/Atom feeds you point it at
Process -> gather the day's headlines, ask the AI to theme them into a short briefing
Output  -> markdown printed to the terminal; with --apply, saved to
           ~/briefings/YYYY-MM-DD.md (what the scheduler uses)

Run it like:
    uv run demos/03-intelligence-briefing/briefing.py
    uv run demos/03-intelligence-briefing/briefing.py --rss https://hnrss.org/frontpage --apply
    uv run demos/03-intelligence-briefing/briefing.py --no-hn --rss https://www.theverge.com/rss/index.xml

Needs: OPENAI_API_KEY in the repo-root .env, and an internet connection.
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

import feedparser
import requests
from dotenv import load_dotenv
from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parents[2]
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


def require_key(name: str, where: str) -> str:
    """Load .env from the repo root, fall back to the environment, or explain the fix."""
    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get(name)
    if not key:
        print(f"No {name} found.")
        print(f"1) Get a key at {where}")
        print(f"2) Add this line to {REPO_ROOT / '.env'}:  {name}=your-key-here")
        sys.exit(1)
    return key


def fetch_hacker_news(limit: int) -> list[str]:
    """Two-step API dance: one call for the story IDs, one per story for details."""
    story_ids = requests.get(TOP_STORIES_URL, timeout=20).json()[:limit]
    headlines = []
    for story_id in story_ids:
        item = requests.get(ITEM_URL.format(id=story_id), timeout=20).json()
        if item and item.get("title"):
            headlines.append(f"- [Hacker News] {item['title']} ({item.get('url', 'no link')})")
    return headlines


def fetch_rss(url: str, limit: int) -> list[str]:
    """Any RSS/Atom feed becomes the same kind of headline line as Hacker News."""
    feed = feedparser.parse(url)
    source = feed.feed.get("title", url)
    return [f"- [{source}] {entry.title} ({entry.get('link', 'no link')})"
            for entry in feed.entries[:limit]]


def gather_headlines(use_hn: bool, feeds: list[str], limit: int) -> list[str]:
    headlines = []
    if use_hn:
        headlines += fetch_hacker_news(limit)
    for url in feeds:
        try:
            headlines += fetch_rss(url, limit)
        except Exception as error:                       # one bad feed shouldn't kill the run
            print(f"Skipping feed {url}: {error}")
    return headlines


def write_briefing(headlines: list[str]) -> str:
    prompt = ("Here are today's headlines from a few sources. Group them into a few "
              "themes and write a 5-bullet intelligence briefing of what matters "
              "today, keeping the source in mind. Markdown, concise:\n\n"
              + "\n".join(headlines))
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def main() -> None:
    parser = argparse.ArgumentParser(description="AI intelligence briefing from your chosen sources.")
    parser.add_argument("--limit", type=int, default=10,
                        help="How many items to pull per source (default: 10)")
    parser.add_argument("--rss", action="append", default=[], metavar="URL",
                        help="RSS/Atom feed URL to include (repeat for more)")
    parser.add_argument("--no-hn", action="store_true",
                        help="Skip Hacker News (use only your --rss feeds)")
    parser.add_argument("--apply", action="store_true",
                        help="Also save to ~/briefings/YYYY-MM-DD.md")
    args = parser.parse_args()

    # Fail fast so a scheduled run with a missing key logs a clear message.
    require_key("OPENAI_API_KEY", "https://platform.openai.com/api-keys")

    print(f"Gathering the day's headlines (limit {args.limit} per source)...\n")
    try:
        headlines = gather_headlines(not args.no_hn, args.rss, args.limit)
    except requests.RequestException as error:
        print(f"Could not reach a source: {error}")
        sys.exit(1)
    if not headlines:
        print("No headlines gathered. Add --rss URL or drop --no-hn.")
        sys.exit(1)

    briefing = f"# Briefing — {date.today().isoformat()}\n\n{write_briefing(headlines)}\n"
    print(briefing)

    if not args.apply:
        print("Dry run: not saved. Re-run with --apply to write the briefing file.")
        return

    out_dir = Path.home() / "briefings"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"{date.today().isoformat()}.md"
    out_file.write_text(briefing, encoding="utf-8")
    print(f"Saved {out_file}")


if __name__ == "__main__":
    main()
