# Build python app that queries wikipedia using python libraries 
# wikipedia and/or Wikipedia-API and use FastAPI to build the
# web server that the user will send queries to via http
# It will need to summarize the wikipedia response, so maybe just print the summary
# or whatever component of the wikipedia response is easy to use and understand by the end user

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "wikipedia-api",
#     "fastapi",
#     "uvicorn",
#     "requests",
# ]
# ///
#

# ─────────────────────────────────────────────────────────────────────────────
# wikisummary — fetch Wikipedia summaries, exposed two ways from one core.
#
#   uv run wikisummary.py query "Python (programming language)"
#   uv run wikisummary.py serve
# ─────────────────────────────────────────────────────────────────────────────

"""Fetch Wikipedia summaries via a shared core, as a CLI tool or an HTTP API.

Architecture note (the key idea to internalize):
    get_summary() is the ONLY place that knows how to talk to Wikipedia.
    The CLI and the FastAPI server are thin "adapters" that translate an
    input (argv / an HTTP request) into a get_summary() call and translate
    the result back out (printed text / JSON). Add a third front-end later
    (a Slack bot, a GUI) and you still wouldn't touch the core.
"""

import argparse
import sys

import requests
import wikipediaapi


# ── Configuration ────────────────────────────────────────────────────────────
# Wikimedia's API etiquette asks every client to identify itself with a
# descriptive User-Agent (app name + contact). Wikipedia-API *requires* you to
# pass one. Edit this to your own app + email before using it for real.
USER_AGENT = "WikiSummaryDemo/1.0 (lucas@automatalearninglab.com)"
LANG = "en"

# Build the Wikipedia client ONCE at module load, not per request. Under the
# server, this client (and its underlying HTTP session) is reused across every
# incoming request — cheaper than reconstructing it each time. For read-only
# use this sharing is fine.
#   [Inference] Reuse being safe for concurrent reads follows from it being a
#   read-only HTTP wrapper; if you later run uvicorn with multiple *worker
#   processes* each gets its own copy anyway, so that's a non-issue. True
#   in-process thread-safety I have not verified against the source.
_wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language=LANG)


# ── A domain-specific error ──────────────────────────────────────────────────
# Defining our own exception lets the core signal "couldn't find a page" in a
# way that's meaningful regardless of front-end. Each adapter then decides how
# to present it: the CLI prints to stderr + exits non-zero; the server maps it
# to an HTTP 404. The core stays ignorant of HTTP and of terminals.
class SummaryNotFound(Exception):
    """Raised when no usable Wikipedia page can be resolved for a query."""


# ── Step 1 of the core: turn free text into a real page title ────────────────
def _resolve_title(query):
    """Normalize a free-text query into an actual Wikipedia page title.

    Why this exists: Wikipedia-API has NO search function — it only fetches a
    page by exact title. So `_wiki.page("python language")` would miss. We hit
    the MediaWiki search endpoint directly (plain HTTP via `requests`) and take
    the top hit, letting "python language" resolve to
    "Python (programming language)".

    Returns the best-match title, or None if nothing matched.
    """
    # The MediaWiki "action API". `list=search` runs a full-text search;
    # `srlimit=1` means "just give me the single best match".
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 1,
        "format": "json",
    }
    resp = requests.get(
        f"https://{LANG}.wikipedia.org/w/api.php",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=10,  # never hang forever on a slow network
    )
    # Turn a 4xx/5xx HTTP status into a raised exception so callers can catch it
    # rather than silently parsing an error body as if it were data.
    resp.raise_for_status()

    # Dig into the JSON defensively: `.get(..., {})` / `[]` mean a missing key
    # yields an empty result instead of a KeyError.
    hits = resp.json().get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None


# ── Step 2 of the core: fetch + shape the result ─────────────────────────────
def get_summary(query, sentences=None):
    """Generate a Wikipedia summary for a free-text query.

    Flow: resolve the query to a title → fetch that page → confirm it exists →
    return a small structured dict. We return DATA, not formatted text, on
    purpose: each adapter renders it however it needs (terminal vs JSON).

    Args:
        query:     free-text search term.
        sentences: if set, return only the first N sentences of the summary.

    Returns:
        dict with keys: title, url, summary.

    Raises:
        SummaryNotFound: if no page can be resolved or it doesn't exist.
    """
    title = _resolve_title(query)
    if title is None:
        raise SummaryNotFound(f"No Wikipedia page found for: {query!r}")

    # `.page()` is lazy — it doesn't hit the network 
    # until you read a property
    # like `.exists()`, `.summary`, or `.fullurl`.
    page = _wiki.page(title)
    if not page.exists():
        # Rare, but the search index can point at a title the page API won't
        # resolve. Guard against it rather than returning empty text.
        raise SummaryNotFound(f"Resolved title {title!r} has no page.")

    summary = page.summary

    # Optional length cap. This is a DELIBERATELY naive sentence split on ". ".
    #   [Inference] It will mis-split on abbreviations like "U.S." or "Dr.".
    #   That's an acceptable trade for a preview; a real fix would use a
    #   sentence tokenizer (e.g. nltk/spacy), which isn't worth the dependency
    #   weight here.
    if sentences is not None:
        parts = summary.split(". ")
        summary = ". ".join(parts[:sentences]).rstrip(".") + "."

    return {"title": page.title, "url": page.fullurl, "summary": summary}


