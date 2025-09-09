#!/bin/bash
# 🔧 Install Packages for DSLR System
# Handles externally managed environment

echo "🔧 Installing DSLR System Packages"
echo "=================================="

echo "📦 Installing essential packages with --user flag..."

# Install essential packages to user directory
pip3 install --user requests python-dotenv

echo "✅ Essential packages installed!"

echo ""
echo "🧪 Testing installation..."
python3 -c "
try:
    import requests
    import os
    from dotenv import load_dotenv
    print('✅ requests: Working')
    print('✅ python-dotenv: Working')
    print('✅ Ready for DSLR system!')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

echo ""
echo "📋 Optional packages (install if needed):"
echo "pip3 install --user Pillow numpy supabase boto3"
echo ""
echo "📋 Next steps:"
echo "1. Run ./setup_credentials.sh"
echo "2. Test: python3 simple_test.py"
echo "3. Run: python3 lib/uploader_robust.py"
