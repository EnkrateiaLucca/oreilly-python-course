# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "openai", "python-dotenv"]
# ///
"""Fetch today's top Hacker News stories and turn them into an AI morning briefing.

This is the demo that ends in UNATTENDED automation: alias it, then schedule it
(launchd on macOS, Task Scheduler on Windows) so a briefing waits for you at 8am.

Input   -> the public Hacker News API (top story titles + links, no key needed)
Process -> ask the AI to group the headlines and write a 5-bullet briefing
Output  -> markdown printed to the terminal; with --apply, saved to
           ~/morning-briefings/YYYY-MM-DD.md (what the scheduler uses)

Run it like:
    uv run demos/05-morning-briefing/briefing.py
    uv run demos/05-morning-briefing/briefing.py --limit 15 --apply

Needs: OPENAI_API_KEY in the repo-root .env, and an internet connection.
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

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


def fetch_top_titles(limit: int) -> list[str]:
    """Two-step API dance: one call for the story IDs, one per story for details."""
    story_ids = requests.get(TOP_STORIES_URL, timeout=20).json()[:limit]
    titles = []
    for story_id in story_ids:
        item = requests.get(ITEM_URL.format(id=story_id), timeout=20).json()
        if item and item.get("title"):
            titles.append(f"- {item['title']} ({item.get('url', 'no link')})")
    return titles


def write_briefing(titles: list[str]) -> str:
    prompt = ("Here are today's top Hacker News headlines. Group them into a few "
              "themes and write a 5-bullet morning briefing of what the tech "
              "community cares about today. Markdown, concise:\n\n"
              + "\n".join(titles))
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def main() -> None:
    parser = argparse.ArgumentParser(description="AI briefing of today's top Hacker News stories.")
    parser.add_argument("--limit", type=int, default=10,
                        help="How many top stories to fetch (default: 10)")
    parser.add_argument("--apply", action="store_true",
                        help="Also save to ~/morning-briefings/YYYY-MM-DD.md")
    args = parser.parse_args()

    # Fail fast so a scheduled run with a missing key logs a clear message.
    require_key("OPENAI_API_KEY", "https://platform.openai.com/api-keys")

    print(f"Fetching the top {args.limit} Hacker News stories...\n")
    try:
        titles = fetch_top_titles(args.limit)
    except requests.RequestException as error:
        print(f"Could not reach the Hacker News API: {error}")
        sys.exit(1)

    briefing = f"# Morning briefing — {date.today().isoformat()}\n\n{write_briefing(titles)}\n"
    print(briefing)

    if not args.apply:
        print("Dry run: not saved. Re-run with --apply to write the briefing file.")
        return

    out_dir = Path.home() / "morning-briefings"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"{date.today().isoformat()}.md"
    out_file.write_text(briefing, encoding="utf-8")
    print(f"Saved {out_file}")


if __name__ == "__main__":
    main()
