import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

def load_csv_stats(csv_path):
    """
    Loads advanced stat CSV (FanGraphs/Baseball-Reference) as DataFrame.
    """
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV {csv_path}: {e}")
        return pd.DataFrame()

def scrape_fangraphs_leaderboard(stat_type="batting", season=2024):
    """
    Scrapes FanGraphs leaderboards for advanced stats.
    stat_type: "batting" or "pitching"
    Returns DataFrame.
    """
    stat_map = {
        "batting": "https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season={season}&month=0&season1={season}&ind=0",
        "pitching": "https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=0&type=8&season={season}&month=0&season1={season}&ind=0"
    }
    url = stat_map.get(stat_type, stat_map["batting"]).format(season=season)
    try:
        dfs = pd.read_html(url)
        # Usually the first table is the leaderboard
        df = dfs[0]
        return df
    except Exception as e:
        print(f"FanGraphs scrape failed: {e}")
        return pd.DataFrame()

def scrape_bref_splits(player_url):
    """
    Scrapes Baseball Reference splits for a player.
    Example player_url: 'https://www.baseball-reference.com/players/s/smithdo02.shtml'
    Returns DataFrame for splits.
    """
    try:
        resp = requests.get(player_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Find the splits table
        table = soup.find("table", {"id": "splits"})
        if table:
            df = pd.read_html(str(table))[0]
            return df
        else:
            print(f"No splits table found for {player_url}")
            return pd.DataFrame()
    except Exception as e:
        print(f"BRef scrape failed: {e}")
        return pd.DataFrame()

def get_player_bref_url(player_name):
    """
    Tries to construct a Baseball Reference player URL from name.
    For robust use, keep a lookup CSV mapping names to URLs.
    """
    # This is a placeholder; proper mapping recommended
    base_url = "https://www.baseball-reference.com/players/"
    last, first = player_name.split()[-1], player_name.split()[0]
    # BRef uses first letter of last name for folder, then a rough code
    folder = last[0].lower()
    code = (last[:5] + first[:2] + "01").lower()
    url = f"{base_url}{folder}/{code}.shtml"
    return url

def load_all_advanced_stats():
    """
    Loads all advanced stats for use in analytics.
    Returns dict of DataFrames: fangraphs_batting, fangraphs_pitching, bref_splits.
    """
    fg_batting = scrape_fangraphs_leaderboard("batting")
    fg_pitching = scrape_fangraphs_leaderboard("pitching")
    # Example: load splits for Mike Trout
    trout_url = get_player_bref_url("Mike Trout")
    trout_splits = scrape_bref_splits(trout_url)
    return {
        "fangraphs_batting": fg_batting,
        "fangraphs_pitching": fg_pitching,
        "trout_splits": trout_splits
    }

def get_stat_for_player(df, player_name, stat_col):
    """
    Looks up a stat for a player from a DataFrame (e.g., wOBA, FIP).
    """
    try:
        row = df[df['Name'].str.contains(player_name, case=False, na=False)]
        if not row.empty and stat_col in row.columns:
            return row.iloc[0][stat_col]
        else:
            return None
    except Exception as e:
        print(f"Error getting stat {stat_col} for {player_name}: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    stats = load_all_advanced_stats()
    df_fg = stats["fangraphs_batting"]
    woba = get_stat_for_player(df_fg, "Mike Trout", "wOBA")
    print(f"Mike Trout wOBA: {woba}")
    # For more robust usage, process all players and stats as needed