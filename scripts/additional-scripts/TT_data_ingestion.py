# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "boto3",
#     "pandas",
#     "pyarrow",
#     "fastparquet",
#     "requests",
#     "sqlalchemy",
#     "psycopg2-binary",
# ]
# ///

"""
TT Data Ingestion
Student: TT
Description: Notebook script to handle big data ingestion from middleware,
data stored in Amazon AWS for further processing

This script demonstrates how to:
1. Connect to various data sources (APIs, databases, files)
2. Ingest large datasets efficiently using chunking and streaming
3. Transform and validate data during ingestion
4. Store data in AWS S3 and other cloud storage
5. Handle errors, retries, and data quality issues
6. Monitor ingestion progress and performance

Educational Focus:
- Working with AWS services (S3, RDS, etc.)
- Batch and streaming data processing
- Data validation and cleaning
- Error handling and resilience
- Performance optimization for large datasets
- Data pipeline design patterns
"""

import boto3
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Iterator, Any, Union
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from io import StringIO, BytesIO
import os
import tempfile

# Database connectivity (optional)
try:
    from sqlalchemy import create_engine, text
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AWSDataManager:
    """
    Manages AWS connections and operations for data ingestion
    """

    def __init__(self, aws_access_key: str = None, aws_secret_key: str = None, region: str = 'us-east-1'):
        """
        Initialize AWS connection

        Args:
            aws_access_key: AWS access key (if None, uses environment variables or IAM roles)
            aws_secret_key: AWS secret key (if None, uses environment variables or IAM roles)
            region: AWS region
        """
        # Initialize AWS clients
        try:
            if aws_access_key and aws_secret_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region
                )
            else:
                # Use default credential chain (environment variables, IAM roles, etc.)
                self.s3_client = boto3.client('s3', region_name=region)

            self.region = region
            logger.info(f"✅ AWS S3 client initialized for region: {region}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS client: {e}")
            self.s3_client = None

    def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """
        Create S3 bucket if it doesn't exist

        Args:
            bucket_name: Name of the S3 bucket

        Returns:
            True if bucket exists or was created successfully
        """
        if not self.s3_client:
            logger.error("AWS S3 client not initialized")
            return False

        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"✅ Bucket '{bucket_name}' already exists")
            return True

        except self.s3_client.exceptions.NoSuchBucket:
            # Bucket doesn't exist, create it
            try:
                if self.region == 'us-east-1':
                    # us-east-1 doesn't need LocationConstraint
                    self.s3_client.create_bucket(Bucket=bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
                logger.info(f"✅ Created bucket '{bucket_name}'")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to create bucket '{bucket_name}': {e}")
                return False

        except Exception as e:
            logger.error(f"❌ Error checking bucket '{bucket_name}': {e}")
            return False

    def upload_dataframe_to_s3(self, df: pd.DataFrame, bucket_name: str, key: str,
                              format: str = 'parquet') -> bool:
        """
        Upload a pandas DataFrame to S3

        Args:
            df: DataFrame to upload
            bucket_name: S3 bucket name
            key: S3 key (file path)
            format: File format ('parquet', 'csv', 'json')

        Returns:
            True if upload successful
        """
        if not self.s3_client:
            logger.error("AWS S3 client not initialized")
            return False

        try:
            # Convert DataFrame to bytes based on format
            if format.lower() == 'parquet':
                buffer = BytesIO()
                df.to_parquet(buffer, index=False)
                content_type = 'application/octet-stream'
            elif format.lower() == 'csv':
                buffer = StringIO()
                df.to_csv(buffer, index=False)
                content_type = 'text/csv'
            elif format.lower() == 'json':
                buffer = StringIO()
                df.to_json(buffer, orient='records', lines=True)
                content_type = 'application/json'
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Upload to S3
            if isinstance(buffer, StringIO):
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=buffer.getvalue(),
                    ContentType=content_type
                )
            else:
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=buffer.getvalue(),
                    ContentType=content_type
                )

            logger.info(f"✅ Uploaded DataFrame to s3://{bucket_name}/{key}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload DataFrame to S3: {e}")
            return False

    def upload_file_to_s3(self, local_file_path: Union[str, Path], bucket_name: str, key: str) -> bool:
        """
        Upload a local file to S3

        Args:
            local_file_path: Path to local file
            bucket_name: S3 bucket name
            key: S3 key (file path)

        Returns:
            True if upload successful
        """
        if not self.s3_client:
            logger.error("AWS S3 client not initialized")
            return False

        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                logger.error(f"Local file not found: {local_path}")
                return False

            self.s3_client.upload_file(str(local_path), bucket_name, key)
            logger.info(f"✅ Uploaded {local_path.name} to s3://{bucket_name}/{key}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload file to S3: {e}")
            return False

    def list_s3_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        """
        List objects in S3 bucket

        Args:
            bucket_name: S3 bucket name
            prefix: Prefix to filter objects

        Returns:
            List of object keys
        """
        if not self.s3_client:
            logger.error("AWS S3 client not initialized")
            return []

        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            objects = [obj['Key'] for obj in response.get('Contents', [])]
            logger.info(f"✅ Found {len(objects)} objects in s3://{bucket_name}/{prefix}")
            return objects

        except Exception as e:
            logger.error(f"❌ Failed to list S3 objects: {e}")
            return []

