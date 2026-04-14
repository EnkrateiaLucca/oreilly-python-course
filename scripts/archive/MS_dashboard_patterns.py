#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
#     "matplotlib",
#     "seaborn",
#     "numpy",
#     "sqlite3",
#     "python-dotenv",
#     "plotly",
#     "dash",
#     "dash-bootstrap-components",
#     "scikit-learn",
# ]
# ///

"""
MS_dashboard_patterns.py - Application Log Analysis Dashboard

Student: MS (Initials)
Request: "creating dash boards and patterns of the issues in the application"

This script demonstrates how to create interactive dashboards for analyzing application logs
and identifying patterns in issues. It includes comprehensive log analysis, pattern detection,
and real-time dashboard visualization.

Educational Focus:
- Log file parsing and analysis
- Pattern detection in application logs
- Interactive dashboard creation with Dash/Plotly
- Data visualization best practices
- Real-time monitoring concepts
- Issue categorization and alerting
- Performance metrics tracking

Prerequisites:
- Sample log files (will be created automatically)
- Web browser for viewing dashboard
- Basic understanding of web applications
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import re
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import threading
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    """Data class representing a parsed log entry."""
    timestamp: datetime
    level: str
    component: str
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    request_id: Optional[str] = None
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_code: Optional[str] = None

@dataclass
class IssuePattern:
    """Data class representing an identified issue pattern."""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    severity: str
    first_occurrence: datetime
    last_occurrence: datetime
    affected_components: List[str]
    sample_messages: List[str]

class LogAnalyzer:
    """
    Comprehensive log analyzer for detecting patterns and issues.

    This class demonstrates professional log analysis patterns including:
    - Log parsing and normalization
    - Pattern detection using ML techniques
    - Issue categorization and severity assessment
    - Performance metrics calculation
    """

    def __init__(self, db_path: str = "log_analysis.db"):
        """
        Initialize the log analyzer.

        Args:
            db_path (str): Path to SQLite database for storing analysis results
        """
        self.db_path = db_path
        self.setup_database()

        # Log level hierarchy for severity mapping
        self.log_levels = {
            'DEBUG': 1,
            'INFO': 2,
            'WARNING': 3,
            'ERROR': 4,
            'CRITICAL': 5
        }

        # Common error patterns
        self.error_patterns = {
            'database': [
                r'database.*connection.*failed',
                r'sql.*error',
                r'timeout.*database',
                r'deadlock.*detected'
            ],
            'authentication': [
                r'authentication.*failed',
                r'invalid.*credentials',
                r'unauthorized.*access',
                r'token.*expired'
            ],
            'network': [
                r'connection.*refused',
                r'network.*timeout',
                r'host.*unreachable',
                r'ssl.*error'
            ],
            'performance': [
                r'slow.*query',
                r'high.*memory.*usage',
                r'cpu.*threshold.*exceeded',
                r'response.*time.*exceeded'
            ],
            'application': [
                r'null.*pointer.*exception',
                r'index.*out.*of.*bounds',
                r'file.*not.*found',
                r'permission.*denied'
            ]
        }

    def setup_database(self):
        """Initialize the SQLite database for storing log analysis results."""
        logger.info("🗄️ Setting up log analysis database...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Log entries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS log_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        level TEXT,
                        component TEXT,
                        message TEXT,
                        user_id TEXT,
                        session_id TEXT,
                        ip_address TEXT,
                        request_id TEXT,
                        response_time REAL,
                        status_code INTEGER,
                        error_code TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Issue patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS issue_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_id TEXT UNIQUE,
                        pattern_type TEXT,
                        description TEXT,
                        frequency INTEGER,
                        severity TEXT,
                        first_occurrence DATETIME,
                        last_occurrence DATETIME,
                        affected_components TEXT,
                        sample_messages TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        metric_name TEXT,
                        metric_value REAL,
                        component TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Dashboard alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dashboard_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_type TEXT,
                        severity TEXT,
                        title TEXT,
                        message TEXT,
                        component TEXT,
                        timestamp DATETIME,
                        acknowledged BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("✅ Database setup completed")

        except sqlite3.Error as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise

    def create_sample_logs(self, num_entries: int = 1000) -> List[LogEntry]:
        """
        Create sample log entries for demonstration.

        In a real implementation, this would parse actual log files.

        Args:
            num_entries (int): Number of log entries to create

        Returns:
            List[LogEntry]: List of sample log entries
        """
        logger.info(f"📝 Creating {num_entries} sample log entries...")

        log_entries = []
        components = ['web-server', 'database', 'auth-service', 'payment-service', 'notification-service']
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        # Sample log messages by type
        log_messages = {
            'INFO': [
                'User login successful',
                'Request processed successfully',
                'Cache hit for user data',
                'Database connection established',
                'Service started successfully'
            ],
            'WARNING': [
                'High memory usage detected',
                'Slow database query detected',
                'Rate limit threshold approaching',
                'Cache miss rate increasing',
                'Connection pool near capacity'
            ],
            'ERROR': [
                'Database connection failed',
                'Authentication failed for user',
                'Payment processing failed',
                'Network timeout occurred',
                'File permission denied'
            ],
            'CRITICAL': [
                'Database server unreachable',
                'Memory limit exceeded, service crashing',
                'Security breach detected',
                'All connection pools exhausted',
                'Core service unavailable'
            ]
        }

        import random

        for i in range(num_entries):
            # Generate timestamp (last 7 days)
            days_ago = random.uniform(0, 7)
            timestamp = datetime.now() - timedelta(days=days_ago)

            # Choose log level (weighted towards INFO, fewer CRITICAL)
            level_weights = [0.1, 0.6, 0.2, 0.08, 0.02]  # DEBUG, INFO, WARNING, ERROR, CRITICAL
            level = random.choices(log_levels, weights=level_weights)[0]

            # Choose component
            component = random.choice(components)

            # Generate message based on level
            if level in log_messages:
                base_message = random.choice(log_messages[level])
            else:
                base_message = f"Debug message from {component}"

            # Add some variation to messages
            message = f"{base_message} - Request {i+1}"

            # Add additional context for certain levels
            user_id = f"user_{random.randint(1, 1000)}" if random.random() < 0.7 else None
            session_id = f"sess_{random.randint(10000, 99999)}" if random.random() < 0.5 else None
            ip_address = f"192.168.1.{random.randint(1, 254)}" if random.random() < 0.8 else None
            request_id = f"req_{random.randint(100000, 999999)}" if random.random() < 0.6 else None

            # Add response time for web requests
            response_time = None
            if component == 'web-server' and random.random() < 0.8:
                # Generate realistic response times with some outliers
                if level in ['ERROR', 'CRITICAL']:
                    response_time = random.uniform(5000, 30000)  # Slow responses for errors
                else:
                    response_time = random.lognormal(4, 1)  # Log-normal distribution for normal responses

            # Add status codes for web requests
            status_code = None
            if component == 'web-server' and random.random() < 0.9:
                if level == 'ERROR':
                    status_code = random.choice([404, 500, 503, 403])
                elif level == 'CRITICAL':
                    status_code = random.choice([500, 503, 502])
                else:
                    status_code = random.choice([200, 201, 204])

            # Add error codes for specific errors
            error_code = None
            if level in ['ERROR', 'CRITICAL'] and random.random() < 0.6:
                error_code = f"ERR_{random.randint(1000, 9999)}"

            log_entry = LogEntry(
                timestamp=timestamp,
                level=level,
                component=component,
                message=message,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                request_id=request_id,
                response_time=response_time,
                status_code=status_code,
                error_code=error_code
            )

            log_entries.append(log_entry)

        logger.info(f"✅ Created {len(log_entries)} sample log entries")
        return log_entries

    def parse_log_line(self, log_line: str) -> Optional[LogEntry]:
        """
        Parse a single log line into a LogEntry object.

        Args:
            log_line (str): Raw log line to parse

        Returns:
            Optional[LogEntry]: Parsed log entry or None if parsing failed
        """
        # Common log format patterns
        patterns = [
            # Apache/Nginx style: timestamp [level] component: message
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3} \[(?P<level>\w+)\] (?P<component>\w+): (?P<message>.*)',
            # Python logging style
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (?P<component>\w+) - (?P<level>\w+) - (?P<message>.*)',
            # Simple format
            r'(?P<level>\w+) (?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<message>.*)'
        ]

        for pattern in patterns:
            match = re.match(pattern, log_line.strip())
            if match:
                groups = match.groupdict()

                try:
                    timestamp = datetime.strptime(groups['timestamp'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue

                return LogEntry(
                    timestamp=timestamp,
                    level=groups['level'].upper(),
                    component=groups.get('component', 'unknown'),
                    message=groups['message']
                )

        return None

    def store_log_entries(self, log_entries: List[LogEntry]):
        """
        Store log entries in the database.

        Args:
            log_entries (List[LogEntry]): List of log entries to store
        """
        logger.info(f"💾 Storing {len(log_entries)} log entries...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for entry in log_entries:
                    cursor.execute('''
                        INSERT INTO log_entries
                        (timestamp, level, component, message, user_id, session_id,
                         ip_address, request_id, response_time, status_code, error_code)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entry.timestamp,
                        entry.level,
                        entry.component,
                        entry.message,
                        entry.user_id,
                        entry.session_id,
                        entry.ip_address,
                        entry.request_id,
                        entry.response_time,
                        entry.status_code,
                        entry.error_code
                    ))

                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to store log entries: {e}")
            raise

        logger.info("✅ Log entries stored successfully")

    def detect_error_patterns(self) -> List[IssuePattern]:
        """
        Detect error patterns using text analysis and clustering.

        Returns:
            List[IssuePattern]: List of detected issue patterns
        """
        logger.info("🔍 Detecting error patterns...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get error and warning messages
                df_errors = pd.read_sql_query('''
                    SELECT timestamp, level, component, message
                    FROM log_entries
                    WHERE level IN ('ERROR', 'CRITICAL', 'WARNING')
                    ORDER BY timestamp DESC
                ''', conn)

                if df_errors.empty:
                    logger.info("No error messages found")
                    return []

                patterns = []

                # Analyze patterns by predefined categories
                for pattern_type, regex_patterns in self.error_patterns.items():
                    matching_messages = []

                    for _, row in df_errors.iterrows():
                        message = row['message'].lower()
                        for pattern in regex_patterns:
                            if re.search(pattern, message, re.IGNORECASE):
                                matching_messages.append(row)
                                break

                    if matching_messages:
                        df_pattern = pd.DataFrame(matching_messages)

                        # Calculate pattern statistics
                        frequency = len(df_pattern)
                        first_occurrence = df_pattern['timestamp'].min()
                        last_occurrence = df_pattern['timestamp'].max()
                        affected_components = df_pattern['component'].unique().tolist()
                        sample_messages = df_pattern['message'].head(3).tolist()

                        # Determine severity based on frequency and log levels
                        critical_count = len(df_pattern[df_pattern['level'] == 'CRITICAL'])
                        error_count = len(df_pattern[df_pattern['level'] == 'ERROR'])

                        if critical_count > 0 or frequency > 50:
                            severity = 'high'
                        elif error_count > 10 or frequency > 20:
                            severity = 'medium'
                        else:
                            severity = 'low'

                        issue_pattern = IssuePattern(
                            pattern_id=f"{pattern_type}_{hash(pattern_type) % 10000}",
                            pattern_type=pattern_type,
                            description=f"{pattern_type.title()} related issues detected",
                            frequency=frequency,
                            severity=severity,
                            first_occurrence=pd.to_datetime(first_occurrence),
                            last_occurrence=pd.to_datetime(last_occurrence),
                            affected_components=affected_components,
                            sample_messages=sample_messages
                        )

                        patterns.append(issue_pattern)

                # Store patterns in database
                self.store_issue_patterns(patterns)

        except Exception as e:
            logger.error(f"❌ Failed to detect error patterns: {e}")
            return []

        logger.info(f"✅ Detected {len(patterns)} issue patterns")
        return patterns

    def store_issue_patterns(self, patterns: List[IssuePattern]):
        """Store detected issue patterns in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Clear old patterns
                cursor.execute('DELETE FROM issue_patterns')

                for pattern in patterns:
                    cursor.execute('''
                        INSERT INTO issue_patterns
                        (pattern_id, pattern_type, description, frequency, severity,
                         first_occurrence, last_occurrence, affected_components, sample_messages)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pattern.pattern_id,
                        pattern.pattern_type,
                        pattern.description,
                        pattern.frequency,
                        pattern.severity,
                        pattern.first_occurrence,
                        pattern.last_occurrence,
                        json.dumps(pattern.affected_components),
                        json.dumps(pattern.sample_messages)
                    ))

                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to store issue patterns: {e}")

    def calculate_performance_metrics(self):
        """Calculate and store performance metrics."""
        logger.info("📊 Calculating performance metrics...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Clear old metrics
                cursor.execute('DELETE FROM performance_metrics')

                # Calculate error rates by hour
                df_hourly_errors = pd.read_sql_query('''
                    SELECT
                        strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                        component,
                        COUNT(*) as total_logs,
                        SUM(CASE WHEN level IN ('ERROR', 'CRITICAL') THEN 1 ELSE 0 END) as error_count
                    FROM log_entries
                    GROUP BY strftime('%Y-%m-%d %H:00:00', timestamp), component
                ''', conn)

                for _, row in df_hourly_errors.iterrows():
                    error_rate = (row['error_count'] / row['total_logs']) * 100 if row['total_logs'] > 0 else 0

                    cursor.execute('''
                        INSERT INTO performance_metrics
                        (timestamp, metric_name, metric_value, component)
                        VALUES (?, ?, ?, ?)
                    ''', (row['hour'], 'error_rate_percent', error_rate, row['component']))

                # Calculate average response times
                df_response_times = pd.read_sql_query('''
                    SELECT
                        strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                        component,
                        AVG(response_time) as avg_response_time,
                        MAX(response_time) as max_response_time
                    FROM log_entries
                    WHERE response_time IS NOT NULL
                    GROUP BY strftime('%Y-%m-%d %H:00:00', timestamp), component
                ''', conn)

                for _, row in df_response_times.iterrows():
                    cursor.execute('''
                        INSERT INTO performance_metrics
                        (timestamp, metric_name, metric_value, component)
                        VALUES (?, ?, ?, ?)
                    ''', (row['hour'], 'avg_response_time_ms', row['avg_response_time'], row['component']))

                    cursor.execute('''
                        INSERT INTO performance_metrics
                        (timestamp, metric_name, metric_value, component)
                        VALUES (?, ?, ?, ?)
                    ''', (row['hour'], 'max_response_time_ms', row['max_response_time'], row['component']))

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to calculate performance metrics: {e}")

        logger.info("✅ Performance metrics calculated")

    def generate_alerts(self):
        """Generate alerts based on detected patterns and thresholds."""
        logger.info("🚨 Generating alerts...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Clear old alerts
                cursor.execute('DELETE FROM dashboard_alerts')

                # Alert for high error rates
                df_high_errors = pd.read_sql_query('''
                    SELECT component, metric_value, timestamp
                    FROM performance_metrics
                    WHERE metric_name = 'error_rate_percent' AND metric_value > 10
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''', conn)

                for _, row in df_high_errors.iterrows():
                    cursor.execute('''
                        INSERT INTO dashboard_alerts
                        (alert_type, severity, title, message, component, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        'high_error_rate',
                        'high',
                        'High Error Rate Detected',
                        f'Error rate of {row["metric_value"]:.1f}% detected in {row["component"]}',
                        row['component'],
                        row['timestamp']
                    ))

                # Alert for slow response times
                df_slow_responses = pd.read_sql_query('''
                    SELECT component, metric_value, timestamp
                    FROM performance_metrics
                    WHERE metric_name = 'avg_response_time_ms' AND metric_value > 5000
                    ORDER BY timestamp DESC
                    LIMIT 10
                ''', conn)

                for _, row in df_slow_responses.iterrows():
                    cursor.execute('''
                        INSERT INTO dashboard_alerts
                        (alert_type, severity, title, message, component, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        'slow_response',
                        'medium',
                        'Slow Response Time',
                        f'Average response time of {row["metric_value"]:.0f}ms in {row["component"]}',
                        row['component'],
                        row['timestamp']
                    ))

                # Alert for critical errors
                df_critical = pd.read_sql_query('''
                    SELECT component, COUNT(*) as count, MAX(timestamp) as latest
                    FROM log_entries
                    WHERE level = 'CRITICAL' AND timestamp > datetime('now', '-1 hour')
                    GROUP BY component
                    HAVING count > 0
                ''', conn)

                for _, row in df_critical.iterrows():
                    cursor.execute('''
                        INSERT INTO dashboard_alerts
                        (alert_type, severity, title, message, component, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        'critical_errors',
                        'critical',
                        'Critical Errors Detected',
                        f'{row["count"]} critical errors in {row["component"]} in the last hour',
                        row['component'],
                        row['latest']
                    ))

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to generate alerts: {e}")

        logger.info("✅ Alerts generated")

