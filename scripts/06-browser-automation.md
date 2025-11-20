# Introduction to Browser Automation with Playwright in Python

This lesson covers automating web browser interactions using the Playwright library in Python, drawing from Python programming fundamentals.

## Basic Setup and Imports

**<span style="color: red">DISCLAIMER: this notebook will only run locally (not on Google Colab)</span>**

%pip install playwright
%playwright install

## Understanding Browser Automation Flow


Let's break down the script: `./add_movie_to_watchlist.py`:

```python
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
```

# Browser Automation with Playwright - A Tutorial

## Overview
This script uses Playwright to automate the process of adding movies to a Letterboxd watchlist.

## Script Structure

### 1. Imports and Setup
```python
import re
from playwright.sync_api import Playwright, sync_playwright, expect
import os
import sys
```
Key imports for browser automation, environment variables, and system arguments.

### 2. Main Function
```python
def run(playwright: Playwright) -> None:
```
The main function that handles browser automation, taking a Playwright instance as parameter.

### 3. Browser Setup
```python
browser = playwright.chromium.launch(headless=False)
context = browser.new_context()
page = context.new_page()
```
- Launches Chromium browser in visible mode
- Creates a new browser context
- Opens a new page

### 4. Authentication Flow
```python
page.get_by_label("Username").fill(os.environ["LETTERBOXD_USER"])
page.get_by_label("Password").fill(os.environ["LETTERBOXD_PWD"])
page.get_by_role("button", name="Sign in").click()
```
Handles login using environment variables for credentials.

### 5. Movie Search and Addition
```python
page.get_by_label("Search:").fill(movie_to_search)
page.get_by_role("button", name="Search").click()
page.get_by_role("link", name=movie_to_search, exact=True).first.click()
page.get_by_role("link", name="Add this film to your").click()
```
Searches for and adds the specified movie to watchlist.

### 6. Cleanup
```python
context.close()
browser.close()
```
Properly closes browser context and instance.

### 7. Script Execution
```python
with sync_playwright() as playwright:
    run(playwright)
```
Runs the automation script using Playwright's context manager.

## Usage
Run the script with a movie title as argument:
```bash
python add_movie_to_watchlist.py "Movie Title"
```

## Environment Variables
Required environment variables:
- `LETTERBOXD_USER`: Letterboxd username
- `LETTERBOXD_PWD`: Letterboxd password

This code demonstrates core Playwright concepts:
- Browser and context management
- Page navigation and interaction
- Form filling and button clicking
- Error handling and retries
- Environment variable usage
- Command line arguments
- Type hints and documentation

The example uses IMDb instead of Letterboxd but follows similar patterns while introducing additional programming concepts.

![](2025-02-04-14-30-46.png)

But what is cool about the script is that I didn't really write it! I obtained through a mix of prompting ChatGPT and playwright `codegen` tool that allows us to interact with a browser and get the necessary code to reproduce such action! Example of a terminal command you can run:

`playwright codegen https://letterboxd.com/`

To save credentials to avoid having to redo login steps see example scripts at:
- `./letterboxd_saving_auth_browser.py`
- `./letterboxd_using_auth.py`
