"""
Advanced Sabermetrics and External Data Integration for MLB Betting System.
This module provides advanced statistical analysis and integration with multiple data sources.
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import time
from bs4 import BeautifulSoup
import re
from api_key_manager import get_api_key


class AdvancedSabermetrics:
    """
    Advanced sabermetric calculations and analysis.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MLB-Advanced-Analytics/1.0 (Educational Use)'
        })
    
    def calculate_woba(self, stats: Dict) -> float:
        """
        Calculate weighted On-Base Average (wOBA).
        
        Args:
            stats: Dictionary with batting statistics
            
        Returns:
            wOBA value
        """
        # 2024 wOBA weights (adjust for current season)
        weights = {
            'uBB': 0.692,  # Unintentional walks
            'HBP': 0.723,  # Hit by pitch
            '1B': 0.888,   # Singles
            '2B': 1.271,   # Doubles
            '3B': 1.616,   # Triples
            'HR': 2.101    # Home runs
        }
        
        # Get stats with defaults
        bb = stats.get('walks', 0)
        hbp = stats.get('hit_by_pitch', 0)
        singles = stats.get('singles', stats.get('hits', 0) - stats.get('doubles', 0) - stats.get('triples', 0) - stats.get('home_runs', 0))
        doubles = stats.get('doubles', 0)
        triples = stats.get('triples', 0)
        hr = stats.get('home_runs', 0)
        ab = stats.get('at_bats', 0)
        sf = stats.get('sac_flies', 0)
        
        numerator = (weights['uBB'] * bb + weights['HBP'] * hbp + 
                    weights['1B'] * singles + weights['2B'] * doubles +
                    weights['3B'] * triples + weights['HR'] * hr)
        
        denominator = ab + bb + sf + hbp
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def calculate_babip(self, stats: Dict) -> float:
        """
        Calculate Batting Average on Balls In Play (BABIP).
        
        Args:
            stats: Dictionary with batting statistics
            
        Returns:
            BABIP value
        """
        hits = stats.get('hits', 0)
        hr = stats.get('home_runs', 0)
        ab = stats.get('at_bats', 0)
        so = stats.get('strikeouts', 0)
        sf = stats.get('sac_flies', 0)
        
        balls_in_play = ab - so - hr + sf
        hits_in_play = hits - hr
        
        return hits_in_play / balls_in_play if balls_in_play > 0 else 0.0
    
    def calculate_iso(self, stats: Dict) -> float:
        """
        Calculate Isolated Power (ISO).
        
        Args:
            stats: Dictionary with batting statistics
            
        Returns:
            ISO value
        """
        slg = stats.get('slg', 0)
        avg = stats.get('avg', 0)
        
        return slg - avg
    
    def calculate_pitcher_fip(self, stats: Dict) -> float:
        """
        Calculate Fielding Independent Pitching (FIP).
        
        Args:
            stats: Dictionary with pitching statistics
            
        Returns:
            FIP value
        """
        # FIP constants (adjust for current season)
        fip_constant = 3.10  # 2024 constant
        
        hr = stats.get('home_runs_allowed', 0)
        bb = stats.get('walks', 0)
        hbp = stats.get('hit_by_pitch', 0)
        so = stats.get('strikeouts', 0)
        ip = stats.get('innings_pitched', 0)
        
        if ip == 0:
            return 0.0
        
        fip = ((13 * hr + 3 * (bb + hbp) - 2 * so) / ip) + fip_constant
        
        return fip


