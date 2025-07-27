/**
 * MLB Betting Sheet Automation
 * - Fetches latest game data
 * - Updates historical, park, and matchup tabs
 * - Calculates expected value (EV)
 * - Can run on a schedule or via a custom menu
 */

// --- Get API keys securely ---
function getApiKey(keyName) {
  return PropertiesService.getScriptProperties().getProperty(keyName);
}

// --- Utility: Get/Create Sheet ---
function getOrCreateSheet(sheetName, headers) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    sheet.appendRow(headers);
  }
  return sheet;
}

// --- Fetch Historical Data (sample for Sportradar) ---
function fetchHistoricalData() {
  var SPORTRADAR_KEY = getApiKey('SPORTRADAR_KEY');
  var sheet = getOrCreateSheet('Historical Data', ['Date','Home','Away','Home Runs','Away Runs','Winner']);
  sheet.clearContents();
  sheet.appendRow(['Date','Home','Away','Home Runs','Away Runs','Winner']);
  var today = new Date();
  for (var i = 0; i < 14; i++) {
    var date = new Date(today);
    date.setDate(today.getDate() - i);
    var formatted = Utilities.formatDate(date, 'UTC', 'yyyy/MM/dd');
    var endpoint = 'https://api.sportradar.com/mlb/trial/v7/en/games/' + formatted + '/schedule.json?api_key=' + SPORTRADAR_KEY;
    try {
      var response = UrlFetchApp.fetch(endpoint);
      var data = JSON.parse(response.getContentText());
      if (data.games) {
        data.games.forEach(function(g) {
          var winner = '';
          if (g.status === 'completed') {
            winner = g.home.runs > g.away.runs ? g.home.name : g.away.name;
          }
          sheet.appendRow([
            formatted,
            g.home.name,
            g.away.name,
            g.home.runs || '',
            g.away.runs || '',
            winner
          ]);
        });
      }
    } catch(e) {
      Logger.log('Error fetching ' + formatted + ': ' + e);
    }
    Utilities.sleep(1100); // avoid rate limit
  }
}

// --- Park Factors Import (CSV or manual) ---
function importParkFactors() {
  var sheet = getOrCreateSheet('Park Factors', ['Park Name','Runs','HR','2B','3B']);
  sheet.clearContents();
  sheet.appendRow(['Park Name','Runs','HR','2B','3B']);
  // Paste CSV rows manually or fetch from a URL as needed
}

// --- Pitcher vs Batter Setup ---
function setupPitcherVsBatter() {
  var sheet = getOrCreateSheet('Pitcher vs Batter', ['Pitcher','Batter','AB','Hits','HR','K','AVG','OBP']);
  sheet.clearContents();
  sheet.appendRow(['Pitcher','Batter','AB','Hits','HR','K','AVG','OBP']);
}

// --- EV & Poisson Calculations (formulas in Game Analyzer tab) ---
function setupGameAnalyzer() {
  var headers = [
    'Game ID','Home Team','Away Team','Scheduled','Venue','Status',
    'Moneyline Home','Moneyline Away','Runline Home','Runline Away','O/U Odds',
    'Team Total Home','Team Total Away',
    'Avg Home Runs (λ)','Avg Away Runs (λ)','k (runs)',
    'Poisson Home','Poisson Away','Implied Prob Home','Implied Prob Away','EV Home','EV Away'
  ];
  var sheet = getOrCreateSheet('Game Analyzer', headers);
  sheet.clearContents();
  sheet.appendRow(headers);
  // Sample formulas in row 2 for user reference
  sheet.getRange('P2').setFormula('=POISSON(N2,O2,FALSE)');
  sheet.getRange('Q2').setFormula('=POISSON(O2,P2,FALSE)');
  sheet.getRange('R2').setFormula('=1/G2');
  sheet.getRange('S2').setFormula('=1/H2');
  sheet.getRange('T2').setFormula('=(R2*G2*100)-(100*(1-R2))');
  sheet.getRange('U2').setFormula('=(S2*H2*100)-(100*(1-S2))');
}

// --- Master Automation Function ---
function runMLBAnalyticsAutomation() {
  fetchHistoricalData();
  importParkFactors();
  setupPitcherVsBatter();
  setupGameAnalyzer();
  SpreadsheetApp.getUi().alert('MLB Betting Sheet updated automatically!');
}

// --- Add Custom Menu for Manual Run ---
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('MLB Automation')
    .addItem('Run MLB Update', 'runMLBAnalyticsAutomation')
    .addToUi();
}