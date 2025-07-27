"""
Enhanced data processing module integrating Chadwick Tools with MLB statistical analysis.
Combines real-time API data with historical Retrosheet data processing.
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from chadwick_integration import ChadwickDataProcessor


class EnhancedMLBDataProcessor:
    """
    Advanced MLB data processor combining live APIs with historical Chadwick data.
    """
    
    def __init__(self):
        self.chadwick = ChadwickDataProcessor()
        self.data_dir = "data"
        self.retrosheet_dir = os.path.join(self.data_dir, "retrosheet")
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories for data storage."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.retrosheet_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "processed"), exist_ok=True)
    
    def process_historical_season(self, year: int) -> Dict[str, pd.DataFrame]:
        """
        Process complete historical season data using Chadwick Tools.
        
        Args:
            year: Season year to process
            
        Returns:
            Dictionary containing various processed datasets
        """
        print(f"🔄 Processing {year} season data with Chadwick Tools...")
        
        results = {
            'events': pd.DataFrame(),
            'games': pd.DataFrame(),
            'player_stats': pd.DataFrame(),
            'team_stats': pd.DataFrame(),
            'park_factors': {}
        }
        
        # Look for Retrosheet files for this year
        event_files = self._find_retrosheet_files(year, 'EV')
        game_files = self._find_retrosheet_files(year, 'GL')
        
        # Process event files (American League, National League, etc.)
        all_events = []
        for event_file in event_files:
            events_df = self.chadwick.process_retrosheet_events(event_file, year)
            if not events_df.empty:
                all_events.append(events_df)
        
        if all_events:
            results['events'] = pd.concat(all_events, ignore_index=True)
            print(f"✅ Processed {len(results['events'])} total events")
            
            # Calculate advanced player statistics
            results['player_stats'] = self.chadwick.calculate_advanced_stats(results['events'])
            
            # Calculate park factors
            results['park_factors'] = self.chadwick.get_park_factors_from_data(results['events'])
            
            # Calculate team statistics
            results['team_stats'] = self._calculate_team_stats(results['events'])
        
        # Process game logs
        all_games = []
        for game_file in game_files:
            games_df = self.chadwick.process_game_logs(game_file, year)
            if not games_df.empty:
                all_games.append(games_df)
        
        if all_games:
            results['games'] = pd.concat(all_games, ignore_index=True)
            print(f"✅ Processed {len(results['games'])} games")
        
        # Save processed data
        self._save_processed_data(results, year)
        
        return results
    
    def _find_retrosheet_files(self, year: int, file_type: str) -> List[str]:
        """
        Find Retrosheet files for a given year and type.
        
        Args:
            year: Year to search for
            file_type: File type ('EV' for events, 'GL' for game logs)
            
        Returns:
            List of file paths
        """
        files = []
        extensions = {
            'EV': ['.EVA', '.EVN', '.EVO', '.EVD'],  # Event files by league/division
            'GL': ['.TXT', '.CSV']  # Game log files
        }
        
        for ext in extensions.get(file_type, []):
            # Common Retrosheet naming patterns
            patterns = [
                f"{year}AL{ext}",  # American League
                f"{year}NL{ext}",  # National League
                f"{year}{ext}",    # Combined
                f"GL{year}{ext}"   # Game logs
            ]
            
            for pattern in patterns:
                file_path = os.path.join(self.retrosheet_dir, pattern)
                if os.path.exists(file_path):
                    files.append(file_path)
                    print(f"📁 Found: {pattern}")
        
        return files
    
    def _calculate_team_stats(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate team-level statistics from events data.
        
        Args:
            events_df: Events DataFrame from Chadwick processing
            
        Returns:
            DataFrame with team statistics
        """
        team_stats = []
        
        # Get unique teams
        home_teams = events_df['HOME_TEAM_ID'].unique()
        away_teams = events_df['AWAY_TEAM_ID'].unique()
        all_teams = set(list(home_teams) + list(away_teams))
        all_teams.discard(None)  # Remove None values
        
        for team in all_teams:
            # Get team's batting events (when they're the batting team)
            team_batting = events_df[events_df['BAT_TEAM_ID'] == team]
            
            if len(team_batting) > 0:
                # Calculate team offensive stats
                games_played = team_batting['GAME_ID'].nunique()
                total_ab = len(team_batting[team_batting['AB_FL'] == 1])
                total_hits = len(team_batting[team_batting['H_FL'] > 0])
                home_runs = len(team_batting[team_batting['H_FL'] == 4])
                walks = len(team_batting[team_batting['EVENT_CD'].isin([14, 15])])
                strikeouts = len(team_batting[team_batting['EVENT_CD'] == 3])
                
                # Calculate rates
                avg = total_hits / total_ab if total_ab > 0 else 0
                hr_per_game = home_runs / games_played if games_played > 0 else 0
                runs_scored = team_batting['RBI_CT'].sum()
                
                team_stats.append({
                    'team_id': team,
                    'games': games_played,
                    'at_bats': total_ab,
                    'hits': total_hits,
                    'home_runs': home_runs,
                    'walks': walks,
                    'strikeouts': strikeouts,
                    'runs_scored': runs_scored,
                    'avg': round(avg, 3),
                    'hr_per_game': round(hr_per_game, 2)
                })
        
        return pd.DataFrame(team_stats)
    
    def _save_processed_data(self, results: Dict[str, pd.DataFrame], year: int):
        """Save processed data to files."""
        processed_dir = os.path.join(self.data_dir, "processed")
        
        for data_type, data in results.items():
            if isinstance(data, pd.DataFrame) and not data.empty:
                filename = f"{data_type}_{year}.csv"
                filepath = os.path.join(processed_dir, filename)
                data.to_csv(filepath, index=False)
                print(f"💾 Saved {filename}")
            elif isinstance(data, dict) and data:
                # Save park factors as CSV
                if data_type == 'park_factors':
                    park_df = pd.DataFrame(list(data.items()), columns=['park_id', 'factor'])
                    filename = f"park_factors_{year}.csv"
                    filepath = os.path.join(processed_dir, filename)
                    park_df.to_csv(filepath, index=False)
                    print(f"💾 Saved {filename}")
    
    def get_historical_player_performance(self, player_id: str, years: List[int]) -> pd.DataFrame:
        """
        Get historical performance for a specific player across multiple years.
        
        Args:
            player_id: Retrosheet player ID
            years: List of years to analyze
            
        Returns:
            DataFrame with player's historical performance
        """
        player_data = []
        
        for year in years:
            try:
                # Load processed events data
                events_file = os.path.join(self.data_dir, "processed", f"events_{year}.csv")
                if os.path.exists(events_file):
                    events_df = pd.read_csv(events_file)
                    player_events = events_df[events_df['BAT_ID'] == player_id]
                    
                    if not player_events.empty:
                        # Calculate yearly stats
                        stats = self._calculate_player_year_stats(player_events, year)
                        player_data.append(stats)
            except Exception as e:
                print(f"⚠️  Error processing {year} data for {player_id}: {e}")
        
        return pd.DataFrame(player_data)
    
    def _calculate_player_year_stats(self, player_events: pd.DataFrame, year: int) -> Dict:
        """Calculate player statistics for a specific year."""
        ab = len(player_events[player_events['AB_FL'] == 1])
        hits = len(player_events[player_events['H_FL'] > 0])
        hr = len(player_events[player_events['H_FL'] == 4])
        bb = len(player_events[player_events['EVENT_CD'].isin([14, 15])])
        
        return {
            'year': year,
            'games': player_events['GAME_ID'].nunique(),
            'at_bats': ab,
            'hits': hits,
            'home_runs': hr,
            'walks': bb,
            'avg': round(hits / ab, 3) if ab > 0 else 0
        }
    
    def generate_advanced_park_factors(self, years: List[int]) -> pd.DataFrame:
        """
        Generate comprehensive park factors across multiple years.
        
        Args:
            years: List of years to analyze
            
        Returns:
            DataFrame with multi-year park factors
        """
        all_park_data = {}
        
        for year in years:
            try:
                events_file = os.path.join(self.data_dir, "processed", f"events_{year}.csv")
                if os.path.exists(events_file):
                    events_df = pd.read_csv(events_file)
                    year_factors = self.chadwick.get_park_factors_from_data(events_df)
                    
                    for park, factor in year_factors.items():
                        if park not in all_park_data:
                            all_park_data[park] = []
                        all_park_data[park].append(factor)
            except Exception as e:
                print(f"⚠️  Error processing park factors for {year}: {e}")
        
        # Calculate multi-year averages
        park_factors = []
        for park, factors in all_park_data.items():
            if len(factors) >= 2:  # At least 2 years of data
                avg_factor = sum(factors) / len(factors)
                park_factors.append({
                    'park_id': park,
                    'factor': round(avg_factor, 3),
                    'years': len(factors),
                    'std_dev': round(pd.Series(factors).std(), 3)
                })
        
        return pd.DataFrame(park_factors)


