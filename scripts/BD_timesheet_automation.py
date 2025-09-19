#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "playwright",
#     "pandas",
#     "python-dotenv",
# ]
# ///

"""
BD_timesheet_automation.py - Appointment Booking Timesheet Filling

Student: BD (Initials)
Request: "appointment booking timesheet filling"

This script demonstrates how to automate timesheet filling using Playwright for web automation.
It creates a realistic example that fills out a timesheet form with appointment data.

Educational Focus:
- Web automation with Playwright
- Form filling automation
- Data handling for timesheet entries
- Error handling and waiting strategies
- Creating reusable automation functions

Prerequisites:
- Run: playwright install
- Ensure you have a timesheet web form to test with
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Page
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TimesheetAutomator:
    """
    A class to automate timesheet filling using Playwright.

    This demonstrates how to structure web automation code for maintainability
    and reusability across different timesheet systems.
    """

    def __init__(self, headless: bool = False):
        """
        Initialize the timesheet automator.

        Args:
            headless (bool): Whether to run browser in headless mode
        """
        self.headless = headless
        self.browser = None
        self.page = None

    async def start_browser(self):
        """
        Start the browser and create a new page.

        This method initializes Playwright and opens a browser instance.
        Using async/await allows for better performance with multiple operations.
        """
        print("🚀 Starting browser for timesheet automation...")

        # Initialize Playwright
        self.playwright = await async_playwright().start()

        # Launch browser (Chromium by default)
        # You can also use firefox or webkit
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=1000  # Add 1 second delay between actions for demo purposes
        )

        # Create a new browser context (isolated session)
        self.context = await self.browser.new_context()

        # Create a new page
        self.page = await self.context.new_page()

        print("✅ Browser started successfully")

    async def close_browser(self):
        """
        Clean up browser resources.

        Always important to close browser instances to free up system resources.
        """
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        print("🔒 Browser closed")

    def generate_sample_timesheet_data(self, num_days: int = 5) -> pd.DataFrame:
        """
        Generate sample timesheet data for demonstration.

        In a real scenario, this data might come from:
        - Calendar API (Google Calendar, Outlook)
        - CRM system
        - Database of appointments
        - CSV file exports

        Args:
            num_days (int): Number of days to generate data for

        Returns:
            pd.DataFrame: Sample timesheet data
        """
        print(f"📊 Generating sample timesheet data for {num_days} days...")

        # Sample appointment types and clients
        appointment_types = [
            "Client Meeting",
            "Project Planning",
            "Code Review",
            "Training Session",
            "Documentation",
            "System Maintenance"
        ]

        clients = [
            "TechCorp Inc.",
            "StartupXYZ",
            "Enterprise Solutions",
            "Digital Innovations",
            "Cloud Systems Ltd."
        ]

        # Generate data for the past week
        data = []
        start_date = datetime.now() - timedelta(days=num_days-1)

        for day in range(num_days):
            current_date = start_date + timedelta(days=day)

            # Skip weekends for this example
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue

            # Generate 2-4 appointments per day
            import random
            num_appointments = random.randint(2, 4)

            for _ in range(num_appointments):
                # Random start time between 9 AM and 5 PM
                start_hour = random.randint(9, 16)
                start_minute = random.choice([0, 15, 30, 45])

                # Duration between 1-3 hours
                duration_hours = random.uniform(1.0, 3.0)

                appointment = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'start_time': f"{start_hour:02d}:{start_minute:02d}",
                    'duration_hours': round(duration_hours, 2),
                    'appointment_type': random.choice(appointment_types),
                    'client': random.choice(clients),
                    'description': f"Working on {random.choice(['analysis', 'development', 'consultation', 'planning'])} tasks"
                }
                data.append(appointment)

        df = pd.DataFrame(data)
        print(f"✅ Generated {len(df)} timesheet entries")
        return df

    async def create_demo_timesheet_page(self):
        """
        Create a demo HTML timesheet form for testing purposes.

        In a real scenario, you would navigate to your actual timesheet system.
        This creates a realistic form to demonstrate the automation concepts.
        """
        print("🎭 Creating demo timesheet page...")

        # HTML for a realistic timesheet form
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Employee Timesheet System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #333; margin-bottom: 30px; }
                .form-group { margin-bottom: 15px; }
                label { display: block; font-weight: bold; margin-bottom: 5px; color: #555; }
                input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                button:hover { background: #0056b3; }
                .entry { border: 1px solid #eee; padding: 15px; margin-bottom: 10px; border-radius: 4px; background: #fafafa; }
                .success { color: green; font-weight: bold; margin-top: 20px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="header">📅 Employee Timesheet Entry System</h1>

                <div class="form-group">
                    <label for="employee-name">Employee Name:</label>
                    <input type="text" id="employee-name" name="employee-name" placeholder="Enter your full name">
                </div>

                <div class="form-group">
                    <label for="week-ending">Week Ending Date:</label>
                    <input type="date" id="week-ending" name="week-ending">
                </div>

                <h3>⏰ Time Entries</h3>
                <div id="time-entries">
                    <!-- Time entries will be added here -->
                </div>

                <button type="button" onclick="addTimeEntry()">+ Add Time Entry</button>
                <button type="button" onclick="submitTimesheet()" style="margin-left: 10px; background: #28a745;">Submit Timesheet</button>

                <div id="success-message" class="success" style="display: none;">
                    ✅ Timesheet submitted successfully!
                </div>
            </div>

            <script>
                let entryCount = 0;

                function addTimeEntry() {
                    entryCount++;
                    const container = document.getElementById('time-entries');
                    const entry = document.createElement('div');
                    entry.className = 'entry';
                    entry.innerHTML = `
                        <h4>Entry ${entryCount}</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                            <div>
                                <label>Date:</label>
                                <input type="date" name="entry-date-${entryCount}" required>
                            </div>
                            <div>
                                <label>Start Time:</label>
                                <input type="time" name="entry-start-${entryCount}" required>
                            </div>
                            <div>
                                <label>Hours:</label>
                                <input type="number" name="entry-hours-${entryCount}" step="0.25" min="0" max="24" required>
                            </div>
                        </div>
                        <div style="margin-top: 10px;">
                            <label>Project/Client:</label>
                            <input type="text" name="entry-client-${entryCount}" placeholder="Client or project name" required>
                        </div>
                        <div style="margin-top: 10px;">
                            <label>Description:</label>
                            <textarea name="entry-description-${entryCount}" rows="2" placeholder="Brief description of work performed"></textarea>
                        </div>
                    `;
                    container.appendChild(entry);
                }

                function submitTimesheet() {
                    // Simple validation
                    const employeeName = document.getElementById('employee-name').value;
                    const weekEnding = document.getElementById('week-ending').value;

                    if (!employeeName || !weekEnding) {
                        alert('Please fill in employee name and week ending date');
                        return;
                    }

                    if (entryCount === 0) {
                        alert('Please add at least one time entry');
                        return;
                    }

                    // Show success message
                    document.getElementById('success-message').style.display = 'block';

                    // In a real application, this would submit to a server
                    console.log('Timesheet submitted successfully');
                }

                // Initialize with one empty entry
                addTimeEntry();
            </script>
        </body>
        </html>
        '''

        # Set the HTML content directly to the page
        await self.page.set_content(html_content)
        print("✅ Demo timesheet page created")

    async def fill_employee_info(self, employee_name: str, week_ending: str):
        """
        Fill in the employee information section.

        Args:
            employee_name (str): Name of the employee
            week_ending (str): Week ending date in YYYY-MM-DD format
        """
        print(f"👤 Filling employee info: {employee_name}, Week ending: {week_ending}")

        # Fill employee name
        await self.page.fill('#employee-name', employee_name)

        # Fill week ending date
        await self.page.fill('#week-ending', week_ending)

        # Wait a moment for the form to update
        await self.page.wait_for_timeout(500)

    async def add_time_entry(self, entry_data: dict, entry_number: int):
        """
        Add a single time entry to the timesheet.

        Args:
            entry_data (dict): Dictionary containing entry information
            entry_number (int): The entry number (for form field identification)
        """
        print(f"⏰ Adding time entry {entry_number}: {entry_data['appointment_type']} for {entry_data['client']}")

        # If this is not the first entry, click "Add Time Entry" button
        if entry_number > 1:
            await self.page.click('button:has-text("+ Add Time Entry")')
            await self.page.wait_for_timeout(500)  # Wait for new entry to be added

        # Fill in the time entry fields
        # Note: The entry number in the form starts from 1
        form_entry_num = entry_number

        # Fill date
        await self.page.fill(f'input[name="entry-date-{form_entry_num}"]', entry_data['date'])

        # Fill start time
        await self.page.fill(f'input[name="entry-start-{form_entry_num}"]', entry_data['start_time'])

        # Fill hours
        await self.page.fill(f'input[name="entry-hours-{form_entry_num}"]', str(entry_data['duration_hours']))

        # Fill client/project
        await self.page.fill(f'input[name="entry-client-{form_entry_num}"]', entry_data['client'])

        # Fill description
        description = f"{entry_data['appointment_type']}: {entry_data['description']}"
        await self.page.fill(f'textarea[name="entry-description-{form_entry_num}"]', description)

        # Wait a moment for the form to update
        await self.page.wait_for_timeout(300)

    async def submit_timesheet(self):
        """
        Submit the completed timesheet.

        This method handles the final submission and verifies success.
        """
        print("📤 Submitting timesheet...")

        # Click the submit button
        await self.page.click('button:has-text("Submit Timesheet")')

        # Wait for success message to appear
        await self.page.wait_for_selector('#success-message', state='visible', timeout=5000)

        # Verify submission was successful
        success_message = await self.page.text_content('#success-message')
        if "successfully" in success_message.lower():
            print("✅ Timesheet submitted successfully!")
            return True
        else:
            print("❌ Timesheet submission may have failed")
            return False

    async def automate_timesheet_filling(self, timesheet_data: pd.DataFrame, employee_name: str = "John Doe"):
        """
        Main automation method that orchestrates the entire timesheet filling process.

        Args:
            timesheet_data (pd.DataFrame): DataFrame containing timesheet entries
            employee_name (str): Name of the employee
        """
        print("🤖 Starting timesheet automation process...")

        try:
            # Start the browser
            await self.start_browser()

            # Create demo page (in real scenario, navigate to actual timesheet URL)
            await self.create_demo_timesheet_page()

            # Calculate week ending date (assuming current week)
            from datetime import datetime, timedelta
            today = datetime.now()
            days_until_friday = (4 - today.weekday()) % 7  # Friday is day 4
            if days_until_friday == 0 and today.weekday() != 4:  # If today is not Friday
                days_until_friday = 7  # Next Friday
            week_ending = (today + timedelta(days=days_until_friday)).strftime('%Y-%m-%d')

            # Fill employee information
            await self.fill_employee_info(employee_name, week_ending)

            # Process each time entry
            for index, entry in timesheet_data.iterrows():
                await self.add_time_entry(entry.to_dict(), index + 1)

            # Wait a moment before submitting
            await self.page.wait_for_timeout(1000)

            # Submit the timesheet
            success = await self.submit_timesheet()

            if success:
                print(f"🎉 Successfully automated timesheet with {len(timesheet_data)} entries!")

            # Wait a moment to see the result
            await self.page.wait_for_timeout(2000)

        except Exception as e:
            print(f"❌ Error during automation: {str(e)}")
            raise
        finally:
            # Always close the browser
            await self.close_browser()

async def main():
    """
    Main function demonstrating the timesheet automation workflow.

    This function shows how to:
    1. Create sample data
    2. Initialize the automator
    3. Run the automation
    4. Handle errors appropriately
    """
    print("🚀 Welcome to BD's Timesheet Automation Demo!")
    print("=" * 50)

    try:
        # Create the timesheet automator
        # Set headless=False to watch the automation in action
        automator = TimesheetAutomator(headless=False)

        # Generate sample timesheet data
        # In a real scenario, this might come from your calendar API or database
        timesheet_data = automator.generate_sample_timesheet_data(num_days=5)

        print("\n📊 Sample timesheet data:")
        print(timesheet_data.to_string(index=False))
        print()

        # Run the automation
        await automator.automate_timesheet_filling(
            timesheet_data=timesheet_data,
            employee_name="BD (Student)"  # Using student's initials
        )

        print("\n✅ Timesheet automation completed successfully!")

    except Exception as e:
        print(f"\n❌ Automation failed: {str(e)}")
        print("💡 Tips for troubleshooting:")
        print("   - Ensure Playwright is installed: playwright install")
        print("   - Check if the timesheet website is accessible")
        print("   - Verify selectors match the actual form elements")
        print("   - Consider adding more wait times for slow-loading pages")

def create_real_world_integration_examples():
    """
    Function demonstrating how to integrate with real-world systems.

    This shows concepts for connecting to actual data sources and timesheet systems.
    """
    print("\n🔗 Real-world Integration Examples:")
    print("=" * 40)

    print("""
    1. Calendar Integration:
       - Google Calendar API: Extract appointments
       - Outlook Calendar API: Sync meeting data
       - CalDAV: Connect to various calendar systems

    2. Data Sources:
       - CRM Systems: Salesforce, HubSpot APIs
       - Project Management: Jira, Asana, Trello APIs
       - CSV/Excel exports from existing systems

    3. Timesheet Systems:
       - Modify selectors for your specific timesheet platform
       - Add authentication handling (login flows)
       - Handle different form layouts and validation rules

    4. Error Handling:
       - Implement retry logic for network issues
       - Add screenshot capture on failures
       - Log all actions for debugging

    5. Scheduling:
       - Use cron jobs or Task Scheduler for regular automation
       - Set up monitoring and alerting for failures
       - Implement backup and recovery procedures
    """)

if __name__ == "__main__":
    # Run the main automation demo
    asyncio.run(main())

    # Show additional integration examples
    create_real_world_integration_examples()

    print("\n🎓 Learning Summary:")
    print("- Web automation with Playwright")
    print("- Asynchronous programming for better performance")
    print("- Data handling with Pandas")
    print("- Error handling and resource cleanup")
    print("- Structuring automation code for maintainability")
    print("\n💡 Next Steps:")
    print("- Adapt selectors for your actual timesheet system")
    print("- Add authentication and login handling")
    print("- Integrate with your real data sources")
    print("- Set up scheduling for regular automation")