# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.32",
#     "openai>=1.0",
# ]
# ///
"""Fetch today's top Hacker News stories and turn them into an AI briefing.

Automation category: Web / API + AI.

Input   -> the public Hacker News API (top story titles + links)
Process -> ask an LLM to group the headlines and write a short briefing
Output  -> a markdown briefing printed to the terminal

Run it like:
    uv run scripts/demos/email-comms/news_briefing.py
    uv run scripts/demos/email-comms/news_briefing.py --limit 15

Needs: OPENAI_API_KEY (set in your environment) and an internet connection.
"""

import argparse

import requests
from openai import OpenAI

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


def fetch_top_titles(limit: int) -> list[str]:
    story_ids = requests.get(TOP_STORIES_URL, timeout=20).json()[:limit]
    titles = []
    for story_id in story_ids:
        item = requests.get(ITEM_URL.format(id=story_id), timeout=20).json()
        if item and item.get("title"):
            titles.append(f"- {item['title']} ({item.get('url', 'no link')})")
    return titles


def summarize(titles: list[str]) -> str:
    prompt = (
        "Here are today's top Hacker News headlines. Group them into a few themes "
        "and write a 5-bullet briefing of what the tech community cares about today:\n\n"
        + "\n".join(titles)
    )
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize the top Hacker News stories with AI.")
    parser.add_argument("--limit", type=int, default=10, help="How many top stories to fetch")
    args = parser.parse_args()

    print(f"Fetching the top {args.limit} Hacker News stories...\n")
    titles = fetch_top_titles(args.limit)

    print("## Today on Hacker News\n")
    print(summarize(titles))
