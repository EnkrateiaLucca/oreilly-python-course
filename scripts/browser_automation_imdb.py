# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright>=1.45",
#     "typer>=0.12",
#     "rich>=13.7",
# ]
# ///
"""
Usage:
  uv run imdb_fetch.py "The Matrix"
  uv run imdb_fetch.py "Interstellar" --show --json out.json

Notes:
  - First time only, install browsers: `uv run playwright install`
"""

from __future__ import annotations
import json
import re
from typing import Optional, List, Dict
import typer
from rich import print as rprint
from playwright.sync_api import sync_playwright, Playwright, Page, TimeoutError as PWTimeout

app = typer.Typer(add_completion=False)

def _click_consent(page: Page) -> None:
    """Best-effort click for IMDB/GDPR consent banners (varies by region)."""
    candidates = [
        # IMDB / Amazon consent variants
        {"role": "button", "name": re.compile(r"Accept all|Accept|Agree|OK|Got it", re.I)},
        {"role": "button", "name": re.compile(r"Reject all|Reject", re.I)},  # sometimes required before Accept
    ]
    for sel in candidates:
        try:
            page.get_by_role(sel["role"], name=sel["name"]).click(timeout=2000)
        except PWTimeout:
            pass
    # Some regions use shadow/iframes; ignore silently if not found.

def _text_or_none(page: Page, selector: str) -> Optional[str]:
    try:
        el = page.locator(selector).first
        el.wait_for(state="attached", timeout=1000)
        txt = el.inner_text().strip()
        return txt if txt else None
    except PWTimeout:
        return None
    except Exception:
        return None

def _all_text(page: Page, selector: str, limit: int | None = None) -> List[str]:
    try:
        loc = page.locator(selector)
        count = loc.count()
        items = []
        for i in range(min(count, limit or count)):
            txt = loc.nth(i).inner_text().strip()
            if txt:
                items.append(re.sub(r"\s+", " ", txt))
        return items
    except Exception:
        return []

def _parse_title_year_block(page: Page) -> Dict[str, Optional[str]]:
    # Title
    title = (
        _text_or_none(page, '[data-testid="hero__pageTitle"] h1')
        or _text_or_none(page, 'h1[data-testid="hero-title-block__title"]')
        or _text_or_none(page, "h1")
    )
    # Year (first item in hero metadata list)
    year = None
    try:
        metas = _all_text(page, '[data-testid="hero-title-block__metadata"] li', limit=3)
        # Usually: [YEAR, "Xh Ym", "Genre count/age rating"] — pick a 4-digit year if present
        for m in metas:
            m_year = re.search(r"(19|20|21)\d{2}", m)
            if m_year:
                year = m_year.group(0)
                break
    except Exception:
        pass
    return {"title": title, "year": year}

def _parse_rating(page: Page) -> Optional[str]:
    # New IMDB selector (score like "8.7 /10")
    rating = _text_or_none(page, '[data-testid="hero-rating-bar__aggregate-rating__score"] span')
    if rating:
        rating = rating.replace("\n", " ").strip()
        return rating
    # Fallback older layouts
    rating = _text_or_none(page, '[itemprop="ratingValue"]')
    return rating

def _parse_genres(page: Page) -> List[str]:
    # Common genres container
    genres = _all_text(page, '[data-testid="genres"] a')
    if not genres:
        genres = _all_text(page, 'a[href*="/search/title/?genres="]')
    return genres

def _parse_plot(page: Page) -> Optional[str]:
    for sel in [
        '[data-testid="plot"] span',
        '[data-testid="plot-xl"]',
        '[data-testid="storyline-plot-summary"]',
        '.sc-16ede01-2 span',  # occasional summary block
    ]:
        txt = _text_or_none(page, sel)
        if txt:
            return re.sub(r"\s+", " ", txt)
    return None

def _parse_people_block(page: Page, role_labels: List[str]) -> List[str]:
    """
    Extract names from the principal credits box by role label (e.g., 'Director', 'Writers', 'Stars').
    IMDB often uses data-testid="title-pc-principal-credit".
    """
    names: List[str] = []
    try:
        credits = page.locator('[data-testid="title-pc-principal-credit"]')
        for i in range(credits.count()):
            block = credits.nth(i)
            label = block.locator("span").first.inner_text().strip()
            if any(lbl.lower() in label.lower() for lbl in role_labels):
                people_links = block.locator("a[href*='/name/']")
                for j in range(people_links.count()):
                    nm = people_links.nth(j).inner_text().strip()
                    if nm:
                        names.append(nm)
    except Exception:
        pass
    # Fallback: generic cast header sections
    if not names:
        names = _all_text(page, "a[href*='/name/']")[:5]
    return names

def fetch_movie(playwright: Playwright, query: str, show: bool = False) -> Dict[str, object]:
    browser = playwright.chromium.launch(headless=not show)
    context = browser.new_context()
    page = context.new_page()

    # 1) Go to IMDB and accept consent if present
    page.goto("https://www.imdb.com/", wait_until="domcontentloaded")
    _click_consent(page)

    # 2) Search for the query
    try:
        searchbox = page.get_by_role("combobox", name=re.compile(r"Search IMDb", re.I))
    except Exception:
        searchbox = page.locator("input[type='text'][name='q']").first
    searchbox.click()
    searchbox.fill(query)
    searchbox.press("Enter")

    # 3) On results page, click the first "Titles" result
    try:
        # Prefer the new results list (data-testid on result items)
        page.wait_for_selector('[data-testid="find-results-section-title"]', timeout=5000)
        # Try "Titles" section first
        titles_section = page.locator('section:has(h3:has-text("Titles"))')
        if titles_section.count() == 0:
            titles_section = page  # fallback: any result list
        first_result = titles_section.locator("a[href*='/title/']").first
        first_result.click()
    except PWTimeout:
        # Fallback: generic first /title/ link
        page.locator("a[href*='/title/']").first.click()

    page.wait_for_load_state("domcontentloaded")

    # 4) Extract details from the title page
    meta = _parse_title_year_block(page)
    rating = _parse_rating(page)
    genres = _parse_genres(page)
    plot = _parse_plot(page)
    directors = _parse_people_block(page, ["Director"])
    stars = _parse_people_block(page, ["Stars", "Cast"])

    url = page.url

    context.close()
    browser.close()

    return {
        "query": query,
        "url": url,
        "title": meta.get("title"),
        "year": meta.get("year"),
        "rating": rating,          # e.g., "8.7 /10"
        "genres": genres,          # list[str]
        "plot": plot,              # short summary
        "directors": directors,    # list[str]
        "stars": stars[:5],        # first few names
    }

@app.command()
def main(
    query: str = typer.Argument(..., help="Movie title to search on IMDB (e.g., 'The Matrix')"),
    show: bool = typer.Option(False, "--show", help="Show the browser (headless=False)"),
    json_out: Optional[str] = typer.Option(None, "--json", help="Output path to save JSON result"),
):
    """Fetch movie info from IMDB via Playwright and print JSON to stdout."""
    with sync_playwright() as pw:
        data = fetch_movie(pw, query=query, show=show)

    # Pretty print to console
    rprint(data)

    # Optional save to file
    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        rprint(f"[green]Saved JSON to[/green] {json_out}")

if __name__ == "__main__":
    app()
