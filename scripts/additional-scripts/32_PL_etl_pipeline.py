#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas",
#     "sqlite3",
#     "numpy",
#     "python-dotenv",
#     "sqlalchemy",
#     "openpyxl",
# ]
# ///

"""
PL_etl_automation.py - ETL Automation Scripts

Student: PL (Initials)
Request: "like ETL automation scripts"

This script demonstrates comprehensive ETL (Extract, Transform, Load) automation patterns.
It shows how to extract data from various sources, transform it according to business rules,
and load it into different target systems.

Educational Focus:
- ETL pipeline design and implementation
- Data extraction from multiple sources (CSV, Excel, JSON, APIs)
- Data transformation and cleaning techniques
- Data validation and quality checks
- Loading data into databases and other targets
- Error handling and logging in ETL processes
- Scheduling and monitoring ETL jobs

Prerequisites:
- Sample data files (will be created automatically)
- SQLite for database operations
- Pandas for data manipulation
"""

import pandas as pd
import sqlite3
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re
from dotenv import load_dotenv
import os
import shutil

# Load environment variables
load_dotenv()

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ETLConfig:
    """
    Configuration class for ETL operations.

    This centralizes all ETL settings and makes the pipeline configurable.
    """
    source_directory: str = "etl_sources"
    staging_directory: str = "etl_staging"
    archive_directory: str = "etl_archive"
    output_directory: str = "etl_output"
    database_path: str = "etl_data.db"
    batch_size: int = 1000
    error_threshold: float = 0.05  # 5% error threshold
    data_retention_days: int = 30

