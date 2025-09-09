#!/usr/bin/env python3
"""
🧪 Test DSLR System Without Heavy Dependencies
Minimal test using only built-in Python modules
"""

import json
import os
import sys
from pathlib import Path

def test_basic_functionality():
    """Test basic functionality without external packages"""
    
    print("🧪 HafiPortrait DSLR - Basic Functionality Test")
    print("=" * 50)
    
    # Test 1: Configuration loading
    print("\n1️⃣ Testing Configuration Loading...")
    try:
        with open('config.json') as f:
            config = json.load(f)
        print("✅ config.json loaded successfully")
        print(f"   Base URL: {config['web_project']['base_url']}")
        print(f"   Upload Endpoint: {config['web_project']['upload_endpoint']}")
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False
    
    # Test 2: Directory structure
    print("\n2️⃣ Testing Directory Structure...")
    required_dirs = ['lib', 'presets', 'test_photos', 'temp', 'logs']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ exists")
        else:
            print(f"⚠️  {dir_name}/ missing - creating...")
            dir_path.mkdir(exist_ok=True)
    
    # Test 3: Required files
    print("\n3️⃣ Testing Required Files...")
    required_files = [
        'lib/uploader_robust.py',
        'setup_credentials.sh',
        '.env.example'
    ]
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")
    
    # Test 4: Environment setup
    print("\n4️⃣ Testing Environment Setup...")
    if Path('.env').exists():
        print("✅ .env file exists")
        # Load basic env vars
        env_vars = {}
        with open('.env') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        
        important_vars = ['NEXT_PUBLIC_SUPABASE_URL', 'NEXT_PUBLIC_APP_URL']
        for var in important_vars:
            if var in env_vars:
                print(f"✅ {var} configured")
            else:
                print(f"⚠️  {var} missing")
    else:
        print("⚠️  .env file missing - run ./setup_credentials.sh")
    
    print("\n🎉 Basic functionality test completed!")
    return True

def create_simple_test_script():
    """Create simple test script without external dependencies"""
    
    test_script = '''#!/usr/bin/env python3
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
    
    print("\\n📋 Next Steps:")
    print("1. Run ./setup_credentials.sh")
    print("2. Install packages: pip install --user requests python-dotenv")
    print("3. Test connection: python3 simple_connection_test.py")

if __name__ == "__main__":
    simple_config_test()
'''
    
    with open('simple_test.py', 'w') as f:
        f.write(test_script)
    
    os.chmod('simple_test.py', 0o755)
    print("✅ Created simple_test.py")

if __name__ == "__main__":
    test_basic_functionality()
    create_simple_test_script()
