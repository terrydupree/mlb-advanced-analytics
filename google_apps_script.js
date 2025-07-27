/**
 * Google Apps Script to access Script Properties and provide them to your Python application
 * Deploy this as a web app to securely access your API keys
 */

function doGet(e) {
  try {
    // Get the action parameter
    const action = e.parameter.action;
    
    // Security: You might want to add authentication here
    // For example, check for a secret token
    const token = e.parameter.token;
    const validToken = PropertiesService.getScriptProperties().getProperty('ACCESS_TOKEN');
    
    if (token !== validToken) {
      return ContentService
        .createTextOutput(JSON.stringify({error: 'Unauthorized'}))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    let result = {};
    
    switch(action) {
      case 'get_keys':
        // Get all API keys from Script Properties
        const properties = PropertiesService.getScriptProperties().getProperties();
        result = {
          sportradar_key: properties.SPORTRADAR_KEY || '',
          other_api_key: properties.OTHER_API_KEY || '',
          // Add other keys as needed
        };
        break;
        
      case 'get_key':
        // Get a specific key
        const keyName = e.parameter.key;
        if (keyName) {
          result = {
            key: keyName,
            value: PropertiesService.getScriptProperties().getProperty(keyName) || ''
          };
        } else {
          result = {error: 'Key parameter required'};
        }
        break;
        
      default:
        result = {error: 'Invalid action'};
    }
    
    return ContentService
      .createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({error: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Test function to verify Script Properties are accessible
 */
function testProperties() {
  const properties = PropertiesService.getScriptProperties().getProperties();
  console.log('Available properties:', Object.keys(properties));
  
  // Test getting a specific property
  const sportRadarKey = PropertiesService.getScriptProperties().getProperty('SPORTRADAR_KEY');
  console.log('SportRadar Key exists:', !!sportRadarKey);
}

/**
 * Setup function to create an access token
 */
function setupAccessToken() {
  const token = Utilities.getUuid();
  PropertiesService.getScriptProperties().setProperty('ACCESS_TOKEN', token);
  console.log('Access token created:', token);
  console.log('Use this token in your Python requests for authentication');
}
