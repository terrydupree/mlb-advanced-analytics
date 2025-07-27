import os
import requests
import csv
from datetime import datetime

def get_games_today():
    """Get today's MLB games. Uses sample data if API key not available."""
    key = os.getenv("APISPORTS_KEY")
    
    if not key:
        print("⚠️  APISPORTS_KEY not found. Using sample game data...")
        return [
            {
                "id": 1,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "teams": {
                    "home": {"name": "New York Yankees"},
                    "away": {"name": "Boston Red Sox"}
                },
                "status": {"short": "NS"}
            },
            {
                "id": 2,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "teams": {
                    "home": {"name": "Los Angeles Dodgers"},
                    "away": {"name": "San Francisco Giants"}
                },
                "status": {"short": "NS"}
            }
        ]
    
    try:
        url = "https://v1.baseball.api-sports.io/games?date=today"
        headers = {"x-apisports-key": key}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()["response"]
    except Exception as e:
        print(f"⚠️  Error fetching games: {e}. Using sample data...")
        return get_games_today()  # Fallback to sample data

def get_odds():
    """Odds functionality removed - system focuses on pure analytics."""
    print("📊 Odds module disabled - focusing on statistical analysis only")
    return []

def get_park_factors(csv_path):
    """Get park factors from CSV or use sample data if file not found."""
    factors = []
    
    try:
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                factors.append(row)
        print(f"✅ Loaded park factors from {csv_path}")
        return factors
    except FileNotFoundError:
        print(f"⚠️  Park factors file not found: {csv_path}. Using sample data...")
        return [
            {"team": "COL", "park_factor": "1.15", "hr_factor": "1.25"},
            {"team": "BOS", "park_factor": "1.05", "hr_factor": "1.10"}, 
            {"team": "TEX", "park_factor": "1.03", "hr_factor": "1.08"},
            {"team": "CIN", "park_factor": "1.02", "hr_factor": "1.05"},
            {"team": "NYY", "park_factor": "1.01", "hr_factor": "1.03"},
            {"team": "LAA", "park_factor": "0.99", "hr_factor": "0.98"},
            {"team": "ATL", "park_factor": "0.98", "hr_factor": "0.97"},
            {"team": "LAD", "park_factor": "0.95", "hr_factor": "0.92"},
            {"team": "SF", "park_factor": "0.92", "hr_factor": "0.88"},
            {"team": "SD", "park_factor": "0.90", "hr_factor": "0.85"}
        ]
    except Exception as e:
        print(f"⚠️  Error loading park factors: {e}. Using sample data...")
        return get_park_factors(csv_path)  # Fallback