#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.32.3",
# ]
# ///

from __future__ import annotations

import html
import json
import os
import re
import socket
import threading
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
REQUEST_TIMEOUT = 20
DEFAULT_LIMIT = 15
MAX_LIMIT = 20

AI_QUERIES = [
    "AI",
    "LLM",
    "OpenAI",
    "Anthropic",
    "Claude",
    "Gemini",
    "Mistral",
    "Stable Diffusion",
    "Midjourney",
    "Copilot",
]

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "uv-hn-ai-news-viewer/1.0",
        "Accept": "application/json, text/plain, */*",
    }
)


def strip_html(raw: str | None) -> str:
    if not raw:
        return ""
    text = re.sub(r"<pre><code>(.*?)</code></pre>", r"\n\1\n", raw, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def format_age(unix_ts: int | None) -> str:
    if not unix_ts:
        return "unknown"
    now = int(time.time())
    diff = max(0, now - unix_ts)
    if diff < 60:
        return f"{diff}s ago"
    if diff < 3600:
        return f"{diff // 60}m ago"
    if diff < 86400:
        return f"{diff // 3600}h ago"
    if diff < 86400 * 30:
        return f"{diff // 86400}d ago"
    dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def fetch_json(url: str, params: dict[str, Any] | None = None) -> Any:
    response = SESSION.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_latest_ai_story_candidates(limit_per_query: int = 12) -> list[dict[str, Any]]:
    candidates: dict[int, dict[str, Any]] = {}

    for query in AI_QUERIES:
        payload = fetch_json(
            ALGOLIA_SEARCH_URL,
            params={
                "query": query,
                "tags": "story",
                "hitsPerPage": limit_per_query,
            },
        )

        for hit in payload.get("hits", []):
            try:
                story_id = int(hit["objectID"])
            except (KeyError, ValueError, TypeError):
                continue

            title = (hit.get("title") or "").strip()
            if not title:
                continue

            text_blob = " ".join(
                filter(
                    None,
                    [
                        title,
                        hit.get("story_text") or "",
                        hit.get("comment_text") or "",
                        hit.get("url") or "",
                    ],
                )
            ).lower()

            if not is_ai_related(text_blob):
                continue

            existing = candidates.get(story_id)
            candidate = {
                "id": story_id,
                "title": title,
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                "author": hit.get("author") or "unknown",
                "points": hit.get("points") or 0,
                "num_comments": hit.get("num_comments") or 0,
                "created_at_i": hit.get("created_at_i") or 0,
            }

            if existing is None or candidate["created_at_i"] > existing["created_at_i"]:
                candidates[story_id] = candidate

    stories = list(candidates.values())
    stories.sort(key=lambda x: (x["created_at_i"], x["points"]), reverse=True)
    return stories


def is_ai_related(text: str) -> bool:
    keywords = [
        " ai ",
        "artificial intelligence",
        "llm",
        "language model",
        "openai",
        "anthropic",
        "claude",
        "gemini",
        "gpt-",
        "gpt ",
        "mistral",
        "deepseek",
        "copilot",
        "midjourney",
        "stable diffusion",
        "diffusion model",
        "rag ",
        "agentic",
        "agent ",
        "agents ",
        "reasoning model",
        "transformer",
    ]
    padded = f" {text.lower()} "
    return any(keyword in padded for keyword in keywords)


def fetch_item(item_id: int) -> dict[str, Any] | None:
    try:
        data = fetch_json(HN_ITEM_URL.format(item_id=item_id))
    except requests.RequestException:
        return None
    return data if isinstance(data, dict) else None


def fetch_story_details(story_id: int, max_comments: int = 80) -> dict[str, Any]:
    story = fetch_item(story_id)
    if not story:
        raise ValueError(f"Unable to fetch story {story_id}")

    kids = story.get("kids", []) or []
    comments: list[dict[str, Any]] = []

    def walk_comment(comment_id: int, depth: int = 0) -> None:
        if len(comments) >= max_comments:
            return
        item = fetch_item(comment_id)
        if not item or item.get("deleted") or item.get("dead"):
            return
        if item.get("type") != "comment":
            return

        comments.append(
            {
                "id": item.get("id"),
                "author": item.get("by", "unknown"),
                "time": item.get("time"),
                "depth": depth,
                "text_html": item.get("text", ""),
                "text_plain": strip_html(item.get("text", "")),
            }
        )

        for child_id in item.get("kids", []) or []:
            if len(comments) >= max_comments:
                break
            walk_comment(child_id, depth + 1)

    for kid in kids:
        if len(comments) >= max_comments:
            break
        walk_comment(kid, 0)

    return {
        "story": {
            "id": story.get("id"),
            "title": html.unescape(story.get("title", "Untitled")),
            "by": story.get("by", "unknown"),
            "time": story.get("time"),
            "score": story.get("score", 0),
            "descendants": story.get("descendants", 0),
            "url": story.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
            "hn_url": f"https://news.ycombinator.com/item?id={story_id}",
            "text_html": story.get("text", ""),
            "text_plain": strip_html(story.get("text", "")),
        },
        "comments": comments,
    }


def build_story_cards(stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for story in stories:
        created = int(story.get("created_at_i") or 0)
        cards.append(
            {
                "id": story["id"],
                "title": story["title"],
                "url": story["url"],
                "hn_url": f"https://news.ycombinator.com/item?id={story['id']}",
                "author": story["author"],
                "points": story["points"],
                "num_comments": story["num_comments"],
                "created_at_i": created,
                "age": format_age(created),
                "domain": extract_domain(story["url"]),
            }
        )
    return cards


def extract_domain(url: str | None) -> str:
    if not url:
        return "news.ycombinator.com"
    try:
        host = urlparse(url).netloc.lower()
        return host.removeprefix("www.") or "news.ycombinator.com"
    except Exception:
        return "unknown"


def render_index_html(stories: list[dict[str, Any]]) -> str:
    stories_json = json.dumps(stories, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>HN AI News Viewer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #121936;
      --panel-2: #192246;
      --text: #e8ecff;
      --muted: #99a4d1;
      --accent: #7aa2ff;
      --accent-2: #9a7bff;
      --border: rgba(255,255,255,.08);
      --chip: rgba(122,162,255,.12);
      --shadow: 0 10px 30px rgba(0,0,0,.28);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; height: 100%; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background: linear-gradient(180deg, #0a0f1f 0%, #10162d 100%); color: var(--text); }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .app {{
      display: grid;
      grid-template-columns: minmax(360px, 460px) 1fr;
      height: 100vh;
    }}
    .sidebar {{
      border-right: 1px solid var(--border);
      background: rgba(12, 18, 38, 0.9);
      backdrop-filter: blur(10px);
      overflow: auto;
    }}
    .content {{
      overflow: auto;
      padding: 24px;
    }}
    .header {{
      position: sticky;
      top: 0;
      z-index: 5;
      padding: 20px;
      background: linear-gradient(180deg, rgba(12,18,38,0.98), rgba(12,18,38,0.9));
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(10px);
    }}
    .title {{
      font-size: 26px;
      font-weight: 800;
      margin: 0 0 8px 0;
      letter-spacing: -0.02em;
    }}
    .subtitle {{
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
      margin: 0 0 14px 0;
    }}
    .controls {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
    }}
    input[type="search"] {{
      width: 100%;
      background: rgba(255,255,255,.05);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 14px;
      outline: none;
      font-size: 14px;
    }}
    button {{
      border: 1px solid var(--border);
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      color: white;
      padding: 12px 14px;
      border-radius: 14px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: var(--shadow);
    }}
    button.secondary {{
      background: rgba(255,255,255,.05);
      color: var(--text);
      box-shadow: none;
    }}
    .list {{
      padding: 14px;
      display: grid;
      gap: 12px;
    }}
    .story {{
      background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02));
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 14px;
      cursor: pointer;
      transition: transform .12s ease, border-color .12s ease, background .12s ease;
    }}
    .story:hover {{
      transform: translateY(-1px);
      border-color: rgba(122,162,255,.45);
      background: rgba(122,162,255,.08);
    }}
    .story.active {{
      border-color: rgba(122,162,255,.8);
      background: rgba(122,162,255,.12);
    }}
    .story-title {{
      margin: 0 0 10px 0;
      font-size: 16px;
      line-height: 1.35;
      font-weight: 700;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
    }}
    .chip {{
      padding: 6px 9px;
      border-radius: 999px;
      background: var(--chip);
      border: 1px solid var(--border);
    }}
    .empty {{
      color: var(--muted);
      padding: 20px;
    }}
    .detail-card {{
      max-width: 980px;
      margin: 0 auto;
      background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.02));
      border: 1px solid var(--border);
      border-radius: 24px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .detail-head {{
      padding: 24px 24px 18px 24px;
      border-bottom: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(122,162,255,.08), rgba(122,162,255,0));
    }}
    .detail-title {{
      margin: 0 0 12px 0;
      font-size: 30px;
      line-height: 1.15;
      letter-spacing: -0.03em;
    }}
    .detail-body {{
      padding: 24px;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
    }}
    .section-title {{
      margin: 0 0 14px 0;
      font-size: 18px;
      font-weight: 800;
    }}
    .story-text {{
      color: #d7ddff;
      line-height: 1.65;
      margin-bottom: 24px;
    }}
    .comments {{
      display: grid;
      gap: 12px;
    }}
    .comment {{
      border: 1px solid var(--border);
      background: rgba(255,255,255,.03);
      border-radius: 16px;
      padding: 14px;
    }}
    .comment-meta {{
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 10px;
    }}
    .comment-text {{
      color: #edf1ff;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .loading, .hint {{
      max-width: 980px;
      margin: 0 auto;
      color: var(--muted);
      padding: 36px 14px;
      text-align: center;
    }}
    .footer-note {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 18px;
    }}
    @media (max-width: 980px) {{
      .app {{ grid-template-columns: 1fr; }}
      .sidebar {{ height: 48vh; border-right: none; border-bottom: 1px solid var(--border); }}
      .content {{ height: 52vh; }}
      .detail-title {{ font-size: 24px; }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="header">
        <h1 class="title">HN AI News</h1>
        <p class="subtitle">Latest AI-related stories from Hacker News. Click a story to load the article details and a readable nested comment feed.</p>
        <div class="controls">
          <input id="search" type="search" placeholder="Filter stories by title, author, or domain..." />
          <button id="refreshBtn" class="secondary" title="Refresh the page">Refresh</button>
        </div>
      </div>
      <div id="storyList" class="list"></div>
    </aside>

    <main class="content">
      <div id="detail" class="hint">Select a story on the left.</div>
    </main>
  </div>

  <script>
    const STORIES = {stories_json};
    const storyListEl = document.getElementById("storyList");
    const detailEl = document.getElementById("detail");
    const searchEl = document.getElementById("search");
    const refreshBtn = document.getElementById("refreshBtn");
    let activeId = null;

    function escapeHtml(value) {{
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }}

    function renderStoryList(items) {{
      if (!items.length) {{
        storyListEl.innerHTML = '<div class="empty">No stories matched your filter.</div>';
        return;
      }}

      storyListEl.innerHTML = items.map((story) => `
        <article class="story ${{story.id === activeId ? "active" : ""}}" data-id="${{story.id}}">
          <h3 class="story-title">${{escapeHtml(story.title)}}</h3>
          <div class="meta">
            <span class="chip">${{escapeHtml(story.domain)}}</span>
            <span class="chip">${{story.points}} points</span>
            <span class="chip">${{story.num_comments}} comments</span>
            <span class="chip">@${{escapeHtml(story.author)}}</span>
            <span class="chip">${{escapeHtml(story.age)}}</span>
          </div>
        </article>
      `).join("");

      for (const card of storyListEl.querySelectorAll(".story")) {{
        card.addEventListener("click", () => {{
          const id = Number(card.getAttribute("data-id"));
          loadStory(id);
        }});
      }}
    }}

    function filteredStories() {{
      const q = searchEl.value.trim().toLowerCase();
      if (!q) return STORIES;
      return STORIES.filter((story) =>
        story.title.toLowerCase().includes(q) ||
        story.author.toLowerCase().includes(q) ||
        story.domain.toLowerCase().includes(q)
      );
    }}

    function renderComment(comment) {{
      const margin = Math.min(comment.depth * 18, 72);
      return `
        <div class="comment" style="margin-left: ${{margin}}px">
          <div class="comment-meta">@${{escapeHtml(comment.author)}} · ${{escapeHtml(comment.age || "")}}</div>
          <div class="comment-text">${{escapeHtml(comment.text_plain || "[no text]")}}</div>
        </div>
      `;
    }}

    async function loadStory(id) {{
      activeId = id;
      renderStoryList(filteredStories());
      detailEl.innerHTML = '<div class="loading">Loading story and comments…</div>';

      try {{
        const res = await fetch(`/api/story?id=${{encodeURIComponent(id)}}`);
        if (!res.ok) {{
          throw new Error(`HTTP ${{res.status}}`);
        }}
        const data = await res.json();
        const story = data.story;
        const comments = data.comments || [];

        detailEl.innerHTML = `
          <div class="detail-card">
            <div class="detail-head">
              <h2 class="detail-title">${{escapeHtml(story.title)}}</h2>
              <div class="meta">
                <span class="chip">${{story.score}} points</span>
                <span class="chip">${{story.descendants}} total comments</span>
                <span class="chip">@${{escapeHtml(story.by)}}</span>
                <span class="chip">${{escapeHtml(story.age)}}</span>
              </div>
              <div class="actions">
                <a href="${{escapeHtml(story.url)}}" target="_blank" rel="noopener"><button>Open article</button></a>
                <a href="${{escapeHtml(story.hn_url)}}" target="_blank" rel="noopener"><button class="secondary">Open HN thread</button></a>
              </div>
            </div>
            <div class="detail-body">
              ${{story.text_plain ? `
                <div class="story-text">
                  <h3 class="section-title">Story text</h3>
                  <div>${{escapeHtml(story.text_plain)}}</div>
                </div>
              ` : ""}}

              <h3 class="section-title">Top comment thread sample</h3>
              <div class="comments">
                ${{comments.length ? comments.map(renderComment).join("") : '<div class="empty">No comments available.</div>'}}
              </div>

              <div class="footer-note">
                Showing a readable sample of the thread so the page stays fast and easy to browse.
              </div>
            </div>
          </div>
        `;
      }} catch (err) {{
        detailEl.innerHTML = `<div class="loading">Failed to load story details: ${{escapeHtml(err.message || err)}}</div>`;
      }}
    }}

    searchEl.addEventListener("input", () => renderStoryList(filteredStories()));
    refreshBtn.addEventListener("click", () => window.location.reload());

    renderStoryList(STORIES);
    if (STORIES.length) {{
      loadStory(STORIES[0].id);
    }}
  </script>
</body>
</html>
"""


class AppState:
    def __init__(self, limit: int) -> None:
        self.limit = max(1, min(limit, MAX_LIMIT))
        self.stories = self._load_stories()
        self.index_html = render_index_html(self.stories)

    def _load_stories(self) -> list[dict[str, Any]]:
        raw = fetch_latest_ai_story_candidates(limit_per_query=12)
        selected = raw[: self.limit]
        return build_story_cards(selected)

    def get_story_detail_payload(self, story_id: int) -> bytes:
        payload = fetch_story_details(story_id)
        payload["story"]["age"] = format_age(payload["story"].get("time"))
        for comment in payload["comments"]:
            comment["age"] = format_age(comment.get("time"))
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def make_handler(state: AppState):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: bytes, status: int = 200, content_type: str = "text/html; charset=utf-8") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)

            if parsed.path == "/":
                self._send(state.index_html.encode("utf-8"))
                return

            if parsed.path == "/api/story":
                params = parse_qs(parsed.query)
                raw_id = params.get("id", [None])[0]
                if raw_id is None or not str(raw_id).isdigit():
                    self._send(b'{"error":"missing or invalid id"}', status=400, content_type="application/json; charset=utf-8")
                    return

                try:
                    payload = state.get_story_detail_payload(int(raw_id))
                except Exception as exc:
                    error = json.dumps({"error": str(exc)}).encode("utf-8")
                    self._send(error, status=500, content_type="application/json; charset=utf-8")
                    return

                self._send(payload, content_type="application/json; charset=utf-8")
                return

            self._send(b"Not found", status=404, content_type="text/plain; charset=utf-8")

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    return Handler


def main() -> None:
    limit = int(os.environ.get("HN_AI_LIMIT", DEFAULT_LIMIT))
    state = AppState(limit=limit)

    port = find_free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(state))

    url = f"http://127.0.0.1:{port}"
    print(f"Serving HN AI news viewer at {url}")
    print("Press Ctrl+C to stop.")

    timer = threading.Timer(0.8, lambda: webbrowser.open(url))
    timer.daemon = True
    timer.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()