class DataQualityValidator:
    """
    Class for validating data quality during ETL processes.

    This demonstrates professional data quality practices.
    """

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email))) if pd.notna(email) else False

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if pd.isna(phone):
            return False
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone))
        # Check if it has 10-15 digits (international format)
        return 10 <= len(digits) <= 15

    @staticmethod
    def validate_date(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
        """Validate date format."""
        if pd.isna(date_str):
            return False
        try:
            datetime.strptime(str(date_str), date_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def check_data_completeness(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, float]:
        """Check data completeness for required columns."""
        completeness = {}
        for col in required_columns:
            if col in df.columns:
                completeness[col] = (df[col].notna().sum() / len(df)) * 100
            else:
                completeness[col] = 0.0
        return completeness

    @staticmethod
    def detect_duplicates(df: pd.DataFrame, key_columns: List[str]) -> pd.DataFrame:
        """Detect duplicate records based on key columns."""
        if all(col in df.columns for col in key_columns):
            return df[df.duplicated(subset=key_columns, keep=False)]
        return pd.DataFrame()

class ETLPipeline:
    """
    Comprehensive ETL pipeline implementation.

    This class demonstrates professional ETL patterns including:
    - Modular design
    - Error handling
    - Data quality validation
    - Logging and monitoring
    - Incremental loading
    """

    def __init__(self, config: ETLConfig):
        """
        Initialize the ETL pipeline.

        Args:
            config (ETLConfig): ETL configuration settings
        """
        self.config = config
        self.validator = DataQualityValidator()
        self.setup_directories()
        self.setup_database()

        # Track ETL metrics
        self.metrics = {
            'records_extracted': 0,
            'records_transformed': 0,
            'records_loaded': 0,
            'errors_count': 0,
            'start_time': None,
            'end_time': None
        }

    def setup_directories(self):
        """Create necessary directories for ETL operations."""
        directories = [
            self.config.source_directory,
            self.config.staging_directory,
            self.config.archive_directory,
            self.config.output_directory
        ]

        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"📁 Directory ready: {directory}")

    def setup_database(self):
        """Initialize the target database with necessary tables."""
        logger.info("🗄️ Setting up target database...")

        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()

                # ETL job tracking table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS etl_job_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_name TEXT NOT NULL,
                        start_time DATETIME,
                        end_time DATETIME,
                        status TEXT,
                        records_processed INTEGER,
                        errors_count INTEGER,
                        error_details TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Customer data table (example target)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id TEXT UNIQUE NOT NULL,
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT,
                        phone TEXT,
                        address TEXT,
                        city TEXT,
                        state TEXT,
                        zip_code TEXT,
                        country TEXT,
                        registration_date DATE,
                        last_purchase_date DATE,
                        total_purchases DECIMAL(10,2),
                        customer_segment TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Sales data table (example target)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_id TEXT UNIQUE NOT NULL,
                        customer_id TEXT,
                        product_id TEXT,
                        product_name TEXT,
                        category TEXT,
                        quantity INTEGER,
                        unit_price DECIMAL(10,2),
                        total_amount DECIMAL(10,2),
                        discount_amount DECIMAL(10,2),
                        tax_amount DECIMAL(10,2),
                        sale_date DATE,
                        sales_rep TEXT,
                        region TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                    )
                ''')

                # Data quality issues table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS data_quality_issues (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_name TEXT,
                        table_name TEXT,
                        issue_type TEXT,
                        issue_description TEXT,
                        record_id TEXT,
                        field_name TEXT,
                        field_value TEXT,
                        severity TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("✅ Database setup completed")

        except sqlite3.Error as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise

    def create_sample_data(self):
        """
        Create sample data files for demonstration.

        In a real ETL pipeline, this data would come from external systems.
        """
        logger.info("📊 Creating sample data files...")

        # Create sample customer data (CSV)
        customer_data = []
        for i in range(1000):
            customer = {
                'customer_id': f'CUST{i+1:06d}',
                'first_name': np.random.choice(['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Chris', 'Amy']),
                'last_name': np.random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']),
                'email': f'customer{i+1}@email.com',
                'phone': f'+1-555-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}',
                'address': f'{np.random.randint(1, 9999)} Main St',
                'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia']),
                'state': np.random.choice(['NY', 'CA', 'IL', 'TX', 'AZ', 'PA']),
                'zip_code': f'{np.random.randint(10000, 99999)}',
                'country': 'USA',
                'registration_date': (datetime.now() - timedelta(days=np.random.randint(1, 365))).strftime('%Y-%m-%d'),
                'total_purchases': round(np.random.uniform(100, 5000), 2),
                'customer_segment': np.random.choice(['Premium', 'Standard', 'Basic'])
            }

            # Introduce some data quality issues for demonstration
            if np.random.random() < 0.05:  # 5% bad email addresses
                customer['email'] = 'invalid-email'
            if np.random.random() < 0.03:  # 3% missing phone numbers
                customer['phone'] = ''
            if np.random.random() < 0.02:  # 2% invalid dates
                customer['registration_date'] = 'invalid-date'

            customer_data.append(customer)

        df_customers = pd.DataFrame(customer_data)
        customer_file = Path(self.config.source_directory) / 'customers.csv'
        df_customers.to_csv(customer_file, index=False)
        logger.info(f"✅ Created customer data: {customer_file}")

        # Create sample sales data (Excel)
        sales_data = []
        for i in range(2000):
            sale = {
                'transaction_id': f'TXN{i+1:08d}',
                'customer_id': f'CUST{np.random.randint(1, 1001):06d}',
                'product_id': f'PROD{np.random.randint(1, 101):04d}',
                'product_name': np.random.choice(['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Tablet', 'Phone', 'Headphones']),
                'category': np.random.choice(['Electronics', 'Accessories', 'Computers']),
                'quantity': np.random.randint(1, 5),
                'unit_price': round(np.random.uniform(10, 1000), 2),
                'discount_amount': round(np.random.uniform(0, 50), 2),
                'tax_amount': round(np.random.uniform(5, 100), 2),
                'sale_date': (datetime.now() - timedelta(days=np.random.randint(1, 90))).strftime('%Y-%m-%d'),
                'sales_rep': np.random.choice(['Alice Johnson', 'Bob Smith', 'Carol Brown', 'David Wilson']),
                'region': np.random.choice(['North', 'South', 'East', 'West'])
            }

            # Calculate total amount
            sale['total_amount'] = round(
                (sale['unit_price'] * sale['quantity']) - sale['discount_amount'] + sale['tax_amount'], 2
            )

            # Introduce some data quality issues
            if np.random.random() < 0.01:  # 1% negative quantities
                sale['quantity'] = -1
            if np.random.random() < 0.02:  # 2% missing product names
                sale['product_name'] = ''

            sales_data.append(sale)

        df_sales = pd.DataFrame(sales_data)
        sales_file = Path(self.config.source_directory) / 'sales.xlsx'
        df_sales.to_excel(sales_file, index=False)
        logger.info(f"✅ Created sales data: {sales_file}")

        # Create sample JSON data
        json_data = {
            'metadata': {
                'source': 'external_api',
                'extraction_date': datetime.now().isoformat(),
                'version': '1.0'
            },
            'customer_updates': [
                {
                    'customer_id': f'CUST{i+1:06d}',
                    'last_purchase_date': (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime('%Y-%m-%d'),
                    'updated_segment': np.random.choice(['Premium', 'Standard', 'Basic'])
                }
                for i in range(100)
            ]
        }

        json_file = Path(self.config.source_directory) / 'customer_updates.json'
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"✅ Created JSON data: {json_file}")

    def extract_csv_data(self, file_path: Path) -> pd.DataFrame:
        """
        Extract data from CSV files with error handling.

        Args:
            file_path (Path): Path to the CSV file

        Returns:
            pd.DataFrame: Extracted data
        """
        logger.info(f"📤 Extracting data from CSV: {file_path}")

        try:
            # Read CSV with error handling
            df = pd.read_csv(file_path, encoding='utf-8')

            # Log extraction metrics
            self.metrics['records_extracted'] += len(df)
            logger.info(f"✅ Extracted {len(df)} records from {file_path.name}")

            return df

        except Exception as e:
            logger.error(f"❌ Failed to extract data from {file_path}: {e}")
            self.metrics['errors_count'] += 1
            return pd.DataFrame()

    def extract_excel_data(self, file_path: Path, sheet_name: str = None) -> pd.DataFrame:
        """
        Extract data from Excel files.

        Args:
            file_path (Path): Path to the Excel file
            sheet_name (str): Specific sheet to read

        Returns:
            pd.DataFrame: Extracted data
        """
        logger.info(f"📤 Extracting data from Excel: {file_path}")

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            self.metrics['records_extracted'] += len(df)
            logger.info(f"✅ Extracted {len(df)} records from {file_path.name}")

            return df

        except Exception as e:
            logger.error(f"❌ Failed to extract data from {file_path}: {e}")
            self.metrics['errors_count'] += 1
            return pd.DataFrame()

    def extract_json_data(self, file_path: Path) -> Dict:
        """
        Extract data from JSON files.

        Args:
            file_path (Path): Path to the JSON file

        Returns:
            Dict: Extracted JSON data
        """
        logger.info(f"📤 Extracting data from JSON: {file_path}")

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            logger.info(f"✅ Extracted JSON data from {file_path.name}")
            return data

        except Exception as e:
            logger.error(f"❌ Failed to extract data from {file_path}: {e}")
            self.metrics['errors_count'] += 1
            return {}

    def transform_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform customer data according to business rules.

        Args:
            df (pd.DataFrame): Raw customer data

        Returns:
            pd.DataFrame: Transformed customer data
        """
        logger.info("🔄 Transforming customer data...")

        if df.empty:
            return df

        df_transformed = df.copy()

        # Data cleaning and standardization
        # 1. Standardize names (title case)
        df_transformed['first_name'] = df_transformed['first_name'].str.title()
        df_transformed['last_name'] = df_transformed['last_name'].str.title()

        # 2. Clean and validate email addresses
        df_transformed['email_valid'] = df_transformed['email'].apply(self.validator.validate_email)
        df_transformed.loc[~df_transformed['email_valid'], 'email'] = None

        # 3. Clean and validate phone numbers
        df_transformed['phone_valid'] = df_transformed['phone'].apply(self.validator.validate_phone)
        df_transformed.loc[~df_transformed['phone_valid'], 'phone'] = None

        # 4. Validate registration dates
        df_transformed['date_valid'] = df_transformed['registration_date'].apply(
            lambda x: self.validator.validate_date(x)
        )
        df_transformed.loc[~df_transformed['date_valid'], 'registration_date'] = None

        # 5. Standardize state codes
        df_transformed['state'] = df_transformed['state'].str.upper()

        # 6. Clean zip codes (remove any non-numeric characters)
        df_transformed['zip_code'] = df_transformed['zip_code'].astype(str).str.replace(r'\D', '', regex=True)

        # 7. Set active status based on recent activity
        df_transformed['registration_date_parsed'] = pd.to_datetime(
            df_transformed['registration_date'], errors='coerce'
        )
        cutoff_date = datetime.now() - timedelta(days=365)
        df_transformed['is_active'] = df_transformed['registration_date_parsed'] > cutoff_date

        # 8. Create derived fields
        df_transformed['full_name'] = (
            df_transformed['first_name'].fillna('') + ' ' + df_transformed['last_name'].fillna('')
        ).str.strip()

        # 9. Categorize customers by purchase amount
        df_transformed['purchase_category'] = pd.cut(
            df_transformed['total_purchases'],
            bins=[0, 500, 1500, float('inf')],
            labels=['Low', 'Medium', 'High']
        )

        # Remove validation helper columns
        columns_to_drop = ['email_valid', 'phone_valid', 'date_valid', 'registration_date_parsed']
        df_transformed = df_transformed.drop(columns=columns_to_drop, errors='ignore')

        self.metrics['records_transformed'] += len(df_transformed)
        logger.info(f"✅ Transformed {len(df_transformed)} customer records")

        return df_transformed

    def transform_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform sales data according to business rules.

        Args:
            df (pd.DataFrame): Raw sales data

        Returns:
            pd.DataFrame: Transformed sales data
        """
        logger.info("🔄 Transforming sales data...")

        if df.empty:
            return df

        df_transformed = df.copy()

        # Data cleaning and validation
        # 1. Ensure positive quantities
        df_transformed.loc[df_transformed['quantity'] <= 0, 'quantity'] = 1

        # 2. Ensure positive prices
        df_transformed.loc[df_transformed['unit_price'] <= 0, 'unit_price'] = 0.01

        # 3. Recalculate total amount to ensure consistency
        df_transformed['calculated_total'] = (
            (df_transformed['unit_price'] * df_transformed['quantity']) -
            df_transformed['discount_amount'] +
            df_transformed['tax_amount']
        ).round(2)

        # Flag discrepancies
        df_transformed['amount_discrepancy'] = abs(
            df_transformed['total_amount'] - df_transformed['calculated_total']
        ) > 0.01

        # Use calculated total for consistency
        df_transformed['total_amount'] = df_transformed['calculated_total']

        # 4. Standardize product names
        df_transformed['product_name'] = df_transformed['product_name'].str.title()

        # 5. Validate and convert sale dates
        df_transformed['sale_date_parsed'] = pd.to_datetime(
            df_transformed['sale_date'], errors='coerce'
        )

        # 6. Create derived fields
        df_transformed['profit_margin'] = (
            (df_transformed['total_amount'] - df_transformed['discount_amount']) /
            df_transformed['total_amount'] * 100
        ).round(2)

        # 7. Categorize sales by amount
        df_transformed['sale_category'] = pd.cut(
            df_transformed['total_amount'],
            bins=[0, 100, 500, 1000, float('inf')],
            labels=['Small', 'Medium', 'Large', 'Enterprise']
        )

        # 8. Add time-based features
        df_transformed['sale_month'] = df_transformed['sale_date_parsed'].dt.month
        df_transformed['sale_quarter'] = df_transformed['sale_date_parsed'].dt.quarter
        df_transformed['sale_year'] = df_transformed['sale_date_parsed'].dt.year

        # Remove helper columns
        df_transformed = df_transformed.drop(columns=['calculated_total', 'sale_date_parsed'], errors='ignore')

        self.metrics['records_transformed'] += len(df_transformed)
        logger.info(f"✅ Transformed {len(df_transformed)} sales records")

        return df_transformed

    def validate_data_quality(self, df: pd.DataFrame, table_name: str, required_fields: List[str]) -> List[Dict]:
        """
        Validate data quality and log issues.

        Args:
            df (pd.DataFrame): Data to validate
            table_name (str): Name of the target table
            required_fields (List[str]): List of required fields

        Returns:
            List[Dict]: List of data quality issues
        """
        logger.info(f"🔍 Validating data quality for {table_name}...")

        issues = []

        # Check completeness
        completeness = self.validator.check_data_completeness(df, required_fields)
        for field, percentage in completeness.items():
            if percentage < 95:  # Less than 95% complete
                issues.append({
                    'job_name': f'{table_name}_etl',
                    'table_name': table_name,
                    'issue_type': 'completeness',
                    'issue_description': f'Field {field} is only {percentage:.1f}% complete',
                    'field_name': field,
                    'severity': 'high' if percentage < 80 else 'medium'
                })

        # Check for duplicates
        if table_name == 'customers':
            duplicates = self.validator.detect_duplicates(df, ['customer_id'])
            if not duplicates.empty:
                issues.append({
                    'job_name': f'{table_name}_etl',
                    'table_name': table_name,
                    'issue_type': 'duplicates',
                    'issue_description': f'Found {len(duplicates)} duplicate customer IDs',
                    'field_name': 'customer_id',
                    'severity': 'high'
                })

        elif table_name == 'sales':
            duplicates = self.validator.detect_duplicates(df, ['transaction_id'])
            if not duplicates.empty:
                issues.append({
                    'job_name': f'{table_name}_etl',
                    'table_name': table_name,
                    'issue_type': 'duplicates',
                    'issue_description': f'Found {len(duplicates)} duplicate transaction IDs',
                    'field_name': 'transaction_id',
                    'severity': 'high'
                })

        # Log issues to database
        if issues:
            self.log_data_quality_issues(issues)

        logger.info(f"✅ Data quality validation completed. Found {len(issues)} issues.")
        return issues

    def log_data_quality_issues(self, issues: List[Dict]):
        """Log data quality issues to the database."""
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                for issue in issues:
                    cursor.execute('''
                        INSERT INTO data_quality_issues
                        (job_name, table_name, issue_type, issue_description,
                         field_name, severity)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        issue['job_name'],
                        issue['table_name'],
                        issue['issue_type'],
                        issue['issue_description'],
                        issue.get('field_name'),
                        issue['severity']
                    ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to log data quality issues: {e}")

    def load_data_to_database(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append') -> bool:
        """
        Load transformed data into the target database.

        Args:
            df (pd.DataFrame): Data to load
            table_name (str): Target table name
            if_exists (str): What to do if table exists ('append', 'replace', 'fail')

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"📥 Loading {len(df)} records to {table_name}...")

        if df.empty:
            logger.warning(f"⚠️ No data to load for {table_name}")
            return True

        try:
            with sqlite3.connect(self.config.database_path) as conn:
                # Load data in batches to avoid memory issues
                batch_size = self.config.batch_size
                total_batches = (len(df) + batch_size - 1) // batch_size

                for i in range(0, len(df), batch_size):
                    batch_df = df.iloc[i:i + batch_size]
                    batch_num = (i // batch_size) + 1

                    logger.info(f"  Loading batch {batch_num}/{total_batches} ({len(batch_df)} records)")

                    batch_df.to_sql(
                        table_name,
                        conn,
                        if_exists=if_exists if i == 0 else 'append',
                        index=False,
                        method='multi'
                    )

                self.metrics['records_loaded'] += len(df)
                logger.info(f"✅ Successfully loaded {len(df)} records to {table_name}")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to load data to {table_name}: {e}")
            self.metrics['errors_count'] += 1
            return False

    def archive_processed_files(self, file_paths: List[Path]):
        """
        Archive processed files with timestamp.

        Args:
            file_paths (List[Path]): List of files to archive
        """
        logger.info("📦 Archiving processed files...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for file_path in file_paths:
            if file_path.exists():
                archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
                archive_path = Path(self.config.archive_directory) / archive_name

                try:
                    shutil.move(str(file_path), str(archive_path))
                    logger.info(f"📦 Archived: {file_path.name} -> {archive_path.name}")
                except Exception as e:
                    logger.error(f"❌ Failed to archive {file_path.name}: {e}")

    def log_etl_job(self, job_name: str, status: str):
        """
        Log ETL job execution details.

        Args:
            job_name (str): Name of the ETL job
            status (str): Job status (success, failed, warning)
        """
        try:
            with sqlite3.connect(self.config.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO etl_job_log
                    (job_name, start_time, end_time, status, records_processed, errors_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    job_name,
                    self.metrics['start_time'],
                    self.metrics['end_time'],
                    status,
                    self.metrics['records_loaded'],
                    self.metrics['errors_count']
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to log ETL job: {e}")

    def run_customer_etl(self):
        """Run the complete customer data ETL pipeline."""
        logger.info("🚀 Starting customer ETL pipeline...")

        # Extract
        customer_file = Path(self.config.source_directory) / 'customers.csv'
        df_customers = self.extract_csv_data(customer_file)

        if not df_customers.empty:
            # Transform
            df_transformed = self.transform_customer_data(df_customers)

            # Validate
            required_fields = ['customer_id', 'first_name', 'last_name', 'email']
            self.validate_data_quality(df_transformed, 'customers', required_fields)

            # Load
            success = self.load_data_to_database(df_transformed, 'customers', 'replace')

            if success:
                # Archive processed file
                self.archive_processed_files([customer_file])
                logger.info("✅ Customer ETL pipeline completed successfully")
                return True
            else:
                logger.error("❌ Customer ETL pipeline failed during load phase")
                return False
        else:
            logger.error("❌ Customer ETL pipeline failed - no data extracted")
            return False

    def run_sales_etl(self):
        """Run the complete sales data ETL pipeline."""
        logger.info("🚀 Starting sales ETL pipeline...")

        # Extract
        sales_file = Path(self.config.source_directory) / 'sales.xlsx'
        df_sales = self.extract_excel_data(sales_file)

        if not df_sales.empty:
            # Transform
            df_transformed = self.transform_sales_data(df_sales)

            # Validate
            required_fields = ['transaction_id', 'customer_id', 'product_name', 'quantity', 'unit_price']
            self.validate_data_quality(df_transformed, 'sales', required_fields)

            # Load
            success = self.load_data_to_database(df_transformed, 'sales', 'replace')

            if success:
                # Archive processed file
                self.archive_processed_files([sales_file])
                logger.info("✅ Sales ETL pipeline completed successfully")
                return True
            else:
                logger.error("❌ Sales ETL pipeline failed during load phase")
                return False
        else:
            logger.error("❌ Sales ETL pipeline failed - no data extracted")
            return False

    def run_incremental_update(self):
        """Run incremental updates from JSON data."""
        logger.info("🚀 Starting incremental update pipeline...")

        # Extract JSON data
        json_file = Path(self.config.source_directory) / 'customer_updates.json'
        json_data = self.extract_json_data(json_file)

        if json_data and 'customer_updates' in json_data:
            updates = json_data['customer_updates']
            logger.info(f"Processing {len(updates)} customer updates...")

            try:
                with sqlite3.connect(self.config.database_path) as conn:
                    cursor = conn.cursor()

                    for update in updates:
                        cursor.execute('''
                            UPDATE customers
                            SET last_purchase_date = ?, customer_segment = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE customer_id = ?
                        ''', (
                            update['last_purchase_date'],
                            update['updated_segment'],
                            update['customer_id']
                        ))

                    conn.commit()
                    logger.info(f"✅ Applied {len(updates)} incremental updates")

                    # Archive processed file
                    self.archive_processed_files([json_file])
                    return True

            except sqlite3.Error as e:
                logger.error(f"❌ Incremental update failed: {e}")
                return False
        else:
            logger.error("❌ No update data found in JSON file")
            return False

    def generate_etl_report(self):
        """Generate a comprehensive ETL execution report."""
        logger.info("📊 Generating ETL report...")

        try:
            with sqlite3.connect(self.config.database_path) as conn:
                # Get job summary
                df_jobs = pd.read_sql_query('''
                    SELECT job_name, status, records_processed, errors_count,
                           start_time, end_time
                    FROM etl_job_log
                    ORDER BY start_time DESC
                    LIMIT 10
                ''', conn)

                # Get data quality issues
                df_issues = pd.read_sql_query('''
                    SELECT table_name, issue_type, severity, COUNT(*) as count
                    FROM data_quality_issues
                    WHERE created_at >= datetime('now', '-1 day')
                    GROUP BY table_name, issue_type, severity
                ''', conn)

                # Get record counts
                customer_count = pd.read_sql_query('SELECT COUNT(*) as count FROM customers', conn).iloc[0]['count']
                sales_count = pd.read_sql_query('SELECT COUNT(*) as count FROM sales', conn).iloc[0]['count']

                print("\n📈 ETL Execution Report")
                print("=" * 50)

                print(f"\n📊 Current Data Status:")
                print(f"  Customers: {customer_count:,} records")
                print(f"  Sales: {sales_count:,} records")

                if not df_jobs.empty:
                    print(f"\n📋 Recent ETL Jobs:")
                    print(df_jobs.to_string(index=False))

                if not df_issues.empty:
                    print(f"\n⚠️ Data Quality Issues (Last 24h):")
                    print(df_issues.to_string(index=False))
                else:
                    print(f"\n✅ No data quality issues found in the last 24 hours")

                # Runtime metrics
                if self.metrics['start_time'] and self.metrics['end_time']:
                    duration = (self.metrics['end_time'] - self.metrics['start_time']).total_seconds()
                    print(f"\n⏱️ Pipeline Metrics:")
                    print(f"  Execution time: {duration:.2f} seconds")
                    print(f"  Records extracted: {self.metrics['records_extracted']:,}")
                    print(f"  Records transformed: {self.metrics['records_transformed']:,}")
                    print(f"  Records loaded: {self.metrics['records_loaded']:,}")
                    print(f"  Errors encountered: {self.metrics['errors_count']}")

        except sqlite3.Error as e:
            logger.error(f"❌ Failed to generate ETL report: {e}")

    def run_full_etl_pipeline(self):
        """
        Run the complete ETL pipeline with all components.

        This is the main orchestration method that runs all ETL processes.
        """
        logger.info("🚀 Starting full ETL pipeline...")

        self.metrics['start_time'] = datetime.now()
        overall_success = True

        try:
            # Create sample data (in production, this would be skipped)
            self.create_sample_data()

            # Run customer ETL
            if not self.run_customer_etl():
                overall_success = False

            # Run sales ETL
            if not self.run_sales_etl():
                overall_success = False

            # Run incremental updates
            if not self.run_incremental_update():
                overall_success = False

            self.metrics['end_time'] = datetime.now()

            # Log the overall job
            status = 'success' if overall_success else 'failed'
            self.log_etl_job('full_pipeline', status)

            # Generate report
            self.generate_etl_report()

            if overall_success:
                logger.info("🎉 Full ETL pipeline completed successfully!")
            else:
                logger.error("❌ ETL pipeline completed with errors")

            return overall_success

        except Exception as e:
            self.metrics['end_time'] = datetime.now()
            logger.error(f"❌ ETL pipeline failed: {e}")
            self.log_etl_job('full_pipeline', 'failed')
            return False

def demonstrate_advanced_etl_patterns():
    """
    Demonstrate advanced ETL patterns and concepts.
    """
    print("\n🎓 Advanced ETL Patterns & Concepts:")
    print("=" * 50)

    concepts = {
        "Change Data Capture (CDC)": [
            "Track changes in source systems",
            "Use timestamps or version numbers",
            "Implement incremental loading strategies"
        ],
        "Data Lineage": [
            "Track data flow from source to target",
            "Document transformation rules",
            "Enable impact analysis for changes"
        ],
        "Error Handling Strategies": [
            "Dead letter queues for bad records",
            "Circuit breakers for external systems",
            "Retry mechanisms with exponential backoff"
        ],
        "Performance Optimization": [
            "Parallel processing for large datasets",
            "Partitioning strategies",
            "Indexing for fast lookups"
        ],
        "Data Governance": [
            "Data quality scorecards",
            "Automated data profiling",
            "Compliance and audit trails"
        ]
    }

    for concept, details in concepts.items():
        print(f"\n🔧 {concept}:")
        for detail in details:
            print(f"  • {detail}")

def main():
    """
    Main function demonstrating the complete ETL automation workflow.
    """
    print("🚀 Welcome to PL's ETL Automation Demo!")
    print("=" * 50)

    try:
        # Initialize ETL pipeline with configuration
        config = ETLConfig()
        etl_pipeline = ETLPipeline(config)

        # Run the full ETL pipeline
        success = etl_pipeline.run_full_etl_pipeline()

        if success:
            print("\n✅ ETL automation demonstration completed successfully!")

            # Show database file info
            db_path = Path(config.database_path)
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                print(f"\n📁 Database file: {db_path.absolute()}")
                print(f"   Size: {size_mb:.2f} MB")

            print(f"\n📂 Generated directories:")
            for directory in [config.source_directory, config.staging_directory,
                             config.archive_directory, config.output_directory]:
                dir_path = Path(directory)
                if dir_path.exists():
                    file_count = len(list(dir_path.iterdir()))
                    print(f"   {directory}: {file_count} files")

        else:
            print("\n❌ ETL pipeline encountered errors. Check the logs for details.")

    except Exception as e:
        logger.error(f"❌ ETL demonstration failed: {e}")
        print("💡 Troubleshooting tips:")
        print("   - Ensure you have write permissions in the current directory")
        print("   - Check available disk space")
        print("   - Verify all dependencies are installed")

    # Show advanced patterns
    demonstrate_advanced_etl_patterns()

    print("\n🎓 Learning Summary:")
    print("- ETL pipeline design and implementation")
    print("- Data extraction from multiple sources")
    print("- Data transformation and cleaning techniques")
    print("- Data quality validation and monitoring")
    print("- Database operations and batch processing")
    print("- Error handling and logging strategies")

    print("\n💡 Next Steps:")
    print("- Implement real-time streaming ETL with Apache Kafka")
    print("- Add data profiling and automated quality checks")
    print("- Integrate with cloud data warehouses (Snowflake, BigQuery)")
    print("- Build data lineage and impact analysis tools")
    print("- Set up monitoring and alerting for production ETL jobs")

if __name__ == "__main__":
    main()