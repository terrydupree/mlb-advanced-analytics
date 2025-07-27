import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import sys

def get_gsheet(sheet_name, creds_path="credentials.json"):
    """
    Connect to Google Sheets using service account credentials.
    
    Args:
        sheet_name: Name of the Google Sheet to open
        creds_path: Path to the credentials JSON file
    
    Returns:
        gspread.Spreadsheet object
    """
    # Check if credentials file exists
    if not os.path.exists(creds_path):
        print(f"Error: Credentials file '{creds_path}' not found!")
        print("\nTo set up Google Sheets API credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API")
        print("4. Create Service Account credentials")
        print("5. Download the JSON key file and rename it to 'credentials.json'")
        print("6. Place it in your project directory")
        print(f"\nA template file 'credentials_template.json' has been created.")
        print("Replace the placeholder values with your actual credentials.")
        sys.exit(1)
    
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        
        # Try to open the spreadsheet by ID first, then by name
        try:
            # If sheet_name looks like an ID (contains alphanumeric characters), try opening by ID
            if len(sheet_name) > 20 and sheet_name.replace('-', '').replace('_', '').isalnum():
                spreadsheet = client.open_by_key(sheet_name)
                print(f"Successfully connected to Google Sheet by ID: '{sheet_name}'")
            else:
                spreadsheet = client.open(sheet_name)
                print(f"Successfully connected to Google Sheet by name: '{sheet_name}'")
        except gspread.SpreadsheetNotFound:
            # If opening by ID failed, try by name as fallback
            try:
                spreadsheet = client.open(sheet_name)
                print(f"Successfully connected to Google Sheet by name: '{sheet_name}'")
            except gspread.SpreadsheetNotFound:
                raise gspread.SpreadsheetNotFound
        
        return spreadsheet
        
    except gspread.SpreadsheetNotFound:
        print(f"Error: Google Sheet '{sheet_name}' not found!")
        print("Make sure:")
        print("1. The sheet name/ID is correct")
        print("2. The service account email has access to the sheet")
        print("3. The sheet exists in your Google Drive")
        print("4. If using Sheet ID, the service account has been shared with the sheet")
        print("\nTo share with service account:")
        print("1. Open your Google Sheet")
        print("2. Click 'Share' button")
        print("3. Add the service account email (from credentials.json)")
        print("4. Give it 'Editor' permissions")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error connecting to Google Sheets: {str(e)}")
        print("Please check your credentials and try again.")
        sys.exit(1)