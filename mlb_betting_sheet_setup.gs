/**
 * MLB Betting Sheet Setup Script
 * - Uses Script Properties to securely store API key
 */

// --- Store your API key (run once in Apps Script editor) ---
function setSportradarKey() {
  PropertiesService.getScriptProperties().setProperty('SPORTRADAR_KEY', 'YOUR-SPORTRADAR-KEY');
}

// --- Retrieve API key from Script Properties ---
function getSportradarKey() {
  return PropertiesService.getScriptProperties().getProperty('SPORTRADAR_KEY');
}

// --- Example usage in API call ---
function fetchHistoricalData() {
  var SPORTRADAR_KEY = getSportradarKey();
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

// --- Utility: Ensure tab exists (as before) ---
function getOrCreateSheet(sheetName, headers) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    sheet.appendRow(headers);
  } else if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
  }
  return sheet;
}

// --- Other functions remain unchanged ---

// --- Master function to set up all tabs ---
function runUnifiedMLBSetup() {
  fetchHistoricalData();
  importParkFactors();
  setupPitcherVsBatter();
  setupGameAnalyzer();
  SpreadsheetApp.getUi().alert('MLB Betting Sheet updated!');
}