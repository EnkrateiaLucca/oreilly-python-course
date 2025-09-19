#!/usr/bin/env python3
# /// script
# dependencies = ["anthropic", "python-dotenv"]
# ///

"""
SW_email_filter_urgency.py
Student: SW - "Filtering emails for specific topics and levels of urgent replies req'd"

This script demonstrates email filtering and urgency classification using AI.
It simulates email data and uses AI to categorize emails by urgency level and topics.

Key Learning Objectives:
- Text analysis and classification
- AI-powered content filtering
- Data organization and reporting
- Email automation concepts
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

class EmailUrgencyFilter:
    """
    A class to filter and categorize emails by urgency and topics.
    In a real implementation, this would connect to email APIs like Gmail or Outlook.
    """

    def __init__(self):
        """Initialize the email filter with AI client."""
        # Initialize Anthropic client for AI-powered analysis
        self.ai_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        # Define urgency levels for classification
        self.urgency_levels = {
            "critical": "Immediate action required (within 1 hour)",
            "high": "Response needed today",
            "medium": "Response needed within 2-3 days",
            "low": "Response can wait a week or more"
        }

        # Common business topics to filter for
        self.topics = [
            "customer_support", "sales_inquiry", "technical_issue",
            "meeting_request", "project_update", "billing",
            "partnership", "feedback", "internal_communication"
        ]

    def get_sample_emails(self) -> List[Dict[str, Any]]:
        """
        Generate sample email data for demonstration.
        In a real scenario, this would fetch from email APIs.
        """
        sample_emails = [
            {
                "id": "email_001",
                "sender": "customer@urgentcorp.com",
                "subject": "URGENT: Production server down - immediate assistance needed",
                "body": "Our production server has been down for 2 hours. This is affecting all our customers. Please help immediately!",
                "received_time": datetime.now() - timedelta(hours=1),
                "attachments": []
            },
            {
                "id": "email_002",
                "sender": "sales@potential-client.com",
                "subject": "Partnership opportunity discussion",
                "body": "Hi, we're interested in exploring a potential partnership. Could we schedule a call next week to discuss?",
                "received_time": datetime.now() - timedelta(hours=3),
                "attachments": []
            },
            {
                "id": "email_003",
                "sender": "support@currentclient.com",
                "subject": "Question about invoice #12345",
                "body": "I have a question about the charges on invoice #12345. When you have a chance, could you explain the additional fees?",
                "received_time": datetime.now() - timedelta(days=1),
                "attachments": ["invoice_12345.pdf"]
            },
            {
                "id": "email_004",
                "sender": "team@company.com",
                "subject": "Weekly team meeting moved to Friday",
                "body": "FYI - our weekly team meeting has been moved from Thursday to Friday at 2 PM. See you there!",
                "received_time": datetime.now() - timedelta(hours=6),
                "attachments": []
            },
            {
                "id": "email_005",
                "sender": "bug-reports@client.com",
                "subject": "Critical bug in payment processing",
                "body": "We've discovered a critical bug in the payment processing module that's preventing customers from completing purchases. This needs immediate attention.",
                "received_time": datetime.now() - timedelta(minutes=30),
                "attachments": ["error_logs.txt", "screenshot.png"]
            }
        ]

        return sample_emails

    def analyze_email_with_ai(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to analyze email content and determine urgency and topics.

        Args:
            email: Dictionary containing email data

        Returns:
            Dictionary with urgency level, topics, and reasoning
        """

        # Prepare the email content for analysis
        email_content = f"""
        Subject: {email['subject']}
        From: {email['sender']}
        Body: {email['body']}
        Attachments: {', '.join(email['attachments']) if email['attachments'] else 'None'}
        """

        # Create AI prompt for email analysis
        prompt = f"""
        Analyze this email and provide:
        1. Urgency level (critical, high, medium, low)
        2. Primary topic category from: {', '.join(self.topics)}
        3. Brief reasoning for the urgency classification
        4. Suggested response timeframe

        Email to analyze:
        {email_content}

        Respond in JSON format:
        {{
            "urgency": "level",
            "topic": "category",
            "reasoning": "explanation",
            "response_timeframe": "timeframe",
            "key_indicators": ["indicator1", "indicator2"]
        }}
        """

        try:
            # Make API call to Anthropic
            response = self.ai_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the AI response
            ai_analysis = json.loads(response.content[0].text)
            return ai_analysis

        except Exception as e:
            print(f"AI analysis failed for email {email['id']}: {str(e)}")
            # Fallback to rule-based analysis
            return self.fallback_analysis(email)

    def fallback_analysis(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback rule-based analysis when AI is unavailable.

        Args:
            email: Dictionary containing email data

        Returns:
            Dictionary with basic urgency and topic classification
        """

        subject_lower = email['subject'].lower()
        body_lower = email['body'].lower()

        # Rule-based urgency detection
        urgency = "low"  # default

        urgent_keywords = ["urgent", "emergency", "critical", "immediately", "asap", "down", "broken"]
        high_keywords = ["important", "priority", "soon", "today"]

        if any(keyword in subject_lower or keyword in body_lower for keyword in urgent_keywords):
            urgency = "critical"
        elif any(keyword in subject_lower or keyword in body_lower for keyword in high_keywords):
            urgency = "high"
        elif "question" in subject_lower or "invoice" in subject_lower:
            urgency = "medium"

        # Simple topic detection
        topic = "internal_communication"  # default

        if "support" in email['sender'] or "bug" in subject_lower:
            topic = "customer_support"
        elif "sales" in email['sender'] or "partnership" in subject_lower:
            topic = "sales_inquiry"
        elif "invoice" in subject_lower or "billing" in subject_lower:
            topic = "billing"
        elif "meeting" in subject_lower:
            topic = "meeting_request"

        return {
            "urgency": urgency,
            "topic": topic,
            "reasoning": "Rule-based analysis (AI unavailable)",
            "response_timeframe": self.urgency_levels[urgency],
            "key_indicators": ["keyword_matching"]
        }

    def filter_and_categorize_emails(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process all emails and organize them by urgency and topic.

        Args:
            emails: List of email dictionaries

        Returns:
            Organized email data with analysis results
        """

        print("🔍 Starting email analysis and filtering...")

        # Process each email
        analyzed_emails = []
        for email in emails:
            print(f"📧 Analyzing: {email['subject'][:50]}...")

            # Get AI analysis
            analysis = self.analyze_email_with_ai(email)

            # Combine original email with analysis
            email_with_analysis = {
                **email,
                "analysis": analysis
            }
            analyzed_emails.append(email_with_analysis)

        # Organize by urgency
        emails_by_urgency = {level: [] for level in self.urgency_levels.keys()}
        emails_by_topic = {topic: [] for topic in self.topics}

        for email in analyzed_emails:
            urgency = email['analysis']['urgency']
            topic = email['analysis']['topic']

            emails_by_urgency[urgency].append(email)
            emails_by_topic[topic].append(email)

        return {
            "total_emails": len(emails),
            "analyzed_emails": analyzed_emails,
            "by_urgency": emails_by_urgency,
            "by_topic": emails_by_topic,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def generate_urgency_report(self, filtered_data: Dict[str, Any]) -> str:
        """
        Generate a detailed report of email urgency analysis.

        Args:
            filtered_data: Organized email data from filtering

        Returns:
            Formatted report string
        """

        report = []
        report.append("=" * 60)
        report.append("📧 EMAIL URGENCY ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Analysis completed: {filtered_data['analysis_timestamp']}")
        report.append(f"Total emails processed: {filtered_data['total_emails']}")
        report.append("")

        # Urgency breakdown
        report.append("🚨 URGENCY BREAKDOWN:")
        report.append("-" * 30)

        for urgency, emails in filtered_data['by_urgency'].items():
            count = len(emails)
            if count > 0:
                report.append(f"  {urgency.upper()}: {count} emails")
                report.append(f"    Action needed: {self.urgency_levels[urgency]}")

                for email in emails:
                    report.append(f"    • {email['subject'][:40]}... (from: {email['sender']})")
                report.append("")

        # Topic breakdown
        report.append("📂 TOPIC BREAKDOWN:")
        report.append("-" * 30)

        for topic, emails in filtered_data['by_topic'].items():
            count = len(emails)
            if count > 0:
                report.append(f"  {topic.replace('_', ' ').title()}: {count} emails")

        report.append("")

        # Immediate action items
        critical_emails = filtered_data['by_urgency']['critical']
        high_emails = filtered_data['by_urgency']['high']

        if critical_emails or high_emails:
            report.append("⚡ IMMEDIATE ACTION REQUIRED:")
            report.append("-" * 30)

            for email in critical_emails + high_emails:
                report.append(f"  📍 {email['analysis']['urgency'].upper()}: {email['subject']}")
                report.append(f"     From: {email['sender']}")
                report.append(f"     Reason: {email['analysis']['reasoning']}")
                report.append(f"     Action: {email['analysis']['response_timeframe']}")
                report.append("")

        return "\n".join(report)

def main():
    """
    Main function to demonstrate email filtering and urgency analysis.
    """

    print("🚀 Email Urgency Filter Demo")
    print("=" * 40)

    # Initialize the email filter
    email_filter = EmailUrgencyFilter()

    # Get sample emails (in real app, this would fetch from email API)
    print("📥 Loading sample emails...")
    emails = email_filter.get_sample_emails()
    print(f"Loaded {len(emails)} emails for analysis")
    print()

    # Filter and categorize emails
    filtered_data = email_filter.filter_and_categorize_emails(emails)

    # Generate and display report
    print("\n" + "=" * 60)
    report = email_filter.generate_urgency_report(filtered_data)
    print(report)

    # Save results to file for further processing
    output_file = "email_urgency_analysis.json"
    with open(output_file, 'w') as f:
        # Convert datetime objects to strings for JSON serialization
        serializable_data = {
            "total_emails": filtered_data["total_emails"],
            "analysis_timestamp": filtered_data["analysis_timestamp"],
            "urgency_summary": {
                urgency: len(emails)
                for urgency, emails in filtered_data["by_urgency"].items()
            },
            "topic_summary": {
                topic: len(emails)
                for topic, emails in filtered_data["by_topic"].items()
                if len(emails) > 0
            }
        }
        json.dump(serializable_data, f, indent=2)

    print(f"💾 Analysis results saved to: {output_file}")

    # Demonstrate integration possibilities
    print("\n🔗 INTEGRATION POSSIBILITIES:")
    print("- Connect to Gmail API for real email processing")
    print("- Set up automated email rules and forwarding")
    print("- Create dashboard for email analytics")
    print("- Send notifications for critical emails")
    print("- Integration with task management systems")

if __name__ == "__main__":
    main()