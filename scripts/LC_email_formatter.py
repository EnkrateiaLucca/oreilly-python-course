# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests",
#     "beautifulsoup4",
#     "pandas",
#     "jinja2",
#     "smtplib",
# ]
# ///

"""
LC Email Formatter
Student: LC
Description: Formatting e-mail based on data from a website... looking at webpage that has
table of tasks with due date and shows if task is overdue, then create email to send to
person with list of overdue tasks

This script demonstrates how to:
1. Scrape task data from web pages (tables)
2. Parse and analyze due dates
3. Identify overdue tasks
4. Generate formatted emails with task summaries
5. Use email templates for consistent formatting
6. Send emails programmatically (with safety measures)

Educational Focus:
- Web scraping with BeautifulSoup
- Date/time manipulation
- Email composition and formatting
- Template engines (Jinja2)
- Error handling and validation
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple
import re
from pathlib import Path
import json
from jinja2 import Template
import time

class TaskScraper:
    """
    A web scraper specifically designed to extract task data from web pages

    This class handles:
    - Scraping HTML tables containing task information
    - Parsing various date formats
    - Extracting assignee information
    - Handling different website structures
    """

    def __init__(self):
        """Initialize the scraper with default settings"""
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Common date formats we might encounter
        self.date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y-%m-%d %H:%M:%S",
            "%m-%d-%Y"
        ]

        print("✅ Task Scraper initialized")

    def scrape_task_table(self, url: str, table_selector: str = None) -> pd.DataFrame:
        """
        Scrape task data from a webpage table

        Args:
            url: URL of the webpage to scrape
            table_selector: CSS selector for the specific table (optional)

        Returns:
            DataFrame containing task data
        """
        print(f"🌐 Scraping task data from: {url}")

        try:
            # Fetch the webpage
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the task table
            if table_selector:
                table = soup.select_one(table_selector)
            else:
                # Try to find the most likely task table
                table = self._find_task_table(soup)

            if not table:
                print("❌ No suitable table found on the webpage")
                return pd.DataFrame()

            # Extract table data
            return self._extract_table_data(table)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching webpage: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error parsing webpage: {e}")
            return pd.DataFrame()

    def _find_task_table(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """
        Intelligently find the most likely task table on a page

        Looks for tables with headers that suggest task management
        """
        tables = soup.find_all('table')

        # Keywords that suggest a task table
        task_keywords = ['task', 'due', 'deadline', 'assigned', 'status', 'priority', 'project']

        best_table = None
        best_score = 0

        for table in tables:
            score = 0

            # Check headers for task-related keywords
            headers = table.find_all(['th', 'td'])
            for header in headers[:10]:  # Check first 10 cells
                header_text = header.get_text().lower()
                for keyword in task_keywords:
                    if keyword in header_text:
                        score += 1

            if score > best_score:
                best_score = score
                best_table = table

        return best_table

    def _extract_table_data(self, table) -> pd.DataFrame:
        """Extract data from an HTML table and return as DataFrame"""

        # Find header row
        header_row = table.find('tr')
        if not header_row:
            return pd.DataFrame()

        # Extract headers
        headers = []
        for th in header_row.find_all(['th', 'td']):
            headers.append(th.get_text().strip())

        # Extract data rows
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip header row
            row = []
            for td in tr.find_all(['td', 'th']):
                row.append(td.get_text().strip())
            if row:  # Only add non-empty rows
                rows.append(row)

        # Create DataFrame
        if rows and headers:
            # Ensure all rows have the same number of columns as headers
            max_cols = len(headers)
            normalized_rows = []
            for row in rows:
                # Pad with empty strings if row is too short
                while len(row) < max_cols:
                    row.append("")
                # Truncate if row is too long
                normalized_rows.append(row[:max_cols])

            df = pd.DataFrame(normalized_rows, columns=headers)
            print(f"✅ Extracted {len(df)} rows with columns: {list(df.columns)}")
            return df

        return pd.DataFrame()

class TaskAnalyzer:
    """
    Analyzes task data to identify overdue tasks and generate insights
    """

    def __init__(self):
        """Initialize the analyzer"""
        self.today = datetime.now().date()
        print("✅ Task Analyzer initialized")

    def identify_overdue_tasks(self, df: pd.DataFrame,
                             due_date_column: str = None,
                             assignee_column: str = None) -> pd.DataFrame:
        """
        Identify overdue tasks from a DataFrame of tasks

        Args:
            df: DataFrame containing task data
            due_date_column: Name of the column containing due dates
            assignee_column: Name of the column containing assignee names

        Returns:
            DataFrame containing only overdue tasks with additional analysis
        """
        if df.empty:
            print("⚠️  No task data to analyze")
            return pd.DataFrame()

        print(f"📊 Analyzing {len(df)} tasks for overdue items...")

        # Auto-detect date column if not specified
        if due_date_column is None:
            due_date_column = self._detect_date_column(df)

        if due_date_column is None:
            print("❌ Could not identify due date column")
            return df  # Return original data if we can't find dates

        # Auto-detect assignee column if not specified
        if assignee_column is None:
            assignee_column = self._detect_assignee_column(df)

        # Parse dates
        df_copy = df.copy()
        df_copy['parsed_due_date'] = df_copy[due_date_column].apply(self._parse_date)

        # Filter for valid dates and overdue tasks
        valid_dates = df_copy['parsed_due_date'].notna()
        df_valid = df_copy[valid_dates].copy()

        if df_valid.empty:
            print("⚠️  No valid dates found in task data")
            return pd.DataFrame()

        # Identify overdue tasks
        df_valid['is_overdue'] = df_valid['parsed_due_date'] < self.today
        overdue_tasks = df_valid[df_valid['is_overdue']].copy()

        # Calculate days overdue
        overdue_tasks['days_overdue'] = (self.today - overdue_tasks['parsed_due_date']).dt.days

        # Add priority based on how overdue the task is
        overdue_tasks['priority'] = overdue_tasks['days_overdue'].apply(self._calculate_priority)

        print(f"🔍 Found {len(overdue_tasks)} overdue tasks")

        return overdue_tasks

    def _detect_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Auto-detect which column contains due dates"""
        date_keywords = ['due', 'deadline', 'date', 'end', 'finish', 'completion']

        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in date_keywords):
                # Test if this column contains date-like values
                sample_values = df[col].dropna().head(5)
                date_count = sum(1 for val in sample_values if self._parse_date(val) is not None)
                if date_count >= len(sample_values) * 0.5:  # At least 50% are valid dates
                    print(f"📅 Detected due date column: {col}")
                    return col

        return None

    def _detect_assignee_column(self, df: pd.DataFrame) -> Optional[str]:
        """Auto-detect which column contains assignee names"""
        assignee_keywords = ['assign', 'owner', 'responsible', 'user', 'person', 'name']

        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in assignee_keywords):
                print(f"👤 Detected assignee column: {col}")
                return col

        return None

    def _parse_date(self, date_str: str) -> Optional[datetime.date]:
        """Parse a date string into a datetime.date object"""
        if pd.isna(date_str) or not date_str:
            return None

        date_str = str(date_str).strip()

        # Try different date formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"]:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        # Try parsing with pandas for more flexibility
        try:
            return pd.to_datetime(date_str).date()
        except:
            return None

    def _calculate_priority(self, days_overdue: int) -> str:
        """Calculate priority level based on how many days overdue"""
        if days_overdue >= 30:
            return "CRITICAL"
        elif days_overdue >= 14:
            return "HIGH"
        elif days_overdue >= 7:
            return "MEDIUM"
        else:
            return "LOW"