class FanGraphsIntegration:
    """
    Integration with FanGraphs data (requires proper authentication/access).
    """
    
    def __init__(self):
        self.base_url = "https://www.fangraphs.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_player_stats(self, player_name: str, season: int = None) -> Dict:
        """
        Get player statistics from FanGraphs.
        
        Note: This is a placeholder implementation. Real implementation would require:
        1. Proper authentication/API access
        2. Respect for rate limits and robots.txt
        3. Error handling for website changes
        
        Args:
            player_name: Name of the player
            season: Season year (default: current year)
            
        Returns:
            Dictionary with player statistics
        """
        if season is None:
            season = datetime.now().year
        
        print(f"💡 FanGraphs integration placeholder for {player_name} ({season})")
        
        # Placeholder data structure
        return {
            'wrc_plus': 0,
            'war': 0.0,
            'woba': 0.0,
            'babip': 0.0,
            'iso': 0.0,
            'bb_rate': 0.0,
            'k_rate': 0.0,
            'hard_hit_rate': 0.0,
            'barrel_rate': 0.0,
            'xwoba': 0.0,
            'xbacon': 0.0
        }
    
    def get_pitcher_stats(self, pitcher_name: str, season: int = None) -> Dict:
        """
        Get pitcher statistics from FanGraphs.
        
        Args:
            pitcher_name: Name of the pitcher
            season: Season year
            
        Returns:
            Dictionary with pitcher statistics
        """
        if season is None:
            season = datetime.now().year
        
        print(f"💡 FanGraphs pitcher data placeholder for {pitcher_name} ({season})")
        
        return {
            'era': 0.0,
            'fip': 0.0,
            'xfip': 0.0,
            'siera': 0.0,
            'war': 0.0,
            'k_rate': 0.0,
            'bb_rate': 0.0,
            'hr_per_9': 0.0,
            'lob_rate': 0.0,
            'babip_against': 0.0,
            'hard_hit_rate_against': 0.0
        }


class BaseballReferenceIntegration:
    """
    Integration with Baseball Reference data.
    """
    
    def __init__(self):
        self.base_url = "https://www.baseball-reference.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_player_splits(self, player_name: str, player_id: str = None) -> Dict:
        """
        Get player splits data from Baseball Reference.
        
        Note: This is a placeholder. Real implementation would require:
        1. Web scraping with proper rate limiting
        2. Handling of dynamic content
        3. Respect for robots.txt and terms of service
        
        Args:
            player_name: Name of the player
            player_id: Baseball Reference player ID
            
        Returns:
            Dictionary with split statistics
        """
        print(f"💡 Baseball Reference splits placeholder for {player_name}")
        
        return {
            'vs_left': {'avg': 0.0, 'obp': 0.0, 'slg': 0.0, 'ops': 0.0},
            'vs_right': {'avg': 0.0, 'obp': 0.0, 'slg': 0.0, 'ops': 0.0},
            'home': {'avg': 0.0, 'obp': 0.0, 'slg': 0.0, 'ops': 0.0},
            'away': {'avg': 0.0, 'obp': 0.0, 'slg': 0.0, 'ops': 0.0},
            'vs_fastball': {'avg': 0.0, 'slg': 0.0, 'whiff_rate': 0.0},
            'vs_breaking': {'avg': 0.0, 'slg': 0.0, 'whiff_rate': 0.0},
            'vs_offspeed': {'avg': 0.0, 'slg': 0.0, 'whiff_rate': 0.0}
        }
    
    def get_head_to_head_history(self, pitcher_name: str, batter_name: str) -> Dict:
        """
        Get historical head-to-head data.
        
        Args:
            pitcher_name: Name of the pitcher
            batter_name: Name of the batter
            
        Returns:
            Dictionary with historical matchup data
        """
        print(f"💡 Baseball Reference H2H placeholder for {pitcher_name} vs {batter_name}")
        
        return {
            'career_stats': {
                'at_bats': 0,
                'hits': 0,
                'avg': 0.0,
                'home_runs': 0,
                'rbis': 0,
                'strikeouts': 0
            },
            'recent_performance': [],
            'situational_stats': {}
        }


class StatcastIntegration:
    """
    Integration with MLB Statcast data.
    """
    
    def __init__(self):
        self.base_url = "https://baseballsavant.mlb.com"
        self.session = requests.Session()
    
    def get_statcast_data(self, player_id: int, season: int = None) -> Dict:
        """
        Get Statcast data for a player.
        
        Args:
            player_id: MLB player ID
            season: Season year
            
        Returns:
            Dictionary with Statcast metrics
        """
        if season is None:
            season = datetime.now().year
        
        try:
            # This would be the actual Statcast API endpoint
            # For now, returning placeholder data
            print(f"💡 Statcast data placeholder for player {player_id} ({season})")
            
            return {
                'exit_velocity': 0.0,
                'launch_angle': 0.0,
                'barrel_rate': 0.0,
                'hard_hit_rate': 0.0,
                'xba': 0.0,
                'xslg': 0.0,
                'xwoba': 0.0,
                'expected_stats': {
                    'avg': 0.0,
                    'slg': 0.0,
                    'woba': 0.0
                }
            }
        
        except Exception as e:
            print(f"⚠️  Error fetching Statcast data: {e}")
            return {}


