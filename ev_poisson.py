"""
Expected Value and Poisson Distribution calculations for MLB betting system.
This module calculates expected values using Poisson distribution for baseball games.
"""

import pandas as pd
import numpy as np
from scipy.stats import poisson
import gspread
from typing import Dict, List, Tuple


def calculate_poisson_probabilities(team_avg: float, opponent_avg: float, max_runs: int = 15) -> Dict[int, float]:
    """
    Calculate Poisson probabilities for runs scored.
    
    Args:
        team_avg: Team's average runs per game
        opponent_avg: Opponent's average runs allowed per game
        max_runs: Maximum runs to calculate probabilities for
    
    Returns:
        Dictionary of {runs: probability}
    """
    # Adjust team average based on opponent's defensive performance
    expected_runs = (team_avg + opponent_avg) / 2
    
    probabilities = {}
    for runs in range(max_runs + 1):
        probabilities[runs] = poisson.pmf(runs, expected_runs)
    
    return probabilities


def calculate_game_probabilities(home_team_avg: float, away_team_avg: float,
                               home_allowed_avg: float, away_allowed_avg: float) -> Dict[str, float]:
    """
    Calculate win probabilities for a game using Poisson distribution.
    
    Args:
        home_team_avg: Home team's average runs scored per game
        away_team_avg: Away team's average runs scored per game
        home_allowed_avg: Home team's average runs allowed per game
        away_allowed_avg: Away team's average runs allowed per game
    
    Returns:
        Dictionary with game outcome probabilities
    """
    # Calculate expected runs for each team
    home_expected = (home_team_avg + away_allowed_avg) / 2
    away_expected = (away_team_avg + home_allowed_avg) / 2
    
    # Calculate probabilities for different run totals
    max_runs = 15
    home_probs = [poisson.pmf(i, home_expected) for i in range(max_runs + 1)]
    away_probs = [poisson.pmf(i, away_expected) for i in range(max_runs + 1)]
    
    # Calculate win probabilities
    home_win_prob = 0
    away_win_prob = 0
    tie_prob = 0
    
    for home_runs in range(max_runs + 1):
        for away_runs in range(max_runs + 1):
            prob = home_probs[home_runs] * away_probs[away_runs]
            
            if home_runs > away_runs:
                home_win_prob += prob
            elif away_runs > home_runs:
                away_win_prob += prob
            else:
                tie_prob += prob
    
    # Calculate total runs probabilities
    total_runs_probs = {}
    for total in range(max_runs * 2 + 1):
        total_prob = 0
        for home_runs in range(min(total + 1, max_runs + 1)):
            away_runs = total - home_runs
            if 0 <= away_runs <= max_runs:
                total_prob += home_probs[home_runs] * away_probs[away_runs]
        total_runs_probs[total] = total_prob
    
    return {
        'home_win_prob': home_win_prob,
        'away_win_prob': away_win_prob,
        'tie_prob': tie_prob,
        'home_expected_runs': home_expected,
        'away_expected_runs': away_expected,
        'total_expected_runs': home_expected + away_expected,
        'total_runs_probs': total_runs_probs
    }


def calculate_expected_value(probability: float, odds: float, bet_amount: float = 100) -> float:
    """
    Calculate expected value of a bet.
    
    Args:
        probability: Probability of winning (0-1)
        odds: American odds (e.g., +150, -110)
        bet_amount: Amount to bet
    
    Returns:
        Expected value of the bet
    """
    if odds > 0:
        # Positive odds (underdog)
        payout = bet_amount * (odds / 100)
        ev = (probability * payout) - ((1 - probability) * bet_amount)
    else:
        # Negative odds (favorite)
        payout = bet_amount * (100 / abs(odds))
        ev = (probability * payout) - ((1 - probability) * bet_amount)
    
    return ev


