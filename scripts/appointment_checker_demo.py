#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "playwright",
# ]
# ///

"""
Demo Appointment Checker - Educational Script for Learning Web Automation

This script demonstrates the basics of web automation for checking appointments.
It uses a real, publicly accessible demo booking site for testing.

Key Learning Points:
1. How to use Playwright for browser automation
2. How to find and interact with web elements
3. How to extract information from web pages
4. How to structure an automation script

To run:
    uv run appointment_checker_demo.py
"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright


async def demo_appointment_checker():
    """
    Demonstrates checking hotel room availability on a demo booking site
    This uses a real demo site that's always available for testing
    """

    # Use a real demo booking site for testing
    demo_url = "https://www.booking.com"

    async with async_playwright() as p:
        # === STEP 1: Launch Browser ===
        print("🚀 Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # False = see the browser (good for learning!)
            slow_mo=1000     # Slow down actions so students can see what's happening
        )

        try:
            # === STEP 2: Open New Page ===
            print("📄 Opening new page...")
            page = await browser.new_page()

            # === STEP 3: Navigate to Website ===
            print(f"🌐 Going to {demo_url}")
            await page.goto(demo_url)

            # Wait for page to load
            print("⏳ Waiting for page to load...")
            await page.wait_for_timeout(3000)

            # === STEP 4: Search for Availability ===
            print("🔍 Looking for search box...")

            # Find the search input field
            # On Booking.com, it's usually an input with placeholder about destination
            search_input = page.locator('input[placeholder*="destination" i], input[name*="destination" i]').first

            if await search_input.count() > 0:
                # Type a destination
                destination = "San Francisco"
                print(f"✏️ Typing destination: {destination}")
                await search_input.fill(destination)
                await page.wait_for_timeout(1000)

                # Press Enter or click search
                print("🔎 Searching...")
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(3000)

            # === STEP 5: Check for Results ===
            print("📊 Checking for available options...")

            # Look for hotel/property cards (common patterns)
            result_selectors = [
                'div[data-testid*="property-card"]',  # Booking.com uses this
                'article[data-testid*="property"]',
                'a[href*="/hotel/"]',
                'h3:has-text("hotel")',
            ]

            results_found = False
            for selector in result_selectors:
                results = page.locator(selector)
                count = await results.count()

                if count > 0:
                    print(f"✅ Found {count} available properties!")
                    results_found = True

                    # Get details of first few results
                    print("\n📋 Sample available options:")
                    for i in range(min(3, count)):  # Show first 3
                        try:
                            item = results.nth(i)
                            # Try to get the property name
                            name_element = item.locator('h3, [data-testid*="title"]').first
                            if await name_element.count() > 0:
                                name = await name_element.text_content()
                                print(f"   {i+1}. {name[:50]}...")  # Truncate long names
                        except:
                            continue
                    break

            if not results_found:
                print("ℹ️ No results found on this page")

            # === STEP 6: Take Screenshot ===
            screenshot_name = "demo_results.png"
            await page.screenshot(path=screenshot_name)
            print(f"\n📸 Screenshot saved as '{screenshot_name}'")

            # === STEP 7: Show Summary ===
            print("\n" + "=" * 50)
            print("✨ DEMO COMPLETE!")
            print("=" * 50)
            print("\nWhat we learned:")
            print("1. ✓ Launched a browser with Playwright")
            print("2. ✓ Navigated to a website")
            print("3. ✓ Found and interacted with page elements")
            print("4. ✓ Extracted information from the page")
            print("5. ✓ Took a screenshot for documentation")

            print("\n💡 Try modifying this script to:")
            print("   - Search for different destinations")
            print("   - Extract more details (prices, ratings)")
            print("   - Check multiple dates")
            print("   - Save results to a file")

        except Exception as e:
            print(f"❌ Something went wrong: {e}")
            print("💡 This is normal when learning! Check the error and try again.")

        finally:
            # === CLEANUP: Close Browser ===
            print("\n🧹 Closing browser...")
            await browser.close()
            print("👋 Done!")


async def simple_example():
    """
    An even simpler example that just opens a page and takes a screenshot
    Great for absolute beginners!
    """
    print("🎯 Simple Playwright Example")
    print("-" * 30)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)

        # Open page
        page = await browser.new_page()

        # Go to website
        await page.goto("https://example.com")

        # Wait a bit
        await page.wait_for_timeout(2000)

        # Take screenshot
        await page.screenshot(path="example.png")
        print("📸 Screenshot saved!")

        # Close browser
        await browser.close()


def explain_script():
    """
    Explains how this script works for educational purposes
    """
    print("""
    🎓 HOW THIS SCRIPT WORKS
    ========================

    1. SETUP PHASE:
       - Import necessary libraries (asyncio, playwright)
       - Define async functions (required for Playwright)

    2. BROWSER LAUNCH:
       - Creates a browser instance (like opening Chrome)
       - headless=False means you can see the browser
       - slow_mo slows down actions for learning

    3. PAGE INTERACTION:
       - page.goto() - Navigate to a URL
       - page.locator() - Find elements on the page
       - .fill() - Type into input fields
       - .click() - Click buttons/links
       - page.keyboard.press() - Keyboard actions

    4. WAITING STRATEGIES:
       - wait_for_timeout() - Wait fixed time (simple but not ideal)
       - wait_for_selector() - Wait for element to appear (better)
       - wait_until='networkidle' - Wait for network to settle

    5. INFORMATION EXTRACTION:
       - .count() - How many elements match
       - .text_content() - Get text from element
       - .get_attribute() - Get element attributes
       - .screenshot() - Take screenshots

    6. ERROR HANDLING:
       - try/except blocks catch errors
       - finally ensures browser closes

    7. ASYNC/AWAIT:
       - Required for Playwright's asynchronous operations
       - Allows multiple operations to happen efficiently

    💡 TIPS FOR STUDENTS:
    - Start with headless=False to see what's happening
    - Use slow_mo to slow down actions
    - Take screenshots to debug issues
    - Print messages to track progress
    - Use browser DevTools to find selectors
    """)


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 APPOINTMENT CHECKER DEMO - Learning Edition")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}\n")

    # Uncomment the version you want to run:

    # Option 1: Run the full demo (default)
    asyncio.run(demo_appointment_checker())

    # Option 2: Run the simple example
    # asyncio.run(simple_example())

    # Option 3: Just show the explanation
    # explain_script()