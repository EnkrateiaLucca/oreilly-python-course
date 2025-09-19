#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright",
# ]
# ///

import re
from playwright.sync_api import Playwright, sync_playwright, expect
import os
import sys

def run(playwright: Playwright) -> None:
    movie_to_search = sys.argv[1]
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://letterboxd.com/")
    page.get_by_label("Do not consent").click()
    page.get_by_role("link", name="Sign in").click()
    page.get_by_label("Username").fill(os.environ["LETTERBOXD_USER"])
    page.get_by_label("Username").press("Tab")
    page.get_by_label("Password").fill(os.environ["LETTERBOXD_PWD"])
    page.get_by_role("button", name="Sign in").click()
    page.locator(".navitem > .replace").click()
    page.get_by_label("Search:").fill(movie_to_search)
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name=movie_to_search, exact=True).first.click()
    page.get_by_role("link", name="Add this film to your").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)