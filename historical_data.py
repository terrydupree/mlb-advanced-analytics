"""
Historical data fetching module for MLB betting system.
Fetches historical game data from SportRadar API.
"""

import requests
import datetime
import time
import gspread
from typing import Optional


def fetch_historical(spreadsheet: gspread.Spreadsheet, api_key: str, days: int = 14):
    """
    Fetch historical MLB game data and populate the Historical Data worksheet.
    
    Args:
        spreadsheet: The Google Sheets spreadsheet object
        api_key: SportRadar API key
        days: Number of days of historical data to fetch
    """
    # Check if API key is set
    if not api_key or api_key == "YOUR-SPORTRADAR-KEY":
        print("⚠️  SportRadar API key not configured. Skipping historical data fetch.")
        print("To get historical data:")
        print("1. Sign up at https://developer.sportradar.com/")
        print("2. Get your MLB API key")
        print("3. Update SPORTRADAR_KEY in run_all.py")
        
        # Create empty worksheet with headers
        try:
            worksheet = spreadsheet.worksheet("Historical Data")
            worksheet.clear()
            headers = ["Date", "Home", "Away", "Home Runs", "Away Runs", "Winner"]
            worksheet.append_row(headers)
            print("📊 Historical Data worksheet created with headers only.")
        except Exception as e:
            print(f"Error setting up Historical Data worksheet: {e}")
        return
    
    try:
        worksheet = spreadsheet.worksheet("Historical Data")
        worksheet.clear()
        headers = ["Date", "Home", "Away", "Home Runs", "Away Runs", "Winner"]
        worksheet.append_row(headers)
        
        print(f"📊 Fetching {days} days of historical MLB data...")
        games_added = 0
        
        for i in range(days):
            date = (datetime.datetime.utcnow() - datetime.timedelta(days=i)).strftime('%Y/%m/%d')
            endpoint = f"https://api.sportradar.com/mlb/trial/v7/en/games/{date}/schedule.json?api_key={api_key}"
            
            try:
                resp = requests.get(endpoint, timeout=10)
                if resp.status_code == 403:
                    print(f"⚠️  API access denied for {date} (403) - Check your API key permissions")
                    continue
                elif resp.status_code == 429:
                    print(f"⚠️  Rate limit hit for {date} (429) - Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                elif resp.status_code != 200:
                    print(f"⚠️  API error {resp.status_code} for {date}")
                    continue
                
                data = resp.json()
                day_games = 0
                
                for g in data.get('games', []):
                    winner = ''
                    if g.get('status') == 'completed' and g.get('scoring'):
                        home_runs = g['scoring'].get('home_runs', 0)
                        away_runs = g['scoring'].get('away_runs', 0)
                        
                        if home_runs > away_runs:
                            winner = g.get('home', {}).get('name', 'Home')
                        elif away_runs > home_runs:
                            winner = g.get('away', {}).get('name', 'Away')
                        else:
                            winner = 'Tie'
                        
                        row = [
                            date,
                            g.get('home', {}).get('name', 'Unknown'),
                            g.get('away', {}).get('name', 'Unknown'),
                            home_runs,
                            away_runs,
                            winner
                        ]
                        worksheet.append_row(row)
                        games_added += 1
                        day_games += 1
                
                if day_games > 0:
                    print(f"✅ {date}: Added {day_games} completed games")
                else:
                    print(f"📅 {date}: No completed games found")
                
                # Rate limiting - be nice to the API
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Network error for {date}: {e}")
                continue
            except Exception as e:
                print(f"⚠️  Error processing {date}: {e}")
                continue
        
        print(f"✅ Historical data fetch completed. Added {games_added} total games.")
        
    except Exception as e:
        print(f"❌ Error in historical data fetch: {str(e)}")


if __name__ == "__main__":
    print("This module fetches historical MLB data from SportRadar API.")
    print("Run 'python run_all.py' to execute the full system.")