import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def connect_sheet(sheet_id):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)

def update_sheets(gs, analysis):
    worksheet = gs.worksheet("Game Analyzer")
    worksheet.clear()
    worksheet.append_row([
        "Home Team", "Away Team", "λ Home", "λ Away", "k", "Poisson Home", "Poisson Away", "Implied Home", "Implied Away", "EV Home", "EV Away"
    ])
    for row in analysis["game_analyzer"]:
        worksheet.append_row(row)
    # Add similar logic for other tabs