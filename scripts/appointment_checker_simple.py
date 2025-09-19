#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "playwright",
# ]
# ///

"""
Simple Appointment Availability Checker using Playwright

This educational script demonstrates how to check for appointment availability
on websites. It's designed to be simple and adaptable for various booking systems.

Common use cases:
- DMV appointments
- Medical appointments
- Passport/visa appointments
- Service appointments

To run this script:
1. Install: uv tool install playwright && playwright install chromium
2. Run: uv run appointment_checker_simple.py
"""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright


async def check_appointments(url: str, location_text: str = None):
    """
    Check for available appointments on a booking website

    Args:
        url: The booking page URL
        location_text: Optional location to select
    """

    # Launch playwright
    async with async_playwright() as p:
        # Launch browser (set headless=False to see browser actions)
        print("🚀 Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # Set to True for production
            slow_mo=500      # Slow down by 500ms to see actions
        )

        try:
            # Create new page with realistic settings
            page = await browser.new_page()

            # Navigate to appointment page
            print(f"📍 Navigating to: {url}")
            await page.goto(url, wait_until='domcontentloaded')

            # Wait for page to fully load
            await page.wait_for_timeout(3000)

            # === STEP 1: Look for location selector (if needed) ===
            if location_text:
                print(f"🏢 Looking for location: {location_text}")

                # Try different common selectors for location
                location_selectors = [
                    f'select:has-text("{location_text}")',  # Dropdown
                    f'button:has-text("{location_text}")',  # Button
                    f'a:has-text("{location_text}")',       # Link
                    f'input[placeholder*="location" i]',    # Input field
                ]

                for selector in location_selectors:
                    if await page.locator(selector).count() > 0:
                        element = page.locator(selector).first

                        # Click or select the location
                        if 'select' in selector:
                            await page.select_option(selector, label=location_text)
                        elif 'input' in selector:
                            await element.fill(location_text)
                            await page.keyboard.press('Enter')
                        else:
                            await element.click()

                        print(f"   ✓ Selected location")
                        await page.wait_for_timeout(2000)
                        break

            # === STEP 2: Look for appointment type selector ===
            print("📋 Looking for appointment types...")

            # Common patterns for appointment type buttons/links
            appointment_selectors = [
                'button:has-text("Schedule")',
                'button:has-text("Book")',
                'a:has-text("appointment")',
                'button:has-text("Next")',
                'button[class*="appointment"]',
            ]

            for selector in appointment_selectors:
                if await page.locator(selector).count() > 0:
                    print(f"   ✓ Found appointment button")
                    await page.locator(selector).first.click()
                    await page.wait_for_timeout(2000)
                    break

            # === STEP 3: Check for available dates/times ===
            print("📅 Checking for available slots...")

            # Look for calendar or time slot elements
            slot_indicators = [
                # Calendar-based systems
                'td[class*="available"]',
                'button[class*="available"]',
                'div[class*="slot"]:not([class*="unavailable"])',

                # Time-based systems
                'button:has-text("AM")',
                'button:has-text("PM")',
                'a[href*="reserve"]',
                'button[data-available="true"]',

                # Text-based availability
                ':has-text("available")',
                ':has-text("open")',
            ]

            available_slots = []

            for selector in slot_indicators:
                elements = page.locator(selector)
                count = await elements.count()

                if count > 0:
                    print(f"   ✓ Found {count} potential slots")

                    # Collect information about each slot
                    for i in range(min(count, 10)):  # Check first 10
                        try:
                            element = elements.nth(i)
                            text = await element.text_content()

                            if text and text.strip():
                                # Check if element is clickable (likely available)
                                is_enabled = await element.is_enabled()
                                is_visible = await element.is_visible()

                                if is_enabled and is_visible:
                                    available_slots.append(text.strip())
                        except:
                            continue

                    if available_slots:
                        break

            # === STEP 4: Report results ===
            print("\n" + "=" * 50)
            print("📊 RESULTS:")

            if available_slots:
                print(f"✅ Found {len(available_slots)} available appointment slots:")
                for slot in available_slots[:5]:  # Show first 5
                    print(f"   • {slot}")

                # Take screenshot of availability
                await page.screenshot(path="appointment_availability.png")
                print("\n📸 Screenshot saved as 'appointment_availability.png'")

                return True
            else:
                print("❌ No available appointments found")
                print("   Try checking again later or try different criteria")

                # Take screenshot for debugging
                await page.screenshot(path="no_appointments.png")
                print("\n📸 Screenshot saved as 'no_appointments.png'")

                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

        finally:
            await browser.close()
            print("\n👋 Browser closed")


async def main():
    """
    Main function - configure your appointment check here
    """

    # === CONFIGURATION ===
    # Example URLs (replace with your target website):

    # DMV Example (California)
    # url = "https://www.dmv.ca.gov/appointments/select-appointment-type"

    # CVS Minute Clinic Example
    # url = "https://www.cvs.com/minuteclinic/book-a-visit"

    # Generic booking page example
    url = "https://www.dmv.ca.gov/appointments/select-appointment-type"

    location = "Sacramento"  # Optional: specify location

    # === RUN THE CHECK ===
    print("🔍 Appointment Availability Checker")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Location: {location if location else 'Any'}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50 + "\n")

    # Check appointments
    found = await check_appointments(url, location)

    # === OPTIONAL: Set up monitoring ===
    if not found:
        print("\n💡 TIP: You can run this script periodically:")
        print("   - Use cron (Linux/Mac) or Task Scheduler (Windows)")
        print("   - Or add a loop with sleep to check every X minutes")
        print("   - Add email/SMS notifications when slots become available")


async def monitor_continuously(url: str, location: str = None, check_interval_minutes: int = 30):
    """
    Continuously monitor for appointments

    Args:
        url: Booking page URL
        location: Optional location
        check_interval_minutes: How often to check (in minutes)
    """
    print(f"🔄 Starting continuous monitoring (checking every {check_interval_minutes} minutes)")

    while True:
        print(f"\n{'='*50}")
        print(f"Check at {datetime.now().strftime('%H:%M:%S')}")

        found = await check_appointments(url, location)

        if found:
            print("🎉 APPOINTMENTS AVAILABLE! Check the screenshot.")
            # Here you could add notification logic:
            # - Send email
            # - Send SMS
            # - Play sound
            # - Send Slack message
            break
        else:
            print(f"⏰ Next check in {check_interval_minutes} minutes...")
            await asyncio.sleep(check_interval_minutes * 60)


if __name__ == "__main__":
    # Run the single check
    asyncio.run(main())

    # Uncomment below to run continuous monitoring instead:
    # asyncio.run(monitor_continuously(
    #     url="https://www.dmv.ca.gov/appointments/select-appointment-type",
    #     location="Sacramento",
    #     check_interval_minutes=30
    # ))