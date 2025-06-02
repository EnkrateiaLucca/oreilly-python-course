import openai
import subprocess
import re
from playwright.sync_api import Playwright, sync_playwright, expect
import os
import sys
import pyperclip

def run(playwright: Playwright) -> None:
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
    page.get_by_role("link", name="Popular reviews").click()
    try:
        page.get_by_role("link", name="more").click()
    except:
        print("No big reviews to expand")
    page.locator("#content").click()
    page.locator("body").press("ControlOrMeta+a")
    page.locator("body").press("ControlOrMeta+c")

    # ---------------------
    context.close()
    browser.close()

movie_to_search = sys.argv[1] 
with sync_playwright() as playwright:
    run(playwright)



# Get clipboard content
clipboard_content = pyperclip.paste()

# Extract reviews using OpenAI
from openai import OpenAI
client = OpenAI()

def process_movie_reviews(prompt_question):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a movie review curator. \
                                                    Your task is to extract and format \
                                                    movie reviews from raw HTML content"},
                    {"role": "user", "content": prompt_question}]
    )
    
    return response.choices[0].message.content

# Save formatted reviews to file
reviews_filename = f"{movie_to_search}-reviews.md"
with open(reviews_filename, "w", encoding="utf-8") as f:
    f.write(process_movie_reviews(f"Extract the movie reviews from this raw html: \n {clipboard_content}"))

# Open the file
if sys.platform == "win32":
    os.startfile(reviews_filename)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, reviews_filename])



    