class DataSourceConnector:
    """
    Connects to various data sources (APIs, databases, files)
    """

    def __init__(self):
        """Initialize the data source connector"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TT-Data-Ingestion/1.0'
        })
        logger.info("✅ Data Source Connector initialized")

    def fetch_api_data(self, url: str, params: Dict = None, headers: Dict = None,
                      auth: tuple = None, timeout: int = 30) -> Optional[Dict]:
        """
        Fetch data from REST API

        Args:
            url: API endpoint URL
            params: Query parameters
            headers: Additional headers
            auth: Authentication tuple (username, password)
            timeout: Request timeout in seconds

        Returns:
            JSON response data or None if failed
        """
        try:
            if headers:
                self.session.headers.update(headers)

            response = self.session.get(
                url,
                params=params,
                auth=auth,
                timeout=timeout
            )
            response.raise_for_status()

            logger.info(f"✅ Successfully fetched data from {url}")
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to fetch data from {url}: {e}")
            return None

    def fetch_paginated_api_data(self, base_url: str, page_param: str = 'page',
                                page_size_param: str = 'per_page', page_size: int = 100,
                                max_pages: int = 10) -> Iterator[Dict]:
        """
        Fetch data from paginated API

        Args:
            base_url: Base API URL
            page_param: Parameter name for page number
            page_size_param: Parameter name for page size
            page_size: Number of items per page
            max_pages: Maximum number of pages to fetch

        Yields:
            JSON response data for each page
        """
        page = 1

        while page <= max_pages:
            params = {
                page_param: page,
                page_size_param: page_size
            }

            data = self.fetch_api_data(base_url, params=params)
            if not data:
                break

            yield data

            # Check if we've reached the end
            # This logic depends on the specific API response format
            if isinstance(data, list) and len(data) < page_size:
                break
            elif isinstance(data, dict):
                # Look for common pagination indicators
                if 'next' in data and not data['next']:
                    break
                if 'has_more' in data and not data['has_more']:
                    break

            page += 1
            time.sleep(0.1)  # Be respectful to the API

    def connect_to_database(self, connection_string: str) -> Optional[Any]:
        """
        Connect to a database using SQLAlchemy

        Args:
            connection_string: Database connection string

        Returns:
            SQLAlchemy engine or None if failed
        """
        if not HAS_SQLALCHEMY:
            logger.error("SQLAlchemy not available for database connections")
            return None

        try:
            engine = create_engine(connection_string)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info("✅ Database connection established")
            return engine

        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return None

    def fetch_database_data(self, engine: Any, query: str, chunk_size: int = 10000) -> Iterator[pd.DataFrame]:
        """
        Fetch data from database in chunks

        Args:
            engine: SQLAlchemy engine
            query: SQL query
            chunk_size: Number of rows per chunk

        Yields:
            DataFrame chunks
        """
        if not HAS_SQLALCHEMY:
            logger.error("SQLAlchemy not available")
            return

        try:
            for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
                yield chunk

        except Exception as e:
            logger.error(f"❌ Failed to fetch database data: {e}")

class DataProcessor:
    """
    Processes and transforms data during ingestion
    """

    def __init__(self):
        """Initialize the data processor"""
        self.validation_errors = []
        logger.info("✅ Data Processor initialized")

    def validate_dataframe(self, df: pd.DataFrame, schema: Dict[str, Dict]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Validate DataFrame against a schema

        Args:
            df: DataFrame to validate
            schema: Schema definition with column rules

        Returns:
            Tuple of (cleaned_df, validation_errors)
        """
        errors = []
        cleaned_df = df.copy()

        for column, rules in schema.items():
            if column not in df.columns:
                if rules.get('required', False):
                    errors.append(f"Required column missing: {column}")
                continue

            # Check data type
            expected_type = rules.get('type')
            if expected_type:
                try:
                    if expected_type == 'datetime':
                        cleaned_df[column] = pd.to_datetime(cleaned_df[column], errors='coerce')
                    elif expected_type == 'numeric':
                        cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors='coerce')
                    elif expected_type == 'string':
                        cleaned_df[column] = cleaned_df[column].astype(str)
                except Exception as e:
                    errors.append(f"Type conversion failed for {column}: {e}")

            # Check for null values
            if not rules.get('allow_null', True):
                null_count = cleaned_df[column].isnull().sum()
                if null_count > 0:
                    errors.append(f"Column {column} has {null_count} null values")

            # Check value ranges
            if 'min_value' in rules:
                invalid_count = (cleaned_df[column] < rules['min_value']).sum()
                if invalid_count > 0:
                    errors.append(f"Column {column} has {invalid_count} values below minimum")

            if 'max_value' in rules:
                invalid_count = (cleaned_df[column] > rules['max_value']).sum()
                if invalid_count > 0:
                    errors.append(f"Column {column} has {invalid_count} values above maximum")

        return cleaned_df, errors

    def clean_text_data(self, df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
        """
        Clean text data in specified columns

        Args:
            df: DataFrame to clean
            text_columns: List of column names containing text

        Returns:
            DataFrame with cleaned text
        """
        cleaned_df = df.copy()

        for column in text_columns:
            if column in cleaned_df.columns:
                # Remove extra whitespace
                cleaned_df[column] = cleaned_df[column].astype(str).str.strip()

                # Remove special characters (optional)
                cleaned_df[column] = cleaned_df[column].str.replace(r'[^\w\s]', '', regex=True)

                # Convert to title case (optional)
                # cleaned_df[column] = cleaned_df[column].str.title()

        logger.info(f"✅ Cleaned text data in {len(text_columns)} columns")
        return cleaned_df

    def deduplicate_data(self, df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """
        Remove duplicate rows from DataFrame

        Args:
            df: DataFrame to deduplicate
            subset: Columns to consider for duplication check

        Returns:
            DataFrame without duplicates
        """
        original_count = len(df)
        deduped_df = df.drop_duplicates(subset=subset)
        removed_count = original_count - len(deduped_df)

        if removed_count > 0:
            logger.info(f"✅ Removed {removed_count} duplicate rows")

        return deduped_df

    def add_metadata_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add metadata columns to DataFrame

        Args:
            df: DataFrame to enhance

        Returns:
            DataFrame with metadata columns
        """
        enhanced_df = df.copy()

        # Add ingestion timestamp
        enhanced_df['ingestion_timestamp'] = datetime.now()

        # Add row hash for change detection
        enhanced_df['row_hash'] = enhanced_df.apply(
            lambda row: hashlib.md5(str(row.to_dict()).encode()).hexdigest(),
            axis=1
        )

        # Add data source information
        enhanced_df['data_source'] = 'TT_ingestion_pipeline'

        logger.info("✅ Added metadata columns to DataFrame")
        return enhanced_df

class DataIngestionPipeline:
    """
    Main pipeline orchestrator for data ingestion
    """

    def __init__(self, aws_manager: AWSDataManager):
        """
        Initialize the ingestion pipeline

        Args:
            aws_manager: AWS data manager instance
        """
        self.aws_manager = aws_manager
        self.connector = DataSourceConnector()
        self.processor = DataProcessor()
        self.ingestion_stats = {
            'start_time': None,
            'end_time': None,
            'total_records': 0,
            'successful_records': 0,
            'failed_records': 0,
            'errors': []
        }

        logger.info("✅ Data Ingestion Pipeline initialized")

    def ingest_from_api(self, api_config: Dict[str, Any], s3_config: Dict[str, str],
                       schema: Dict[str, Dict] = None, chunk_size: int = 1000) -> Dict[str, Any]:
        """
        Ingest data from API and store in S3

        Args:
            api_config: API configuration (url, params, headers, etc.)
            s3_config: S3 configuration (bucket, key_prefix)
            schema: Data validation schema
            chunk_size: Number of records to process in each batch

        Returns:
            Ingestion results and statistics
        """
        self.ingestion_stats['start_time'] = datetime.now()
        logger.info(f"🚀 Starting API data ingestion from {api_config.get('url', 'unknown')}")

        try:
            # Determine if API is paginated
            if api_config.get('paginated', False):
                data_generator = self.connector.fetch_paginated_api_data(
                    api_config['url'],
                    page_param=api_config.get('page_param', 'page'),
                    page_size_param=api_config.get('page_size_param', 'per_page'),
                    page_size=api_config.get('page_size', 100),
                    max_pages=api_config.get('max_pages', 10)
                )
            else:
                # Single API call
                single_response = self.connector.fetch_api_data(
                    api_config['url'],
                    params=api_config.get('params'),
                    headers=api_config.get('headers'),
                    auth=api_config.get('auth')
                )
                data_generator = [single_response] if single_response else []

            # Process data in chunks
            batch_number = 0
            all_records = []

            for api_response in data_generator:
                batch_number += 1
                logger.info(f"📊 Processing batch {batch_number}")

                # Extract records from API response
                records = self._extract_records_from_response(api_response, api_config.get('data_path', []))

                if not records:
                    continue

                # Convert to DataFrame
                df = pd.DataFrame(records)

                # Validate data if schema provided
                if schema:
                    df, validation_errors = self.processor.validate_dataframe(df, schema)
                    self.ingestion_stats['errors'].extend(validation_errors)

                # Clean and process data
                df = self.processor.add_metadata_columns(df)

                # Store in S3
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                s3_key = f"{s3_config['key_prefix']}/batch_{batch_number}_{timestamp}.parquet"

                success = self.aws_manager.upload_dataframe_to_s3(
                    df, s3_config['bucket'], s3_key, format='parquet'
                )

                if success:
                    self.ingestion_stats['successful_records'] += len(df)
                    all_records.extend(records)
                else:
                    self.ingestion_stats['failed_records'] += len(df)

                # Respect rate limits
                time.sleep(api_config.get('delay_seconds', 1))

            self.ingestion_stats['total_records'] = len(all_records)

        except Exception as e:
            logger.error(f"❌ Error during API ingestion: {e}")
            self.ingestion_stats['errors'].append(str(e))

        self.ingestion_stats['end_time'] = datetime.now()
        return self._generate_ingestion_report()

    def ingest_from_database(self, db_config: Dict[str, Any], s3_config: Dict[str, str],
                           schema: Dict[str, Dict] = None, chunk_size: int = 10000) -> Dict[str, Any]:
        """
        Ingest data from database and store in S3

        Args:
            db_config: Database configuration (connection_string, query)
            s3_config: S3 configuration (bucket, key_prefix)
            schema: Data validation schema
            chunk_size: Number of records to process in each batch

        Returns:
            Ingestion results and statistics
        """
        self.ingestion_stats['start_time'] = datetime.now()
        logger.info(f"🚀 Starting database data ingestion")

        try:
            # Connect to database
            engine = self.connector.connect_to_database(db_config['connection_string'])
            if not engine:
                raise Exception("Failed to connect to database")

            # Fetch data in chunks
            chunk_number = 0
            for df_chunk in self.connector.fetch_database_data(engine, db_config['query'], chunk_size):
                chunk_number += 1
                logger.info(f"📊 Processing chunk {chunk_number} with {len(df_chunk)} records")

                # Validate data if schema provided
                if schema:
                    df_chunk, validation_errors = self.processor.validate_dataframe(df_chunk, schema)
                    self.ingestion_stats['errors'].extend(validation_errors)

                # Clean and process data
                df_chunk = self.processor.add_metadata_columns(df_chunk)

                # Store in S3
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                s3_key = f"{s3_config['key_prefix']}/chunk_{chunk_number}_{timestamp}.parquet"

                success = self.aws_manager.upload_dataframe_to_s3(
                    df_chunk, s3_config['bucket'], s3_key, format='parquet'
                )

                if success:
                    self.ingestion_stats['successful_records'] += len(df_chunk)
                else:
                    self.ingestion_stats['failed_records'] += len(df_chunk)

            self.ingestion_stats['total_records'] = self.ingestion_stats['successful_records'] + self.ingestion_stats['failed_records']

        except Exception as e:
            logger.error(f"❌ Error during database ingestion: {e}")
            self.ingestion_stats['errors'].append(str(e))

        self.ingestion_stats['end_time'] = datetime.now()
        return self._generate_ingestion_report()

    def ingest_from_files(self, file_config: Dict[str, Any], s3_config: Dict[str, str],
                         schema: Dict[str, Dict] = None) -> Dict[str, Any]:
        """
        Ingest data from local files and store in S3

        Args:
            file_config: File configuration (directory, pattern, format)
            s3_config: S3 configuration (bucket, key_prefix)
            schema: Data validation schema

        Returns:
            Ingestion results and statistics
        """
        self.ingestion_stats['start_time'] = datetime.now()
        logger.info(f"🚀 Starting file data ingestion from {file_config.get('directory', 'unknown')}")

        try:
            file_dir = Path(file_config['directory'])
            file_pattern = file_config.get('pattern', '*')
            file_format = file_config.get('format', 'csv')

            # Find matching files
            files = list(file_dir.glob(file_pattern))
            logger.info(f"📁 Found {len(files)} files to process")

            for file_path in files:
                logger.info(f"📊 Processing file: {file_path.name}")

                try:
                    # Read file based on format
                    if file_format.lower() == 'csv':
                        df = pd.read_csv(file_path)
                    elif file_format.lower() == 'json':
                        df = pd.read_json(file_path)
                    elif file_format.lower() in ['parquet', 'pq']:
                        df = pd.read_parquet(file_path)
                    elif file_format.lower() in ['excel', 'xlsx', 'xls']:
                        df = pd.read_excel(file_path)
                    else:
                        logger.warning(f"⚠️  Unsupported file format: {file_format}")
                        continue

                    # Validate data if schema provided
                    if schema:
                        df, validation_errors = self.processor.validate_dataframe(df, schema)
                        self.ingestion_stats['errors'].extend(validation_errors)

                    # Clean and process data
                    df = self.processor.add_metadata_columns(df)

                    # Store in S3
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    s3_key = f"{s3_config['key_prefix']}/{file_path.stem}_{timestamp}.parquet"

                    success = self.aws_manager.upload_dataframe_to_s3(
                        df, s3_config['bucket'], s3_key, format='parquet'
                    )

                    if success:
                        self.ingestion_stats['successful_records'] += len(df)
                    else:
                        self.ingestion_stats['failed_records'] += len(df)

                except Exception as e:
                    logger.error(f"❌ Error processing file {file_path.name}: {e}")
                    self.ingestion_stats['errors'].append(f"File {file_path.name}: {str(e)}")

            self.ingestion_stats['total_records'] = self.ingestion_stats['successful_records'] + self.ingestion_stats['failed_records']

        except Exception as e:
            logger.error(f"❌ Error during file ingestion: {e}")
            self.ingestion_stats['errors'].append(str(e))

        self.ingestion_stats['end_time'] = datetime.now()
        return self._generate_ingestion_report()

    def _extract_records_from_response(self, response: Dict, data_path: List[str]) -> List[Dict]:
        """
        Extract records from API response using data path

        Args:
            response: API response data
            data_path: Path to the data array in the response

        Returns:
            List of record dictionaries
        """
        data = response
        for key in data_path:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return []

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            return []

    def _generate_ingestion_report(self) -> Dict[str, Any]:
        """Generate comprehensive ingestion report"""
        duration = None
        if self.ingestion_stats['start_time'] and self.ingestion_stats['end_time']:
            duration = self.ingestion_stats['end_time'] - self.ingestion_stats['start_time']

        report = {
            'pipeline_summary': {
                'start_time': self.ingestion_stats['start_time'].isoformat() if self.ingestion_stats['start_time'] else None,
                'end_time': self.ingestion_stats['end_time'].isoformat() if self.ingestion_stats['end_time'] else None,
                'duration_seconds': duration.total_seconds() if duration else None,
                'total_records': self.ingestion_stats['total_records'],
                'successful_records': self.ingestion_stats['successful_records'],
                'failed_records': self.ingestion_stats['failed_records'],
                'success_rate': (self.ingestion_stats['successful_records'] / self.ingestion_stats['total_records']) * 100 if self.ingestion_stats['total_records'] > 0 else 0
            },
            'errors': self.ingestion_stats['errors'],
            'performance_metrics': {
                'records_per_second': self.ingestion_stats['total_records'] / duration.total_seconds() if duration and duration.total_seconds() > 0 else 0
            }
        }

        return report

def create_sample_data():
    """Create sample data for demonstration"""
    # Sample sales data
    sample_data = []
    for i in range(1000):
        record = {
            'transaction_id': f"TXN_{i:06d}",
            'customer_id': f"CUST_{(i % 100):03d}",
            'product_id': f"PROD_{(i % 50):03d}",
            'quantity': (i % 10) + 1,
            'unit_price': round(10 + (i % 100) * 0.5, 2),
            'transaction_date': (datetime.now() - timedelta(days=i % 365)).strftime('%Y-%m-%d'),
            'sales_rep': f"Rep_{(i % 10):02d}",
            'region': ['North', 'South', 'East', 'West'][i % 4]
        }
        sample_data.append(record)

    return sample_data

def main():
    """
    Main function demonstrating the data ingestion pipeline
    """
    print("🗃️  TT Data Ingestion Pipeline - Educational Demo")
    print("=" * 60)

    # Note: This demo uses mock AWS credentials for educational purposes
    # In real usage, you would use actual AWS credentials
    print("⚠️  Demo Mode: Using mock AWS operations (no actual S3 uploads)")

    # Initialize AWS manager (with demo credentials)
    aws_manager = AWSDataManager(
        aws_access_key="demo_key",
        aws_secret_key="demo_secret",
        region="us-east-1"
    )

    # Initialize pipeline
    pipeline = DataIngestionPipeline(aws_manager)

    # Example 1: Sample data validation schema
    print("\n📚 Example 1: Data validation schema definition...")
    sample_schema = {
        'transaction_id': {
            'type': 'string',
            'required': True,
            'allow_null': False
        },
        'customer_id': {
            'type': 'string',
            'required': True,
            'allow_null': False
        },
        'quantity': {
            'type': 'numeric',
            'required': True,
            'min_value': 1,
            'max_value': 100
        },
        'unit_price': {
            'type': 'numeric',
            'required': True,
            'min_value': 0.01
        },
        'transaction_date': {
            'type': 'datetime',
            'required': True,
            'allow_null': False
        }
    }

    print("✅ Schema defined with validation rules for 5 columns")

    # Example 2: Create and process sample data
    print("\n📚 Example 2: Creating and processing sample data...")
    sample_data = create_sample_data()
    df = pd.DataFrame(sample_data)

    print(f"📊 Created sample dataset with {len(df)} records")
    print(f"Columns: {list(df.columns)}")
    print(f"Sample record:\n{df.iloc[0].to_dict()}")

    # Validate the data
    processor = DataProcessor()
    validated_df, validation_errors = processor.validate_dataframe(df, sample_schema)

    if validation_errors:
        print(f"⚠️  Validation errors found: {len(validation_errors)}")
        for error in validation_errors[:3]:  # Show first 3 errors
            print(f"  - {error}")
    else:
        print("✅ Data validation passed")

    # Example 3: Demonstrate file-based ingestion
    print("\n📚 Example 3: File-based data ingestion simulation...")

    # Create sample files
    sample_dir = Path(__file__).parent / "sample_ingestion_data"
    sample_dir.mkdir(exist_ok=True)

    # Save sample data to different formats
    sample_files = {
        'sales_data.csv': df.to_csv,
        'sales_data.json': df.to_json,
        'sales_data.parquet': df.to_parquet
    }

    for filename, save_func in sample_files.items():
        file_path = sample_dir / filename
        if filename.endswith('.csv'):
            save_func(file_path, index=False)
        elif filename.endswith('.json'):
            save_func(file_path, orient='records', lines=True)
        else:
            save_func(file_path, index=False)

    print(f"📁 Created sample files in {sample_dir}")

    # Simulate file ingestion
    file_config = {
        'directory': str(sample_dir),
        'pattern': '*.csv',
        'format': 'csv'
    }

    s3_config = {
        'bucket': 'tt-data-ingestion-demo',
        'key_prefix': 'sales_data/raw'
    }

    # This would normally upload to S3, but we'll simulate it
    print("🚀 Simulating file ingestion pipeline...")
    print(f"  Source: {file_config['directory']}")
    print(f"  Target: s3://{s3_config['bucket']}/{s3_config['key_prefix']}")
    print(f"  Schema validation: {'Enabled' if sample_schema else 'Disabled'}")

    # Example 4: API ingestion simulation
    print("\n📚 Example 4: API data ingestion simulation...")

    api_config = {
        'url': 'https://jsonplaceholder.typicode.com/posts',
        'paginated': False,
        'headers': {'Accept': 'application/json'},
        'data_path': [],  # Data is at root level
        'delay_seconds': 0.5
    }

    print("🌐 Simulating API data ingestion...")
    print(f"  API Endpoint: {api_config['url']}")
    print(f"  Pagination: {'Yes' if api_config['paginated'] else 'No'}")

    # Fetch sample API data for demonstration
    connector = DataSourceConnector()
    api_data = connector.fetch_api_data(api_config['url'])

    if api_data:
        api_df = pd.DataFrame(api_data[:10])  # Use first 10 records
        print(f"✅ Fetched {len(api_df)} records from API")
        print(f"Sample columns: {list(api_df.columns)}")

        # Add metadata
        enriched_df = processor.add_metadata_columns(api_df)
        print(f"📊 Enhanced data with metadata columns")

    # Example 5: Performance monitoring
    print("\n📚 Example 5: Performance monitoring and reporting...")

    # Simulate processing statistics
    mock_stats = {
        'total_files_processed': 3,
        'total_records_ingested': len(df),
        'processing_time_seconds': 45.2,
        'average_throughput_records_per_second': len(df) / 45.2,
        'validation_errors': len(validation_errors),
        'data_quality_score': 95.5
    }

    print("📈 Ingestion Performance Report:")
    print(f"  Total Records: {mock_stats['total_records_ingested']:,}")
    print(f"  Processing Time: {mock_stats['processing_time_seconds']:.1f} seconds")
    print(f"  Throughput: {mock_stats['average_throughput_records_per_second']:.1f} records/sec")
    print(f"  Data Quality Score: {mock_stats['data_quality_score']:.1f}%")
    print(f"  Validation Errors: {mock_stats['validation_errors']}")

    # Example 6: Error handling and retry logic
    print("\n📚 Example 6: Error handling and retry simulation...")

    def simulate_unreliable_operation():
        """Simulate an operation that might fail"""
        import random
        if random.random() < 0.3:  # 30% chance of failure
            raise Exception("Simulated network timeout")
        return "Operation successful"

    def retry_operation(operation, max_retries=3, delay=1):
        """Retry an operation with exponential backoff"""
        for attempt in range(max_retries):
            try:
                result = operation()
                print(f"  ✅ Operation succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt)
                    print(f"  ⚠️  Attempt {attempt + 1} failed: {e}")
                    print(f"     Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ All {max_retries} attempts failed: {e}")
                    raise

    print("🔄 Demonstrating retry logic...")
    try:
        retry_operation(simulate_unreliable_operation)
    except Exception as e:
        print(f"💥 Final failure: {e}")

    print(f"\n🎓 Educational Notes:")
    print("1. Always validate data before storing in production systems")
    print("2. Use chunking for large datasets to manage memory usage")
    print("3. Implement retry logic for network operations")
    print("4. Monitor data quality and ingestion performance")
    print("5. Use appropriate data formats (Parquet for analytics, JSON for flexibility)")
    print("6. Handle different time zones and date formats carefully")
    print("7. Implement data lineage tracking for debugging")
    print("8. Use AWS IAM roles instead of hardcoded credentials")
    print("9. Consider data encryption for sensitive information")
    print("10. Plan for data archival and retention policies")

    # Cleanup
    try:
        import shutil
        shutil.rmtree(sample_dir)
        print(f"🧹 Cleaned up sample data directory")
    except Exception as e:
        print(f"⚠️  Could not clean up directory: {e}")

    print("\n🚀 Real Implementation Notes:")
    print("To use this script with real AWS:")
    print("1. Install AWS CLI and configure credentials")
    print("2. Set up appropriate IAM permissions")
    print("3. Replace demo credentials with real ones")
    print("4. Test with small datasets first")
    print("5. Monitor AWS costs and usage")

if __name__ == "__main__":
    main()