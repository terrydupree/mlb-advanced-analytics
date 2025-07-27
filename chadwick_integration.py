"""
Chadwick Tools integration for advanced baseball data manipulation.
Chadwick is a collection of tools for parsing and analyzing baseball data,
particularly Retrosheet data and event files.
"""

import subprocess
import pandas as pd
import os
import tempfile
from typing import Dict, List, Optional
from pathlib import Path


class ChadwickDataProcessor:
    """
    Integration class for Chadwick Tools baseball data processing.
    """
    
    def __init__(self):
        self.chadwick_path = self._find_chadwick_tools()
        self.temp_dir = tempfile.mkdtemp()
        
    def _find_chadwick_tools(self) -> Optional[str]:
        """Find Chadwick Tools installation path."""
        # Common installation paths
        possible_paths = [
            "C:\\chadwick\\bin",
            "C:\\Program Files\\chadwick\\bin",
            "/usr/local/bin",
            "/usr/bin",
            "/opt/chadwick/bin"
        ]
        
        for path in possible_paths:
            if os.path.exists(os.path.join(path, "cwevent.exe")) or os.path.exists(os.path.join(path, "cwevent")):
                print(f"✅ Found Chadwick Tools at: {path}")
                return path
        
        print("⚠️  Chadwick Tools not found. Please install from: https://chadwick.sourceforge.net/")
        return None
    
    def process_retrosheet_events(self, event_file: str, year: int) -> pd.DataFrame:
        """
        Process Retrosheet event files using cwevent.
        
        Args:
            event_file: Path to Retrosheet event file (.EVA, .EVN, etc.)
            year: Year of the data
            
        Returns:
            DataFrame with processed game events
        """
        if not self.chadwick_path:
            print("❌ Chadwick Tools not available")
            return pd.DataFrame()
        
        try:
            output_file = os.path.join(self.temp_dir, f"events_{year}.csv")
            cwevent_path = os.path.join(self.chadwick_path, "cwevent.exe" if os.name == 'nt' else "cwevent")
            
            # Run cwevent to process the event file
            cmd = [
                cwevent_path,
                "-f", "0-96",  # All fields
                "-y", str(year),
                event_file
            ]
            
            print(f"🔄 Processing Retrosheet events for {year}...")
            
            with open(output_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                # Read the processed data
                df = pd.read_csv(output_file, header=None)
                
                # Add column names for key fields
                df.columns = self._get_cwevent_columns()
                
                print(f"✅ Processed {len(df)} events from {event_file}")
                return df
            else:
                print(f"❌ Error processing events: {result.stderr}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error in process_retrosheet_events: {e}")
            return pd.DataFrame()
    
    def process_game_logs(self, game_log_file: str, year: int) -> pd.DataFrame:
        """
        Process Retrosheet game logs using cwgame.
        
        Args:
            game_log_file: Path to Retrosheet game log file
            year: Year of the data
            
        Returns:
            DataFrame with game statistics
        """
        if not self.chadwick_path:
            print("❌ Chadwick Tools not available")
            return pd.DataFrame()
        
        try:
            output_file = os.path.join(self.temp_dir, f"games_{year}.csv")
            cwgame_path = os.path.join(self.chadwick_path, "cwgame.exe" if os.name == 'nt' else "cwgame")
            
            # Run cwgame to process the game log
            cmd = [
                cwgame_path,
                "-f", "0-83",  # All game fields
                "-y", str(year),
                game_log_file
            ]
            
            print(f"🔄 Processing game logs for {year}...")
            
            with open(output_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                df = pd.read_csv(output_file, header=None)
                df.columns = self._get_cwgame_columns()
                
                print(f"✅ Processed {len(df)} games from {game_log_file}")
                return df
            else:
                print(f"❌ Error processing games: {result.stderr}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error in process_game_logs: {e}")
            return pd.DataFrame()
    
    def calculate_advanced_stats(self, events_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate advanced statistics from event data.
        
        Args:
            events_df: DataFrame from process_retrosheet_events
            
        Returns:
            DataFrame with advanced player statistics
        """
        if events_df.empty:
            return pd.DataFrame()
        
        try:
            # Group by player and calculate stats
            player_stats = []
            
            for player_id in events_df['BAT_ID'].unique():
                if pd.isna(player_id):
                    continue
                
                player_events = events_df[events_df['BAT_ID'] == player_id]
                
                # Basic counting stats
                pa = len(player_events)  # Plate appearances
                ab = len(player_events[player_events['AB_FL'] == 1])  # At bats
                hits = len(player_events[player_events['H_FL'] > 0])  # Hits
                singles = len(player_events[player_events['H_FL'] == 1])
                doubles = len(player_events[player_events['H_FL'] == 2])
                triples = len(player_events[player_events['H_FL'] == 3])
                hr = len(player_events[player_events['H_FL'] == 4])
                bb = len(player_events[player_events['EVENT_CD'].isin([14, 15])])  # Walks
                hbp = len(player_events[player_events['EVENT_CD'] == 16])  # Hit by pitch
                sf = len(player_events[player_events['SF_FL'] == 1])  # Sacrifice flies
                
                # Calculate advanced metrics
                if ab > 0:
                    avg = hits / ab
                    slg = (singles + 2*doubles + 3*triples + 4*hr) / ab
                else:
                    avg = 0
                    slg = 0
                
                if pa > 0:
                    obp = (hits + bb + hbp) / (ab + bb + hbp + sf) if (ab + bb + hbp + sf) > 0 else 0
                else:
                    obp = 0
                
                ops = obp + slg
                
                # wOBA calculation (simplified weights)
                woba_numerator = (0.690 * bb + 0.722 * hbp + 0.888 * singles + 
                                1.271 * doubles + 1.616 * triples + 2.101 * hr)
                woba_denominator = ab + bb + sf + hbp
                woba = woba_numerator / woba_denominator if woba_denominator > 0 else 0
                
                player_stats.append({
                    'player_id': player_id,
                    'PA': pa,
                    'AB': ab,
                    'H': hits,
                    'HR': hr,
                    'BB': bb,
                    'AVG': round(avg, 3),
                    'OBP': round(obp, 3),
                    'SLG': round(slg, 3),
                    'OPS': round(ops, 3),
                    'wOBA': round(woba, 3)
                })
            
            stats_df = pd.DataFrame(player_stats)
            print(f"✅ Calculated advanced stats for {len(stats_df)} players")
            return stats_df
            
        except Exception as e:
            print(f"❌ Error calculating advanced stats: {e}")
            return pd.DataFrame()
    
    def get_park_factors_from_data(self, events_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate park factors from event data.
        
        Args:
            events_df: DataFrame from process_retrosheet_events
            
        Returns:
            Dictionary mapping park codes to park factors
        """
        if events_df.empty:
            return {}
        
        try:
            park_factors = {}
            
            # Group by park and calculate run scoring
            for park in events_df['PARK_ID'].unique():
                if pd.isna(park):
                    continue
                
                park_events = events_df[events_df['PARK_ID'] == park]
                park_games = park_events['GAME_ID'].nunique()
                
                if park_games >= 10:  # Minimum games for statistical significance
                    home_runs = len(park_events[park_events['H_FL'] == 4])
                    total_pa = len(park_events)
                    
                    if total_pa > 0:
                        hr_rate = home_runs / total_pa
                        # Compare to league average (simplified)
                        league_avg_hr_rate = len(events_df[events_df['H_FL'] == 4]) / len(events_df)
                        
                        if league_avg_hr_rate > 0:
                            park_factor = hr_rate / league_avg_hr_rate
                            park_factors[park] = round(park_factor, 3)
            
            print(f"✅ Calculated park factors for {len(park_factors)} parks")
            return park_factors
            
        except Exception as e:
            print(f"❌ Error calculating park factors: {e}")
            return {}
    
    def _get_cwevent_columns(self) -> List[str]:
        """Get column names for cwevent output."""
        return [
            'GAME_ID', 'AWAY_TEAM_ID', 'INN_CT', 'BAT_HOME_ID', 'OUTS_CT',
            'BALLS_CT', 'STRIKES_CT', 'PITCH_SEQ_TX', 'AWAY_SCORE_CT', 'HOME_SCORE_CT',
            'BAT_ID', 'BAT_HAND_CD', 'RESP_BAT_ID', 'RESP_BAT_HAND_CD', 'PIT_ID',
            'PIT_HAND_CD', 'RESP_PIT_ID', 'RESP_PIT_HAND_CD', 'POS2_FLD_ID', 'POS3_FLD_ID',
            'POS4_FLD_ID', 'POS5_FLD_ID', 'POS6_FLD_ID', 'POS7_FLD_ID', 'POS8_FLD_ID',
            'POS9_FLD_ID', 'BASE1_RUN_ID', 'BASE2_RUN_ID', 'BASE3_RUN_ID', 'EVENT_TX',
            'LEADOFF_FL', 'PH_FL', 'BAT_FLD_CD', 'BAT_LINEUP_ID', 'EVENT_CD',
            'BAT_EVENT_FL', 'AB_FL', 'H_FL', 'SH_FL', 'SF_FL', 'EVENT_OUTS_CT',
            'DP_FL', 'TP_FL', 'RBI_CT', 'WP_FL', 'PB_FL', 'FLD_CD', 'BATTEDBALL_CD',
            'BUNT_FL', 'FOUL_FL', 'BATTEDBALL_LOC_TX', 'ERR_CT', 'ERR1_FLD_CD',
            'ERR1_CD', 'ERR2_FLD_CD', 'ERR2_CD', 'ERR3_FLD_CD', 'ERR3_CD',
            'BAT_DEST_ID', 'RUN1_DEST_ID', 'RUN2_DEST_ID', 'RUN3_DEST_ID',
            'BAT_PLAY_TX', 'RUN1_PLAY_TX', 'RUN2_PLAY_TX', 'RUN3_PLAY_TX',
            'RUN1_SB_FL', 'RUN2_SB_FL', 'RUN3_SB_FL', 'RUN1_CS_FL', 'RUN2_CS_FL',
            'RUN3_CS_FL', 'RUN1_PK_FL', 'RUN2_PK_FL', 'RUN3_PK_FL', 'RUN1_RESP_PIT_ID',
            'RUN2_RESP_PIT_ID', 'RUN3_RESP_PIT_ID', 'GAME_NEW_FL', 'GAME_END_FL',
            'PR_RUN1_FL', 'PR_RUN2_FL', 'PR_RUN3_FL', 'REMOVED_FOR_PR_RUN1_ID',
            'REMOVED_FOR_PR_RUN2_ID', 'REMOVED_FOR_PR_RUN3_ID', 'REMOVED_FOR_PH_BAT_ID',
            'REMOVED_FOR_PH_BAT_FLD_CD', 'PO1_FLD_CD', 'PO2_FLD_CD', 'PO3_FLD_CD',
            'ASS1_FLD_CD', 'ASS2_FLD_CD', 'ASS3_FLD_CD', 'ASS4_FLD_CD', 'ASS5_FLD_CD',
            'EVENT_ID', 'HOME_TEAM_ID', 'BAT_TEAM_ID', 'FLD_TEAM_ID', 'BAT_LAST_ID',
            'INN_NEW_FL', 'INN_END_FL', 'START_BAT_SCORE_CT', 'START_FLD_SCORE_CT',
            'INN_RUNS_CT', 'GAME_PA_CT', 'INN_PA_CT', 'PA_NEW_FL', 'PA_TRUNC_FL',
            'START_BASES_CD', 'END_BASES_CD', 'BAT_START_FL', 'RESP_BAT_START_FL',
            'BAT_ON_DECK_ID', 'BAT_IN_HOLD_ID', 'PIT_START_FL', 'RESP_PIT_START_FL',
            'RUN1_FLD_CREDIT_FL', 'RUN2_FLD_CREDIT_FL', 'RUN3_FLD_CREDIT_FL',
            'BAT_FLD_CREDIT_FL', 'BAT_SAFE_ERR_FL', 'BAT_FATE_ID', 'RUN1_FATE_ID',
            'RUN2_FATE_ID', 'RUN3_FATE_ID', 'FATE_RUNS_CT', 'ASS6_FLD_CD',
            'ASS7_FLD_CD', 'ASS8_FLD_CD', 'ASS9_FLD_CD', 'ASS10_FLD_CD',
            'UNKNOWN_OUT_EXC_FL', 'UNCERTAIN_PLAY_EXC_FL'
        ][:97]  # Limit to actual number of columns
    
    def _get_cwgame_columns(self) -> List[str]:
        """Get column names for cwgame output."""
        return [
            'GAME_ID', 'GAME_DT', 'GAME_CT', 'GAME_DY', 'START_GAME_TM', 'DH_FL',
            'DAYNIGHT_PARK_CD', 'AWAY_TEAM_ID', 'HOME_TEAM_ID', 'PARK_ID', 'AWAY_START_PIT_ID',
            'HOME_START_PIT_ID', 'HOME_FIN_PIT_ID', 'AWAY_FIN_PIT_ID', 'AWAY_SCORE_CT',
            'HOME_SCORE_CT', 'INN_CT', 'AWAY_HITS_CT', 'HOME_HITS_CT', 'AWAY_ERR_CT',
            'HOME_ERR_CT', 'AWAY_LOB_CT', 'HOME_LOB_CT', 'WIN_PIT_ID', 'LOSE_PIT_ID',
            'SAVE_PIT_ID', 'GWRBI_BAT_ID', 'AWAY_LINEUP1_BAT_ID', 'AWAY_LINEUP1_FLD_CD',
            'AWAY_LINEUP2_BAT_ID', 'AWAY_LINEUP2_FLD_CD', 'AWAY_LINEUP3_BAT_ID',
            'AWAY_LINEUP3_FLD_CD', 'AWAY_LINEUP4_BAT_ID', 'AWAY_LINEUP4_FLD_CD',
            'AWAY_LINEUP5_BAT_ID', 'AWAY_LINEUP5_FLD_CD', 'AWAY_LINEUP6_BAT_ID',
            'AWAY_LINEUP6_FLD_CD', 'AWAY_LINEUP7_BAT_ID', 'AWAY_LINEUP7_FLD_CD',
            'AWAY_LINEUP8_BAT_ID', 'AWAY_LINEUP8_FLD_CD', 'AWAY_LINEUP9_BAT_ID',
            'AWAY_LINEUP9_FLD_CD', 'HOME_LINEUP1_BAT_ID', 'HOME_LINEUP1_FLD_CD',
            'HOME_LINEUP2_BAT_ID', 'HOME_LINEUP2_FLD_CD', 'HOME_LINEUP3_BAT_ID',
            'HOME_LINEUP3_FLD_CD', 'HOME_LINEUP4_BAT_ID', 'HOME_LINEUP4_FLD_CD',
            'HOME_LINEUP5_BAT_ID', 'HOME_LINEUP5_FLD_CD', 'HOME_LINEUP6_BAT_ID',
            'HOME_LINEUP6_FLD_CD', 'HOME_LINEUP7_BAT_ID', 'HOME_LINEUP7_FLD_CD',
            'HOME_LINEUP8_BAT_ID', 'HOME_LINEUP8_FLD_CD', 'HOME_LINEUP9_BAT_ID',
            'HOME_LINEUP9_FLD_CD', 'ADDITIONAL_INFO_TX', 'ACQUISITION_INFO_TX',
            'TEMP_PARK_CT', 'WIND_DIRECTION_PARK_CD', 'WIND_SPEED_PARK_CT',
            'FIELD_PARK_CD', 'PRECIP_PARK_CD', 'SKY_PARK_CD', 'MINUTES_GAME_CT',
            'ATTEND_PARK_CT', 'SCORER_RECORD_ID', 'TRANSLATOR_RECORD_ID',
            'INPUTTER_RECORD_ID', 'INPUT_RECORD_TS', 'EDIT_RECORD_TS', 'METHOD_RECORD_CD',
            'PITCHES_RECORD_CD', 'UMPHOME_ID', 'UMP1B_ID', 'UMP2B_ID', 'UMP3B_ID',
            'UMPLF_ID', 'UMPRF_ID', 'AWAY_MANAGER_ID', 'HOME_MANAGER_ID', 'WINNING_RBI_BAT_ID',
            'FORFEIT_INFO_TX', 'PROTEST_INFO_TX', 'SUSPENSION_INFO_TX', 'COMPLETION_INFO_TX'
        ][:84]  # Limit to actual number of columns


def install_chadwick_tools():
    """
    Provide instructions for installing Chadwick Tools.
    """
    print("🔧 Chadwick Tools Installation Guide")
    print("=" * 40)
    print()
    print("📥 Download and Installation:")
    print("1. Visit: https://chadwick.sourceforge.net/")
    print("2. Download the appropriate version for your OS")
    print()
    print("🖥️  Windows:")
    print("   - Download the Windows binary")
    print("   - Extract to C:\\chadwick\\")
    print("   - Add C:\\chadwick\\bin to your PATH")
    print()
    print("🐧 Linux/Mac:")
    print("   - Download source code")
    print("   - Compile: ./configure && make && sudo make install")
    print("   - Or use package manager: apt-get install chadwick-tools")
    print()
    print("📊 Retrosheet Data:")
    print("1. Visit: https://retrosheet.org/game.htm")
    print("2. Download event files (.EVA, .EVN, .EVO, .EVD)")
    print("3. Download game logs")
    print("4. Place in data/retrosheet/ directory")
    print()
    print("✅ Verification:")
    print("   Run: cwevent -h")
    print("   Should display Chadwick help information")


def main():
    """
    Demonstration of Chadwick Tools integration.
    """
    print("🔥 Chadwick Tools Integration for MLB Analysis")
    print("=" * 50)
    
    processor = ChadwickDataProcessor()
    
    if not processor.chadwick_path:
        print("\n📋 Installation Required:")
        install_chadwick_tools()
        return
    
    print("\n💡 Available Functions:")
    print("✅ Process Retrosheet event files")
    print("✅ Process game logs")
    print("✅ Calculate advanced statistics")
    print("✅ Generate park factors")
    print("✅ Historical data analysis")
    
    print("\n📖 Example Usage:")
    print("# Process 2023 events")
    print("events_df = processor.process_retrosheet_events('2023AL.EVA', 2023)")
    print("stats_df = processor.calculate_advanced_stats(events_df)")
    print("park_factors = processor.get_park_factors_from_data(events_df)")
    
    print("\n🚀 Integration Complete!")
    print("Ready to process historical baseball data with Chadwick Tools")


if __name__ == "__main__":
    main()
