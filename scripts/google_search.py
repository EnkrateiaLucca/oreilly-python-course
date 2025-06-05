#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_FILE = Path("google_search_results.txt")

def scrape_google(query: str, max_results: int = 3):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Search Google
        page.goto("https://www.google.com")
        page.locator("textarea[name='q']").fill(query)
        page.keyboard.press("Enter")
        page.wait_for_selector("h3")

        # Collect search result links
        links = page.locator("h3").all()
        results = []
        for i, link in enumerate(links[:max_results]):
            try:
                link_href = link.evaluate("e => e.closest('a').href")
                results.append(link_href)
            except Exception:
                continue

        print(f"🔗 Visiting top {len(results)} results...")

        all_texts = []

        for url in results:
            print(f"🌐 Visiting {url}")
            page.goto(url, timeout=15000)
            try:
                body_text = page.locator("body").inner_text()
                all_texts.append(f"--- {url} ---\n{body_text[:2000]}...\n")
            except Exception as e:
                print(f"⚠️ Failed to extract from {url}: {e}")

        context.close()
        browser.close()

    return all_texts

def save_results(texts):
    OUTPUT_FILE.write_text("\n".join(texts), encoding="utf-8")
    print(f"✅ Results saved to {OUTPUT_FILE.resolve()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run google_scrape.py 'search query'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"🔍 Searching Google for: {query}")
    extracted = scrape_google(query)
    save_results(extracted)
