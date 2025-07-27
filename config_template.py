# MLB Betting System Configuration
# Copy this file to config.py and update with your actual values

# Google Sheets Configuration
SPREADSHEET_NAME = "MLB Betting System 2025"  # Replace with your actual Google Sheet name
CREDENTIALS_PATH = "credentials.json"  # Path to your Google service account credentials

# SportRadar API Configuration  
SPORTRADAR_KEY = "YOUR-SPORTRADAR-API-KEY-HERE"  # Get from https://developer.sportradar.com/

# Data Sources
PARK_FACTORS_CSV = "https://raw.githubusercontent.com/chadwickbureau/baseballdatabank/master/core/ParkFactors.csv"

# Betting Configuration
MIN_EXPECTED_VALUE = 5.0  # Minimum EV threshold for betting recommendations
DEFAULT_BET_AMOUNT = 100  # Default bet amount for calculations

# Historical Data Configuration
HISTORICAL_DAYS = 14  # Number of days of historical data to fetch

# Update Instructions:
# 1. Rename this file to 'config.py'
# 2. Update SPREADSHEET_NAME with your Google Sheet name
# 3. Download Google service account credentials and save as 'credentials.json'
# 4. Get SportRadar API key and update SPORTRADAR_KEY
# 5. Share your Google Sheet with the service account email