# ── CLI adapter: render core output for a human at a terminal ────────────────
def _format_for_cli(result):
    """Render a get_summary() result as readable terminal text."""
    # Underline the title with a row of dashes the same width — a cheap way to
    # make terminal output scannable without any formatting library.
    return (
        f"\n{result['title']}\n"
        f"{'-' * len(result['title'])}\n"
        f"{result['summary']}\n\n"
        f"Source: {result['url']}\n"
    )


# ── Server adapter: build the FastAPI app ────────────────────────────────────
def build_app():
    """Construct and return the FastAPI application.

    FastAPI is imported INSIDE the function (a "lazy import") on purpose: the
    CLI path never needs it, so importing it only when serving keeps the
    common `query` command's startup lean. (With uv the dependency is always
    installed; the saving here is import time, not install time.)
    """
    from fastapi import FastAPI, HTTPException

    app = FastAPI(title="Wikipedia Summary Service")

    # A single GET route. FastAPI reads the function's type hints to parse the
    # URL query string automatically: `?query=Python&sentences=2` becomes the
    # `query` (str) and `sentences` (int|None) arguments. It also validates
    # them — pass `sentences=abc` and FastAPI returns a 422 before your code
    # ever runs.
    @app.get("/summary")
    def summary_endpoint(query: str, sentences: int | None = None):
        try:
            # Returning a dict makes FastAPI serialize it to JSON for us.
            return get_summary(query, sentences=sentences)
        except SummaryNotFound as exc:
            # Translate our domain error into the right HTTP status.
            raise HTTPException(status_code=404, detail=str(exc))
        except requests.RequestException as exc:
            # Upstream Wikipedia/network failure → 502 Bad Gateway, signaling
            # "the problem is a service I depend on", not a bug in this server.
            raise HTTPException(status_code=502, detail=f"Wikipedia request failed: {exc}")

    return app


def run_server(host="127.0.0.1", port=8000):
    """Launch the FastAPI app with uvicorn (the ASGI server that runs it).

    Once it's up, visit http://127.0.0.1:8000/docs for FastAPI's
    auto-generated interactive API explorer — you can fire test queries there
    without writing any client code.
    """
    import uvicorn

    uvicorn.run(build_app(), host=host, port=port)


# ── Entry point: parse subcommands and dispatch to the chosen adapter ────────
def main():
    """Parse the command line and route to either the CLI or the server."""
    parser = argparse.ArgumentParser(description="Wikipedia summary tool.")
    # `subparsers` gives us git-style subcommands. `required=True` means the
    # user MUST pick one ("query" or "serve"); bare `wikisummary.py` errors out
    # with usage help instead of doing something surprising.
    sub = parser.add_subparsers(dest="command", required=True)

    # `query` subcommand: one positional arg + an optional sentence cap.
    q = sub.add_parser("query", help="Print a summary to the terminal.")
    q.add_argument("query", help="What to look up.")
    q.add_argument("-s", "--sentences", type=int, default=None,
                   help="Limit the summary to the first N sentences.")

    # `serve` subcommand: optional host/port for the HTTP server.
    s = sub.add_parser("serve", help="Run the HTTP server.")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "query":
        # The CLI adapter owns error PRESENTATION: catch the core's exceptions
        # and turn them into a stderr message + a non-zero exit code, which is
        # what shell pipelines and scripts expect on failure.
        try:
            result = get_summary(args.query, sentences=args.sentences)
        except SummaryNotFound as exc:
            print(exc, file=sys.stderr)
            sys.exit(1)
        except requests.RequestException as exc:
            print(f"Network error talking to Wikipedia: {exc}", file=sys.stderr)
            sys.exit(2)
        print(_format_for_cli(result))

    elif args.command == "serve":
        run_server(host=args.host, port=args.port)


# Standard Python idiom: only run main() when this file is executed directly,
# not when it's imported as a module by something else (e.g. a test).
if __name__ == "__main__":
    main()