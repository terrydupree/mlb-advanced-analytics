# 🚀 MLB Advanced Betting System — VSCode Quick Start & User Guide

## 1. **What is this System?**
This project is an automated MLB betting analytics toolkit, built in Python and designed for use with VSCode and Google Sheets.
It:
- Fetches game and odds data from APIs
- Scrapes advanced stats from FanGraphs/Baseball Reference
- Calculates expected value (EV), Poisson distributions, and confidence scores
- Pushes results to Google Sheets for visualization
- Enables you to analyze today's MLB slate with powerful, customizable metrics

---

## 2. **How Does it Work?**

**Workflow:**
1. **Configure API keys:** Add your keys to `.env`
2. **Download advanced stats CSVs or let the system scrape live data**
3. **Run the main script** — it fetches, analyzes, and updates all sheets
4. **View results in Google Sheets** and/or visualize in Python

---

## 3. **Step-by-Step Usage in VSCode**

### **A. Setup**
- Open VSCode in the project folder
- Install dependencies (once):  
  `pip install -r requirements.txt`
- Add your API keys to `.env`
- Download `credentials.json` for Google Sheets API access (see README)

### **B. Run the System**
- Make sure you have up-to-date CSVs in `/data` or let the scraper run automatically
- In VSCode terminal, run:
  ```sh
  python run_all.py
  ```
- The script will:
  - Fetch today's games and odds
  - Scrape or load advanced stats
  - Analyze matchups
  - Calculate EV, Poisson, and confidence scores
  - Update Google Sheets tabs with results

### **C. Check Results**
- Open your Google Sheet (the one configured in `.env`)
- Review tabs:
  - **Game Analyzer**: EV, Poisson, odds, implied probabilities
  - **Historical Data**: Game results
  - **Park Factors**: Effects of stadiums
  - **Pitcher vs Batter**: Matchup splits and confidence
  - **EV Poisson**: Team-level value bets

### **D. Visualize**
- Use Google Sheets charts (Insert > Chart) or Python scripts with matplotlib/seaborn
- Highlight value bets (EV > 0) with conditional formatting

---

## 4. **Troubleshooting & Tips**
- If a tab is empty, check API keys and CSV paths
- For quota errors, wait and try again (Google limits write frequency)
- To update stats, rerun the script
- To enhance, add more stat scraping in `modules/data_scraper.py`

---

## 5. **Next Steps**
- Try running for today's slate, review the output, and experiment with formulas
- Tweak analytics in `modules/analytics.py` for your custom strategies
- Add new stat sources or improve matchup logic as you learn

---

**Ready to start? Open VSCode, run the script, and dominate MLB analytics!**
