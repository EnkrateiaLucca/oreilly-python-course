from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    page = context.new_page()
    page.goto("https://letterboxd.com/")
    
    input("Manually log in and press Enter to continue...")

    context.storage_state(path="auth.json")
    print("Auth state saved to auth.json")
    browser.close()