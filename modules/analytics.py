import numpy as np
import pandas as pd

def poisson_prob(lam, k):
    # lam = mean runs, k = runs
    return (lam ** k) * np.exp(-lam) / np.math.factorial(k)

def run_ev_poisson_analysis(games, odds, parks):
    # Example: build analysis dict for sheets
    game_analyzer = []
    for game, odd in zip(games, odds):
        home_team = game['teams']['home']['name']
        away_team = game['teams']['away']['name']
        # Dummy values for λ, replace with park/historical factors
        lam_home = 4.5
        lam_away = 4.2
        k = 5
        p_home = poisson_prob(lam_home, k)
        p_away = poisson_prob(lam_away, k)
        implied_home = 1 / odd['home_odds']
        implied_away = 1 / odd['away_odds']
        ev_home = (implied_home * odd['home_odds'] * 100) - (100 * (1 - implied_home))
        ev_away = (implied_away * odd['away_odds'] * 100) - (100 * (1 - implied_away))
        game_analyzer.append([
            home_team, away_team, lam_home, lam_away, k, p_home, p_away, implied_home, implied_away, ev_home, ev_away
        ])
    return {"game_analyzer": game_analyzer}