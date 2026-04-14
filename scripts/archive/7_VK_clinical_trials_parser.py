# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests",
#     "pandas",
#     "beautifulsoup4",
#     "xmltodict",
# ]
# ///

"""
VK Clinical Trials Parser
Student: VK
Description: Parse through clinical trials.gov and other trial registries

This script demonstrates how to:
1. Query the ClinicalTrials.gov API
2. Parse XML/JSON responses
3. Extract key trial information
4. Export data to various formats (CSV, JSON)
5. Filter and search trials by criteria

Educational Focus:
- Working with REST APIs
- XML/JSON data parsing
- Data cleaning and transformation
- Pandas data manipulation
"""

import requests
import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import time
from typing import Dict, List, Optional
import sys
from pathlib import Path

class ClinicalTrialsParser:
    """
    A comprehensive parser for clinical trials data from ClinicalTrials.gov

    This class provides methods to:
    - Search for trials based on various criteria
    - Parse trial details from API responses
    - Export data in multiple formats
    """

    def __init__(self):
        """Initialize the parser with API endpoints and rate limiting"""
        # ClinicalTrials.gov API endpoints
        self.base_url = "https://clinicaltrials.gov/api"
        self.search_url = f"{self.base_url}/query/study_fields"
        self.full_study_url = f"{self.base_url}/query/full_studies"

        # Rate limiting - be respectful to the API
        self.request_delay = 1  # seconds between requests

        # Common fields we want to extract from trials
        self.standard_fields = [
            "NCTId",
            "BriefTitle",
            "OfficialTitle",
            "OverallStatus",
            "Phase",
            "StudyType",
            "Condition",
            "InterventionName",
            "PrimaryCompletionDate",
            "EnrollmentCount",
            "LocationCountry",
            "Sponsor",
            "CollaboratorName"
        ]

    def search_trials(self,
                     condition: str = None,
                     intervention: str = None,
                     status: str = None,
                     country: str = None,
                     max_results: int = 100) -> Dict:
        """
        Search for clinical trials based on specified criteria

        Args:
            condition: Disease or condition (e.g., "diabetes", "cancer")
            intervention: Treatment or intervention (e.g., "metformin", "surgery")
            status: Trial status (e.g., "Recruiting", "Completed")
            country: Country where trial is conducted
            max_results: Maximum number of results to return

        Returns:
            Dictionary containing search results and metadata
        """
        print(f"🔍 Searching clinical trials...")

        # Build search parameters
        params = {
            "expr": self._build_search_expression(condition, intervention, status, country),
            "fields": ",".join(self.standard_fields),
            "min_rnk": 1,
            "max_rnk": max_results,
            "fmt": "json"
        }

        try:
            # Make API request with rate limiting
            time.sleep(self.request_delay)
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()

            data = response.json()

            print(f"✅ Found {data.get('StudyFieldsResponse', {}).get('NStudiesFound', 0)} total studies")
            print(f"📊 Retrieved {len(data.get('StudyFieldsResponse', {}).get('StudyFields', []))} studies in this batch")

            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching trials: {e}")
            return {}

    def _build_search_expression(self, condition, intervention, status, country) -> str:
        """
        Build a search expression for the ClinicalTrials.gov API

        The API uses a specific query syntax for combining search terms
        """
        expressions = []

        if condition:
            expressions.append(f"AREA[Condition]{condition}")
        if intervention:
            expressions.append(f"AREA[InterventionName]{intervention}")
        if status:
            expressions.append(f"AREA[OverallStatus]{status}")
        if country:
            expressions.append(f"AREA[LocationCountry]{country}")

        # If no specific criteria, search for recent studies
        if not expressions:
            expressions.append("AREA[StudyFirstPostDate]RANGE[2023-01-01,MAX]")

        return " AND ".join(expressions)

    def get_detailed_study(self, nct_id: str) -> Dict:
        """
        Get detailed information for a specific study by NCT ID

        Args:
            nct_id: The NCT identifier (e.g., "NCT04123456")

        Returns:
            Dictionary containing detailed study information
        """
        print(f"📋 Getting detailed information for study {nct_id}...")

        params = {
            "expr": f"AREA[NCTId]{nct_id}",
            "fmt": "json"
        }

        try:
            time.sleep(self.request_delay)
            response = requests.get(self.full_study_url, params=params)
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting study details: {e}")
            return {}

    def parse_trials_to_dataframe(self, search_results: Dict) -> pd.DataFrame:
        """
        Convert API search results to a clean pandas DataFrame

        Args:
            search_results: Raw API response from search_trials()

        Returns:
            Cleaned pandas DataFrame with trial information
        """
        print("🔄 Converting results to DataFrame...")

        study_fields = search_results.get('StudyFieldsResponse', {}).get('StudyFields', [])

        if not study_fields:
            print("⚠️  No study data found to convert")
            return pd.DataFrame()

        # Convert to list of dictionaries for DataFrame creation
        trials_data = []

        for study in study_fields:
            trial_dict = {}

            # Extract each field, handling missing data gracefully
            for field in self.standard_fields:
                field_data = study.get(field, [])

                # Most fields return lists, so we need to extract the values
                if isinstance(field_data, list):
                    if len(field_data) > 0:
                        # For single values, take the first item
                        if field in ["NCTId", "BriefTitle", "OfficialTitle", "OverallStatus", "StudyType"]:
                            trial_dict[field] = field_data[0] if field_data else ""
                        # For lists that might have multiple values, join them
                        else:
                            trial_dict[field] = "; ".join(field_data) if field_data else ""
                    else:
                        trial_dict[field] = ""
                else:
                    trial_dict[field] = str(field_data) if field_data else ""

            trials_data.append(trial_dict)

        # Create DataFrame
        df = pd.DataFrame(trials_data)

        # Clean up data types and formats
        df = self._clean_dataframe(df)

        print(f"✅ Created DataFrame with {len(df)} trials and {len(df.columns)} columns")
        return df

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and format the DataFrame for better usability"""

        # Convert enrollment count to numeric
        if 'EnrollmentCount' in df.columns:
            df['EnrollmentCount'] = pd.to_numeric(df['EnrollmentCount'], errors='coerce')

        # Parse dates if present
        date_columns = ['PrimaryCompletionDate']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Clean up phase information
        if 'Phase' in df.columns:
            df['Phase'] = df['Phase'].str.replace('Phase ', '', regex=False)

        return df

    def export_data(self, df: pd.DataFrame, filename: str = None, format: str = "csv"):
        """
        Export trial data to various formats

        Args:
            df: DataFrame containing trial data
            filename: Output filename (without extension)
            format: Export format ("csv", "json", "excel")
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clinical_trials_{timestamp}"

        # Ensure we're in the scripts directory for output
        output_dir = Path(__file__).parent

        if format.lower() == "csv":
            filepath = output_dir / f"{filename}.csv"
            df.to_csv(filepath, index=False)
            print(f"💾 Exported to CSV: {filepath}")

        elif format.lower() == "json":
            filepath = output_dir / f"{filename}.json"
            df.to_json(filepath, orient='records', indent=2)
            print(f"💾 Exported to JSON: {filepath}")

        elif format.lower() == "excel":
            filepath = output_dir / f"{filename}.xlsx"
            df.to_excel(filepath, index=False)
            print(f"💾 Exported to Excel: {filepath}")

        return filepath

    def generate_summary_report(self, df: pd.DataFrame):
        """Generate a summary report of the clinical trials data"""
        print("\n" + "="*50)
        print("📊 CLINICAL TRIALS SUMMARY REPORT")
        print("="*50)

        if df.empty:
            print("No data available for summary")
            return

        print(f"Total Trials: {len(df)}")

        # Status distribution
        if 'OverallStatus' in df.columns:
            print("\n🏥 Trial Status Distribution:")
            status_counts = df['OverallStatus'].value_counts()
            for status, count in status_counts.head(5).items():
                print(f"  {status}: {count}")

        # Phase distribution
        if 'Phase' in df.columns:
            print("\n🧪 Phase Distribution:")
            phase_counts = df['Phase'].value_counts()
            for phase, count in phase_counts.head(5).items():
                print(f"  Phase {phase}: {count}")

        # Top conditions
        if 'Condition' in df.columns:
            print("\n🏥 Top Conditions Studied:")
            # Split multiple conditions and count
            all_conditions = []
            for conditions in df['Condition'].dropna():
                all_conditions.extend([c.strip() for c in conditions.split(';')])
            condition_series = pd.Series(all_conditions)
            top_conditions = condition_series.value_counts().head(5)
            for condition, count in top_conditions.items():
                print(f"  {condition}: {count}")

        # Country distribution
        if 'LocationCountry' in df.columns:
            print("\n🌍 Top Countries:")
            country_data = df['LocationCountry'].dropna()
            all_countries = []
            for countries in country_data:
                all_countries.extend([c.strip() for c in countries.split(';')])
            country_series = pd.Series(all_countries)
            top_countries = country_series.value_counts().head(5)
            for country, count in top_countries.items():
                print(f"  {country}: {count}")

