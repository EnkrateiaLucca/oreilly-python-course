#!/usr/bin/env python3
# /// script
# dependencies = ["anthropic", "python-dotenv", "pandas"]
# ///

"""
VN_user_test_summarizer.py
Student: VN - "summarizing common pain points in user tests"

This script demonstrates automated analysis of user testing feedback to identify
common pain points, themes, and actionable insights using AI.

Key Learning Objectives:
- Text analysis and pattern recognition
- User feedback processing
- AI-powered insight extraction
- Data aggregation and reporting
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

class UserTestSummarizer:
    """
    A class to analyze user testing feedback and extract common pain points.
    This simulates processing user test sessions, surveys, and feedback forms.
    """

    def __init__(self):
        """Initialize the user test summarizer with AI client."""
        # Initialize Anthropic client for AI-powered analysis
        self.ai_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        # Define categories for pain point classification
        self.pain_point_categories = [
            "navigation", "usability", "performance", "content_clarity",
            "functionality", "accessibility", "visual_design", "mobile_experience",
            "onboarding", "error_handling"
        ]

        # Severity levels for pain points
        self.severity_levels = {
            "critical": "Prevents task completion",
            "high": "Significantly impacts user experience",
            "medium": "Minor frustration but task can be completed",
            "low": "Cosmetic or preference-based issue"
        }

    def get_sample_user_feedback(self) -> List[Dict[str, Any]]:
        """
        Generate sample user testing feedback for demonstration.
        In a real scenario, this would come from testing platforms or surveys.
        """
        sample_feedback = [
            {
                "session_id": "test_001",
                "user_id": "user_123",
                "test_date": "2024-01-15",
                "user_demographics": {
                    "age_range": "25-34",
                    "tech_savviness": "intermediate",
                    "device": "desktop"
                },
                "task": "Complete product purchase",
                "completion_status": "failed",
                "time_taken_minutes": 12,
                "feedback": "I couldn't find the checkout button after adding items to cart. The cart icon was too small and I didn't realize I needed to click it. When I finally found it, the payment form was confusing - too many fields and unclear which ones were required.",
                "frustration_level": 4,  # 1-5 scale
                "quotes": [
                    "Where is the checkout button?",
                    "This payment form is overwhelming",
                    "I'm not sure if I need to fill out all these fields"
                ]
            },
            {
                "session_id": "test_002",
                "user_id": "user_456",
                "test_date": "2024-01-15",
                "user_demographics": {
                    "age_range": "45-54",
                    "tech_savviness": "beginner",
                    "device": "mobile"
                },
                "task": "Find product information",
                "completion_status": "completed",
                "time_taken_minutes": 8,
                "feedback": "The search function worked well, but the product details page was hard to read on my phone. The text was too small and the images didn't zoom properly. I also couldn't find the product specifications easily.",
                "frustration_level": 2,
                "quotes": [
                    "The text is too small to read",
                    "I can't zoom in on the product images",
                    "Where are the technical specs?"
                ]
            },
            {
                "session_id": "test_003",
                "user_id": "user_789",
                "test_date": "2024-01-16",
                "user_demographics": {
                    "age_range": "18-24",
                    "tech_savviness": "advanced",
                    "device": "mobile"
                },
                "task": "Create user account",
                "completion_status": "completed",
                "time_taken_minutes": 3,
                "feedback": "Account creation was straightforward, but the email verification process was annoying. I didn't get the verification email for 10 minutes, and there was no way to resend it. The error messages were also generic and didn't help me understand what went wrong when I tried to use a password that was apparently too weak.",
                "frustration_level": 3,
                "quotes": [
                    "Why didn't I get the verification email?",
                    "The error message doesn't tell me what's wrong with my password",
                    "There's no resend button for the verification email"
                ]
            },
            {
                "session_id": "test_004",
                "user_id": "user_321",
                "test_date": "2024-01-16",
                "user_demographics": {
                    "age_range": "35-44",
                    "tech_savviness": "intermediate",
                    "device": "desktop"
                },
                "task": "Navigate to customer support",
                "completion_status": "failed",
                "time_taken_minutes": 15,
                "feedback": "I spent way too long trying to find customer support. I looked in the footer, header, and even tried the search function. Finally found it buried in a dropdown menu that wasn't labeled clearly. When I got there, the contact form had a captcha that was impossible to read.",
                "frustration_level": 5,
                "quotes": [
                    "Where is customer support?",
                    "This captcha is unreadable",
                    "The contact form is hidden too deep in the menu"
                ]
            },
            {
                "session_id": "test_005",
                "user_id": "user_654",
                "test_date": "2024-01-17",
                "user_demographics": {
                    "age_range": "55-64",
                    "tech_savviness": "beginner",
                    "device": "tablet"
                },
                "task": "Update profile information",
                "completion_status": "completed",
                "time_taken_minutes": 20,
                "feedback": "The profile page was cluttered and overwhelming. I couldn't tell which sections I could edit and which were just for display. The save button was at the bottom of a very long page, and I wasn't sure if my changes were saved because there was no confirmation message.",
                "frustration_level": 3,
                "quotes": [
                    "This page has too much information",
                    "Can I edit this section or not?",
                    "Did my changes save? I don't see any confirmation"
                ]
            },
            {
                "session_id": "test_006",
                "user_id": "user_987",
                "test_date": "2024-01-17",
                "user_demographics": {
                    "age_range": "25-34",
                    "tech_savviness": "advanced",
                    "device": "desktop"
                },
                "task": "Use advanced search filters",
                "completion_status": "completed",
                "time_taken_minutes": 5,
                "feedback": "The search filters worked well overall, but some of the filter options were confusing. The price range slider was hard to use precisely, and the category filters seemed to overlap in weird ways. Also, clearing all filters required clicking each one individually - there was no 'clear all' button.",
                "frustration_level": 2,
                "quotes": [
                    "The price slider is hard to control",
                    "Why do some products appear in multiple categories?",
                    "I need a way to clear all filters at once"
                ]
            }
        ]

        return sample_feedback

    def analyze_feedback_with_ai(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use AI to analyze a batch of user feedback and extract insights.

        Args:
            feedback_batch: List of user feedback dictionaries

        Returns:
            Dictionary with analyzed insights and pain points
        """

        # Prepare feedback for AI analysis
        feedback_text = ""
        for fb in feedback_batch:
            feedback_text += f"""
            Session {fb['session_id']}:
            Task: {fb['task']}
            Status: {fb['completion_status']}
            Device: {fb['user_demographics']['device']}
            Frustration Level: {fb['frustration_level']}/5
            Feedback: {fb['feedback']}
            User Quotes: {'; '.join(fb['quotes'])}
            ---
            """

        # Create AI prompt for comprehensive analysis
        prompt = f"""
        Analyze this user testing feedback and identify:

        1. Top 5 most common pain points across all sessions
        2. Categorize each pain point into: {', '.join(self.pain_point_categories)}
        3. Assign severity level: critical, high, medium, low
        4. Identify patterns by device type (mobile vs desktop vs tablet)
        5. Extract specific actionable recommendations
        6. Highlight any accessibility concerns
        7. Note which issues caused task failures vs completions

        User Feedback Data:
        {feedback_text}

        Respond in JSON format:
        {{
            "common_pain_points": [
                {{
                    "issue": "description",
                    "category": "category",
                    "severity": "level",
                    "frequency": "how often mentioned",
                    "affected_tasks": ["task1", "task2"],
                    "devices_affected": ["device1", "device2"],
                    "user_quotes": ["quote1", "quote2"]
                }}
            ],
            "device_specific_issues": {{
                "mobile": ["issue1", "issue2"],
                "desktop": ["issue1", "issue2"],
                "tablet": ["issue1", "issue2"]
            }},
            "task_failure_causes": ["cause1", "cause2"],
            "actionable_recommendations": [
                {{
                    "recommendation": "specific action",
                    "priority": "high/medium/low",
                    "impact": "expected improvement",
                    "effort": "implementation difficulty"
                }}
            ],
            "accessibility_concerns": ["concern1", "concern2"],
            "overall_sentiment": "summary of user satisfaction"
        }}
        """

        try:
            # Make API call to Anthropic
            response = self.ai_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the AI response
            ai_analysis = json.loads(response.content[0].text)
            return ai_analysis

        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
            # Fallback to rule-based analysis
            return self.fallback_analysis(feedback_batch)

    def fallback_analysis(self, feedback_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fallback rule-based analysis when AI is unavailable.

        Args:
            feedback_batch: List of user feedback dictionaries

        Returns:
            Dictionary with basic analysis results
        """

        # Basic keyword-based analysis
        all_feedback_text = " ".join([fb['feedback'] for fb in feedback_batch])
        all_quotes = [quote for fb in feedback_batch for quote in fb['quotes']]

        # Simple pain point detection based on keywords
        pain_point_keywords = {
            "navigation": ["find", "locate", "hidden", "menu", "where"],
            "usability": ["confusing", "unclear", "difficult", "hard"],
            "performance": ["slow", "loading", "wait", "delay"],
            "mobile_experience": ["small", "zoom", "mobile", "phone"],
            "error_handling": ["error", "message", "wrong", "failed"]
        }

        detected_issues = []
        for category, keywords in pain_point_keywords.items():
            if any(keyword in all_feedback_text.lower() for keyword in keywords):
                detected_issues.append({
                    "issue": f"Issues related to {category}",
                    "category": category,
                    "severity": "medium",
                    "frequency": "multiple mentions",
                    "affected_tasks": [],
                    "devices_affected": [],
                    "user_quotes": [q for q in all_quotes if any(kw in q.lower() for kw in keywords)][:3]
                })

        return {
            "common_pain_points": detected_issues,
            "device_specific_issues": {"mobile": [], "desktop": [], "tablet": []},
            "task_failure_causes": ["Rule-based analysis - limited insights"],
            "actionable_recommendations": [
                {
                    "recommendation": "Conduct detailed analysis with AI",
                    "priority": "high",
                    "impact": "Better insights",
                    "effort": "low"
                }
            ],
            "accessibility_concerns": [],
            "overall_sentiment": "Mixed - rule-based analysis"
        }

    def generate_pain_point_report(self, analysis: Dict[str, Any],
                                 original_feedback: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive report of user testing pain points.

        Args:
            analysis: AI analysis results
            original_feedback: Original user feedback data

        Returns:
            Formatted report string
        """

        report = []
        report.append("=" * 70)
        report.append("👥 USER TESTING PAIN POINT ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total user sessions analyzed: {len(original_feedback)}")

        # Calculate basic metrics
        failed_tasks = [fb for fb in original_feedback if fb['completion_status'] == 'failed']
        avg_frustration = sum(fb['frustration_level'] for fb in original_feedback) / len(original_feedback)

        report.append(f"Task failure rate: {len(failed_tasks)}/{len(original_feedback)} ({len(failed_tasks)/len(original_feedback)*100:.1f}%)")
        report.append(f"Average frustration level: {avg_frustration:.1f}/5")
        report.append("")

        # Top pain points
        report.append("🔍 TOP PAIN POINTS IDENTIFIED:")
        report.append("-" * 40)

        for i, pain_point in enumerate(analysis.get('common_pain_points', []), 1):
            report.append(f"{i}. {pain_point['issue']}")
            report.append(f"   Category: {pain_point['category'].replace('_', ' ').title()}")
            report.append(f"   Severity: {pain_point['severity'].upper()}")
            report.append(f"   Frequency: {pain_point['frequency']}")

            if pain_point.get('user_quotes'):
                report.append("   User Quotes:")
                for quote in pain_point['user_quotes'][:2]:
                    report.append(f"   • \"{quote}\"")
            report.append("")

        # Device-specific issues
        device_issues = analysis.get('device_specific_issues', {})
        if any(device_issues.values()):
            report.append("📱 DEVICE-SPECIFIC ISSUES:")
            report.append("-" * 30)
            for device, issues in device_issues.items():
                if issues:
                    report.append(f"  {device.title()}:")
                    for issue in issues:
                        report.append(f"    • {issue}")
            report.append("")

        # Task failure analysis
        failure_causes = analysis.get('task_failure_causes', [])
        if failure_causes:
            report.append("❌ PRIMARY CAUSES OF TASK FAILURES:")
            report.append("-" * 40)
            for cause in failure_causes:
                report.append(f"  • {cause}")
            report.append("")

        # Actionable recommendations
        recommendations = analysis.get('actionable_recommendations', [])
        if recommendations:
            report.append("💡 ACTIONABLE RECOMMENDATIONS:")
            report.append("-" * 35)

            # Sort by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            sorted_recs = sorted(recommendations,
                               key=lambda x: priority_order.get(x.get('priority', 'medium'), 1))

            for rec in sorted_recs:
                report.append(f"🎯 {rec['recommendation']}")
                report.append(f"   Priority: {rec.get('priority', 'medium').upper()}")
                report.append(f"   Expected Impact: {rec.get('impact', 'Not specified')}")
                report.append(f"   Implementation Effort: {rec.get('effort', 'Not specified')}")
                report.append("")

        # Accessibility concerns
        accessibility = analysis.get('accessibility_concerns', [])
        if accessibility:
            report.append("♿ ACCESSIBILITY CONCERNS:")
            report.append("-" * 30)
            for concern in accessibility:
                report.append(f"  • {concern}")
            report.append("")

        # Overall sentiment
        sentiment = analysis.get('overall_sentiment', 'Not available')
        report.append("📊 OVERALL USER SENTIMENT:")
        report.append("-" * 30)
        report.append(f"  {sentiment}")
        report.append("")

        # Next steps
        report.append("🚀 RECOMMENDED NEXT STEPS:")
        report.append("-" * 30)
        report.append("  1. Prioritize high-severity pain points for immediate fixes")
        report.append("  2. Conduct follow-up testing on critical issues")
        report.append("  3. Create detailed user stories for recommended improvements")
        report.append("  4. Set up continuous user feedback collection")
        report.append("  5. Track metrics before and after implementing changes")

        return "\n".join(report)

    def export_to_csv(self, analysis: Dict[str, Any], filename: str = "user_pain_points.csv"):
        """
        Export pain points analysis to CSV for further analysis.

        Args:
            analysis: Analysis results dictionary
            filename: Output CSV filename
        """

        pain_points = analysis.get('common_pain_points', [])

        if not pain_points:
            print("No pain points to export")
            return

        # Convert to DataFrame
        df_data = []
        for pp in pain_points:
            df_data.append({
                'Issue': pp.get('issue', ''),
                'Category': pp.get('category', ''),
                'Severity': pp.get('severity', ''),
                'Frequency': pp.get('frequency', ''),
                'Affected_Tasks': '; '.join(pp.get('affected_tasks', [])),
                'Devices_Affected': '; '.join(pp.get('devices_affected', [])),
                'User_Quotes': '; '.join(pp.get('user_quotes', []))
            })

        df = pd.DataFrame(df_data)
        df.to_csv(filename, index=False)
        print(f"📁 Pain points exported to: {filename}")

