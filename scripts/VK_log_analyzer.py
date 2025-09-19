#!/usr/bin/env python3
# /// script
# dependencies = ["anthropic", "python-dotenv", "pandas", "matplotlib"]
# ///

"""
VK_log_analyzer.py
Student: VK - "Auto log analysis of ECU results"

This script demonstrates automated analysis of ECU (Electronic Control Unit) logs
to identify patterns, anomalies, and potential issues using AI and statistical analysis.

Key Learning Objectives:
- Log file parsing and processing
- Pattern recognition in time-series data
- Anomaly detection techniques
- Automated alerting and reporting
- Statistical analysis of automotive data
"""

import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

class ECULogAnalyzer:
    """
    A class to analyze ECU (Electronic Control Unit) logs for automotive systems.
    This simulates analysis of vehicle diagnostic data, sensor readings, and error codes.
    """

    def __init__(self):
        """Initialize the ECU log analyzer with AI client."""
        # Initialize Anthropic client for AI-powered analysis
        self.ai_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        # Define ECU systems and their normal operating ranges
        self.ecu_systems = {
            "engine": {
                "parameters": ["rpm", "coolant_temp", "oil_pressure", "throttle_position"],
                "normal_ranges": {
                    "rpm": (500, 6000),
                    "coolant_temp": (80, 105),  # Celsius
                    "oil_pressure": (20, 80),   # PSI
                    "throttle_position": (0, 100)  # Percentage
                }
            },
            "transmission": {
                "parameters": ["gear", "fluid_temp", "torque"],
                "normal_ranges": {
                    "gear": (1, 8),
                    "fluid_temp": (70, 120),  # Celsius
                    "torque": (100, 500)  # Nm
                }
            },
            "braking": {
                "parameters": ["brake_pressure", "abs_active", "brake_temp"],
                "normal_ranges": {
                    "brake_pressure": (0, 2000),  # PSI
                    "abs_active": (0, 1),  # Boolean
                    "brake_temp": (20, 200)  # Celsius
                }
            },
            "emissions": {
                "parameters": ["o2_sensor", "cat_temp", "egr_position"],
                "normal_ranges": {
                    "o2_sensor": (0.1, 0.9),  # Voltage
                    "cat_temp": (300, 800),   # Celsius
                    "egr_position": (0, 100)  # Percentage
                }
            }
        }

        # Common ECU error codes and their meanings
        self.error_codes = {
            "P0301": "Cylinder 1 Misfire Detected",
            "P0420": "Catalyst System Efficiency Below Threshold",
            "P0171": "System Too Lean (Bank 1)",
            "P0172": "System Too Rich (Bank 1)",
            "P0128": "Coolant Thermostat (Coolant Temperature Below Thermostat Regulating Temperature)",
            "P0441": "Evaporative Emission Control System Incorrect Purge Flow",
            "P0700": "Transmission Control System Malfunction",
            "P0750": "Shift Solenoid 'A' Malfunction",
            "C1201": "Engine Control System Malfunction",
            "B1342": "ECM Battery Voltage Out of Range"
        }

    def generate_sample_ecu_logs(self) -> List[Dict[str, Any]]:
        """
        Generate sample ECU log data for demonstration.
        In a real scenario, this would come from vehicle diagnostic tools or CAN bus data.
        """
        import random

        logs = []
        base_time = datetime.now() - timedelta(hours=2)

        # Generate 500 log entries over 2 hours
        for i in range(500):
            timestamp = base_time + timedelta(seconds=i * 14.4)  # Every ~14 seconds

            # Simulate normal operation with occasional anomalies
            log_entry = {
                "timestamp": timestamp.isoformat(),
                "vehicle_id": "VIN123456789",
                "ecu_id": "ECU_ENGINE_01",
                "system": "engine",
                "parameters": {
                    "rpm": random.normalvariate(2000, 500) + (50 if i > 300 else 0),  # Anomaly after time 300
                    "coolant_temp": random.normalvariate(90, 5) + (20 if i > 350 else 0),  # Overheating
                    "oil_pressure": random.normalvariate(45, 8) - (20 if i > 400 else 0),  # Pressure drop
                    "throttle_position": random.uniform(10, 80)
                },
                "error_codes": [],
                "severity": "normal"
            }

            # Add some error conditions
            if i > 300 and random.random() < 0.1:  # 10% chance of error after entry 300
                error_code = random.choice(list(self.error_codes.keys()))
                log_entry["error_codes"].append(error_code)
                log_entry["severity"] = "warning" if error_code.startswith('P') else "critical"

            # Add transmission data occasionally
            if i % 50 == 0:
                log_entry["system"] = "transmission"
                log_entry["ecu_id"] = "ECU_TRANS_01"
                log_entry["parameters"] = {
                    "gear": random.randint(1, 6),
                    "fluid_temp": random.normalvariate(95, 10),
                    "torque": random.normalvariate(250, 50)
                }

            logs.append(log_entry)

        return logs

    def parse_log_patterns(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse ECU logs to identify patterns and anomalies.

        Args:
            logs: List of ECU log entries

        Returns:
            Dictionary with parsed patterns and anomalies
        """

        print("🔍 Parsing ECU log patterns...")

        # Convert to DataFrame for easier analysis
        df_data = []
        for log in logs:
            row = {
                "timestamp": log["timestamp"],
                "vehicle_id": log["vehicle_id"],
                "ecu_id": log["ecu_id"],
                "system": log["system"],
                "severity": log["severity"],
                "error_codes": ";".join(log["error_codes"]) if log["error_codes"] else ""
            }

            # Flatten parameters
            for param, value in log["parameters"].items():
                row[param] = value

            df_data.append(row)

        df = pd.DataFrame(df_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Analyze patterns
        patterns = {
            "total_entries": len(df),
            "time_range": {
                "start": df['timestamp'].min().isoformat(),
                "end": df['timestamp'].max().isoformat(),
                "duration_hours": (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
            },
            "systems_analyzed": df['system'].unique().tolist(),
            "severity_breakdown": df['severity'].value_counts().to_dict(),
            "error_frequency": Counter([code for codes in df['error_codes'] if codes for code in codes.split(';')]),
            "anomalies_detected": [],
            "parameter_statistics": {}
        }

        # Detect anomalies for each system
        for system in df['system'].unique():
            system_df = df[df['system'] == system]
            system_config = self.ecu_systems.get(system, {})
            normal_ranges = system_config.get("normal_ranges", {})

            for param in system_config.get("parameters", []):
                if param in system_df.columns:
                    values = system_df[param].dropna()

                    if len(values) > 0:
                        # Calculate statistics
                        patterns["parameter_statistics"][f"{system}_{param}"] = {
                            "mean": float(values.mean()),
                            "std": float(values.std()),
                            "min": float(values.min()),
                            "max": float(values.max()),
                            "median": float(values.median())
                        }

                        # Check for out-of-range values
                        if param in normal_ranges:
                            min_val, max_val = normal_ranges[param]
                            out_of_range = values[(values < min_val) | (values > max_val)]

                            if len(out_of_range) > 0:
                                patterns["anomalies_detected"].append({
                                    "system": system,
                                    "parameter": param,
                                    "anomaly_type": "out_of_range",
                                    "count": len(out_of_range),
                                    "percentage": (len(out_of_range) / len(values)) * 100,
                                    "normal_range": normal_ranges[param],
                                    "observed_range": (float(out_of_range.min()), float(out_of_range.max()))
                                })

                        # Detect sudden spikes (values > 2 standard deviations from mean)
                        if len(values) > 10:
                            mean_val = values.mean()
                            std_val = values.std()
                            spikes = values[abs(values - mean_val) > 2 * std_val]

                            if len(spikes) > 0:
                                patterns["anomalies_detected"].append({
                                    "system": system,
                                    "parameter": param,
                                    "anomaly_type": "statistical_spike",
                                    "count": len(spikes),
                                    "percentage": (len(spikes) / len(values)) * 100,
                                    "threshold": f">{mean_val:.2f} ± {2*std_val:.2f}",
                                    "spike_values": spikes.tolist()[:5]  # Show first 5 spikes
                                })

        return patterns

    def analyze_with_ai(self, patterns: Dict[str, Any], sample_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use AI to analyze ECU patterns and provide insights.

        Args:
            patterns: Parsed patterns from log analysis
            sample_logs: Sample of original log entries

        Returns:
            AI analysis with insights and recommendations
        """

        # Prepare data for AI analysis
        analysis_summary = f"""
        ECU Log Analysis Summary:
        - Total entries: {patterns['total_entries']}
        - Time range: {patterns['time_range']['duration_hours']:.1f} hours
        - Systems: {', '.join(patterns['systems_analyzed'])}
        - Severity breakdown: {patterns['severity_breakdown']}
        - Error codes found: {dict(patterns['error_frequency'])}
        - Anomalies detected: {len(patterns['anomalies_detected'])}

        Key Anomalies:
        """

        for anomaly in patterns['anomalies_detected'][:5]:  # Top 5 anomalies
            analysis_summary += f"""
        - {anomaly['system']}.{anomaly['parameter']}: {anomaly['anomaly_type']}
          ({anomaly['count']} occurrences, {anomaly['percentage']:.1f}% of readings)
        """

        # Add sample of recent error codes
        recent_errors = [log for log in sample_logs[-50:] if log.get('error_codes')]
        if recent_errors:
            analysis_summary += "\n\nRecent Error Codes:\n"
            for log in recent_errors[:3]:
                for code in log['error_codes']:
                    analysis_summary += f"- {code}: {self.error_codes.get(code, 'Unknown error')}\n"

        # Create AI prompt for ECU analysis
        prompt = f"""
        As an automotive diagnostics expert, analyze this ECU log data and provide:

        1. Critical issues that need immediate attention
        2. Potential root causes for detected anomalies
        3. Predictive maintenance recommendations
        4. Risk assessment (safety, performance, emissions)
        5. Suggested diagnostic procedures
        6. Timeline for addressing issues (immediate, short-term, long-term)

        ECU Analysis Data:
        {analysis_summary}

        Respond in JSON format:
        {{
            "critical_issues": [
                {{
                    "issue": "description",
                    "system": "affected_system",
                    "severity": "critical/high/medium/low",
                    "immediate_action_required": true/false,
                    "potential_consequences": "description"
                }}
            ],
            "root_cause_analysis": [
                {{
                    "symptom": "observed_anomaly",
                    "likely_causes": ["cause1", "cause2"],
                    "diagnostic_steps": ["step1", "step2"]
                }}
            ],
            "maintenance_recommendations": [
                {{
                    "action": "recommended_action",
                    "timeframe": "immediate/1_week/1_month/3_months",
                    "priority": "high/medium/low",
                    "estimated_cost": "cost_category"
                }}
            ],
            "risk_assessment": {{
                "safety_risk": "low/medium/high",
                "performance_impact": "description",
                "emissions_compliance": "compliant/at_risk/non_compliant",
                "overall_vehicle_health": "excellent/good/fair/poor"
            }},
            "trending_issues": ["issue1", "issue2"],
            "summary": "overall_assessment"
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
            return self.fallback_analysis(patterns)

    def fallback_analysis(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback rule-based analysis when AI is unavailable.

        Args:
            patterns: Parsed patterns from log analysis

        Returns:
            Basic analysis results
        """

        critical_issues = []
        maintenance_recs = []

        # Check for critical anomalies
        for anomaly in patterns['anomalies_detected']:
            if anomaly['percentage'] > 10:  # More than 10% out of range
                critical_issues.append({
                    "issue": f"{anomaly['system']} {anomaly['parameter']} anomaly",
                    "system": anomaly['system'],
                    "severity": "high" if anomaly['percentage'] > 20 else "medium",
                    "immediate_action_required": anomaly['percentage'] > 20,
                    "potential_consequences": "System performance degradation"
                })

        # Check error codes
        if patterns['error_frequency']:
            critical_issues.append({
                "issue": "Active error codes detected",
                "system": "multiple",
                "severity": "high",
                "immediate_action_required": True,
                "potential_consequences": "Vehicle reliability and compliance issues"
            })

        return {
            "critical_issues": critical_issues,
            "root_cause_analysis": [
                {
                    "symptom": "Multiple anomalies detected",
                    "likely_causes": ["Sensor degradation", "Component wear"],
                    "diagnostic_steps": ["Visual inspection", "Component testing"]
                }
            ],
            "maintenance_recommendations": [
                {
                    "action": "Comprehensive diagnostic scan",
                    "timeframe": "immediate",
                    "priority": "high",
                    "estimated_cost": "medium"
                }
            ],
            "risk_assessment": {
                "safety_risk": "medium",
                "performance_impact": "Potential degradation detected",
                "emissions_compliance": "at_risk",
                "overall_vehicle_health": "fair"
            },
            "trending_issues": ["Sensor anomalies"],
            "summary": "Rule-based analysis - AI analysis recommended for detailed insights"
        }

    def generate_diagnostic_report(self, patterns: Dict[str, Any],
                                 ai_analysis: Dict[str, Any]) -> str:
        """
        Generate a comprehensive ECU diagnostic report.

        Args:
            patterns: Parsed patterns from log analysis
            ai_analysis: AI analysis results

        Returns:
            Formatted diagnostic report
        """

        report = []
        report.append("=" * 70)
        report.append("🚗 ECU LOG ANALYSIS - DIAGNOSTIC REPORT")
        report.append("=" * 70)
        report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Vehicle ID: {patterns.get('vehicle_id', 'Multiple vehicles')}")
        report.append(f"Analysis period: {patterns['time_range']['duration_hours']:.1f} hours")
        report.append(f"Total log entries: {patterns['total_entries']}")
        report.append("")

        # Overall health assessment
        risk_assessment = ai_analysis.get('risk_assessment', {})
        report.append("🏥 OVERALL VEHICLE HEALTH:")
        report.append("-" * 30)
        report.append(f"Overall Status: {risk_assessment.get('overall_vehicle_health', 'Unknown').upper()}")
        report.append(f"Safety Risk Level: {risk_assessment.get('safety_risk', 'Unknown').upper()}")
        report.append(f"Performance Impact: {risk_assessment.get('performance_impact', 'Not assessed')}")
        report.append(f"Emissions Compliance: {risk_assessment.get('emissions_compliance', 'Unknown').upper()}")
        report.append("")

        # Critical issues
        critical_issues = ai_analysis.get('critical_issues', [])
        if critical_issues:
            report.append("🚨 CRITICAL ISSUES REQUIRING ATTENTION:")
            report.append("-" * 45)
            for issue in critical_issues:
                report.append(f"⚠️  {issue['issue']}")
                report.append(f"    System: {issue['system']}")
                report.append(f"    Severity: {issue['severity'].upper()}")
                report.append(f"    Immediate Action: {'YES' if issue.get('immediate_action_required') else 'NO'}")
                report.append(f"    Consequences: {issue.get('potential_consequences', 'Not specified')}")
                report.append("")

        # Detected anomalies
        if patterns['anomalies_detected']:
            report.append("📊 DETECTED ANOMALIES:")
            report.append("-" * 25)
            for anomaly in patterns['anomalies_detected']:
                report.append(f"• {anomaly['system'].title()} - {anomaly['parameter']}")
                report.append(f"  Type: {anomaly['anomaly_type']}")
                report.append(f"  Occurrences: {anomaly['count']} ({anomaly['percentage']:.1f}% of readings)")
                if 'normal_range' in anomaly:
                    report.append(f"  Normal Range: {anomaly['normal_range']}")
                    report.append(f"  Observed Range: {anomaly['observed_range']}")
                report.append("")

        # Error codes
        if patterns['error_frequency']:
            report.append("🔍 ACTIVE ERROR CODES:")
            report.append("-" * 25)
            for code, count in patterns['error_frequency'].most_common():
                description = self.error_codes.get(code, "Unknown error code")
                report.append(f"  {code}: {description} (occurred {count} times)")
            report.append("")

        # Root cause analysis
        root_causes = ai_analysis.get('root_cause_analysis', [])
        if root_causes:
            report.append("🔬 ROOT CAUSE ANALYSIS:")
            report.append("-" * 27)
            for analysis in root_causes:
                report.append(f"Symptom: {analysis['symptom']}")
                report.append("Likely Causes:")
                for cause in analysis.get('likely_causes', []):
                    report.append(f"  • {cause}")
                report.append("Diagnostic Steps:")
                for step in analysis.get('diagnostic_steps', []):
                    report.append(f"  1. {step}")
                report.append("")

        # Maintenance recommendations
        maintenance_recs = ai_analysis.get('maintenance_recommendations', [])
        if maintenance_recs:
            report.append("🔧 MAINTENANCE RECOMMENDATIONS:")
            report.append("-" * 35)

            # Sort by priority and timeframe
            priority_order = {"high": 0, "medium": 1, "low": 2}
            timeframe_order = {"immediate": 0, "1_week": 1, "1_month": 2, "3_months": 3}

            sorted_recs = sorted(maintenance_recs,
                               key=lambda x: (priority_order.get(x.get('priority', 'medium'), 1),
                                            timeframe_order.get(x.get('timeframe', '1_month'), 2)))

            for rec in sorted_recs:
                priority_icon = "🔴" if rec.get('priority') == 'high' else "🟡" if rec.get('priority') == 'medium' else "🟢"
                report.append(f"{priority_icon} {rec['action']}")
                report.append(f"    Timeframe: {rec.get('timeframe', 'Not specified')}")
                report.append(f"    Priority: {rec.get('priority', 'medium').upper()}")
                report.append(f"    Estimated Cost: {rec.get('estimated_cost', 'Not specified')}")
                report.append("")

        # Summary
        summary = ai_analysis.get('summary', 'No summary available')
        report.append("📋 EXECUTIVE SUMMARY:")
        report.append("-" * 22)
        report.append(f"  {summary}")
        report.append("")

        # Next steps
        report.append("🚀 RECOMMENDED NEXT STEPS:")
        report.append("-" * 30)
        report.append("  1. Address all critical issues immediately")
        report.append("  2. Schedule diagnostic procedures for anomalies")
        report.append("  3. Plan maintenance based on recommendations")
        report.append("  4. Set up continuous monitoring for trending issues")
        report.append("  5. Update maintenance schedules based on findings")

        return "\n".join(report)

    def create_visualizations(self, patterns: Dict[str, Any], logs: List[Dict[str, Any]]):
        """
        Create visualizations of ECU data patterns.

        Args:
            patterns: Parsed patterns from log analysis
            logs: Original log data
        """

        # Convert logs to DataFrame for plotting
        df_data = []
        for log in logs:
            row = {
                "timestamp": log["timestamp"],
                "system": log["system"],
                "severity": log["severity"]
            }
            # Flatten parameters
            for param, value in log["parameters"].items():
                row[param] = value
            df_data.append(row)

        df = pd.DataFrame(df_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('ECU Log Analysis Dashboard', fontsize=16)

        # Plot 1: Parameter trends over time (Engine RPM)
        engine_data = df[df['system'] == 'engine']
        if not engine_data.empty and 'rpm' in engine_data.columns:
            axes[0, 0].plot(engine_data['timestamp'], engine_data['rpm'], 'b-', alpha=0.7)
            axes[0, 0].set_title('Engine RPM Over Time')
            axes[0, 0].set_ylabel('RPM')
            axes[0, 0].tick_params(axis='x', rotation=45)

        # Plot 2: Severity distribution
        severity_counts = df['severity'].value_counts()
        axes[0, 1].pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%')
        axes[0, 1].set_title('Severity Distribution')

        # Plot 3: Temperature readings
        if not engine_data.empty and 'coolant_temp' in engine_data.columns:
            axes[1, 0].scatter(engine_data['timestamp'], engine_data['coolant_temp'],
                             c=engine_data['coolant_temp'], cmap='coolwarm', alpha=0.6)
            axes[1, 0].set_title('Coolant Temperature')
            axes[1, 0].set_ylabel('Temperature (°C)')
            axes[1, 0].tick_params(axis='x', rotation=45)

        # Plot 4: System activity
        system_counts = df['system'].value_counts()
        axes[1, 1].bar(system_counts.index, system_counts.values)
        axes[1, 1].set_title('Log Entries by System')
        axes[1, 1].set_ylabel('Number of Entries')

        plt.tight_layout()
        plt.savefig('ecu_analysis_dashboard.png', dpi=300, bbox_inches='tight')
        print("📊 Visualization saved as: ecu_analysis_dashboard.png")

def main():
    """
    Main function to demonstrate ECU log analysis.
    """

    print("🚀 ECU Log Analyzer Demo")
    print("=" * 40)

    # Initialize the analyzer
    analyzer = ECULogAnalyzer()

    # Generate sample ECU logs (in real app, this would read from log files)
    print("📄 Generating sample ECU logs...")
    logs = analyzer.generate_sample_ecu_logs()
    print(f"Generated {len(logs)} ECU log entries")
    print()

    # Parse log patterns and detect anomalies
    print("🔍 Analyzing log patterns...")
    patterns = analyzer.parse_log_patterns(logs)
    print(f"Detected {len(patterns['anomalies_detected'])} anomalies")
    print()

    # Get AI analysis of patterns
    print("🤖 Performing AI-powered analysis...")
    ai_analysis = analyzer.analyze_with_ai(patterns, logs[-10:])  # Send last 10 logs as sample
    print("AI analysis complete!")
    print()

    # Generate comprehensive report
    report = analyzer.generate_diagnostic_report(patterns, ai_analysis)
    print(report)

    # Create visualizations
    print("\n📊 Creating visualizations...")
    analyzer.create_visualizations(patterns, logs)

    # Save analysis results
    output_file = "ecu_analysis_results.json"
    with open(output_file, 'w') as f:
        export_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "log_summary": {
                "total_entries": patterns["total_entries"],
                "time_range": patterns["time_range"],
                "systems_analyzed": patterns["systems_analyzed"]
            },
            "patterns": patterns,
            "ai_analysis": ai_analysis
        }
        json.dump(export_data, f, indent=2, default=str)

    print(f"\n💾 Analysis results saved to: {output_file}")

    # Demonstrate integration possibilities
    print("\n🔗 INTEGRATION POSSIBILITIES:")
    print("- Real-time CAN bus data integration")
    print("- OBD-II diagnostic tool connectivity")
    print("- Fleet management system integration")
    print("- Predictive maintenance scheduling")
    print("- Automated alert systems for critical issues")
    print("- Integration with dealer service systems")
    print("- Telematics and remote diagnostics")

if __name__ == "__main__":
    main()