class EmailFormatter:
    """
    Generates and formats emails for overdue task notifications
    """

    def __init__(self):
        """Initialize the email formatter"""
        self.templates = self._load_email_templates()
        print("✅ Email Formatter initialized")

    def _load_email_templates(self) -> Dict[str, str]:
        """Load email templates for different scenarios"""
        return {
            'overdue_tasks': """
Dear {{ recipient_name }},

I hope this email finds you well. This is a friendly reminder about some overdue tasks that require your attention.

**OVERDUE TASKS SUMMARY**
Total Overdue Tasks: {{ total_tasks }}
{% if critical_tasks > 0 %}🔴 Critical (30+ days): {{ critical_tasks }}{% endif %}
{% if high_tasks > 0 %}🟠 High Priority (14+ days): {{ high_tasks }}{% endif %}
{% if medium_tasks > 0 %}🟡 Medium Priority (7+ days): {{ medium_tasks }}{% endif %}
{% if low_tasks > 0 %}🟢 Low Priority (< 7 days): {{ low_tasks }}{% endif %}

**TASK DETAILS**
{% for task in tasks %}
{{ loop.index }}. **{{ task.title }}**
   - Due Date: {{ task.due_date }}
   - Days Overdue: {{ task.days_overdue }}
   - Priority: {{ task.priority }}
   {% if task.description %}- Description: {{ task.description }}{% endif %}

{% endfor %}

**NEXT STEPS**
Please review these tasks and update their status or completion dates as appropriate. If you need assistance or have questions about any of these tasks, please don't hesitate to reach out.

Best regards,
{{ sender_name }}

---
This is an automated reminder generated on {{ current_date }}.
            """,

            'summary_report': """
Subject: Weekly Overdue Tasks Report - {{ report_date }}

**OVERDUE TASKS SUMMARY REPORT**

Report Generated: {{ current_date }}
Total People with Overdue Tasks: {{ total_people }}
Total Overdue Tasks: {{ total_tasks }}

**BREAKDOWN BY PERSON**
{% for person, person_tasks in tasks_by_person.items() %}
**{{ person }}** ({{ person_tasks|length }} tasks)
{% for task in person_tasks %}
  - {{ task.title }} ({{ task.days_overdue }} days overdue)
{% endfor %}

{% endfor %}

**PRIORITY BREAKDOWN**
- Critical (30+ days): {{ critical_count }}
- High (14+ days): {{ high_count }}
- Medium (7+ days): {{ medium_count }}
- Low (< 7 days): {{ low_count }}

This report was automatically generated by the Task Management System.
            """
        }

    def generate_overdue_email(self,
                             overdue_tasks: pd.DataFrame,
                             recipient_name: str,
                             sender_name: str = "Task Management System") -> Dict[str, str]:
        """
        Generate an email for a specific person's overdue tasks

        Args:
            overdue_tasks: DataFrame containing overdue tasks for one person
            recipient_name: Name of the person receiving the email
            sender_name: Name of the sender

        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        if overdue_tasks.empty:
            return {
                'subject': f"Good News - No Overdue Tasks!",
                'body': f"Dear {recipient_name},\n\nGreat news! You currently have no overdue tasks. Keep up the excellent work!\n\nBest regards,\n{sender_name}"
            }

        # Prepare template data
        template_data = {
            'recipient_name': recipient_name,
            'sender_name': sender_name,
            'current_date': datetime.now().strftime("%B %d, %Y"),
            'total_tasks': len(overdue_tasks),
            'critical_tasks': len(overdue_tasks[overdue_tasks['priority'] == 'CRITICAL']),
            'high_tasks': len(overdue_tasks[overdue_tasks['priority'] == 'HIGH']),
            'medium_tasks': len(overdue_tasks[overdue_tasks['priority'] == 'MEDIUM']),
            'low_tasks': len(overdue_tasks[overdue_tasks['priority'] == 'LOW']),
            'tasks': []
        }

        # Prepare task details
        for _, task in overdue_tasks.iterrows():
            task_info = {
                'title': task.get('Task', task.get('Title', 'Untitled Task')),
                'due_date': task.get('Due Date', task.get('Deadline', 'Unknown')),
                'days_overdue': task.get('days_overdue', 0),
                'priority': task.get('priority', 'UNKNOWN'),
                'description': task.get('Description', task.get('Notes', ''))
            }
            template_data['tasks'].append(task_info)

        # Render template
        template = Template(self.templates['overdue_tasks'])
        body = template.render(**template_data)

        # Generate subject
        priority_text = ""
        if template_data['critical_tasks'] > 0:
            priority_text = " - CRITICAL ITEMS"
        elif template_data['high_tasks'] > 0:
            priority_text = " - High Priority"

        subject = f"Overdue Tasks Reminder ({template_data['total_tasks']} items){priority_text}"

        return {
            'subject': subject,
            'body': body
        }

    def generate_summary_report(self, all_overdue_tasks: pd.DataFrame) -> Dict[str, str]:
        """Generate a summary report of all overdue tasks"""

        if all_overdue_tasks.empty:
            return {
                'subject': "Overdue Tasks Report - All Clear!",
                'body': f"No overdue tasks found as of {datetime.now().strftime('%B %d, %Y')}. Excellent work team!"
            }

        # Group tasks by person (assuming there's an assignee column)
        assignee_columns = [col for col in all_overdue_tasks.columns
                          if any(keyword in col.lower() for keyword in ['assign', 'owner', 'person', 'user'])]

        if assignee_columns:
            assignee_col = assignee_columns[0]
            tasks_by_person = {}
            for person in all_overdue_tasks[assignee_col].unique():
                person_tasks = all_overdue_tasks[all_overdue_tasks[assignee_col] == person]
                tasks_by_person[person] = []
                for _, task in person_tasks.iterrows():
                    tasks_by_person[person].append({
                        'title': task.get('Task', task.get('Title', 'Untitled')),
                        'days_overdue': task.get('days_overdue', 0)
                    })
        else:
            tasks_by_person = {'Unassigned': []}

        template_data = {
            'report_date': datetime.now().strftime("%B %d, %Y"),
            'current_date': datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            'total_people': len(tasks_by_person),
            'total_tasks': len(all_overdue_tasks),
            'tasks_by_person': tasks_by_person,
            'critical_count': len(all_overdue_tasks[all_overdue_tasks['priority'] == 'CRITICAL']),
            'high_count': len(all_overdue_tasks[all_overdue_tasks['priority'] == 'HIGH']),
            'medium_count': len(all_overdue_tasks[all_overdue_tasks['priority'] == 'MEDIUM']),
            'low_count': len(all_overdue_tasks[all_overdue_tasks['priority'] == 'LOW']),
        }

        template = Template(self.templates['summary_report'])
        body = template.render(**template_data)

        subject = f"Weekly Overdue Tasks Report - {template_data['total_tasks']} Total Items"

        return {
            'subject': subject,
            'body': body
        }

def create_sample_task_data() -> pd.DataFrame:
    """Create sample task data for demonstration purposes"""

    # Create sample data with various overdue scenarios
    sample_data = [
        {
            'Task': 'Complete quarterly budget review',
            'Assignee': 'Alice Johnson',
            'Due Date': '2024-01-15',
            'Status': 'In Progress',
            'Priority': 'High',
            'Description': 'Review and approve Q1 budget allocations'
        },
        {
            'Task': 'Update employee handbook',
            'Assignee': 'Bob Smith',
            'Due Date': '2024-02-01',
            'Status': 'Not Started',
            'Priority': 'Medium',
            'Description': 'Incorporate new HR policies'
        },
        {
            'Task': 'Client presentation preparation',
            'Assignee': 'Alice Johnson',
            'Due Date': '2024-02-20',
            'Status': 'In Progress',
            'Priority': 'Critical',
            'Description': 'Prepare slides for major client meeting'
        },
        {
            'Task': 'Security audit completion',
            'Assignee': 'Charlie Brown',
            'Due Date': '2023-12-01',
            'Status': 'In Progress',
            'Priority': 'Critical',
            'Description': 'Complete annual security assessment'
        },
        {
            'Task': 'Training module development',
            'Assignee': 'Diana Prince',
            'Due Date': '2024-02-28',
            'Status': 'Planning',
            'Priority': 'Low',
            'Description': 'Create new employee onboarding materials'
        }
    ]

    return pd.DataFrame(sample_data)

def main():
    """
    Main function demonstrating the email formatter functionality
    """
    print("📧 LC Email Formatter - Educational Demo")
    print("=" * 50)

    # Initialize components
    scraper = TaskScraper()
    analyzer = TaskAnalyzer()
    formatter = EmailFormatter()

    # For demo purposes, we'll use sample data instead of scraping
    # In real usage, you would scrape from an actual website
    print("\n📚 Example 1: Creating sample task data...")
    task_df = create_sample_task_data()
    print(f"📊 Created sample data with {len(task_df)} tasks")
    print(task_df[['Task', 'Assignee', 'Due Date', 'Status']].to_string())

    # Analyze for overdue tasks
    print("\n📚 Example 2: Analyzing for overdue tasks...")
    overdue_df = analyzer.identify_overdue_tasks(
        task_df,
        due_date_column='Due Date',
        assignee_column='Assignee'
    )

    if not overdue_df.empty:
        print(f"🔍 Analysis complete:")
        print(overdue_df[['Task', 'Assignee', 'Due Date', 'days_overdue', 'priority']].to_string())

        # Generate individual emails for each person
        print("\n📚 Example 3: Generating individual emails...")
        for assignee in overdue_df['Assignee'].unique():
            person_tasks = overdue_df[overdue_df['Assignee'] == assignee]

            email_content = formatter.generate_overdue_email(
                person_tasks,
                recipient_name=assignee,
                sender_name="LC Task Manager"
            )

            print(f"\n✉️  Email for {assignee}:")
            print(f"Subject: {email_content['subject']}")
            print("=" * 40)
            print(email_content['body'][:500] + "..." if len(email_content['body']) > 500 else email_content['body'])

        # Generate summary report
        print("\n📚 Example 4: Generating summary report...")
        summary = formatter.generate_summary_report(overdue_df)
        print(f"\n📋 Summary Report:")
        print(f"Subject: {summary['subject']}")
        print("=" * 40)
        print(summary['body'][:500] + "..." if len(summary['body']) > 500 else summary['body'])

        # Save emails to files for review
        print("\n📚 Example 5: Saving emails to files...")
        output_dir = Path(__file__).parent / "generated_emails"
        output_dir.mkdir(exist_ok=True)

        # Save individual emails
        for assignee in overdue_df['Assignee'].unique():
            person_tasks = overdue_df[overdue_df['Assignee'] == assignee]
            email_content = formatter.generate_overdue_email(person_tasks, assignee)

            filename = f"overdue_tasks_{assignee.replace(' ', '_')}.txt"
            filepath = output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Subject: {email_content['subject']}\n")
                f.write("=" * 50 + "\n")
                f.write(email_content['body'])

            print(f"💾 Saved email for {assignee}: {filepath}")

        # Save summary report
        summary_file = output_dir / "summary_report.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {summary['subject']}\n")
            f.write("=" * 50 + "\n")
            f.write(summary['body'])

        print(f"💾 Saved summary report: {summary_file}")

    else:
        print("✅ No overdue tasks found - everyone is on track!")

    print(f"\n🎓 Educational Notes:")
    print("1. Always validate scraped data before processing")
    print("2. Handle different date formats gracefully")
    print("3. Use templates for consistent email formatting")
    print("4. Implement rate limiting when scraping websites")
    print("5. Consider privacy and security when handling email data")
    print("6. Test email formatting with various data scenarios")
    print("7. Always respect website robots.txt and terms of service")

    # Demonstrate web scraping (commented out for safety)
    print(f"\n🌐 Web Scraping Example (Demonstration Only):")
    print("# To scrape from a real website:")
    print("# scraped_data = scraper.scrape_task_table('https://example.com/tasks')")
    print("# overdue_tasks = analyzer.identify_overdue_tasks(scraped_data)")
    print("# Note: Always check robots.txt and respect rate limits!")

if __name__ == "__main__":
    main()