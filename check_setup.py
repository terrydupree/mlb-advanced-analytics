"""
Utility script to check Google service account credentials and test connection.
Run this to verify your setup before running the main application.
"""

import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def check_credentials():
    """Check if credentials file exists and show service account email."""
    creds_path = "credentials.json"
    
    if not os.path.exists(creds_path):
        print("❌ credentials.json file not found!")
        print("Please download your service account credentials and save as 'credentials.json'")
        return None
    
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        service_account_email = creds_data.get('client_email', 'Not found')
        project_id = creds_data.get('project_id', 'Not found')
        
        print("✅ Credentials file found!")
        print(f"📧 Service Account Email: {service_account_email}")
        print(f"🏗️  Project ID: {project_id}")
        print(f"\n📋 To share your Google Sheet with the service account:")
        print(f"   1. Open your Google Sheet")
        print(f"   2. Click the 'Share' button")
        print(f"   3. Add this email: {service_account_email}")
        print(f"   4. Give it 'Editor' permissions")
        
        return service_account_email
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials.json file!")
        return None
    except Exception as e:
        print(f"❌ Error reading credentials: {str(e)}")
        return None

def test_connection(sheet_id):
    """Test connection to Google Sheets."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        
        # Try to open the sheet
        spreadsheet = client.open_by_key(sheet_id)
        print(f"✅ Successfully connected to Google Sheet!")
        print(f"📊 Sheet Title: {spreadsheet.title}")
        print(f"🔗 Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
        # List worksheets
        worksheets = spreadsheet.worksheets()
        print(f"📑 Found {len(worksheets)} worksheet(s):")
        for ws in worksheets:
            print(f"   - {ws.title}")
        
        return True
        
    except gspread.SpreadsheetNotFound:
        print("❌ Google Sheet not found!")
        print("Make sure the service account email has access to the sheet.")
        return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Google Sheets Connection Checker")
    print("=" * 40)
    
    # Check credentials
    service_email = check_credentials()
    
    if service_email:
        print("\n" + "=" * 40)
        
        # Test with the sheet ID from run_all.py
        sheet_id = "1EZjH0UllYLvHp4Qq6VnmomtBqNSYZZCYGYEV7ErMgtQ"
        print(f"🧪 Testing connection to sheet: {sheet_id}")
        
        success = test_connection(sheet_id)
        
        if success:
            print("\n✅ All checks passed! Your setup is ready.")
        else:
            print(f"\n❌ Connection failed. Please share the sheet with: {service_email}")
    
    print("\n" + "=" * 40)
    print("Run this script anytime to verify your Google Sheets setup!")
