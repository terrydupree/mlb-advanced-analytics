# MLB Advanced Analytics Platform - Quick Setup Guide

## 🚀 **Fast Track Setup (5 Minutes)**

### **1. Install & Configure**
```bash
# Clone repository
git clone https://github.com/terrydupree/mlb-advanced-analytics.git
cd mlb-advanced-analytics

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env with your Google Sheets credentials
```

### **2. Google Sheets Setup**
1. Create Google Cloud Project → Enable Sheets API
2. Create Service Account → Download credentials JSON
3. Create Google Sheet → Share with service account email
4. Update `.env` with credentials path and sheet ID

### **3. Launch System**
```bash
# Full system with all features
python run_all.py --mode full

# Access dashboard: http://localhost:5000
```

## 🎯 **Quick Launch Options**

| Mode | Command | Features |
|------|---------|----------|
| **Full System** | `python run_all.py --mode full` | Automation + ML + Dashboard + Monitoring |
| **Dashboard Only** | `python run_all.py --mode dashboard_only` | Web interface and visualizations |
| **Automation Only** | `python run_all.py --mode automation_only` | Background data collection |
| **Configuration** | `python run_all.py --config-gui` | Settings management GUI |

## 🔧 **Essential Configuration**

### **Minimum Required (.env)**
```env
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
SPREADSHEET_ID=your_sheet_id
```

### **Enhanced Features (Optional)**
```env
SLACK_WEBHOOK_URL=your_slack_webhook
EMAIL_USERNAME=your_email@gmail.com
FLASK_SECRET_KEY=secure_random_key
```

## 📊 **System Overview**

### **Core Components**
- 🔄 **Automation**: Smart scheduling for data updates
- 🤖 **Machine Learning**: XGBoost/LightGBM predictions
- 🌐 **Web Dashboard**: Interactive visualizations
- 📈 **Historical Database**: SQLite data storage
- 🚨 **Error Handling**: Robust monitoring and recovery

### **Data Sources**
- FanGraphs (advanced metrics)
- Baseball Reference (historical data)
- MLB Stats API (real-time data)
- Custom park factors and matchup analysis

## ⚡ **Troubleshooting**

### **Quick Fixes**
```bash
# Google Sheets connection issues
python -c "from google_sheets_connect import MLBSheetsConnector; MLBSheetsConnector().test_connection()"

# Update dependencies
pip install --upgrade -r requirements.txt

# Check system health
python -c "from run_all import MLBSystemOrchestrator; print(MLBSystemOrchestrator().get_system_status())"
```

### **Common Issues**
- **Credentials Error**: Verify JSON file path and permissions
- **Port Conflict**: Change `DASHBOARD_PORT=5001` in .env
- **Missing Data**: Run `python setup_tabs.py` to initialize sheets

## 🎮 **Using the Dashboard**

Access at `http://localhost:5000` for:
- 📊 Live game tracking and predictions
- 📈 Interactive charts and analytics
- ⚙️ System configuration and settings
- 📱 Mobile-optimized interface

## 🔄 **Automation Schedule**

| Time | Action | Description |
|------|--------|-------------|
| **8:00 AM** | Morning Sync | Daily data collection and model updates |
| **Pre-Game** | Game Prep | Analysis 60 minutes before first game |
| **Live** | Real-Time | Updates every 5 minutes during games |
| **Post-Game** | Results | Process outcomes and update predictions |

---

**🏆 Ready to revolutionize your MLB analysis!**
**Access your dashboard at http://localhost:5000 after launch.**