def update_ev_poisson(spreadsheet: gspread.Spreadsheet):
    """
    Update the Google Sheet with Expected Value and Poisson calculations.
    
    Args:
        spreadsheet: The Google Sheets spreadsheet object
    """
    try:
        # Get the historical data worksheet
        hist_worksheet = spreadsheet.worksheet("Historical Data")
        
        # Read historical data
        hist_data = hist_worksheet.get_all_records()
        
        if not hist_data:
            print("No historical data found. Please run historical data fetch first.")
            return
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(hist_data)
        
        # Calculate team averages (this is a simplified example)
        # In a real implementation, you'd want more sophisticated calculations
        team_stats = {}
        
        for _, row in df.iterrows():
            home_team = row.get('home_team', '')
            away_team = row.get('away_team', '')
            home_score = row.get('home_score', 0)
            away_score = row.get('away_score', 0)
            
            if home_team and away_team:
                # Initialize team stats if not exists
                if home_team not in team_stats:
                    team_stats[home_team] = {'runs_scored': [], 'runs_allowed': []}
                if away_team not in team_stats:
                    team_stats[away_team] = {'runs_scored': [], 'runs_allowed': []}
                
                # Add game data
                try:
                    home_score = float(home_score) if home_score else 0
                    away_score = float(away_score) if away_score else 0
                    
                    team_stats[home_team]['runs_scored'].append(home_score)
                    team_stats[home_team]['runs_allowed'].append(away_score)
                    team_stats[away_team]['runs_scored'].append(away_score)
                    team_stats[away_team]['runs_allowed'].append(home_score)
                except (ValueError, TypeError):
                    continue
        
        # Calculate averages
        team_averages = {}
        for team, stats in team_stats.items():
            if stats['runs_scored'] and stats['runs_allowed']:
                team_averages[team] = {
                    'avg_runs_scored': np.mean(stats['runs_scored']),
                    'avg_runs_allowed': np.mean(stats['runs_allowed'])
                }
        
        # Create or update EV Poisson worksheet
        try:
            ev_worksheet = spreadsheet.worksheet("EV Poisson")
            ev_worksheet.clear()
        except gspread.WorksheetNotFound:
            ev_worksheet = spreadsheet.add_worksheet(title="EV Poisson", rows=1000, cols=20)
        
        # Prepare headers
        headers = [
            "Team", "Avg Runs Scored", "Avg Runs Allowed", 
            "Games Played", "Last Updated"
        ]
        
        # Prepare data
        ev_data = [headers]
        
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for team, averages in team_averages.items():
            games_played = len(team_stats[team]['runs_scored'])
            row = [
                team,
                round(averages['avg_runs_scored'], 2),
                round(averages['avg_runs_allowed'], 2),
                games_played,
                current_time
            ]
            ev_data.append(row)
        
        # Update the worksheet
        if ev_data:
            ev_worksheet.update('A1', ev_data)
            print(f"EV Poisson calculations updated successfully. {len(ev_data) - 1} teams processed.")
        else:
            print("No team data available for EV Poisson calculations.")
    
    except Exception as e:
        print(f"Error updating EV Poisson calculations: {str(e)}")


def get_betting_recommendations(spreadsheet: gspread.Spreadsheet, min_ev: float = 5.0) -> List[Dict]:
    """
    Get betting recommendations based on Expected Value calculations.
    
    Args:
        spreadsheet: The Google Sheets spreadsheet object
        min_ev: Minimum expected value threshold for recommendations
    
    Returns:
        List of betting recommendations
    """
    try:
        ev_worksheet = spreadsheet.worksheet("EV Poisson")
        ev_data = ev_worksheet.get_all_records()
        
        recommendations = []
        
        # This is a placeholder for more sophisticated recommendation logic
        # You would typically compare against current betting lines here
        
        for team_data in ev_data:
            team = team_data.get('Team', '')
            avg_scored = team_data.get('Avg Runs Scored', 0)
            avg_allowed = team_data.get('Avg Runs Allowed', 0)
            
            # Simple recommendation logic (you'd want to enhance this)
            if avg_scored > 5.5 and avg_allowed < 4.0:
                recommendations.append({
                    'team': team,
                    'recommendation': 'Strong offensive team with good pitching',
                    'avg_runs_scored': avg_scored,
                    'avg_runs_allowed': avg_allowed
                })
        
        return recommendations
    
    except Exception as e:
        print(f"Error getting betting recommendations: {str(e)}")
        return []


if __name__ == "__main__":
    # Example usage
    print("EV Poisson module loaded successfully!")
    
    # Example calculation
    home_avg = 5.2
    away_avg = 4.8
    home_allowed = 4.5
    away_allowed = 4.9
    
    game_probs = calculate_game_probabilities(home_avg, away_avg, home_allowed, away_allowed)
    print(f"Example game probabilities: {game_probs}")
    
    # Example EV calculation
    probability = 0.55  # 55% chance of winning
    odds = +150  # +150 American odds
    ev = calculate_expected_value(probability, odds)
    print(f"Expected value for 55% probability at +150 odds: ${ev:.2f}")
