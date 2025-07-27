"""
API Key Manager for MLB betting system.
Retrieves API keys from Google Apps Script Web App or local configuration.
"""

import requests
import json
import os
from typing import Optional, Dict


class APIKeyManager:
    def __init__(self, web_app_url: Optional[str] = None, access_token: Optional[str] = None):
        """
        Initialize the API Key Manager.
        
        Args:
            web_app_url: URL of the deployed Google Apps Script web app
            access_token: Security token for accessing the web app
        """
        self.web_app_url = web_app_url
        self.access_token = access_token
        self.cached_keys = {}
    
    def get_key_from_web_app(self, key_name: str) -> Optional[str]:
        """
        Get a specific API key from Google Apps Script web app.
        
        Args:
            key_name: Name of the key to retrieve
            
        Returns:
            The API key value or None if not found
        """
        if not self.web_app_url or not self.access_token:
            return None
        
        try:
            params = {
                'action': 'get_key',
                'key': key_name,
                'token': self.access_token
            }
            
            response = requests.get(self.web_app_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                print(f"Error getting key {key_name}: {data['error']}")
                return None
            
            return data.get('value', '')
            
        except Exception as e:
            print(f"Error accessing web app for key {key_name}: {e}")
            return None
    
    def get_all_keys_from_web_app(self) -> Dict[str, str]:
        """
        Get all API keys from Google Apps Script web app.
        
        Returns:
            Dictionary of all available keys
        """
        if not self.web_app_url or not self.access_token:
            return {}
        
        try:
            params = {
                'action': 'get_keys',
                'token': self.access_token
            }
            
            response = requests.get(self.web_app_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                print(f"Error getting keys: {data['error']}")
                return {}
            
            # Cache the keys
            self.cached_keys = data
            return data
            
        except Exception as e:
            print(f"Error accessing web app for all keys: {e}")
            return {}
    
    def get_key(self, key_name: str, default: str = '') -> str:
        """
        Get an API key with fallback options.
        
        Priority order:
        1. Cached keys
        2. Environment variables
        3. Web app
        4. Default value
        
        Args:
            key_name: Name of the key to retrieve
            default: Default value if key is not found
            
        Returns:
            The API key value
        """
        # Check cached keys first
        if key_name in self.cached_keys:
            return self.cached_keys[key_name]
        
        # Check environment variables
        env_value = os.getenv(key_name)
        if env_value:
            return env_value
        
        # Try web app
        web_app_value = self.get_key_from_web_app(key_name)
        if web_app_value:
            self.cached_keys[key_name] = web_app_value
            return web_app_value
        
        # Return default
        return default
    
    def setup_from_config_file(self, config_path: str = 'api_config.json'):
        """
        Setup the key manager from a configuration file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self.web_app_url = config.get('web_app_url')
                self.access_token = config.get('access_token')
                
                print(f"✅ API Key Manager configured from {config_path}")
            else:
                print(f"⚠️  Config file {config_path} not found. Creating template...")
                self.create_config_template(config_path)
                
        except Exception as e:
            print(f"❌ Error loading config: {e}")
    
    def create_config_template(self, config_path: str):
        """
        Create a template configuration file.
        
        Args:
            config_path: Path where to create the template
        """
        template = {
            "web_app_url": "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec",
            "access_token": "YOUR_ACCESS_TOKEN_FROM_SETUP_FUNCTION",
            "instructions": [
                "1. Deploy your Google Apps Script as a web app",
                "2. Run the setupAccessToken() function in Apps Script",
                "3. Copy the generated token to access_token above",
                "4. Copy your web app URL to web_app_url above"
            ]
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(template, f, indent=2)
            print(f"📋 Config template created at {config_path}")
        except Exception as e:
            print(f"❌ Error creating config template: {e}")


# Global instance
key_manager = APIKeyManager()


def get_sportradar_key() -> str:
    """Get SportRadar API key."""
    return key_manager.get_key('SPORTRADAR_KEY', 'YOUR-SPORTRADAR-KEY')


def get_api_key(key_name: str, default: str = '') -> str:
    """Get any API key by name."""
    return key_manager.get_key(key_name, default)


def initialize_key_manager(config_path: str = 'api_config.json'):
    """Initialize the global key manager."""
    key_manager.setup_from_config_file(config_path)


if __name__ == "__main__":
    print("🔑 API Key Manager")
    print("=" * 30)
    
    # Initialize from config
    initialize_key_manager()
    
    # Test getting keys
    sportradar_key = get_sportradar_key()
    print(f"SportRadar Key: {'✅ Found' if sportradar_key != 'YOUR-SPORTRADAR-KEY' else '❌ Not configured'}")
    
    # Get all keys if web app is configured
    if key_manager.web_app_url and key_manager.access_token:
        all_keys = key_manager.get_all_keys_from_web_app()
        print(f"Available keys from web app: {list(all_keys.keys())}")
    else:
        print("💡 Configure web app URL and access token to access Script Properties")
