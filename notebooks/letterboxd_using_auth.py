from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    page.goto("https://letterboxd.com/")
    print("Logged in successfully with saved session")
    page.locator(".navitem > .replace").click()
    page.get_by_label("Search:").fill("In Bruges")
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="In Bruges", exact=True).first.click()
    browser.close()