def main():
    """
    Main function demonstrating the clinical trials parser functionality
    """
    print("🏥 VK Clinical Trials Parser - Educational Demo")
    print("=" * 50)

    # Initialize the parser
    parser = ClinicalTrialsParser()

    # Example 1: Search for diabetes trials
    print("\n📚 Example 1: Searching for diabetes trials...")
    diabetes_results = parser.search_trials(
        condition="diabetes",
        status="Recruiting",
        max_results=20
    )

    if diabetes_results:
        df_diabetes = parser.parse_trials_to_dataframe(diabetes_results)
        if not df_diabetes.empty:
            parser.generate_summary_report(df_diabetes)
            # Export to CSV
            parser.export_data(df_diabetes, "diabetes_trials", "csv")

    # Example 2: Search for cancer immunotherapy trials
    print("\n📚 Example 2: Searching for cancer immunotherapy trials...")
    cancer_results = parser.search_trials(
        condition="cancer",
        intervention="immunotherapy",
        max_results=15
    )

    if cancer_results:
        df_cancer = parser.parse_trials_to_dataframe(cancer_results)
        if not df_cancer.empty:
            parser.generate_summary_report(df_cancer)

    # Example 3: Get detailed information for a specific trial
    print("\n📚 Example 3: Getting detailed study information...")
    # Use the first NCT ID from our diabetes search if available
    if 'df_diabetes' in locals() and not df_diabetes.empty and 'NCTId' in df_diabetes.columns:
        first_nct_id = df_diabetes.iloc[0]['NCTId']
        detailed_study = parser.get_detailed_study(first_nct_id)

        if detailed_study:
            print(f"✅ Retrieved detailed information for {first_nct_id}")
            # You could further parse this detailed data as needed

    print("\n🎓 Educational Notes:")
    print("1. Always respect API rate limits when making requests")
    print("2. Handle errors gracefully - APIs can be unreliable")
    print("3. Clean and validate data before analysis")
    print("4. Consider caching results for frequently accessed data")
    print("5. Be aware of data usage policies and terms of service")

if __name__ == "__main__":
    main()