class ComprehensiveAnalyzer:
    """
    Combines data from multiple sources for comprehensive analysis.
    """
    
    def __init__(self):
        self.sabermetrics = AdvancedSabermetrics()
        self.fangraphs = FanGraphsIntegration()
        self.bbref = BaseballReferenceIntegration()
        self.statcast = StatcastIntegration()
    
    def get_complete_player_profile(self, player_name: str, player_id: int = None) -> Dict:
        """
        Get comprehensive player profile from multiple sources.
        
        Args:
            player_name: Name of the player
            player_id: MLB player ID
            
        Returns:
            Dictionary with complete player analysis
        """
        profile = {
            'basic_stats': {},
            'advanced_metrics': {},
            'splits': {},
            'statcast': {},
            'analysis': {},
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            # Get data from different sources
            profile['advanced_metrics'] = self.fangraphs.get_player_stats(player_name)
            profile['splits'] = self.bbref.get_player_splits(player_name)
            
            if player_id:
                profile['statcast'] = self.statcast.get_statcast_data(player_id)
            
            # Perform analysis
            profile['analysis'] = self.analyze_player_profile(profile)
            
        except Exception as e:
            print(f"⚠️  Error building complete profile for {player_name}: {e}")
        
        return profile
    
    def analyze_player_profile(self, profile: Dict) -> Dict:
        """
        Analyze a complete player profile and provide insights.
        
        Args:
            profile: Player profile dictionary
            
        Returns:
            Dictionary with analysis insights
        """
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'trending': 'stable',
            'key_metrics': {},
            'betting_insights': []
        }
        
        # Sample analysis logic (enhance based on actual data)
        advanced = profile.get('advanced_metrics', {})
        
        if advanced.get('wrc_plus', 0) > 120:
            analysis['strengths'].append('Above-average offensive production')
        
        if advanced.get('k_rate', 0) > 0.25:
            analysis['weaknesses'].append('High strikeout rate')
        
        if advanced.get('hard_hit_rate', 0) > 0.40:
            analysis['strengths'].append('Strong contact quality')
        
        # Betting insights
        if advanced.get('babip', 0) > 0.350:
            analysis['betting_insights'].append('BABIP regression candidate')
        
        return analysis
    
    def compare_matchup(self, pitcher_profile: Dict, batter_profile: Dict) -> Dict:
        """
        Compare pitcher vs batter profiles for matchup analysis.
        
        Args:
            pitcher_profile: Complete pitcher profile
            batter_profile: Complete batter profile
            
        Returns:
            Dictionary with matchup comparison
        """
        comparison = {
            'advantage': 'neutral',
            'confidence': 0.5,
            'key_factors': [],
            'expected_outcome': {},
            'betting_recommendations': []
        }
        
        # Sample comparison logic
        pitcher_k_rate = pitcher_profile.get('advanced_metrics', {}).get('k_rate', 0)
        batter_k_rate = batter_profile.get('advanced_metrics', {}).get('k_rate', 0)
        
        if pitcher_k_rate > 0.28 and batter_k_rate > 0.25:
            comparison['key_factors'].append('High strikeout matchup')
            comparison['betting_recommendations'].append('Consider under on batter hits')
        
        return comparison


