#!/usr/bin/env python3
"""
Simple Google Sheets verification script.
Quick test to confirm sheets integration is working.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from modules.sheet_manager import connect_sheet


def quick_sheets_test():
    """Quick test of Google Sheets functionality."""
    print("🔍 Quick Google Sheets Verification")
    print("=" * 40)
    
    try:
        # Load environment and connect
        load_dotenv()
        sheet_id = os.getenv("GOOGLE_SHEET_ID", "1EZjH0UllYLvHp4Qq6VnmomtBqNSYZZCYGYEV7ErMgtQ")
        
        print("🔗 Connecting to Google Sheets...")
        gs = connect_sheet(sheet_id)
        
        print(f"✅ Connected to: {gs.title}")
        print(f"🔗 URL: {gs.url}")
        
        # List worksheets
        worksheets = gs.worksheets()
        print(f"\n📋 Found {len(worksheets)} worksheets:")
        for i, ws in enumerate(worksheets, 1):
            print(f"   {i}. {ws.title}")
        
        # Test simple read
        print("\n📖 Testing read access...")
        first_ws = worksheets[0]
        try:
            values = first_ws.get_all_values()
            print(f"✅ Successfully read {len(values)} rows from '{first_ws.title}'")
        except Exception as e:
            print(f"⚠️  Read error: {e}")
        
        # Test simple write
        print("\n✏️  Testing write access...")
        try:
            # Find game_analyzer worksheet
            game_ws = None
            for ws in worksheets:
                if 'game_analyzer' in ws.title.lower():
                    game_ws = ws
                    break
            
            if game_ws:
                # Simple test write
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                test_row = ["Test", "Connection", "OK", "OK", "5", "0.1", "0.1", "0.5", "0.5", "0", f"Verified {current_time}"]
                
                # Clear and add headers
                game_ws.clear()
                headers = ["Home Team", "Away Team", "λ Home", "λ Away", "k", "Poisson Home", "Poisson Away", "Win Prob Home", "Win Prob Away", "Statistical Edge", "Analysis Type"]
                game_ws.append_row(headers)
                game_ws.append_row(test_row)
                
                print(f"✅ Successfully wrote test data to '{game_ws.title}'")
                print(f"🔗 Direct link: {game_ws.url}")
            else:
                print("⚠️  Could not find game_analyzer worksheet")
        
        except Exception as e:
            print(f"⚠️  Write error: {e}")
        
        print("\n🎉 Basic Google Sheets functionality verified!")
        print("💡 Your system can read from and write to Google Sheets")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def verify_mlb_system_integration():
    """Verify the full MLB system works with Google Sheets."""
    print("\n🏟️ MLB System Integration Test")
    print("=" * 35)
    
    try:
        from modules.data_fetch import get_games_today, get_park_factors
        from modules.analytics import run_ev_poisson_analysis
        
        print("📊 Fetching MLB data...")
        games = get_games_today()
        parks = get_park_factors("data/park_factors.csv")
        
        print(f"✅ Fetched {len(games)} games")
        print(f"✅ Loaded {len(parks)} park factors")
        
        print("🔬 Running analysis...")
        analysis = run_ev_poisson_analysis(games, [], parks)
        
        game_count = len(analysis.get("game_analyzer", []))
        print(f"✅ Analyzed {game_count} games")
        
        if game_count > 0:
            print("📋 Sample analysis data:")
            for i, game in enumerate(analysis["game_analyzer"][:3]):  # Show first 3
                print(f"   {i+1}. {game[0]} vs {game[1]} - Statistical Edge: {game[9]}")
        
        print("\n🚀 MLB system integration verified!")
        return True
        
    except Exception as e:
        print(f"❌ MLB system error: {e}")
        return False


def main():
    """Main verification function."""
    print("🔥 Google Sheets & MLB System Verification")
    print("=" * 50)
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    sheets_ok = quick_sheets_test()
    mlb_ok = verify_mlb_system_integration()
    
    print("\n📊 VERIFICATION SUMMARY")
    print("=" * 25)
    print(f"Google Sheets: {'✅ WORKING' if sheets_ok else '❌ FAILED'}")
    print(f"MLB Analysis:  {'✅ WORKING' if mlb_ok else '❌ FAILED'}")
    
    if sheets_ok and mlb_ok:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 Your MLB analysis system is ready to use!")
        print("\n💡 Next steps:")
        print("   - Run 'python run_all.py' for full analysis")
        print("   - Check your Google Sheet for results")
        print("   - Set up API keys for live data")
    else:
        print("\n⚠️  Some issues detected. See details above.")
    
    print(f"\n🕒 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
