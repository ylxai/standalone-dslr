#!/usr/bin/env python3
"""
🔍 gphoto2 Test Script
Test gphoto2 installation dan camera detection untuk Nikon D7100
"""

import sys
import os
import json
from pathlib import Path

# Add lib directory to path
sys.path.append(str(Path(__file__).parent / 'lib'))

try:
    from camera import CameraDetector, DSLRMonitor
except ImportError as e:
    print(f"❌ Error importing camera module: {e}")
    sys.exit(1)

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def test_gphoto2_installation():
    """Test gphoto2 installation"""
    print_header("Testing gphoto2 Installation")
    
    # Test command line gphoto2
    print("📋 Testing command line gphoto2...")
    result = os.system("gphoto2 --version > /dev/null 2>&1")
    
    if result == 0:
        print("✅ gphoto2 command line: INSTALLED")
        os.system("gphoto2 --version | head -n1")
    else:
        print("❌ gphoto2 command line: NOT FOUND")
        print("   Install gphoto2 terlebih dahulu:")
        print("   Linux: sudo apt install gphoto2")
        print("   macOS: brew install gphoto2")
        print("   Windows: Download dari gphoto.org")
    
    # Test Python binding
    print("\n📋 Testing gphoto2 Python binding...")
    try:
        import gphoto2 as gp
        print("✅ gphoto2 Python binding: AVAILABLE")
        print(f"   Version: {gp.__version__}")
    except ImportError:
        print("❌ gphoto2 Python binding: NOT AVAILABLE")
        print("   Install dengan: pip install gphoto2")
        return False
    
    return True

def test_camera_detection():
    """Test camera detection"""
    print_header("Testing Camera Detection")
    
    detector = CameraDetector()
    
    print("📋 Scanning untuk cameras...")
    cameras = detector.detect_cameras()
    
    if not cameras:
        print("❌ No cameras detected")
        print("\n🔧 Troubleshooting:")
        print("   1. Pastikan Nikon D7100 connected via USB")
        print("   2. Camera dalam mode PTP/MTP (bukan Mass Storage)")
        print("   3. USB cable working properly")
        print("   4. Camera turned ON")
        return False
    
    print(f"✅ Found {len(cameras)} camera(s):")
    for i, camera in enumerate(cameras, 1):
        print(f"   {i}. {camera['name']}")
        print(f"      Address: {camera['address']}")
        print(f"      Model: {camera['model']}")
    
    # Check for Nikon D7100 specifically
    nikon_found = False
    for camera in cameras:
        if 'nikon' in camera['name'].lower():
            nikon_found = True
            if 'd7100' in camera['name'].lower():
                print(f"\n🎯 Nikon D7100 DETECTED: {camera['name']}")
            else:
                print(f"\n📷 Nikon camera found: {camera['name']}")
                print("   (Bukan D7100, tapi mungkin compatible)")
    
    if not nikon_found:
        print("\n⚠️  No Nikon cameras detected")
        print("   Script ini dioptimasi untuk Nikon D7100")
    
    return nikon_found

def test_nikon_connection():
    """Test connection ke Nikon D7100"""
    print_header("Testing Nikon D7100 Connection")
    
    detector = CameraDetector()
    
    print("📋 Attempting to connect to Nikon D7100...")
    if detector.connect_nikon_d7100():
        print("✅ Nikon D7100 connection: SUCCESS")
        
        # Get camera info
        print("\n📋 Getting camera information...")
        info = detector.get_camera_info()
        
        if info.get('connected'):
            print("✅ Camera info retrieved:")
            print(f"   Model: {info.get('model', 'Unknown')}")
            
            if 'battery' in info and info['battery']:
                print(f"   Battery: {info['battery']}")
            
            if 'storage' in info:
                storage = info['storage']
                if storage.get('free_space'):
                    print(f"   Free space: {storage['free_space']} images")
            
            if 'settings' in info:
                settings = info['settings']
                if settings:
                    print("   Current settings:")
                    for key, value in settings.items():
                        print(f"     {key}: {value}")
        
        detector.disconnect()
        return True
    else:
        print("❌ Nikon D7100 connection: FAILED")
        print("\n🔧 Troubleshooting:")
        print("   1. Check USB connection")
        print("   2. Camera mode: PTP/MTP")
        print("   3. Camera permissions (Linux: plugdev group)")
        print("   4. Try different USB port/cable")
        return False

def test_file_monitoring():
    """Test file monitoring setup"""
    print_header("Testing File Monitoring Setup")
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found")
        return False
    
    watch_dir = config['camera']['watch_directory']
    print(f"📋 Watch directory: {watch_dir}")
    
    if watch_dir == "/path/to/camera/folder":
        print("⚠️  Default watch directory detected")
        print("   Edit config.json dan set proper camera folder path")
        return False
    
    if os.path.exists(watch_dir):
        print("✅ Watch directory exists")
        
        # Check permissions
        if os.access(watch_dir, os.R_OK):
            print("✅ Directory readable")
        else:
            print("❌ Directory not readable")
            return False
        
        # List files
        files = list(Path(watch_dir).glob('*'))
        print(f"   Contains {len(files)} files/folders")
        
        # Check for photo files
        photo_extensions = config['camera']['file_extensions']
        photo_files = []
        for ext in photo_extensions:
            photo_files.extend(Path(watch_dir).glob(f'*{ext}'))
            photo_files.extend(Path(watch_dir).glob(f'*{ext.lower()}'))
        
        if photo_files:
            print(f"✅ Found {len(photo_files)} existing photo files")
        else:
            print("📷 No existing photo files (normal untuk new setup)")
        
        return True
    else:
        print("❌ Watch directory does not exist")
        print(f"   Create directory: mkdir -p {watch_dir}")
        return False

def main():
    """Main test function"""
    print("🎯 HafiPortrait DSLR gphoto2 Test")
    print("================================")
    
    tests = [
        ("gphoto2 Installation", test_gphoto2_installation),
        ("Camera Detection", test_camera_detection),
        ("Nikon D7100 Connection", test_nikon_connection),
        ("File Monitoring Setup", test_file_monitoring)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print_header("Test Summary")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready untuk next step.")
        print("\n📋 Next steps:")
        print("1. Add Adobe Lightroom presets ke folder presets/")
        print("2. Add watermark.png file")
        print("3. Edit config.json (set proper watch_directory)")
        print("4. Run: python run.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Fix issues sebelum continue.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)