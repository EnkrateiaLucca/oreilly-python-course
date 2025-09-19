#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "playwright",
#     "python-dotenv",
# ]
# ///

"""
OpenTable Restaurant Reservation Availability Checker

This script demonstrates web automation using Playwright to check
restaurant reservation availability on OpenTable.

Educational purposes: Shows how to automate checking for appointment/reservation
slots on real websites without requiring login credentials.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import List, Dict
from playwright.async_api import async_playwright, Page
import os
from dotenv import load_dotenv

# Load environment variables if needed
load_dotenv()

class OpenTableChecker:
    """
    A class to check restaurant reservation availability on OpenTable
    """

    def __init__(self, restaurant_url: str, party_size: int = 2):
        """
        Initialize the checker with a restaurant URL and party size

        Args:
            restaurant_url: The OpenTable URL for the specific restaurant
            party_size: Number of people for the reservation (default: 2)
        """
        self.restaurant_url = restaurant_url
        self.party_size = party_size
        self.available_slots = []

    async def check_availability(self, date_str: str, preferred_times: List[str] = None) -> List[Dict]:
        """
        Check availability for a specific date and optional preferred times

        Args:
            date_str: Date in format 'YYYY-MM-DD'
            preferred_times: List of preferred times like ['19:00', '19:30', '20:00']

        Returns:
            List of available time slots with details
        """
        async with async_playwright() as p:
            # Launch browser in headless mode (set to False to see the browser)
            browser = await p.chromium.launch(
                headless=True,  # Set to False to see the browser actions
                slow_mo=50      # Slow down actions by 50ms for stability
            )

            try:
                # Create a new browser context with viewport settings
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                # Create a new page
                page = await context.new_page()

                # Navigate to the restaurant page
                print(f"🌐 Navigating to {self.restaurant_url}")
                await page.goto(self.restaurant_url, wait_until='networkidle')

                # Wait for the page to load
                await page.wait_for_timeout(2000)

                # Update party size if needed
                await self._update_party_size(page)

                # Select the date
                await self._select_date(page, date_str)

                # Get available times
                available_slots = await self._get_available_times(page)

                # Filter by preferred times if specified
                if preferred_times:
                    available_slots = self._filter_preferred_times(available_slots, preferred_times)

                return available_slots

            finally:
                await browser.close()

    async def _update_party_size(self, page: Page):
        """
        Update the party size selector
        """
        try:
            # Look for party size selector (typically a select dropdown)
            party_selector = 'select[aria-label*="party size" i], select[data-test*="party-size" i]'

            if await page.locator(party_selector).count() > 0:
                print(f"👥 Setting party size to {self.party_size}")
                await page.select_option(party_selector, str(self.party_size))
                await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"⚠️ Could not update party size: {e}")

    async def _select_date(self, page: Page, date_str: str):
        """
        Select the reservation date
        """
        try:
            # Convert date string to datetime object
            target_date = datetime.strptime(date_str, '%Y-%m-%d')

            # Look for date picker input
            date_input = 'input[type="date"], input[aria-label*="date" i], button[data-test*="date" i]'

            if await page.locator(date_input).count() > 0:
                print(f"📅 Selecting date: {date_str}")

                # Try to set the date value directly
                await page.locator(date_input).first.fill(date_str)
                await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"⚠️ Could not select date: {e}")

    async def _get_available_times(self, page: Page) -> List[Dict]:
        """
        Extract available reservation times from the page
        """
        available_slots = []

        try:
            # Wait for time slots to load
            await page.wait_for_timeout(2000)

            # Common selectors for time slots on OpenTable
            time_selectors = [
                'button[data-test*="time-slot"]',
                'button[class*="time-slot"]',
                'a[href*="/reserve"]',
                'button:has-text("PM"), button:has-text("AM")'
            ]

            for selector in time_selectors:
                time_elements = page.locator(selector)
                count = await time_elements.count()

                if count > 0:
                    print(f"⏰ Found {count} time slots")

                    for i in range(min(count, 20)):  # Limit to first 20 slots
                        element = time_elements.nth(i)

                        try:
                            # Get the time text
                            time_text = await element.text_content()

                            # Check if the button is enabled (available)
                            is_enabled = await element.is_enabled()

                            if time_text and is_enabled:
                                available_slots.append({
                                    'time': time_text.strip(),
                                    'available': True,
                                    'element_index': i
                                })
                        except:
                            continue

                    break  # Stop if we found slots with this selector

        except Exception as e:
            print(f"⚠️ Error getting available times: {e}")

        return available_slots

    def _filter_preferred_times(self, slots: List[Dict], preferred_times: List[str]) -> List[Dict]:
        """
        Filter slots by preferred times
        """
        filtered = []

        for slot in slots:
            slot_time = slot['time'].replace(':', '').replace(' ', '').upper()

            for pref_time in preferred_times:
                pref_clean = pref_time.replace(':', '').replace(' ', '').upper()

                # Check if the slot time contains the preferred time
                if pref_clean in slot_time:
                    filtered.append(slot)
                    break

        return filtered


async def main():
    """
    Main function to demonstrate the reservation checker
    """

    # Example restaurant URL (you can change this to any OpenTable restaurant)
    # This is a sample URL - replace with an actual restaurant URL
    restaurant_url = "https://www.opentable.com/r/the-french-laundry-yountville"

    # Configuration
    party_size = 2  # Number of people
    check_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')  # Check 7 days from now
    preferred_times = ['19:00', '19:30', '20:00']  # 7 PM, 7:30 PM, 8 PM

    # Create checker instance
    checker = OpenTableChecker(restaurant_url, party_size)

    print("🍽️  OpenTable Reservation Availability Checker")
    print("=" * 50)
    print(f"Restaurant: {restaurant_url}")
    print(f"Party Size: {party_size}")
    print(f"Date: {check_date}")
    print(f"Preferred Times: {', '.join(preferred_times) if preferred_times else 'Any'}")
    print("=" * 50)

    # Check availability
    try:
        available_slots = await checker.check_availability(check_date, preferred_times)

        if available_slots:
            print(f"\n✅ Found {len(available_slots)} available slots:")
            for slot in available_slots:
                print(f"  • {slot['time']}")

            # Optional: Send notification (email, SMS, etc.)
            # notify_user(available_slots)
        else:
            print("\n❌ No available slots found for the specified criteria")

    except Exception as e:
        print(f"\n❌ Error checking availability: {e}")
        return 1

    return 0


def notify_user(slots: List[Dict]):
    """
    Send notification about available slots
    This is a placeholder - implement your preferred notification method

    Options:
    - Send email using smtplib
    - Send SMS using Twilio
    - Send Slack message
    - Write to a log file
    """
    print("\n📧 Notification would be sent here with available slots")
    # Implement your notification logic here


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)