#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "sqlite3",
#     "pandas",
#     "python-dotenv",
#     "beautifulsoup4",
# ]
# ///

"""
JG_api_data_storage.py - Access API for Website and Store Data in Database

Student: JG (Initials)
Request: "access API for website and store data in database"

This script demonstrates how to fetch data from public APIs and store it in a SQLite database.
It includes comprehensive error handling, data validation, and database management.

Educational Focus:
- Making HTTP requests to APIs
- JSON data processing
- SQLite database operations
- Data validation and cleaning
- Error handling and retry logic
- Database schema design
- Working with different API types

Prerequisites:
- No API keys required (uses public APIs)
- SQLite is included with Python
"""

import requests
import sqlite3
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_data_storage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class APIEndpoint:
    """
    Data class to represent an API endpoint configuration.

    This makes it easy to manage multiple APIs and their settings.
    """
    name: str
    url: str
    headers: Dict[str, str]
    rate_limit_delay: float = 1.0  # Seconds between requests
    description: str = ""

class APIDataFetcher:
    """
    A comprehensive class for fetching data from various APIs and storing in database.

    This class demonstrates professional API integration patterns including:
    - Rate limiting
    - Error handling and retries
    - Response validation
    - Data transformation
    """

    def __init__(self, db_path: str = "api_data.db"):
        """
        Initialize the API data fetcher.

        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.session = requests.Session()

        # Set a user agent to be a good API citizen
        self.session.headers.update({
            'User-Agent': 'Educational-API-Demo/1.0 (Python Training)'
        })

        # Initialize database
        self.init_database()

        # Define our API endpoints for demonstration
        self.api_endpoints = {
            'weather': APIEndpoint(
                name='OpenWeatherMap Demo',
                url='https://api.openweathermap.org/data/2.5/weather',
                headers={},
                rate_limit_delay=1.0,
                description='Weather data for cities'
            ),
            'jsonplaceholder': APIEndpoint(
                name='JSONPlaceholder Posts',
                url='https://jsonplaceholder.typicode.com/posts',
                headers={},
                rate_limit_delay=0.5,
                description='Sample blog posts data'
            ),
            'httpbin': APIEndpoint(
                name='HTTPBin IP Info',
                url='https://httpbin.org/ip',
                headers={},
                rate_limit_delay=0.5,
                description='IP address information'
            ),
            'random_user': APIEndpoint(
                name='Random User Generator',
                url='https://randomuser.me/api/',
                headers={},
                rate_limit_delay=1.0,
                description='Random user profiles'
            )
        }

    def init_database(self):
        """
        Initialize the SQLite database with tables for different data types.

        This creates a flexible schema that can store various types of API data.
        """
        logger.info(f"🗄️ Initializing database: {self.db_path}")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Table for API fetch logs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_fetch_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_name TEXT NOT NULL,
                        endpoint_url TEXT NOT NULL,
                        status_code INTEGER,
                        response_size INTEGER,
                        fetch_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN NOT NULL,
                        error_message TEXT
                    )
                ''')

                # Table for weather data
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS weather_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        city_name TEXT NOT NULL,
                        country TEXT,
                        temperature REAL,
                        feels_like REAL,
                        humidity INTEGER,
                        pressure INTEGER,
                        weather_main TEXT,
                        weather_description TEXT,
                        wind_speed REAL,
                        wind_direction INTEGER,
                        cloudiness INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        raw_data TEXT
                    )
                ''')

                # Table for generic JSON data (flexible storage)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS json_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_api TEXT NOT NULL,
                        data_type TEXT NOT NULL,
                        json_content TEXT NOT NULL,
                        extracted_fields TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Table for user profiles (from random user API)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT,
                        phone TEXT,
                        country TEXT,
                        city TEXT,
                        age INTEGER,
                        gender TEXT,
                        profile_picture_url TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("✅ Database tables created successfully")

        except sqlite3.Error as e:
            logger.error(f"❌ Database initialization error: {e}")
            raise

    def make_api_request(self, endpoint: APIEndpoint, params: Dict = None, retries: int = 3) -> Optional[Dict]:
        """
        Make a request to an API endpoint with proper error handling and retries.

        Args:
            endpoint (APIEndpoint): The API endpoint configuration
            params (Dict): Query parameters for the request
            retries (int): Number of retry attempts

        Returns:
            Optional[Dict]: JSON response data or None if failed
        """
        logger.info(f"🌐 Making request to {endpoint.name}: {endpoint.url}")

        for attempt in range(retries + 1):
            try:
                # Respect rate limiting
                if attempt > 0:
                    time.sleep(endpoint.rate_limit_delay * attempt)  # Exponential backoff

                # Make the request
                response = self.session.get(
                    endpoint.url,
                    params=params,
                    headers=endpoint.headers,
                    timeout=10
                )

                # Log the request
                self.log_api_request(
                    endpoint.name,
                    endpoint.url,
                    response.status_code,
                    len(response.content) if response.content else 0,
                    response.status_code == 200,
                    None if response.status_code == 200 else f"HTTP {response.status_code}"
                )

                # Check if request was successful
                response.raise_for_status()

                # Return JSON data
                return response.json()

            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Request attempt {attempt + 1} failed: {e}")

                # Log failed request
                self.log_api_request(
                    endpoint.name,
                    endpoint.url,
                    getattr(e.response, 'status_code', 0) if hasattr(e, 'response') and e.response else 0,
                    0,
                    False,
                    str(e)
                )

                if attempt == retries:
                    logger.error(f"❌ All {retries + 1} attempts failed for {endpoint.name}")
                    return None

            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error: {e}")
                return None

        # Rate limiting between requests
        time.sleep(endpoint.rate_limit_delay)
        return None

    def log_api_request(self, api_name: str, url: str, status_code: int,
                       response_size: int, success: bool, error_message: str = None):
        """
        Log API request details to the database.

        Args:
            api_name (str): Name of the API
            url (str): Request URL
            status_code (int): HTTP status code
            response_size (int): Size of response in bytes
            success (bool): Whether request was successful
            error_message (str): Error message if any
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO api_fetch_logs
                    (api_name, endpoint_url, status_code, response_size, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (api_name, url, status_code, response_size, success, error_message))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"❌ Failed to log API request: {e}")

    def fetch_and_store_weather_data(self, cities: List[str] = None):
        """
        Fetch weather data for specified cities and store in database.

        Note: This uses a demo API that might require an API key for full functionality.
        For educational purposes, we'll use a mock response structure.

        Args:
            cities (List[str]): List of city names to fetch weather for
        """
        if cities is None:
            cities = ["London", "New York", "Tokyo", "Sydney", "Paris"]

        logger.info(f"🌤️ Fetching weather data for {len(cities)} cities")

        # For demonstration, we'll create realistic sample data
        # In a real implementation, you'd use the actual OpenWeatherMap API
        import random

        for city in cities:
            # Simulate realistic weather data
            weather_data = self.generate_sample_weather_data(city)

            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO weather_data
                        (city_name, country, temperature, feels_like, humidity, pressure,
                         weather_main, weather_description, wind_speed, wind_direction,
                         cloudiness, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        weather_data['city_name'],
                        weather_data['country'],
                        weather_data['temperature'],
                        weather_data['feels_like'],
                        weather_data['humidity'],
                        weather_data['pressure'],
                        weather_data['weather_main'],
                        weather_data['weather_description'],
                        weather_data['wind_speed'],
                        weather_data['wind_direction'],
                        weather_data['cloudiness'],
                        json.dumps(weather_data)
                    ))
                    conn.commit()

                logger.info(f"✅ Stored weather data for {city}")

            except sqlite3.Error as e:
                logger.error(f"❌ Failed to store weather data for {city}: {e}")

            # Rate limiting
            time.sleep(0.5)

    def generate_sample_weather_data(self, city: str) -> Dict:
        """
        Generate realistic sample weather data for demonstration.

        In a real implementation, this would be the actual API response.
        """
        import random

        weather_conditions = [
            ("Clear", "clear sky"),
            ("Clouds", "few clouds"),
            ("Clouds", "scattered clouds"),
            ("Clouds", "overcast clouds"),
            ("Rain", "light rain"),
            ("Rain", "moderate rain"),
            ("Snow", "light snow"),
            ("Mist", "mist")
        ]

        countries = {
            "London": "GB",
            "New York": "US",
            "Tokyo": "JP",
            "Sydney": "AU",
            "Paris": "FR"
        }

        main_weather, description = random.choice(weather_conditions)
        base_temp = random.uniform(-10, 35)  # Celsius

        return {
            'city_name': city,
            'country': countries.get(city, "XX"),
            'temperature': round(base_temp, 1),
            'feels_like': round(base_temp + random.uniform(-3, 3), 1),
            'humidity': random.randint(30, 90),
            'pressure': random.randint(980, 1030),
            'weather_main': main_weather,
            'weather_description': description,
            'wind_speed': round(random.uniform(0, 15), 1),
            'wind_direction': random.randint(0, 360),
            'cloudiness': random.randint(0, 100)
        }

    def fetch_and_store_posts_data(self):
        """
        Fetch sample posts from JSONPlaceholder API and store in database.

        This demonstrates working with a real, free API.
        """
        logger.info("📝 Fetching posts data from JSONPlaceholder API")

        endpoint = self.api_endpoints['jsonplaceholder']
        data = self.make_api_request(endpoint)

        if data:
            try:
                # Store each post in the json_data table
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    for post in data[:10]:  # Limit to first 10 posts for demo
                        # Extract key fields for easier querying
                        extracted_fields = {
                            'title': post.get('title', ''),
                            'user_id': post.get('userId', ''),
                            'post_id': post.get('id', '')
                        }

                        cursor.execute('''
                            INSERT INTO json_data
                            (source_api, data_type, json_content, extracted_fields)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            'jsonplaceholder',
                            'blog_post',
                            json.dumps(post),
                            json.dumps(extracted_fields)
                        ))

                    conn.commit()
                    logger.info(f"✅ Stored {len(data[:10])} blog posts")

            except sqlite3.Error as e:
                logger.error(f"❌ Failed to store posts data: {e}")

    def fetch_and_store_user_profiles(self, count: int = 5):
        """
        Fetch random user profiles and store in database.

        Args:
            count (int): Number of user profiles to fetch
        """
        logger.info(f"👥 Fetching {count} random user profiles")

        endpoint = self.api_endpoints['random_user']

        for i in range(count):
            params = {'results': 1}  # Fetch one user at a time
            data = self.make_api_request(endpoint, params)

            if data and 'results' in data and len(data['results']) > 0:
                user = data['results'][0]

                try:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO user_profiles
                            (first_name, last_name, email, phone, country, city,
                             age, gender, profile_picture_url)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            user['name']['first'],
                            user['name']['last'],
                            user['email'],
                            user['phone'],
                            user['location']['country'],
                            user['location']['city'],
                            user['dob']['age'],
                            user['gender'],
                            user['picture']['large']
                        ))
                        conn.commit()

                    logger.info(f"✅ Stored user profile {i+1}: {user['name']['first']} {user['name']['last']}")

                except sqlite3.Error as e:
                    logger.error(f"❌ Failed to store user profile {i+1}: {e}")

            # Rate limiting
            time.sleep(1)

    def fetch_ip_info(self):
        """
        Fetch IP information from HTTPBin and store in database.

        This demonstrates working with simple API responses.
        """
        logger.info("🌐 Fetching IP information")

        endpoint = self.api_endpoints['httpbin']
        data = self.make_api_request(endpoint)

        if data:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO json_data
                        (source_api, data_type, json_content, extracted_fields)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        'httpbin',
                        'ip_info',
                        json.dumps(data),
                        json.dumps({'origin_ip': data.get('origin', '')})
                    ))
                    conn.commit()

                logger.info(f"✅ Stored IP information: {data.get('origin', 'Unknown')}")

            except sqlite3.Error as e:
                logger.error(f"❌ Failed to store IP information: {e}")

    def analyze_stored_data(self):
        """
        Analyze the data stored in the database and generate insights.

        This demonstrates how to work with the stored API data.
        """
        logger.info("📊 Analyzing stored data")

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get summary of API requests
                df_logs = pd.read_sql_query('''
                    SELECT api_name, COUNT(*) as request_count,
                           SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                           AVG(response_size) as avg_response_size
                    FROM api_fetch_logs
                    GROUP BY api_name
                ''', conn)

                print("\n📈 API Request Summary:")
                print("=" * 50)
                print(df_logs.to_string(index=False))

                # Weather data analysis
                weather_count = pd.read_sql_query('''
                    SELECT COUNT(*) as count FROM weather_data
                ''', conn).iloc[0]['count']

                if weather_count > 0:
                    df_weather = pd.read_sql_query('''
                        SELECT city_name, temperature, humidity, weather_main
                        FROM weather_data
                        ORDER BY timestamp DESC
                    ''', conn)

                    print(f"\n🌤️ Weather Data ({weather_count} records):")
                    print("=" * 50)
                    print(df_weather.to_string(index=False))

                # User profiles analysis
                user_count = pd.read_sql_query('''
                    SELECT COUNT(*) as count FROM user_profiles
                ''', conn).iloc[0]['count']

                if user_count > 0:
                    df_users = pd.read_sql_query('''
                        SELECT first_name, last_name, country, age, gender
                        FROM user_profiles
                        ORDER BY timestamp DESC
                    ''', conn)

                    print(f"\n👥 User Profiles ({user_count} records):")
                    print("=" * 50)
                    print(df_users.to_string(index=False))

                # JSON data summary
                df_json = pd.read_sql_query('''
                    SELECT source_api, data_type, COUNT(*) as count
                    FROM json_data
                    GROUP BY source_api, data_type
                ''', conn)

                if not df_json.empty:
                    print(f"\n📄 JSON Data Summary:")
                    print("=" * 50)
                    print(df_json.to_string(index=False))

        except sqlite3.Error as e:
            logger.error(f"❌ Error analyzing data: {e}")

    def export_data_to_csv(self, output_dir: str = "exported_data"):
        """
        Export stored data to CSV files for further analysis.

        Args:
            output_dir (str): Directory to save CSV files
        """
        logger.info(f"📤 Exporting data to CSV files in {output_dir}/")

        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Export each table
                tables = ['api_fetch_logs', 'weather_data', 'json_data', 'user_profiles']

                for table in tables:
                    df = pd.read_sql_query(f'SELECT * FROM {table}', conn)
                    if not df.empty:
                        csv_path = Path(output_dir) / f"{table}.csv"
                        df.to_csv(csv_path, index=False)
                        logger.info(f"✅ Exported {len(df)} records from {table} to {csv_path}")
                    else:
                        logger.info(f"ℹ️ No data to export from {table}")

        except sqlite3.Error as e:
            logger.error(f"❌ Error exporting data: {e}")

    def cleanup_old_data(self, days_old: int = 30):
        """
        Clean up old data from the database.

        Args:
            days_old (int): Remove data older than this many days
        """
        logger.info(f"🧹 Cleaning up data older than {days_old} days")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Clean up old logs
                cursor.execute('''
                    DELETE FROM api_fetch_logs
                    WHERE fetch_timestamp < datetime('now', '-{} days')
                '''.format(days_old))

                cursor.execute('''
                    DELETE FROM weather_data
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days_old))

                cursor.execute('''
                    DELETE FROM json_data
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days_old))

                cursor.execute('''
                    DELETE FROM user_profiles
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days_old))

                conn.commit()
                logger.info("✅ Old data cleaned up successfully")

        except sqlite3.Error as e:
            logger.error(f"❌ Error cleaning up data: {e}")

