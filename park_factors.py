"""
Park factors import module for MLB betting system.
Imports park factor data from external sources.
"""

import pandas as pd
import gspread
import requests
from io import StringIO


def import_park_factors(spreadsheet: gspread.Spreadsheet, csv_url: str):
    """
    Import park factors data into the Google Sheet.
    
    Args:
        spreadsheet: The Google Sheets spreadsheet object
        csv_url: URL to the park factors CSV file
    """
    try:
        worksheet = spreadsheet.worksheet("Park Factors")
        worksheet.clear()
        
        print("📊 Fetching park factors data...")
        
        # Try to fetch the CSV data
        try:
            response = requests.get(csv_url, timeout=10)
            response.raise_for_status()
            
            # Read CSV from the response
            df = pd.read_csv(StringIO(response.text))
            
            # Add headers
            headers = list(df.columns)
            worksheet.append_row(headers)
            
            # Add data rows
            rows_added = 0
            for row in df.values.tolist():
                # Convert any NaN values to empty strings
                clean_row = ['' if pd.isna(val) else str(val) for val in row]
                worksheet.append_row(clean_row)
                rows_added += 1
            
            print(f"✅ Park factors imported successfully. Added {rows_added} rows.")
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Could not fetch park factors from URL: {e}")
            print("Creating park factors worksheet with sample data...")
            create_sample_park_factors(worksheet)
            
        except Exception as e:
            print(f"⚠️  Error processing park factors data: {e}")
            print("Creating park factors worksheet with sample data...")
            create_sample_park_factors(worksheet)
            
    except Exception as e:
        print(f"❌ Error setting up Park Factors worksheet: {str(e)}")


def create_sample_park_factors(worksheet: gspread.Worksheet):
    """
    Create sample park factors data when external source is unavailable.
    
    Args:
        worksheet: The Park Factors worksheet
    """
    headers = ["Park Name", "Runs Factor", "HR Factor", "Hits Factor", "Notes"]
    worksheet.append_row(headers)
    
    # Sample park factors data (approximate values)
    sample_data = [
        ["Coors Field", "1.15", "1.08", "1.12", "High altitude"],
        ["Fenway Park", "1.05", "0.95", "1.02", "Green Monster"],
        ["Yankee Stadium", "1.02", "1.05", "1.01", "Short right field"],
        ["Petco Park", "0.95", "0.92", "0.97", "Pitcher friendly"],
        ["Marlins Park", "0.96", "0.94", "0.98", "Retractable roof"],
        ["Tropicana Field", "0.98", "0.96", "0.99", "Dome stadium"],
        ["Kauffman Stadium", "0.97", "0.93", "0.98", "Large outfield"],
        ["Minute Maid Park", "1.01", "1.03", "1.00", "Left field quirks"],
        ["Oracle Park", "0.94", "0.89", "0.96", "Cool weather, wind"],
        ["Comerica Park", "0.99", "0.97", "0.99", "Spacious dimensions"]
    ]
    
    for row in sample_data:
        worksheet.append_row(row)
    
    print(f"✅ Sample park factors created with {len(sample_data)} parks.")


if __name__ == "__main__":
    print("This module imports park factors data for MLB betting analysis.")
    print("Run 'python run_all.py' to execute the full system.")