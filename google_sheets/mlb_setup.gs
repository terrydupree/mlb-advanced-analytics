function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('MLB Automation')
    .addItem('Import Park Factors CSV', 'importParkFactorsCSV')
    .addToUi();
}

function importParkFactorsCSV() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Park Factors');
  sheet.clear();
  sheet.appendRow(['Park Name','Runs','HR','2B','3B']);
  // User: Paste CSV data here manually, then run this function to populate
  // Example: sheet.appendRow(['Fenway Park',1.02,1.05,1.08,1.01]);
}