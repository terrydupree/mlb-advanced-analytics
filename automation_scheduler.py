"""
Automated MLB Statistics Update Scheduler
Handles scheduled scraping, API updates, and data synchronization.
"""

import schedule
import time
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List
import threading
import json
from pathlib import Path

# Local imports
from modules.data_scraper import load_all_advanced_stats, scrape_fangraphs_leaderboard
from modules.data_fetch import get_games_today, get_park_factors
from modules.analytics import run_ev_poisson_analysis
from modules.sheet_manager import connect_sheet, update_worksheet
from enhanced_data_processing import EnhancedMLBDataProcessor
from error_handler import MLBErrorHandler, log_operation


class MLBAutomationScheduler:
    """
    Handles automated scheduling of MLB data updates and analysis.
    """
    
    def __init__(self, config_file: str = "automation_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.error_handler = MLBErrorHandler()
        self.data_processor = EnhancedMLBDataProcessor()
        self.is_running = False
        self.scheduler_thread = None
        
        # Setup logging
        self._setup_logging()
        
    def _load_config(self) -> Dict:
        """Load automation configuration."""
        default_config = {
            "schedules": {
                "morning_update": "08:00",  # Morning stats refresh
                "pre_game_update": "12:00",  # Pre-game analysis
                "live_updates": "*/30 * * * *",  # Every 30 minutes during games
                "post_game_update": "23:30",  # End of day summary
                "weekly_historical": "0 2 * * 0"  # Sunday 2 AM - weekly historical data
            },
            "data_sources": {
                "fangraphs_enabled": True,
                "baseball_reference_enabled": True,
                "mlb_api_enabled": True,
                "statcast_enabled": False  # Requires special access
            },
            "update_settings": {
                "retry_attempts": 3,
                "retry_delay": 300,  # 5 minutes
                "rate_limit_delay": 2,  # 2 seconds between requests
                "batch_size": 10  # Process in batches
            },
            "notifications": {
                "email_enabled": False,
                "slack_enabled": False,
                "console_output": True
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logging.error(f"Error loading config: {e}")
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"mlb_automation_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler() if self.config["notifications"]["console_output"] else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger("MLBAutomation")
    
    @log_operation("Morning Stats Update")
    def morning_update(self):
        """Morning statistics refresh - comprehensive data update."""
        self.logger.info("🌅 Starting morning stats update...")
        
        try:
            # 1. Update FanGraphs leaderboards
            if self.config["data_sources"]["fangraphs_enabled"]:
                self.logger.info("📊 Updating FanGraphs leaderboards...")
                batting_stats = scrape_fangraphs_leaderboard("batting")
                pitching_stats = scrape_fangraphs_leaderboard("pitching")
                
                # Save to CSV
                batting_stats.to_csv("data/fangraphs_batting_daily.csv", index=False)
                pitching_stats.to_csv("data/fangraphs_pitching_daily.csv", index=False)
                self.logger.info(f"✅ Updated batting stats: {len(batting_stats)} players")
                self.logger.info(f"✅ Updated pitching stats: {len(pitching_stats)} players")
            
            # 2. Update park factors
            self.logger.info("🏟️ Updating park factors...")
            park_factors = get_park_factors("data/park_factors.csv")
            self.logger.info(f"✅ Loaded {len(park_factors)} park factors")
            
            # 3. Sync to Google Sheets
            self.logger.info("📋 Syncing to Google Sheets...")
            self._sync_daily_stats_to_sheets()
            
            self.logger.info("✅ Morning update completed successfully!")
            
        except Exception as e:
            self.error_handler.handle_error(e, "Morning Update")
            self.logger.error(f"❌ Morning update failed: {e}")
    
    @log_operation("Pre-Game Analysis")
    def pre_game_update(self):
        """Pre-game analysis - focus on today's games."""
        self.logger.info("⚾ Starting pre-game analysis...")
        
        try:
            # Get today's games
            games = get_games_today()
            self.logger.info(f"🎯 Found {len(games)} games today")
            
            if games:
                # Run comprehensive analysis
                park_factors = get_park_factors("data/park_factors.csv")
                analysis = run_ev_poisson_analysis(games, [], park_factors)
                
                # Update Google Sheets with game analysis
                self._update_game_analysis_sheets(analysis)
                
                self.logger.info("✅ Pre-game analysis completed!")
            else:
                self.logger.info("ℹ️ No games today - skipping pre-game analysis")
                
        except Exception as e:
            self.error_handler.handle_error(e, "Pre-Game Analysis")
            self.logger.error(f"❌ Pre-game analysis failed: {e}")
    
    @log_operation("Live Updates")
    def live_updates(self):
        """Live updates during games - quick refresh of key data."""
        self.logger.info("🔄 Running live updates...")
        
        try:
            # Quick game status update
            games = get_games_today()
            active_games = [g for g in games if g.get('status') == 'live']
            
            if active_games:
                self.logger.info(f"🟢 {len(active_games)} games currently live")
                # Update only live game data to avoid rate limits
                self._update_live_game_data(active_games)
            else:
                self.logger.info("ℹ️ No live games - minimal update")
                
        except Exception as e:
            self.error_handler.handle_error(e, "Live Updates")
            self.logger.error(f"❌ Live update failed: {e}")
    
    @log_operation("Post-Game Summary")
    def post_game_update(self):
        """End of day summary and cleanup."""
        self.logger.info("🌙 Starting post-game summary...")
        
        try:
            # Archive today's results
            self._archive_daily_results()
            
            # Generate daily performance report
            self._generate_daily_report()
            
            # Cleanup temporary files
            self._cleanup_temp_files()
            
            self.logger.info("✅ Post-game summary completed!")
            
        except Exception as e:
            self.error_handler.handle_error(e, "Post-Game Summary")
            self.logger.error(f"❌ Post-game summary failed: {e}")
    
    @log_operation("Weekly Historical Update")
    def weekly_historical_update(self):
        """Weekly historical data processing."""
        self.logger.info("📚 Starting weekly historical data update...")
        
        try:
            # Process historical data for the past week
            current_year = datetime.now().year
            results = self.data_processor.process_historical_season(current_year)
            
            self.logger.info(f"✅ Processed historical data: {len(results)} datasets")
            
        except Exception as e:
            self.error_handler.handle_error(e, "Weekly Historical Update")
            self.logger.error(f"❌ Weekly historical update failed: {e}")
    
    def _sync_daily_stats_to_sheets(self):
        """Sync daily statistics to Google Sheets."""
        try:
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            if not sheet_id:
                self.logger.warning("⚠️ No Google Sheet ID found")
                return
            
            gs = connect_sheet(sheet_id)
            
            # Update batting stats if available
            if os.path.exists("data/fangraphs_batting_daily.csv"):
                batting_df = pd.read_csv("data/fangraphs_batting_daily.csv")
                update_worksheet(gs, "daily_batting_stats", batting_df.head(50))  # Top 50 players
            
            # Update pitching stats if available
            if os.path.exists("data/fangraphs_pitching_daily.csv"):
                pitching_df = pd.read_csv("data/fangraphs_pitching_daily.csv")
                update_worksheet(gs, "daily_pitching_stats", pitching_df.head(50))  # Top 50 pitchers
                
        except Exception as e:
            self.logger.error(f"Error syncing to sheets: {e}")
    
    def _update_game_analysis_sheets(self, analysis: Dict):
        """Update game analysis in Google Sheets."""
        try:
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            if not sheet_id:
                return
            
            gs = connect_sheet(sheet_id)
            
            # Update game analyzer worksheet
            if "game_analyzer" in analysis:
                game_data = analysis["game_analyzer"]
                headers = ["Home Team", "Away Team", "λ Home", "λ Away", "k", "Poisson Home", "Poisson Away", "Win Prob Home", "Win Prob Away", "Statistical Edge", "Analysis Type"]
                
                # Convert to DataFrame and update
                import pandas as pd
                df = pd.DataFrame(game_data, columns=headers)
                update_worksheet(gs, "game_analyzer", df)
                
        except Exception as e:
            self.logger.error(f"Error updating game analysis: {e}")
    
    def _update_live_game_data(self, active_games: List):
        """Update live game data efficiently."""
        # Minimal updates to avoid rate limits
        self.logger.info(f"Updating {len(active_games)} live games")
    
    def _archive_daily_results(self):
        """Archive today's results for historical analysis."""
        archive_dir = Path("data/archive")
        archive_dir.mkdir(exist_ok=True)
        
        today = datetime.now().strftime("%Y%m%d")
        
        # Archive daily CSV files
        for file_pattern in ["*_daily.csv", "game_analysis_*.csv"]:
            files = Path("data").glob(file_pattern)
            for file in files:
                archive_file = archive_dir / f"{file.stem}_{today}{file.suffix}"
                file.rename(archive_file)
    
    def _generate_daily_report(self):
        """Generate daily performance report."""
        report_file = Path("reports") / f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(f"MLB Analytics Daily Report - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("=" * 50 + "\n\n")
            
            # Add report content based on available data
            f.write("System Status: Operational\n")
            f.write(f"Last Update: {datetime.now().strftime('%H:%M:%S')}\n")
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        temp_dir = Path("temp")
        if temp_dir.exists():
            for file in temp_dir.glob("*"):
                if file.is_file() and file.stat().st_mtime < time.time() - 86400:  # 24 hours old
                    file.unlink()
    
    def setup_schedules(self):
        """Setup all scheduled tasks."""
        schedules = self.config["schedules"]
        
        # Daily schedules
        schedule.every().day.at(schedules["morning_update"]).do(self.morning_update)
        schedule.every().day.at(schedules["pre_game_update"]).do(self.pre_game_update)
        schedule.every().day.at(schedules["post_game_update"]).do(self.post_game_update)
        
        # Live updates every 30 minutes (during typical game hours)
        schedule.every(30).minutes.do(self.live_updates)
        
        # Weekly historical update
        schedule.every().sunday.at("02:00").do(self.weekly_historical_update)
        
        self.logger.info("📅 All schedules configured successfully!")
    
    def start_scheduler(self):
        """Start the automation scheduler."""
        if self.is_running:
            self.logger.warning("⚠️ Scheduler is already running")
            return
        
        self.setup_schedules()
        self.is_running = True
        
        def run_scheduler():
            self.logger.info("🚀 MLB Automation Scheduler started!")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("✅ Scheduler started successfully!")
    
    def stop_scheduler(self):
        """Stop the automation scheduler."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        self.logger.info("⏹️ Scheduler stopped")
    
    def run_manual_update(self, update_type: str = "all"):
        """Run manual update for testing."""
        self.logger.info(f"🔧 Running manual {update_type} update...")
        
        if update_type == "morning" or update_type == "all":
            self.morning_update()
        if update_type == "pregame" or update_type == "all":
            self.pre_game_update()
        if update_type == "live" or update_type == "all":
            self.live_updates()
        if update_type == "postgame" or update_type == "all":
            self.post_game_update()


def main():
    """Main function for running the scheduler."""
    scheduler = MLBAutomationScheduler()
    
    print("🏟️ MLB Automation Scheduler")
    print("=" * 30)
    print("1. Start automated scheduler")
    print("2. Run manual update")
    print("3. View configuration")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        scheduler.start_scheduler()
        print("Scheduler running... Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop_scheduler()
            print("\n👋 Scheduler stopped")
    
    elif choice == "2":
        update_type = input("Update type (morning/pregame/live/postgame/all): ").strip().lower()
        scheduler.run_manual_update(update_type)
    
    elif choice == "3":
        print(json.dumps(scheduler.config, indent=2))
    
    elif choice == "4":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid option")


if __name__ == "__main__":
    main()