def main():
    """
    Main function to demonstrate user test summarization and pain point analysis.
    """

    print("🚀 User Test Pain Point Summarizer Demo")
    print("=" * 50)

    # Initialize the summarizer
    summarizer = UserTestSummarizer()

    # Get sample user feedback (in real app, this would come from testing platforms)
    print("📊 Loading user testing feedback...")
    feedback_data = summarizer.get_sample_user_feedback()
    print(f"Loaded {len(feedback_data)} user testing sessions")
    print()

    # Analyze feedback for pain points
    print("🔍 Analyzing feedback with AI...")
    analysis = summarizer.analyze_feedback_with_ai(feedback_data)
    print("Analysis complete!")
    print()

    # Generate comprehensive report
    report = summarizer.generate_pain_point_report(analysis, feedback_data)
    print(report)

    # Export data for further analysis
    summarizer.export_to_csv(analysis)

    # Save full analysis to JSON
    output_file = "user_test_analysis.json"
    with open(output_file, 'w') as f:
        export_data = {
            "analysis_date": datetime.now().isoformat(),
            "sessions_analyzed": len(feedback_data),
            "analysis_results": analysis,
            "raw_feedback_sample": feedback_data[:2]  # Include sample for reference
        }
        json.dump(export_data, f, indent=2, default=str)

    print(f"\n💾 Full analysis saved to: {output_file}")

    # Demonstrate integration possibilities
    print("\n🔗 INTEGRATION POSSIBILITIES:")
    print("- Connect to UserTesting, Maze, or Hotjar APIs")
    print("- Automated analysis of survey responses")
    print("- Integration with product management tools (Jira, Asana)")
    print("- Real-time dashboard for UX teams")
    print("- Automated alerts for critical usability issues")
    print("- Trend analysis over time")

if __name__ == "__main__":
    main()