import os
from modules.data_fetch import get_games_today, get_odds, get_park_factors
from modules.analytics import run_ev_poisson_analysis
from modules.sheet_manager import connect_sheet, update_sheets

def main():
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    gs = connect_sheet(sheet_id)

    games = get_games_today()
    odds = get_odds()
    parks = get_park_factors("data/park_factors.csv")

    analysis = run_ev_poisson_analysis(games, odds, parks)
    update_sheets(gs, analysis)

if __name__ == "__main__":
    main()