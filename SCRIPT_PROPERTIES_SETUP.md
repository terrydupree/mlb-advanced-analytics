# Using Google Apps Script Properties for API Keys

This guide explains how to use Google Apps Script Properties to store and access your API keys securely.

## Step 1: Set Up Google Apps Script

### 1.1 Create a New Google Apps Script Project
1. Go to [script.google.com](https://script.google.com)
2. Click "New Project"
3. Replace the default code with the contents of `google_apps_script.js`
4. Save the project with a meaningful name (e.g., "MLB API Key Manager")

### 1.2 Set Your API Keys in Script Properties
1. In your Apps Script project, go to **Project Settings** (gear icon)
2. Scroll down to **Script Properties**
3. Add your API keys:
   - Property: `SPORTRADAR_KEY`, Value: `your_actual_sportradar_api_key`
   - Property: `OTHER_API_KEY`, Value: `any_other_keys_you_need`
4. Click "Save script properties"

### 1.3 Generate Access Token
1. In the Apps Script editor, select the `setupAccessToken` function
2. Click "Run" (you may need to authorize the script first)
3. Check the "Execution transcript" in the bottom panel
4. Copy the generated access token (it looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### 1.4 Deploy as Web App
1. Click "Deploy" > "New deployment"
2. Choose type: "Web app"
3. Description: "MLB API Key Manager"
4. Execute as: "Me"
5. Who has access: "Anyone" (the access token provides security)
6. Click "Deploy"
7. Copy the Web app URL (it looks like: `https://script.google.com/macros/s/.../exec`)

## Step 2: Configure Your Python Application

### 2.1 Create API Configuration File
1. Run your Python application once to generate the template:
   ```bash
   python api_key_manager.py
   ```

2. Edit `api_config.json`:
   ```json
   {
     "web_app_url": "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec",
     "access_token": "your-generated-access-token-here"
   }
   ```

### 2.2 Test the Configuration
```bash
python api_key_manager.py
```

You should see:
- ✅ API Key Manager configured from api_config.json
- ✅ SportRadar Key: Found
- Available keys from web app: ['sportradar_key', 'other_api_key']

## Step 3: Run Your MLB System

```bash
python run_all.py
```

## Security Benefits

1. **API keys are not in your code** - They're stored securely in Google's infrastructure
2. **Access token protection** - Only requests with the correct token can access keys
3. **Centralized management** - Update keys in one place (Script Properties)
4. **No local files** - No need to manage credential files on your machine

## Troubleshooting

### Error: "Unauthorized"
- Check that your access token is correct in `api_config.json`
- Verify the web app URL is correct
- Make sure the web app is deployed and accessible

### Error: "Key not found"
- Verify the key name exists in Script Properties
- Check spelling of key names (case sensitive)
- Run the `testProperties` function in Apps Script to see available keys

### Error: "Web app not accessible"
- Ensure the web app is deployed with "Anyone" access
- Check that your internet connection is working
- Verify the web app URL is complete and correct

## Alternative: Environment Variables

If you prefer, you can also set environment variables as a fallback:

**Windows PowerShell:**
```powershell
$env:SPORTRADAR_KEY = "your_api_key_here"
```

**Windows Command Prompt:**
```cmd
set SPORTRADAR_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export SPORTRADAR_KEY="your_api_key_here"
```

The system will check in this order:
1. Cached keys from web app
2. Environment variables
3. Web app (if configured)
4. Default values

## Benefits of This Approach

✅ **Secure** - Keys stored in Google's secure infrastructure  
✅ **Flexible** - Multiple fallback options  
✅ **Centralized** - Manage all keys in one place  
✅ **Team-friendly** - Share access without sharing keys  
✅ **Version control safe** - No keys in your code repository  

## Next Steps

Once this is working, you can:
1. Add more API keys to Script Properties as needed
2. Create different access tokens for different team members
3. Set up automatic key rotation schedules
4. Monitor key usage through Apps Script logging