def create_data_integration_report(spreadsheet, player_list: List[str]) -> None:
    """
    Create a comprehensive data integration report in Google Sheets.
    
    Args:
        spreadsheet: Google Sheets spreadsheet object
        player_list: List of player names to analyze
    """
    try:
        # Create or get the Advanced Analytics worksheet
        try:
            worksheet = spreadsheet.worksheet("Advanced Analytics")
            worksheet.clear()
        except:
            worksheet = spreadsheet.add_worksheet(title="Advanced Analytics", rows=1000, cols=25)
        
        # Headers for comprehensive analysis
        headers = [
            "Player", "Position", "wRC+", "WAR", "wOBA", "xwOBA", "BABIP", "ISO",
            "K%", "BB%", "Hard Hit%", "Barrel%", "Exit Velo", "Launch Angle",
            "vs L Avg", "vs R Avg", "Home OPS", "Away OPS", "Trend", "Analysis",
            "Betting Edge", "Confidence", "Data Source", "Last Updated", "Notes"
        ]
        worksheet.append_row(headers)
        
        analyzer = ComprehensiveAnalyzer()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("📊 Creating advanced analytics report...")
        
        for player in player_list[:10]:  # Limit to prevent rate limiting
            try:
                profile = analyzer.get_complete_player_profile(player)
                
                # Extract key metrics
                advanced = profile.get('advanced_metrics', {})
                splits = profile.get('splits', {})
                statcast = profile.get('statcast', {})
                analysis = profile.get('analysis', {})
                
                row = [
                    player,
                    "Unknown",  # Position would come from roster data
                    advanced.get('wrc_plus', 0),
                    advanced.get('war', 0),
                    round(advanced.get('woba', 0), 3),
                    round(advanced.get('xwoba', 0), 3),
                    round(advanced.get('babip', 0), 3),
                    round(advanced.get('iso', 0), 3),
                    f"{advanced.get('k_rate', 0):.1%}",
                    f"{advanced.get('bb_rate', 0):.1%}",
                    f"{advanced.get('hard_hit_rate', 0):.1%}",
                    f"{advanced.get('barrel_rate', 0):.1%}",
                    statcast.get('exit_velocity', 0),
                    statcast.get('launch_angle', 0),
                    round(splits.get('vs_left', {}).get('avg', 0), 3),
                    round(splits.get('vs_right', {}).get('avg', 0), 3),
                    round(splits.get('home', {}).get('ops', 0), 3),
                    round(splits.get('away', {}).get('ops', 0), 3),
                    analysis.get('trending', 'stable'),
                    '; '.join(analysis.get('strengths', [])[:2]),
                    '; '.join(analysis.get('betting_insights', [])[:2]),
                    "Medium",  # Confidence placeholder
                    "Multiple",
                    current_time,
                    "Integrated analysis"
                ]
                
                worksheet.append_row(row)
                print(f"  ✅ Added {player}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"  ⚠️  Error processing {player}: {e}")
                continue
        
        print("✅ Advanced analytics report completed!")
        
    except Exception as e:
        print(f"❌ Error creating advanced analytics report: {e}")


if __name__ == "__main__":
    print("🚀 Advanced Sabermetrics and Data Integration Module")
    print("=" * 60)
    print("Capabilities:")
    print("✅ Advanced sabermetric calculations (wOBA, BABIP, ISO, FIP)")
    print("✅ FanGraphs integration framework")
    print("✅ Baseball Reference integration framework")
    print("✅ Statcast data integration framework")
    print("✅ Comprehensive player profiling")
    print("✅ Multi-source data comparison")
    print("✅ Betting-focused analysis")
    print("\n💡 Ready for integration with real data sources!")
    print("   Configure API keys and access tokens as needed.")
    
    # Test sabermetrics calculations
    test_stats = {
        'at_bats': 100,
        'hits': 30,
        'doubles': 8,
        'triples': 1,
        'home_runs': 5,
        'walks': 12,
        'strikeouts': 25,
        'hit_by_pitch': 2,
        'sac_flies': 1
    }
    
    saber = AdvancedSabermetrics()
    woba = saber.calculate_woba(test_stats)
    babip = saber.calculate_babip(test_stats)
    iso = saber.calculate_iso({'slg': 0.500, 'avg': 0.300})
    
    print(f"\n📊 Sample Calculations:")
    print(f"   wOBA: {woba:.3f}")
    print(f"   BABIP: {babip:.3f}")
    print(f"   ISO: {iso:.3f}")