def setup_retrosheet_data():
    """
    Guide for setting up Retrosheet data for Chadwick processing.
    """
    print("📊 Retrosheet Data Setup Guide")
    print("=" * 40)
    print()
    print("1. 📥 Download Retrosheet Data:")
    print("   - Visit: https://retrosheet.org/game.htm")
    print("   - Download event files for desired years")
    print("   - Files named like: 2023AL.EVA (American League events)")
    print("   - Download game logs: GL2023.TXT")
    print()
    print("2. 📁 File Organization:")
    print("   - Create: data/retrosheet/")
    print("   - Place downloaded files in this directory")
    print("   - Unzip if necessary")
    print()
    print("3. 🔧 Processing:")
    print("   processor = EnhancedMLBDataProcessor()")
    print("   results = processor.process_historical_season(2023)")
    print()
    print("4. 📈 Available Analysis:")
    print("   - Player statistics across seasons")
    print("   - Team performance metrics")
    print("   - Multi-year park factors")
    print("   - Historical matchup data")


def main():
    """
    Demonstrate enhanced MLB data processing with Chadwick integration.
    """
    print("🔥 Enhanced MLB Data Processing with Chadwick Tools")
    print("=" * 55)
    
    processor = EnhancedMLBDataProcessor()
    
    if not processor.chadwick.chadwick_path:
        print("\n⚠️  Chadwick Tools not found!")
        print("Please install Chadwick Tools first.")
        print("Run: python chadwick_integration.py")
        return
    
    print("\n📊 Enhanced Processing Capabilities:")
    print("✅ Historical season analysis")
    print("✅ Multi-year player tracking")
    print("✅ Advanced park factors")
    print("✅ Team performance metrics")
    print("✅ Integration with live MLB API data")
    
    print("\n💡 Example Workflows:")
    print("# Process 2023 season")
    print("results = processor.process_historical_season(2023)")
    print()
    print("# Multi-year park factors")
    print("park_factors = processor.generate_advanced_park_factors([2021, 2022, 2023])")
    print()
    print("# Player historical performance")
    print("player_history = processor.get_historical_player_performance('troumo01', [2020, 2021, 2022, 2023])")
    
    # Check for existing Retrosheet data
    retrosheet_files = []
    if os.path.exists(processor.retrosheet_dir):
        retrosheet_files = [f for f in os.listdir(processor.retrosheet_dir) 
                          if f.endswith(('.EVA', '.EVN', '.TXT', '.CSV'))]
    
    if retrosheet_files:
        print(f"\n📁 Found {len(retrosheet_files)} Retrosheet files:")
        for file in retrosheet_files[:5]:  # Show first 5
            print(f"   - {file}")
        if len(retrosheet_files) > 5:
            print(f"   ... and {len(retrosheet_files) - 5} more")
        print("\n🚀 Ready for historical data processing!")
    else:
        print("\n📋 Setup Required:")
        setup_retrosheet_data()


if __name__ == "__main__":
    main()