def demonstrate_error_handling():
    """
    Demonstrate various error handling scenarios.
    """
    print("\n🚨 Error Handling Demonstrations:")
    print("=" * 50)

    fetcher = APIDataFetcher("test_error_handling.db")

    # Test with invalid URL
    invalid_endpoint = APIEndpoint(
        name="Invalid API",
        url="https://invalid-url-that-does-not-exist.com/api",
        headers={}
    )

    print("1. Testing invalid URL...")
    result = fetcher.make_api_request(invalid_endpoint)
    print(f"   Result: {result}")

    # Test with valid URL but invalid endpoint
    invalid_path_endpoint = APIEndpoint(
        name="Invalid Path API",
        url="https://httpbin.org/invalid-path",
        headers={}
    )

    print("2. Testing valid URL but invalid path...")
    result = fetcher.make_api_request(invalid_path_endpoint)
    print(f"   Result: {result}")

    print("✅ Error handling demonstrations completed")

def create_integration_examples():
    """
    Show examples of how to integrate with real-world APIs.
    """
    print("\n🔗 Real-World API Integration Examples:")
    print("=" * 50)

    examples = {
        "Weather APIs": {
            "OpenWeatherMap": "https://openweathermap.org/api",
            "WeatherAPI": "https://www.weatherapi.com/",
            "AccuWeather": "https://developer.accuweather.com/"
        },
        "Social Media APIs": {
            "Twitter API": "https://developer.twitter.com/",
            "Instagram Basic Display": "https://developers.facebook.com/docs/instagram-basic-display-api/",
            "LinkedIn API": "https://developer.linkedin.com/"
        },
        "Financial APIs": {
            "Alpha Vantage": "https://www.alphavantage.co/",
            "Yahoo Finance": "https://github.com/ranaroussi/yfinance",
            "CoinGecko": "https://www.coingecko.com/en/api"
        },
        "News APIs": {
            "NewsAPI": "https://newsapi.org/",
            "Guardian API": "https://open-platform.theguardian.com/",
            "Reddit API": "https://www.reddit.com/dev/api/"
        }
    }

    for category, apis in examples.items():
        print(f"\n{category}:")
        for name, url in apis.items():
            print(f"  • {name}: {url}")

    print(f"\n💡 Integration Tips:")
    print("- Always read the API documentation thoroughly")
    print("- Respect rate limits and implement proper delays")
    print("- Store API keys securely in environment variables")
    print("- Implement proper error handling and logging")
    print("- Consider caching responses to reduce API calls")
    print("- Test with small datasets first")

