import pandas as pd
import numpy as np

###########################
# 1. Recent Team Trends
###########################

def get_team_trends(df, team_col='Home', runs_col='Home Runs', winner_col='Winner', n=10):
    """Calculate win/loss streaks, last n record, and average runs for a team over last n games."""
    teams = pd.unique(df['Home'].tolist() + df['Away'].tolist())
    trends = []
    for team in teams:
        # Filter for games where team played
        games = df[(df['Home'] == team) | (df['Away'] == team)].tail(n)
        if games.empty:
            continue
        wins = sum(games[winner_col] == team)
        losses = n - wins
        # Average runs scored
        runs = []
        for _, row in games.iterrows():
            if row['Home'] == team:
                runs.append(row['Home Runs'])
            elif row['Away'] == team:
                runs.append(row['Away Runs'])
        avg_runs = np.mean(runs)
        trends.append({'Team': team, 'LastN': n, 'Wins': wins, 'Losses': losses, 'AvgRuns': avg_runs})
    return pd.DataFrame(trends)

###########################
# 2. Pitcher/Batter Splits
###########################

def get_pitcher_batter_splits(pitcher_batter_df, split_col='Handedness', rolling_n=10):
    """
    Example structure for splits and rolling averages. 
    Assumes pitcher_batter_df has columns: Pitcher, Batter, Handedness, Home/Away, Hits, AB
    """
    # Handedness splits
    split_stats = pitcher_batter_df.groupby(['Pitcher', split_col]).agg({
        'Hits': 'sum',
        'AB': 'sum'
    }).reset_index()
    split_stats['AVG'] = split_stats['Hits'] / split_stats['AB']
    # Rolling average for each pitcher-batter over last N matchups
    pitcher_batter_df = pitcher_batter_df.sort_values('Date')
    pitcher_batter_df['Rolling_AVG'] = pitcher_batter_df.groupby(['Pitcher', 'Batter'])['Hits'].rolling(rolling_n, min_periods=1).mean().reset_index(drop=True)
    return split_stats, pitcher_batter_df

###########################
# 3. Park Factor Adjustments
###########################

def adjust_for_park_factors(game_df, park_factors_df):
    """
    Adjust expected runs by park factor.
    game_df must have 'Venue' column matching 'Park Name' in park_factors_df.
    park_factors_df must have 'Park Name' and 'Runs' columns.
    """
    park_map = dict(zip(park_factors_df['Park Name'], park_factors_df['Runs']))
    game_df['ParkFactor'] = game_df['Venue'].map(park_map).fillna(1.0) # Default to 1.0 if missing
    # Adjust average runs by park factor
    game_df['AdjHomeRuns'] = game_df['Avg Home Runs (λ)'] * game_df['ParkFactor']
    game_df['AdjAwayRuns'] = game_df['Avg Away Runs (λ)'] * game_df['ParkFactor']
    return game_df

###########################
# 4. Weighted Averages
###########################

def weighted_team_avg(df, team, n=10, weight_decay=0.9):
    """
    Weighted average runs for a team, more recent games weighted higher.
    """
    games = df[(df['Home'] == team) | (df['Away'] == team)].tail(n)
    weights = np.array([weight_decay**i for i in range(n)][::-1])
    runs = []
    for _, row in games.iterrows():
        if row['Home'] == team:
            runs.append(row['Home Runs'])
        elif row['Away'] == team:
            runs.append(row['Away Runs'])
    if len(runs) == n:
        return np.average(runs, weights=weights)
    else:
        return np.mean(runs) if runs else 0

###########################
# 5. EV Percentile Filters
###########################

def ev_percentile_filter(game_df, ev_col='EV Home', percentile=90):
    """Highlight top bets by EV percentile."""
    threshold = np.percentile(game_df[ev_col].dropna(), percentile)
    game_df['TopEV'] = game_df[ev_col] >= threshold
    return game_df

###########################
# 6. Google Sheets Sync (pseudo-code)
###########################
# For each result DataFrame (trends, splits, park-adjusted, etc.), you can use gspread to update the corresponding worksheet:
#
# import gspread
# worksheet = spreadsheet.worksheet("Team Trends")
# worksheet.clear()
# worksheet.append_row(trends_df.columns.tolist())
# for row in trends_df.values.tolist():
#     worksheet.append_row(row)

###########################
# 7. Example Usage (in your pipeline)
###########################

if __name__ == "__main__":
    # Load your historical data, park factors, pitcher/batter data, and game analyzer sheet
    historical_df = pd.read_csv("historical_data.csv") # or from Google Sheets
    park_factors_df = pd.read_csv("park_factors.csv")
    pitcher_batter_df = pd.read_csv("pitcher_vs_batter.csv")
    game_df = pd.read_csv("game_analyzer.csv")

    # 1. Recent Trends
    trends_df = get_team_trends(historical_df, n=10)
    print(trends_df.head())

    # 2. Pitcher/Batter Splits
    split_stats, pitcher_batter_df = get_pitcher_batter_splits(pitcher_batter_df)
    print(split_stats.head())

    # 3. Park Factor Adjustments
    game_df = adjust_for_park_factors(game_df, park_factors_df)
    print(game_df[['Venue', 'Avg Home Runs (λ)', 'ParkFactor', 'AdjHomeRuns']].head())

    # 4. Weighted Avg
    team = 'Yankees'
    wavg = weighted_team_avg(historical_df, team, n=10)
    print(f"Weighted recent average runs for {team}: {wavg}")

    # 5. EV Percentile Filter
    game_df = ev_percentile_filter(game_df, ev_col='EV Home', percentile=90)
    print(game_df[game_df['TopEV']])

    # 6. Sync to Sheets (see pseudo-code above)