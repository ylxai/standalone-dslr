#!/usr/bin/env python3
"""
Simple DSLR Test - No External Dependencies
"""

import json
import os

def simple_config_test():
    print("🔧 Simple Configuration Test")
    print("=" * 30)
    
    # Load config
    with open('config.json') as f:
        config = json.load(f)
    
    print(f"✅ Base URL: {config['web_project']['base_url']}")
    print(f"✅ Upload Endpoint: {config['web_project']['upload_endpoint']}")
    print(f"✅ Watch Directory: {config['camera']['watch_directory']}")
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("✅ Environment file exists")
    else:
        print("⚠️  Run ./setup_credentials.sh first")
    
    print("\n📋 Next Steps:")
    print("1. Run ./setup_credentials.sh")
    print("2. Install packages: pip install --user requests python-dotenv")
    print("3. Test connection: python3 simple_connection_test.py")

if __name__ == "__main__":
    simple_config_test()