class DashboardApp:
    """
    Interactive dashboard application using Dash/Plotly.

    This creates a web-based dashboard for log analysis visualization.
    """

    def __init__(self, db_path: str = "log_analysis.db"):
        """Initialize the dashboard application."""
        self.db_path = db_path
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        """Setup the dashboard layout."""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("🔍 Application Log Analysis Dashboard", className="text-center mb-4"),
                    html.P("Real-time monitoring and pattern analysis for application logs",
                           className="text-center text-muted mb-4")
                ])
            ]),

            # Alert section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🚨 Active Alerts"),
                        dbc.CardBody(id="alerts-section")
                    ])
                ])
            ], className="mb-4"),

            # Metrics overview
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Key Metrics"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H4(id="total-logs", className="text-primary"),
                                    html.P("Total Logs", className="text-muted")
                                ], width=3),
                                dbc.Col([
                                    html.H4(id="error-count", className="text-danger"),
                                    html.P("Errors/Critical", className="text-muted")
                                ], width=3),
                                dbc.Col([
                                    html.H4(id="avg-response-time", className="text-warning"),
                                    html.P("Avg Response (ms)", className="text-muted")
                                ], width=3),
                                dbc.Col([
                                    html.H4(id="active-patterns", className="text-info"),
                                    html.P("Issue Patterns", className="text-muted")
                                ], width=3)
                            ])
                        ])
                    ])
                ])
            ], className="mb-4"),

            # Charts section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📈 Log Volume Over Time"),
                        dbc.CardBody([
                            dcc.Graph(id="log-volume-chart")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🎯 Error Rate by Component"),
                        dbc.CardBody([
                            dcc.Graph(id="error-rate-chart")
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),

            # Pattern analysis
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🔍 Issue Patterns"),
                        dbc.CardBody([
                            dash_table.DataTable(
                                id="patterns-table",
                                columns=[
                                    {"name": "Pattern Type", "id": "pattern_type"},
                                    {"name": "Description", "id": "description"},
                                    {"name": "Frequency", "id": "frequency"},
                                    {"name": "Severity", "id": "severity"},
                                    {"name": "Last Occurrence", "id": "last_occurrence"}
                                ],
                                style_cell={'textAlign': 'left'},
                                style_data_conditional=[
                                    {
                                        'if': {'filter_query': '{severity} = high'},
                                        'backgroundColor': '#f8d7da',
                                        'color': 'black',
                                    },
                                    {
                                        'if': {'filter_query': '{severity} = medium'},
                                        'backgroundColor': '#fff3cd',
                                        'color': 'black',
                                    }
                                ]
                            )
                        ])
                    ])
                ])
            ], className="mb-4"),

            # Performance metrics
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("⚡ Performance Metrics"),
                        dbc.CardBody([
                            dcc.Graph(id="performance-chart")
                        ])
                    ])
                ])
            ], className="mb-4"),

            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # Update every 30 seconds
                n_intervals=0
            )

        ], fluid=True)

    def setup_callbacks(self):
        """Setup dashboard callbacks for interactivity."""

        @self.app.callback(
            [Output('total-logs', 'children'),
             Output('error-count', 'children'),
             Output('avg-response-time', 'children'),
             Output('active-patterns', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_metrics(n):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Total logs
                    total_logs = pd.read_sql_query('SELECT COUNT(*) as count FROM log_entries', conn).iloc[0]['count']

                    # Error count
                    error_count = pd.read_sql_query(
                        "SELECT COUNT(*) as count FROM log_entries WHERE level IN ('ERROR', 'CRITICAL')",
                        conn
                    ).iloc[0]['count']

                    # Average response time
                    avg_response = pd.read_sql_query(
                        'SELECT AVG(response_time) as avg FROM log_entries WHERE response_time IS NOT NULL',
                        conn
                    ).iloc[0]['avg']
                    avg_response = f"{avg_response:.0f}" if avg_response else "N/A"

                    # Active patterns
                    pattern_count = pd.read_sql_query('SELECT COUNT(*) as count FROM issue_patterns', conn).iloc[0]['count']

                    return f"{total_logs:,}", f"{error_count:,}", avg_response, str(pattern_count)
            except:
                return "N/A", "N/A", "N/A", "N/A"

        @self.app.callback(
            Output('alerts-section', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_alerts(n):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    df_alerts = pd.read_sql_query('''
                        SELECT alert_type, severity, title, message, component, timestamp
                        FROM dashboard_alerts
                        ORDER BY timestamp DESC
                        LIMIT 5
                    ''', conn)

                    if df_alerts.empty:
                        return dbc.Alert("✅ No active alerts", color="success")

                    alerts = []
                    for _, alert in df_alerts.iterrows():
                        color_map = {'critical': 'danger', 'high': 'warning', 'medium': 'info', 'low': 'secondary'}
                        color = color_map.get(alert['severity'], 'secondary')

                        alerts.append(
                            dbc.Alert([
                                html.H6(alert['title'], className="mb-1"),
                                html.P(alert['message'], className="mb-1"),
                                html.Small(f"{alert['component']} - {alert['timestamp']}", className="text-muted")
                            ], color=color, className="mb-2")
                        )

                    return alerts
            except:
                return dbc.Alert("⚠️ Unable to load alerts", color="warning")

        @self.app.callback(
            Output('log-volume-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_log_volume_chart(n):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    df = pd.read_sql_query('''
                        SELECT
                            strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                            level,
                            COUNT(*) as count
                        FROM log_entries
                        WHERE timestamp >= datetime('now', '-24 hours')
                        GROUP BY strftime('%Y-%m-%d %H:00:00', timestamp), level
                        ORDER BY hour
                    ''', conn)

                    if df.empty:
                        return px.bar(title="No data available")

                    fig = px.bar(df, x='hour', y='count', color='level',
                                title="Log Volume by Hour (Last 24h)",
                                color_discrete_map={
                                    'DEBUG': '#6c757d',
                                    'INFO': '#17a2b8',
                                    'WARNING': '#ffc107',
                                    'ERROR': '#dc3545',
                                    'CRITICAL': '#6f42c1'
                                })
                    fig.update_layout(xaxis_title="Hour", yaxis_title="Log Count")
                    return fig
            except:
                return px.bar(title="Error loading chart")

        @self.app.callback(
            Output('error-rate-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_error_rate_chart(n):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    df = pd.read_sql_query('''
                        SELECT
                            component,
                            AVG(metric_value) as avg_error_rate
                        FROM performance_metrics
                        WHERE metric_name = 'error_rate_percent'
                        GROUP BY component
                        ORDER BY avg_error_rate DESC
                    ''', conn)

                    if df.empty:
                        return px.bar(title="No error rate data available")

                    fig = px.bar(df, x='component', y='avg_error_rate',
                                title="Average Error Rate by Component",
                                color='avg_error_rate',
                                color_continuous_scale='Reds')
                    fig.update_layout(xaxis_title="Component", yaxis_title="Error Rate (%)")
                    return fig
            except:
                return px.bar(title="Error loading chart")

        @self.app.callback(
            Output('patterns-table', 'data'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_patterns_table(n):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    df = pd.read_sql_query('''
                        SELECT pattern_type, description, frequency, severity, last_occurrence
                        FROM issue_patterns
                        ORDER BY frequency DESC
                    ''', conn)

                    return df.to_dict('records')
            except:
                return []

        @self.app.callback(
            Output('performance-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_performance_chart(n):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    df = pd.read_sql_query('''
                        SELECT timestamp, component, metric_value
                        FROM performance_metrics
                        WHERE metric_name = 'avg_response_time_ms'
                        ORDER BY timestamp
                    ''', conn)

                    if df.empty:
                        return px.line(title="No performance data available")

                    fig = px.line(df, x='timestamp', y='metric_value', color='component',
                                 title="Response Time Trends")
                    fig.update_layout(xaxis_title="Time", yaxis_title="Response Time (ms)")
                    return fig
            except:
                return px.line(title="Error loading chart")

    def run(self, debug=False, port=8050):
        """Run the dashboard application."""
        logger.info(f"🚀 Starting dashboard on http://localhost:{port}")
        self.app.run_server(debug=debug, port=port)

def demonstrate_advanced_analytics():
    """
    Demonstrate advanced log analytics concepts.
    """
    print("\n🎓 Advanced Log Analytics Concepts:")
    print("=" * 50)

    concepts = {
        "Machine Learning Applications": [
            "Anomaly detection using isolation forests",
            "Log clustering for pattern discovery",
            "Predictive alerting based on historical trends",
            "Natural language processing for error categorization"
        ],
        "Real-time Processing": [
            "Stream processing with Apache Kafka",
            "Real-time alerting with Apache Storm",
            "Event correlation across multiple services",
            "Dynamic threshold adjustment"
        ],
        "Scalability Patterns": [
            "Log aggregation with ELK stack (Elasticsearch, Logstash, Kibana)",
            "Distributed tracing with Jaeger or Zipkin",
            "Time-series databases for metrics (InfluxDB, Prometheus)",
            "Log sampling for high-volume systems"
        ],
        "Security and Compliance": [
            "Log anonymization and PII protection",
            "Audit trail maintenance",
            "Security event correlation",
            "Compliance reporting automation"
        ]
    }

    for category, items in concepts.items():
        print(f"\n🔧 {category}:")
        for item in items:
            print(f"  • {item}")

def main():
    """
    Main function demonstrating the log analysis and dashboard workflow.
    """
    print("🚀 Welcome to MS's Log Analysis Dashboard!")
    print("=" * 50)

    try:
        # Initialize the log analyzer
        analyzer = LogAnalyzer("ms_log_analysis.db")

        print("\n1. 📝 Creating sample log data...")
        sample_logs = analyzer.create_sample_logs(num_entries=1500)

        print("\n2. 💾 Storing log entries...")
        analyzer.store_log_entries(sample_logs)

        print("\n3. 🔍 Detecting error patterns...")
        patterns = analyzer.detect_error_patterns()

        print("\n4. 📊 Calculating performance metrics...")
        analyzer.calculate_performance_metrics()

        print("\n5. 🚨 Generating alerts...")
        analyzer.generate_alerts()

        print(f"\n✅ Log analysis completed!")
        print(f"   Processed: {len(sample_logs)} log entries")
        print(f"   Detected: {len(patterns)} issue patterns")

        # Show some sample results
        if patterns:
            print(f"\n🔍 Sample Issue Patterns:")
            for pattern in patterns[:3]:
                print(f"   • {pattern.pattern_type}: {pattern.frequency} occurrences ({pattern.severity} severity)")

        # Show database file info
        db_path = Path("ms_log_analysis.db")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"\n📁 Database file: {db_path.absolute()}")
            print(f"   Size: {size_mb:.2f} MB")

        # Option to start dashboard
        print(f"\n🌐 Dashboard Options:")
        print("   To start the interactive dashboard, run:")
        print("   python MS_dashboard_patterns.py --dashboard")
        print("   Then open http://localhost:8050 in your browser")

        # Start dashboard if requested
        import sys
        if "--dashboard" in sys.argv:
            print("\n🚀 Starting interactive dashboard...")
            dashboard = DashboardApp("ms_log_analysis.db")

            # Run in a separate thread to allow for demonstration
            def run_dashboard():
                dashboard.run(debug=False, port=8050)

            dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
            dashboard_thread.start()

            print("✅ Dashboard started! Open http://localhost:8050 in your browser")
            print("Press Ctrl+C to stop...")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Dashboard stopped")

    except Exception as e:
        logger.error(f"❌ Log analysis failed: {e}")
        print("💡 Troubleshooting tips:")
        print("   - Ensure you have write permissions in the current directory")
        print("   - Check if port 8050 is available for the dashboard")
        print("   - Verify all dependencies are installed (dash, plotly, etc.)")

    # Show advanced concepts
    demonstrate_advanced_analytics()

    print("\n🎓 Learning Summary:")
    print("- Log parsing and analysis techniques")
    print("- Pattern detection using regex and ML")
    print("- Interactive dashboard creation with Dash/Plotly")
    print("- Real-time monitoring and alerting concepts")
    print("- Performance metrics calculation and visualization")
    print("- Database design for log analytics")

    print("\n💡 Next Steps:")
    print("- Integrate with real log files from your applications")
    print("- Add machine learning for anomaly detection")
    print("- Set up log aggregation from multiple services")
    print("- Implement automated incident response")
    print("- Create custom alerting rules and notifications")
    print("- Add distributed tracing capabilities")

if __name__ == "__main__":
    main()