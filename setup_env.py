#!/usr/bin/env python3
"""
Environment setup script for MLB Advanced Betting System.
Creates .env file from template and guides user through API key setup.
"""

import os
import shutil
from pathlib import Path

def setup_env_file():
    """Set up the .env file from template."""
    
    print("🔧 MLB Advanced Betting System - Environment Setup")
    print("=" * 50)
    
    env_file = Path(".env")
    template_file = Path(".env.template")
    
    # Check if .env already exists
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return False
    
    # Check if template exists
    if not template_file.exists():
        print("❌ .env.template file not found!")
        return False
    
    # Copy template to .env
    try:
        shutil.copy(template_file, env_file)
        print("✅ Created .env file from template")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False
    
    print("\n📝 API Key Setup Guide:")
    print("=" * 30)
    print("1. Open .env file in your text editor")
    print("2. Replace placeholder values with your actual API keys:")
    print()
    
    api_keys = [
        ("GOOGLE_SHEET_ID", "Your Google Sheet ID (already set for testing)"),
        ("APISPORTS_KEY", "Get from: https://api.api-sports.io/"),
        ("ODDSAPI_KEY", "Get from: https://the-odds-api.com/"),
        ("MLB_STATS_API_KEY", "MLB Stats API (often free)"),
        ("FANGRAPHS_API_KEY", "FanGraphs API access"),
        ("BASEBALL_REFERENCE_API_KEY", "Baseball Reference API"),
    ]
    
    for key, description in api_keys:
        print(f"   {key}: {description}")
    
    print("\n💡 Optional Keys:")
    print("   - DISCORD_WEBHOOK_URL: For bet notifications")
    print("   - SLACK_WEBHOOK_URL: For team notifications")
    print("   - DATABASE_URL: For data persistence")
    
    print("\n🔒 Security Notes:")
    print("   - Never commit .env files to Git")
    print("   - Keep API keys secure and private")
    print("   - Use different keys for development/production")
    
    print(f"\n✅ Environment setup complete!")
    print(f"📁 Edit .env file to add your API keys")
    print(f"🚀 Run 'python run_all.py' when ready")
    
    return True

def verify_env_setup():
    """Verify that .env file is properly configured."""
    
    if not Path(".env").exists():
        print("❌ .env file not found. Run setup first.")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n🔍 Environment Verification:")
    print("=" * 30)
    
    required_vars = [
        "GOOGLE_SHEET_ID",
    ]
    
    optional_vars = [
        "APISPORTS_KEY",
        "ODDSAPI_KEY", 
        "MLB_STATS_API_KEY"
    ]
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"✅ {var}: Configured")
        else:
            print(f"❌ {var}: Missing or using placeholder")
            all_good = False
    
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"✅ {var}: Configured")
        else:
            print(f"⚠️  {var}: Using placeholder (system will use sample data)")
    
    if all_good:
        print("\n🎉 Environment is properly configured!")
    else:
        print("\n⚠️  Please configure required variables in .env file")
    
    return all_good

def main():
    """Main setup function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_env_setup()
    else:
        setup_env_file()
        print("\n" + "="*50)
        verify_env_setup()

if __name__ == "__main__":
    main()
