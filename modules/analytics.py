import numpy as np
import pandas as pd
import math

def poisson_prob(lam, k):
    # lam = mean runs, k = runs
    return (lam ** k) * np.exp(-lam) / math.factorial(k)

def run_ev_poisson_analysis(games, odds, parks):
    """Run statistical analysis on games data without odds/betting components."""
    game_analyzer = []
    
    for i, game in enumerate(games):
        try:
            home_team = game['teams']['home']['name']
            away_team = game['teams']['away']['name']
            
            # Pure statistical analysis without odds
            # Use historical run scoring data and park factors
            lam_home = 4.5  # Base runs expectation
            lam_away = 4.2  # Base runs expectation
            
            # Apply park factors
            park_factor = 1.0
            if i < len(parks):
                park_factor = float(parks[i].get('park_factor', 1.0))
            
            lam_home *= park_factor
            lam_away *= (2 - park_factor)  # Inverse effect for away team
            
            # Statistical probabilities
            k = 5  # Expected runs
            p_home = poisson_prob(lam_home, k)
            p_away = poisson_prob(lam_away, k)
            
            # Win probability calculation (simplified)
            home_win_prob = calculate_win_probability(lam_home, lam_away)
            away_win_prob = 1 - home_win_prob
            
            # Statistical edge (no betting odds)
            statistical_edge = abs(home_win_prob - 0.5) * 100
            
            game_analyzer.append([
                home_team, away_team, 
                round(lam_home, 2), round(lam_away, 2), 
                k, round(p_home, 4), round(p_away, 4), 
                round(home_win_prob, 4), round(away_win_prob, 4), 
                round(statistical_edge, 2), "Pure Analytics"
            ])
            
        except Exception as e:
            print(f"⚠️  Error processing game {i}: {e}")
            continue
    
    return {"game_analyzer": game_analyzer}

def calculate_win_probability(home_runs, away_runs):
    """Calculate win probability based on expected runs."""
    # Simplified win probability model
    run_diff = home_runs - away_runs
    # Use logistic function to convert run difference to probability
    import math
    probability = 1 / (1 + math.exp(-run_diff))
    return probability