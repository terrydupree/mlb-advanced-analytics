import os
import requests
import csv

def get_games_today():
    key = os.getenv("APISPORTS_KEY")
    url = "https://v1.baseball.api-sports.io/games?date=today"
    headers = {"x-apisports-key": key}
    resp = requests.get(url, headers=headers)
    return resp.json()["response"]

def get_odds():
    key = os.getenv("ODDSAPI_KEY")
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds?apiKey=" + key
    resp = requests.get(url)
    return resp.json()

def get_park_factors(csv_path):
    factors = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            factors.append(row)
    return factors