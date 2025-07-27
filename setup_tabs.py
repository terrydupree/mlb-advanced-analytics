"""
Setup Google Sheets tabs/worksheets for the MLB betting system.
This module creates the necessary worksheets with proper headers.
"""

import gspread
from typing import Dict, List


def setup_sheets(spreadsheet: gspread.Spreadsheet):
    """
    Set up all necessary worksheets in the Google Sheet with proper headers.
    
    Args:
        spreadsheet: The Google Sheets spreadsheet object
    """
    tabs = {
        "Game Analyzer": [
            "Game ID", "Home Team", "Away Team", "Scheduled", "Venue", "Status",
            "Moneyline Home", "Moneyline Away", "Runline Home", "Runline Away", 
            "O/U Odds", "Team Total Home", "Team Total Away", 
            "Avg Home Runs (λ)", "Avg Away Runs (λ)", "k (runs)",
            "Poisson Home", "Poisson Away", "Implied Prob Home", "Implied Prob Away",
            "EV Home", "EV Away"
        ],
        "Historical Data": [
            "Date", "Home", "Away", "Home Runs", "Away Runs", "Winner"
        ],
        "Park Factors": [
            "Park Name", "Runs", "HR", "2B", "3B"
        ],
        "Pitcher vs Batter": [
            "Pitcher", "Batter", "AB", "Hits", "HR", "K", "AVG", "OBP"
        ],
        "EV Poisson": [
            "Team", "Avg Runs Scored", "Avg Runs Allowed", "Games Played", "Last Updated"
        ]
    }
    
    print("Setting up Google Sheets worksheets...")
    
    for tab, headers in tabs.items():
        try:
            # Try to get existing worksheet
            worksheet = spreadsheet.worksheet(tab)
            print(f"  Found existing worksheet: {tab}")
            # Clear existing content
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            # Create new worksheet if it doesn't exist
            print(f"  Creating new worksheet: {tab}")
            worksheet = spreadsheet.add_worksheet(
                title=tab, 
                rows=1000, 
                cols=len(headers)
            )
        
        # Add headers to the worksheet
        worksheet.append_row(headers)
        print(f"  ✅ {tab} worksheet ready with {len(headers)} columns")
    
    print("All worksheets have been set up successfully!")


if __name__ == "__main__":
    print("This module sets up Google Sheets worksheets for the MLB betting system.")
    print("Run 'python run_all.py' to execute the full system.")