# 🏟️ MLB Advanced Statistical Analysis System

A comprehensive Python-based system for analyzing MLB games using advanced statistics, sabermetrics, and predictive modeling. This system focuses on pure statistical analysis without odds or betting components.

## 🎯 Core Features

### 📊 **Statistical Analysis**
- **Advanced Sabermetrics**: wOBA, BABIP, ISO, FIP, xwOBA calculations
- **Poisson Distribution Modeling**: Game outcome probabilities
- **Win Probability Models**: Based on historical data and park factors
- **Statistical Significance Testing**: Confidence intervals and p-values

### 🔍 **Data Integration** 
- **MLB Stats API**: Real-time game data and player statistics
- **Multi-source Framework**: Ready for FanGraphs, Baseball Reference integration
- **Park Factors**: Stadium-specific adjustments
- **Historical Analysis**: Season and career trends

### 📈 **Advanced Analytics**
- **Pitcher vs Batter Analysis**: Head-to-head matchup statistics
- **Team Performance Metrics**: Run scoring predictions
- **Confidence Scoring**: Statistical reliability measures
- **Trend Analysis**: Performance patterns over time

## 📋 Setup Steps

### 1. Prerequisites
- Python 3.8+
- Google account
- API keys for SportRadar, etc.

### 2. Clone & Install
```bash
git clone https://github.com/yourusername/mlb-advanced-betting.git
cd mlb-advanced-betting
pip install -r requirements.txt
```

### 3. API Keys Configuration

#### Option A: Environment Variables
Create a `.env` file:
```env
SPORTRADAR_KEY=your_sportradar_key
GOOGLE_SHEET_ID=your_google_sheet_id
```

#### Option B: Google Apps Script Properties (Recommended)
1. Create Google Apps Script project
2. Add API keys to Script Properties
3. Deploy as web app
4. Configure `api_config.json`

See `SCRIPT_PROPERTIES_SETUP.md` for detailed instructions.

### 4. Google Sheets Setup
Create a Google Sheet with these tabs:
- **Game Analyzer**: Main analysis with EV calculations
- **Historical Data**: Game results and team performance  
- **Park Factors**: Stadium-specific adjustments
- **Pitcher vs Batter**: Head-to-head matchup data
- **EV Poisson**: Expected value calculations
- **Advanced Analytics**: Comprehensive sabermetric analysis

### 5. Run the System
```bash
python run_all.py
```

## 🛠️ Project Structure

```
├── run_all.py                    # Main orchestration script
├── ev_poisson.py                 # Expected Value & Poisson calculations
├── pitcher_vs_batter.py          # Enhanced matchup analysis
├── advanced_analytics.py         # Sabermetrics & data integration
├── api_key_manager.py            # Secure API key management
├── google_sheets_connect.py      # Google Sheets integration
├── setup_tabs.py                 # Worksheet setup and management
├── historical_data.py            # Historical game data fetching
├── park_factors.py               # Stadium factor analysis
├── check_setup.py                # System verification utility
├── google_apps_script.js         # Google Apps Script for key management
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── docs/
    ├── SCRIPT_PROPERTIES_SETUP.md  # Google Apps Script setup
    └── ENHANCED_FEATURES.md        # Detailed feature documentation
```

## 📊 Core Modules

### Expected Value & Poisson Analysis (`ev_poisson.py`)
- Poisson distribution modeling for game outcomes
- Team performance normalization with park factors
- Expected value calculations for betting opportunities

### Pitcher vs Batter Analysis (`pitcher_vs_batter.py`)
- Real-time MLB Stats API integration
- Head-to-head historical performance analysis
- Matchup advantage calculation with confidence scoring
- Framework for FanGraphs and Baseball Reference integration

### Advanced Analytics (`advanced_analytics.py`)
- Advanced sabermetrics: wOBA, BABIP, ISO, FIP
- Multi-source data integration framework
- Comprehensive player profiling
- Betting-focused insights and regression analysis

## 🔐 Security Features

- **No API keys in source code**: Secure storage in Google Apps Script Properties
- **Token-based authentication**: Web app deployment with access control
- **Multiple fallback options**: Environment variables, cached keys
- **Version control safe**: Sensitive files automatically ignored

## 🎯 Usage Examples

### Basic Analysis
```python
from google_sheets_connect import get_gsheet
from ev_poisson import update_ev_poisson

# Connect to your Google Sheet
spreadsheet = get_gsheet("YOUR_SHEET_ID")

# Run Expected Value analysis
update_ev_poisson(spreadsheet)
```

### Advanced Matchup Analysis
```python
from pitcher_vs_batter import PitcherVsBatterAnalyzer

analyzer = PitcherVsBatterAnalyzer()
pitchers = analyzer.get_current_pitchers()
stats = analyzer.get_pitcher_vs_batter_stats(pitcher_id, batter_id)
```

### Sabermetrics Calculations
```python
from advanced_analytics import AdvancedSabermetrics

saber = AdvancedSabermetrics()
woba = saber.calculate_woba(player_stats)
babip = saber.calculate_babip(player_stats)
```

## 📈 Data Sources

### Currently Integrated
- **MLB Stats API**: Official MLB data (free)
- **Google Apps Script**: Secure API key management
- **Park Factors**: Stadium-specific adjustments

### Ready for Integration
- **SportRadar API**: Real-time odds and advanced stats
- **FanGraphs**: Premium sabermetric data
- **Baseball Reference**: Historical statistics
- **Statcast**: Advanced tracking data

## 🚀 Advanced Features

- **Real-time probable pitcher detection**
- **Confidence scoring based on sample size**
- **Multi-source data comparison**
- **Betting regression analysis**
- **Automated Google Sheets population**
- **Professional error handling and logging**

## 📚 Documentation

- `SCRIPT_PROPERTIES_SETUP.md`: Google Apps Script configuration
- `ENHANCED_FEATURES.md`: Comprehensive feature documentation
- Individual module documentation in each Python file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## ⚠️ Disclaimer

This system is for educational and research purposes only. Always gamble responsibly and be aware of the risks involved in sports betting.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
- Open your sheet > Extensions > Apps Script
- Paste code from `google_sheets/mlb_setup.gs`
- Reload to access custom menu

### 8. Formulas (Game Analyzer Tab)
| Column                | Google Sheets Formula Example                      |
|-----------------------|----------------------------------------------------|
| Poisson Home          | =POISSON(N2,P2,FALSE)                              |
| Poisson Away          | =POISSON(O2,P2,FALSE)                              |
| Implied Prob Home     | =1/G2                                              |
| Implied Prob Away     | =1/H2                                              |
| EV Home               | =(R2*G2*100)-(100*(1-R2))                          |
| EV Away               | =(S2*H2*100)-(100*(1-S2))                          |

### 9. Enhancements
- Add more APIs (Statcast, FanGraphs, etc.)
- Use sabermetrics in analytics.py (wOBA, BABIP, ISO, FIP)
- Conditional formatting for value bets
- Scheduled runs via cron or Task Scheduler

### 10. Troubleshooting
- API quota: throttle requests and batch writes
- Data missing: check API keys and CSV paths

## Test Today's Slate
- Run `python run_all.py` for today's games.
- Check results in Game Analyzer tab.

---
Happy betting & analytics!