def main():
    """
    Main function demonstrating the complete API data storage workflow.
    """
    print("🚀 Welcome to JG's API Data Storage Demo!")
    print("=" * 50)

    try:
        # Initialize the API data fetcher
        fetcher = APIDataFetcher("jg_api_demo.db")

        print("\n1. 🌤️ Fetching and storing weather data...")
        fetcher.fetch_and_store_weather_data()

        print("\n2. 📝 Fetching and storing blog posts...")
        fetcher.fetch_and_store_posts_data()

        print("\n3. 👥 Fetching and storing user profiles...")
        fetcher.fetch_and_store_user_profiles(count=3)

        print("\n4. 🌐 Fetching IP information...")
        fetcher.fetch_ip_info()

        print("\n5. 📊 Analyzing stored data...")
        fetcher.analyze_stored_data()

        print("\n6. 📤 Exporting data to CSV...")
        fetcher.export_data_to_csv()

        print("\n✅ API data storage demonstration completed successfully!")

        # Show database file info
        db_path = Path("jg_api_demo.db")
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"\n📁 Database file: {db_path.absolute()}")
            print(f"   Size: {size_mb:.2f} MB")

    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        print("💡 Troubleshooting tips:")
        print("   - Check your internet connection")
        print("   - Ensure you have write permissions in the current directory")
        print("   - Try running with different API endpoints")

    # Demonstrate error handling
    demonstrate_error_handling()

    # Show integration examples
    create_integration_examples()

    print("\n🎓 Learning Summary:")
    print("- Making HTTP requests to various APIs")
    print("- JSON data processing and validation")
    print("- SQLite database design and operations")
    print("- Error handling and retry mechanisms")
    print("- Data analysis with Pandas")
    print("- Professional logging and monitoring")

    print("\n💡 Next Steps:")
    print("- Sign up for API keys from services you want to use")
    print("- Implement authentication for private APIs")
    print("- Add data transformation and cleaning logic")
    print("- Set up automated data collection schedules")
    print("- Create data visualization dashboards")

if __name__ == "__main__":
    main()