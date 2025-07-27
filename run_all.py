import os
from dotenv import load_dotenv
from modules.data_fetch import get_games_today, get_odds, get_park_factors
from modules.analytics import run_ev_poisson_analysis
from modules.sheet_manager import connect_sheet, update_sheets

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Google Sheet ID from environment variable or use default
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "1EZjH0UllYLvHp4Qq6VnmomtBqNSYZZCYGYEV7ErMgtQ")
    print(f"🔗 Connecting to Google Sheet: {sheet_id}")
    gs = connect_sheet(sheet_id)

    print("📊 Starting MLB Statistical Analysis System...")
    print("💡 Enhanced with Chadwick Tools for historical data processing")
    
    games = get_games_today()
    # odds = get_odds()  # Odds disabled - focusing on pure analytics
    parks = get_park_factors("data/park_factors.csv")

    print("🔬 Running statistical analysis...")
    analysis = run_ev_poisson_analysis(games, [], parks)  # Empty odds array
    
    print("📋 Updating Google Sheets with analysis...")
    update_sheets(gs, analysis)
    
    print("\n🎯 Advanced Features Available:")
    print("   📊 Chadwick Tools integration: python chadwick_integration.py")
    print("   📈 Enhanced data processing: python enhanced_data_processing.py")
    print("   🔍 Historical analysis with Retrosheet data")
    print("   📋 Multi-year statistical trends")
    
    print("\n✅ Analysis complete! Check your Google Sheet for results.")

if __name__ == "__main__":
    main()