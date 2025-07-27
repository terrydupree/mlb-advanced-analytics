import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def connect_sheet(sheet_id):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)

def update_sheets(gs, analysis):
    """Update Google Sheets with statistical analysis results."""
    try:
        # Try lowercase first, then title case
        worksheet_name = "game_analyzer"
        try:
            worksheet = gs.worksheet(worksheet_name)
        except:
            worksheet_name = "Game Analyzer"
            worksheet = gs.worksheet(worksheet_name)
        
        print(f"📊 Updating worksheet: {worksheet_name}")
        worksheet.clear()
        
        # Updated headers for statistical analysis (no betting/odds)
        headers = [
            "Home Team", "Away Team", "λ Home", "λ Away", "k", 
            "Poisson Home", "Poisson Away", "Win Prob Home", "Win Prob Away", 
            "Statistical Edge", "Analysis Type"
        ]
        worksheet.append_row(headers)
        
        # Add analysis data
        for row in analysis["game_analyzer"]:
            worksheet.append_row(row)
        
        print(f"✅ Updated {len(analysis['game_analyzer'])} games in Google Sheets")
        
    except Exception as e:
        print(f"❌ Error updating sheets: {e}")
        print("💡 Make sure the worksheet exists in your Google Sheet")