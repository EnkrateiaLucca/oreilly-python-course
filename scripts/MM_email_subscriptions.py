#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "imaplib",
#     "email",
#     "pandas",
#     "python-dotenv",
#     "beautifulsoup4",
#     "re",
#     "sqlite3",
# ]
# ///

"""
MM_email_subscriptions.py - Email Subscription Scanner and Mailbox Analyzer

Student: MM (Initials)
Request: "scrap my email looking for subscriptions or provide a summary of my mail box during Out of Office"

This script demonstrates how to analyze email for subscriptions and generate mailbox summaries.
It includes comprehensive email processing, subscription detection, and Out of Office reporting.

Educational Focus:
- Email processing with IMAP
- Text analysis for subscription detection
- HTML email parsing
- Data analysis and reporting
- Email automation patterns
- Privacy and security considerations

Prerequisites:
- Email account with IMAP access enabled
- App-specific passwords for secure authentication
- Environment variables for email credentials

IMPORTANT SECURITY NOTE:
This script demonstrates email processing concepts using simulated data.
For real email access, always use app-specific passwords and secure authentication.
"""

import imaplib
import email
import re
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmailMessage:
    """Data class representing an email message."""
    message_id: str
    sender: str
    recipient: str
    subject: str
    date: datetime
    body_text: str
    body_html: str
    is_subscription: bool = False
    subscription_type: str = ""
    unsubscribe_links: List[str] = None
    importance: str = "normal"  # low, normal, high

    def __post_init__(self):
        if self.unsubscribe_links is None:
            self.unsubscribe_links = []

@dataclass
class SubscriptionInfo:
    """Data class representing subscription information."""
    sender_domain: str
    sender_name: str
    subscription_type: str
    frequency: str
    total_emails: int
    last_email_date: datetime
    unsubscribe_method: str
    unsubscribe_links: List[str]

class EmailSubscriptionAnalyzer:
    """
    Comprehensive email analyzer for subscription detection and mailbox summaries.

    This class demonstrates professional email processing patterns including:
    - IMAP email access
    - Subscription pattern detection
    - Email categorization
    - Out of Office reporting
    - Privacy-conscious data handling
    """

    def __init__(self, db_path: str = "email_analysis.db"):
        """
        Initialize the email analyzer.

        Args:
            db_path (str): Path to SQLite database for storing analysis results
        """
        self.db_path = db_path
        self.setup_database()

        # Subscription detection patterns
        self.subscription_patterns = {
            'newsletter': [
                r'newsletter', r'weekly update', r'monthly digest',
                r'news.*letter', r'update.*weekly', r'digest.*monthly'
            ],
            'marketing': [
                r'unsubscribe', r'promotional', r'offer', r'sale',
                r'discount', r'limited time', r'special deal'
            ],
            'notification': [
                r'notification', r'alert', r'reminder',
                r'account.*update', r'security.*alert'
            ],
            'social': [
                r'facebook', r'twitter', r'linkedin', r'instagram',
                r'social.*update', r'friend.*request', r'connection'
            ],
            'ecommerce': [
                r'order.*confirmation', r'shipment', r'delivery',
                r'purchase', r'invoice', r'receipt'
            ]
        }

        # Unsubscribe link patterns
        self.unsubscribe_patterns = [
            r'unsubscribe',
            r'opt.*out',
            r'remove.*from.*list',
            r'email.*preferences',
            r'manage.*subscription'
        ]

        # Important email patterns (for Out of Office filtering)
        self.important_patterns = [
            r'urgent', r'asap', r'important', r'critical',
            r'action.*required', r'time.*sensitive',
            r'please.*respond', r'need.*reply'
        ]

    def setup_database(self):
        """Initialize the SQLite database for storing email analysis results."""
        logger.info("🗄️ Setting up email analysis database...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Email messages table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS email_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id TEXT UNIQUE,
                        sender TEXT,
                        recipient TEXT,
                        subject TEXT,
                        date DATETIME,
                        body_text TEXT,
                        body_html TEXT,
                        is_subscription BOOLEAN,
                        subscription_type TEXT,
                        importance TEXT,
                        analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Subscriptions summary table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_domain TEXT,
                        sender_name TEXT,
                        subscription_type TEXT,
                        frequency TEXT,
                        total_emails INTEGER,
                        last_email_date DATETIME,
                        unsubscribe_method TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Unsubscribe links table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS unsubscribe_links (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_domain TEXT,
                        link_url TEXT,
                        link_text TEXT,
                        discovered_date DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Out of office summary table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ooo_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        summary_date DATE,
                        total_emails INTEGER,
                        important_emails INTEGER,
                        subscription_emails INTEGER,
                        unique_senders INTEGER,
                        top_senders TEXT,
                        urgent_subjects TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("✅ Database setup completed")

        except sqlite3.Error as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise

    def create_sample_emails(self, num_emails: int = 100) -> List[EmailMessage]:
        """
        Create sample email data for demonstration purposes.

        In a real implementation, this would connect to an actual email server.

        Args:
            num_emails (int): Number of sample emails to create

        Returns:
            List[EmailMessage]: List of sample email messages
        """
        logger.info(f"📧 Creating {num_emails} sample emails for demonstration...")

        sample_emails = []

        # Sample senders and subjects for different types
        senders_data = {
            'newsletter': [
                ('newsletter@techcrunch.com', 'TechCrunch Daily'),
                ('updates@github.com', 'GitHub Weekly Digest'),
                ('news@python.org', 'Python Newsletter'),
                ('updates@stackoverflow.com', 'Stack Overflow Weekly')
            ],
            'marketing': [
                ('offers@amazon.com', 'Amazon Prime Day Deals!'),
                ('sales@shopify.com', 'Limited Time Offer - 50% Off'),
                ('promotions@bestbuy.com', 'Black Friday Exclusive Deals'),
                ('deals@target.com', 'Weekend Sale - Up to 70% Off')
            ],
            'notification': [
                ('security@gmail.com', 'Security Alert: New Sign-in'),
                ('noreply@paypal.com', 'Payment Received'),
                ('alerts@bankofamerica.com', 'Account Statement Ready'),
                ('notifications@slack.com', 'You have 5 unread messages')
            ],
            'social': [
                ('noreply@facebook.com', 'John Doe commented on your post'),
                ('notifications@linkedin.com', 'You have 3 new connection requests'),
                ('updates@twitter.com', 'Weekly summary of your activity'),
                ('noreply@instagram.com', 'Sarah liked your photo')
            ],
            'work': [
                ('boss@company.com', 'Urgent: Q4 Budget Review Meeting'),
                ('hr@company.com', 'Benefits Enrollment Deadline'),
                ('client@bigcorp.com', 'Project Status Update Required'),
                ('team@company.com', 'Weekly Team Standup Notes')
            ]
        }

        import random

        for i in range(num_emails):
            # Choose email type
            email_type = random.choice(list(senders_data.keys()))
            sender_email, base_subject = random.choice(senders_data[email_type])

            # Generate email date (last 30 days)
            days_ago = random.randint(0, 30)
            email_date = datetime.now() - timedelta(days=days_ago)

            # Create email content
            if email_type in ['newsletter', 'marketing', 'social']:
                is_subscription = True
                subscription_type = email_type
                # Add unsubscribe content
                body_text = f"This is a {email_type} email.\n\nTo unsubscribe, click here: https://unsubscribe.example.com"
                body_html = f"<html><body><p>This is a {email_type} email.</p><p><a href='https://unsubscribe.example.com'>Unsubscribe</a></p></body></html>"
                unsubscribe_links = ["https://unsubscribe.example.com"]
            else:
                is_subscription = False
                subscription_type = ""
                body_text = f"This is a {email_type} email from work or notifications."
                body_html = f"<html><body><p>This is a {email_type} email from work or notifications.</p></body></html>"
                unsubscribe_links = []

            # Determine importance
            importance = "normal"
            if "urgent" in base_subject.lower() or "asap" in base_subject.lower():
                importance = "high"
            elif email_type == "marketing":
                importance = "low"

            email_msg = EmailMessage(
                message_id=f"<msg{i+1}@example.com>",
                sender=sender_email,
                recipient="mm@example.com",
                subject=f"{base_subject} #{i+1}",
                date=email_date,
                body_text=body_text,
                body_html=body_html,
                is_subscription=is_subscription,
                subscription_type=subscription_type,
                unsubscribe_links=unsubscribe_links,
                importance=importance
            )

            sample_emails.append(email_msg)

        logger.info(f"✅ Created {len(sample_emails)} sample emails")
        return sample_emails

    def detect_subscription(self, email_msg: EmailMessage) -> Tuple[bool, str]:
        """
        Detect if an email is a subscription and categorize it.

        Args:
            email_msg (EmailMessage): Email message to analyze

        Returns:
            Tuple[bool, str]: (is_subscription, subscription_type)
        """
        # Combine subject and body for analysis
        content = f"{email_msg.subject} {email_msg.body_text}".lower()

        # Check for subscription patterns
        for sub_type, patterns in self.subscription_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return True, sub_type

        # Check for unsubscribe links (strong indicator)
        for pattern in self.unsubscribe_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True, "newsletter"  # Default type if pattern found

        return False, ""

    def extract_unsubscribe_links(self, email_msg: EmailMessage) -> List[str]:
        """
        Extract unsubscribe links from email content.

        Args:
            email_msg (EmailMessage): Email message to analyze

        Returns:
            List[str]: List of unsubscribe URLs
        """
        links = []

        # Parse HTML content if available
        if email_msg.body_html:
            try:
                soup = BeautifulSoup(email_msg.body_html, 'html.parser')
                for link in soup.find_all('a', href=True):
                    link_text = link.get_text().lower()
                    link_url = link['href']

                    # Check if link text contains unsubscribe keywords
                    for pattern in self.unsubscribe_patterns:
                        if re.search(pattern, link_text, re.IGNORECASE):
                            links.append(link_url)
                            break

            except Exception as e:
                logger.warning(f"Failed to parse HTML content: {e}")

        # Also check plain text for URLs
        url_pattern = r'https?://[^\s<>"]+(?:unsubscribe|opt-out|preferences)[^\s<>"]*'
        text_links = re.findall(url_pattern, email_msg.body_text, re.IGNORECASE)
        links.extend(text_links)

        return list(set(links))  # Remove duplicates

    def analyze_email_importance(self, email_msg: EmailMessage) -> str:
        """
        Analyze email importance for Out of Office filtering.

        Args:
            email_msg (EmailMessage): Email message to analyze

        Returns:
            str: Importance level (low, normal, high)
        """
        content = f"{email_msg.subject} {email_msg.body_text}".lower()

        # Check for urgent/important patterns
        for pattern in self.important_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return "high"

        # Marketing emails are typically low importance
        if email_msg.is_subscription and email_msg.subscription_type == "marketing":
            return "low"

        # Default importance
        return "normal"

    def process_emails(self, emails: List[EmailMessage]):
        """
        Process a list of emails and store analysis results.

        Args:
            emails (List[EmailMessage]): List of emails to process
        """
        logger.info(f"🔍 Processing {len(emails)} emails...")

        processed_count = 0
        subscription_count = 0

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for email_msg in emails:
                    # Detect subscription
                    is_subscription, subscription_type = self.detect_subscription(email_msg)
                    email_msg.is_subscription = is_subscription
                    email_msg.subscription_type = subscription_type

                    # Extract unsubscribe links
                    if is_subscription:
                        email_msg.unsubscribe_links = self.extract_unsubscribe_links(email_msg)
                        subscription_count += 1

                    # Analyze importance
                    email_msg.importance = self.analyze_email_importance(email_msg)

                    # Store email in database
                    cursor.execute('''
                        INSERT OR REPLACE INTO email_messages
                        (message_id, sender, recipient, subject, date, body_text,
                         body_html, is_subscription, subscription_type, importance)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        email_msg.message_id,
                        email_msg.sender,
                        email_msg.recipient,
                        email_msg.subject,
                        email_msg.date,
                        email_msg.body_text,
                        email_msg.body_html,
                        email_msg.is_subscription,
                        email_msg.subscription_type,
                        email_msg.importance
                    ))

                    processed_count += 1

                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to process emails: {e}")
            raise

        logger.info(f"✅ Processed {processed_count} emails, found {subscription_count} subscriptions")

    def analyze_subscriptions(self) -> List[SubscriptionInfo]:
        """
        Analyze subscription patterns from processed emails.

        Returns:
            List[SubscriptionInfo]: List of subscription analysis results
        """
        logger.info("📊 Analyzing subscription patterns...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get subscription statistics by sender domain
                df_subscriptions = pd.read_sql_query('''
                    SELECT
                        SUBSTR(sender, INSTR(sender, '@') + 1) as sender_domain,
                        sender,
                        subscription_type,
                        COUNT(*) as total_emails,
                        MAX(date) as last_email_date,
                        MIN(date) as first_email_date
                    FROM email_messages
                    WHERE is_subscription = 1
                    GROUP BY sender_domain, subscription_type
                    ORDER BY total_emails DESC
                ''', conn)

                subscriptions = []

                for _, row in df_subscriptions.iterrows():
                    # Calculate frequency
                    first_date = pd.to_datetime(row['first_email_date'])
                    last_date = pd.to_datetime(row['last_email_date'])
                    days_span = (last_date - first_date).days
                    if days_span > 0:
                        frequency = f"{row['total_emails'] / days_span:.1f} emails/day"
                    else:
                        frequency = "Single email"

                    # Get unsubscribe links for this sender
                    unsubscribe_query = '''
                        SELECT DISTINCT body_text, body_html
                        FROM email_messages
                        WHERE sender LIKE ? AND is_subscription = 1
                        LIMIT 1
                    '''
                    result = conn.execute(unsubscribe_query, (f"%{row['sender_domain']}",)).fetchone()
                    unsubscribe_links = []
                    if result:
                        # This is simplified - in real implementation, would parse HTML
                        if 'unsubscribe' in result[0].lower():
                            unsubscribe_links = ['Unsubscribe link found in email']

                    subscription_info = SubscriptionInfo(
                        sender_domain=row['sender_domain'],
                        sender_name=row['sender'].split('@')[0],
                        subscription_type=row['subscription_type'],
                        frequency=frequency,
                        total_emails=row['total_emails'],
                        last_email_date=pd.to_datetime(row['last_email_date']),
                        unsubscribe_method="Link" if unsubscribe_links else "Manual",
                        unsubscribe_links=unsubscribe_links
                    )

                    subscriptions.append(subscription_info)

                # Store subscription summaries
                cursor = conn.cursor()
                cursor.execute('DELETE FROM subscriptions')  # Clear old data

                for sub in subscriptions:
                    cursor.execute('''
                        INSERT INTO subscriptions
                        (sender_domain, sender_name, subscription_type, frequency,
                         total_emails, last_email_date, unsubscribe_method)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        sub.sender_domain,
                        sub.sender_name,
                        sub.subscription_type,
                        sub.frequency,
                        sub.total_emails,
                        sub.last_email_date,
                        sub.unsubscribe_method
                    ))

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to analyze subscriptions: {e}")
            return []

        logger.info(f"✅ Analyzed {len(subscriptions)} subscription sources")
        return subscriptions

    def generate_subscription_report(self) -> str:
        """
        Generate a comprehensive subscription report.

        Returns:
            str: Formatted subscription report
        """
        logger.info("📋 Generating subscription report...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get subscription summary
                df_summary = pd.read_sql_query('''
                    SELECT
                        subscription_type,
                        COUNT(*) as source_count,
                        SUM(total_emails) as total_emails
                    FROM subscriptions
                    GROUP BY subscription_type
                    ORDER BY total_emails DESC
                ''', conn)

                # Get top senders
                df_top_senders = pd.read_sql_query('''
                    SELECT sender_domain, subscription_type, total_emails, frequency
                    FROM subscriptions
                    ORDER BY total_emails DESC
                    LIMIT 10
                ''', conn)

                # Get recent subscriptions
                df_recent = pd.read_sql_query('''
                    SELECT sender_domain, subscription_type, last_email_date
                    FROM subscriptions
                    ORDER BY last_email_date DESC
                    LIMIT 5
                ''', conn)

                report = []
                report.append("📧 EMAIL SUBSCRIPTION ANALYSIS REPORT")
                report.append("=" * 50)

                if not df_summary.empty:
                    report.append("\n📊 Subscription Summary by Type:")
                    for _, row in df_summary.iterrows():
                        report.append(f"  {row['subscription_type'].title()}: {row['source_count']} sources, {row['total_emails']} emails")

                if not df_top_senders.empty:
                    report.append(f"\n🔝 Top 10 Subscription Sources:")
                    for _, row in df_top_senders.iterrows():
                        report.append(f"  {row['sender_domain']} ({row['subscription_type']}) - {row['total_emails']} emails ({row['frequency']})")

                if not df_recent.empty:
                    report.append(f"\n📅 Most Recent Activity:")
                    for _, row in df_recent.iterrows():
                        report.append(f"  {row['sender_domain']} - Last email: {row['last_email_date']}")

                # Get unsubscribe recommendations
                df_heavy = pd.read_sql_query('''
                    SELECT sender_domain, total_emails, unsubscribe_method
                    FROM subscriptions
                    WHERE total_emails > 5
                    ORDER BY total_emails DESC
                ''', conn)

                if not df_heavy.empty:
                    report.append(f"\n💡 Unsubscribe Recommendations (High Volume):")
                    for _, row in df_heavy.iterrows():
                        status = "✅ Easy" if row['unsubscribe_method'] == "Link" else "⚠️ Manual"
                        report.append(f"  {row['sender_domain']} ({row['total_emails']} emails) - {status}")

                return "\n".join(report)

        except Exception as e:
            logger.error(f"❌ Failed to generate subscription report: {e}")
            return "Failed to generate subscription report"

    def generate_ooo_summary(self, days_back: int = 7) -> str:
        """
        Generate an Out of Office summary for the specified period.

        Args:
            days_back (int): Number of days to analyze

        Returns:
            str: Formatted OOO summary
        """
        logger.info(f"🏖️ Generating Out of Office summary for last {days_back} days...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_date = datetime.now() - timedelta(days=days_back)

                # Get overall statistics
                stats_query = '''
                    SELECT
                        COUNT(*) as total_emails,
                        SUM(CASE WHEN importance = 'high' THEN 1 ELSE 0 END) as important_emails,
                        SUM(CASE WHEN is_subscription = 1 THEN 1 ELSE 0 END) as subscription_emails,
                        COUNT(DISTINCT sender) as unique_senders
                    FROM email_messages
                    WHERE date >= ?
                '''
                stats = conn.execute(stats_query, (cutoff_date,)).fetchone()

                # Get top senders
                top_senders_query = '''
                    SELECT sender, COUNT(*) as email_count
                    FROM email_messages
                    WHERE date >= ? AND is_subscription = 0
                    GROUP BY sender
                    ORDER BY email_count DESC
                    LIMIT 5
                '''
                df_top_senders = pd.read_sql_query(top_senders_query, conn, params=(cutoff_date,))

                # Get urgent emails
                urgent_query = '''
                    SELECT sender, subject, date
                    FROM email_messages
                    WHERE date >= ? AND importance = 'high'
                    ORDER BY date DESC
                    LIMIT 10
                '''
                df_urgent = pd.read_sql_query(urgent_query, conn, params=(cutoff_date,))

                # Get daily email counts
                daily_query = '''
                    SELECT DATE(date) as email_date, COUNT(*) as count
                    FROM email_messages
                    WHERE date >= ?
                    GROUP BY DATE(date)
                    ORDER BY email_date DESC
                '''
                df_daily = pd.read_sql_query(daily_query, conn, params=(cutoff_date,))

                # Store OOO summary
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ooo_summaries
                    (summary_date, total_emails, important_emails, subscription_emails,
                     unique_senders, top_senders, urgent_subjects)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().date(),
                    stats[0],
                    stats[1],
                    stats[2],
                    stats[3],
                    df_top_senders.to_json() if not df_top_senders.empty else "{}",
                    df_urgent.to_json() if not df_urgent.empty else "{}"
                ))
                conn.commit()

                # Generate report
                report = []
                report.append(f"🏖️ OUT OF OFFICE EMAIL SUMMARY")
                report.append(f"📅 Period: Last {days_back} days")
                report.append("=" * 50)

                report.append(f"\n📊 Overview:")
                report.append(f"  Total emails: {stats[0]}")
                report.append(f"  Important emails: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)" if stats[0] > 0 else "  Important emails: 0")
                report.append(f"  Subscription emails: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)" if stats[0] > 0 else "  Subscription emails: 0")
                report.append(f"  Unique senders: {stats[3]}")

                if not df_daily.empty:
                    report.append(f"\n📈 Daily Breakdown:")
                    for _, row in df_daily.iterrows():
                        report.append(f"  {row['email_date']}: {row['count']} emails")

                if not df_top_senders.empty:
                    report.append(f"\n👥 Top Non-Subscription Senders:")
                    for _, row in df_top_senders.iterrows():
                        report.append(f"  {row['sender']}: {row['email_count']} emails")

                if not df_urgent.empty:
                    report.append(f"\n🚨 Important/Urgent Emails:")
                    for _, row in df_urgent.iterrows():
                        report.append(f"  📧 {row['sender']}")
                        report.append(f"     Subject: {row['subject']}")
                        report.append(f"     Date: {row['date']}")
                        report.append("")

                non_subscription_count = stats[0] - stats[2]
                report.append(f"\n💡 Action Items:")
                report.append(f"  • Review {stats[1]} important emails requiring attention")
                report.append(f"  • {non_subscription_count} work-related emails to process")
                if stats[2] > 0:
                    report.append(f"  • Consider unsubscribing from high-volume sources")

                return "\n".join(report)

        except Exception as e:
            logger.error(f"❌ Failed to generate OOO summary: {e}")
            return "Failed to generate OOO summary"

    def export_unsubscribe_list(self, output_file: str = "unsubscribe_list.csv"):
        """
        Export a list of subscriptions with unsubscribe information.

        Args:
            output_file (str): Output CSV file path
        """
        logger.info(f"📤 Exporting unsubscribe list to {output_file}...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query('''
                    SELECT
                        sender_domain,
                        sender_name,
                        subscription_type,
                        total_emails,
                        frequency,
                        last_email_date,
                        unsubscribe_method
                    FROM subscriptions
                    ORDER BY total_emails DESC
                ''', conn)

                if not df.empty:
                    df.to_csv(output_file, index=False)
                    logger.info(f"✅ Exported {len(df)} subscriptions to {output_file}")
                else:
                    logger.warning("⚠️ No subscription data to export")

        except Exception as e:
            logger.error(f"❌ Failed to export unsubscribe list: {e}")

def demonstrate_email_security_patterns():
    """
    Demonstrate email security and privacy best practices.
    """
    print("\n🔐 Email Security & Privacy Best Practices:")
    print("=" * 50)

    practices = {
        "Authentication": [
            "Use app-specific passwords, not main account password",
            "Enable 2FA on email accounts",
            "Use OAuth2 when available instead of basic auth"
        ],
        "Data Privacy": [
            "Process emails locally, avoid cloud storage of content",
            "Implement data retention policies",
            "Encrypt sensitive data at rest and in transit"
        ],
        "Access Control": [
            "Limit IMAP permissions to read-only when possible",
            "Use dedicated service accounts for automation",
            "Log all email access for audit purposes"
        ],
        "Content Handling": [
            "Sanitize HTML content to prevent XSS",
            "Validate all extracted URLs before processing",
            "Be careful with email attachments (scan for malware)"
        ]
    }

    for category, items in practices.items():
        print(f"\n🛡️ {category}:")
        for item in items:
            print(f"  • {item}")

def demonstrate_real_world_integration():
    """
    Show examples of real-world email integration scenarios.
    """
    print("\n🌍 Real-World Integration Examples:")
    print("=" * 50)

    scenarios = {
        "Email Service Providers": {
            "Gmail": "Use Gmail API with OAuth2 authentication",
            "Outlook": "Use Microsoft Graph API",
            "Yahoo": "Use IMAP with app passwords",
            "Corporate Exchange": "Use Exchange Web Services (EWS)"
        },
        "Automation Scenarios": {
            "Vacation Responder": "Auto-categorize and respond to emails",
            "Email Forwarding": "Forward important emails to mobile",
            "Cleanup Automation": "Auto-delete old newsletters",
            "Subscription Management": "Bulk unsubscribe from inactive lists"
        },
        "Integration Tools": {
            "Zapier": "Connect email to other business tools",
            "IFTTT": "Simple email automation rules",
            "Microsoft Power Automate": "Enterprise email workflows",
            "Custom Scripts": "Tailored automation for specific needs"
        }
    }

    for category, items in scenarios.items():
        print(f"\n🔧 {category}:")
        for name, description in items.items():
            print(f"  • {name}: {description}")

def main():
    """
    Main function demonstrating the email subscription analysis workflow.
    """
    print("🚀 Welcome to MM's Email Subscription Analyzer!")
    print("=" * 50)

    try:
        # Initialize the email analyzer
        analyzer = EmailSubscriptionAnalyzer("mm_email_analysis.db")

        print("\n1. 📧 Creating sample email data (simulating email processing)...")
        # In a real implementation, this would connect to an email server
        sample_emails = analyzer.create_sample_emails(num_emails=150)

        print("\n2. 🔍 Processing emails for subscription detection...")
        analyzer.process_emails(sample_emails)

        print("\n3. 📊 Analyzing subscription patterns...")
        subscriptions = analyzer.analyze_subscriptions()

        print("\n4. 📋 Generating subscription report...")
        subscription_report = analyzer.generate_subscription_report()
        print(subscription_report)

        print("\n5. 🏖️ Generating Out of Office summary...")
        ooo_summary = analyzer.generate_ooo_summary(days_back=7)
        print(ooo_summary)

        print("\n6. 📤 Exporting unsubscribe list...")
        analyzer.export_unsubscribe_list("mm_unsubscribe_list.csv")

        print("\n✅ Email analysis completed successfully!")

        # Show database file info
        db_path = Path("mm_email_analysis.db")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"\n📁 Database file: {db_path.absolute()}")
            print(f"   Size: {size_mb:.2f} MB")

        print(f"\n📊 Analysis Results:")
        print(f"   Found {len(subscriptions)} subscription sources")
        print(f"   Processed {len(sample_emails)} total emails")

    except Exception as e:
        logger.error(f"❌ Email analysis failed: {e}")
        print("💡 Troubleshooting tips:")
        print("   - Ensure you have write permissions in the current directory")
        print("   - For real email access, set up app-specific passwords")
        print("   - Check email server IMAP settings")
        print("   - Verify firewall allows IMAP connections")

    # Show security and integration patterns
    demonstrate_email_security_patterns()
    demonstrate_real_world_integration()

    print("\n🎓 Learning Summary:")
    print("- Email processing with IMAP protocols")
    print("- Text analysis for pattern detection")
    print("- HTML parsing for link extraction")
    print("- Database design for email analytics")
    print("- Privacy and security considerations")
    print("- Out of Office automation concepts")

    print("\n💡 Next Steps:")
    print("- Set up real email server connections")
    print("- Implement OAuth2 authentication")
    print("- Add machine learning for better categorization")
    print("- Create automated unsubscribe workflows")
    print("- Build email scheduling and forwarding rules")
    print("- Integrate with calendar for vacation detection")

if __name__ == "__main__":
    main()