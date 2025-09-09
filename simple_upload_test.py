#!/usr/bin/env python3
"""
🧪 Simple Upload Test
Test upload tanpa dependencies berat
"""

import sys
import os
sys.path.append('lib')

def test_simple_upload():
    print("🧪 Simple Upload Test")
    print("=" * 30)
    
    # Test 1: Import uploader
    try:
        from uploader_robust import RobustHafiPortraitUploader
        print("✅ Uploader import successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test 2: Create uploader
    try:
        uploader = RobustHafiPortraitUploader()
        print("✅ Uploader created")
    except Exception as e:
        print(f"❌ Uploader creation failed: {e}")
        return
    
    # Test 3: Test connection
    try:
        if uploader.test_connection():
            print("✅ Connection successful")
        else:
            print("❌ Connection failed")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test 4: Get events
    try:
        events = uploader.get_all_events()
        if events:
            print(f"✅ Found {len(events)} events")
            
            # Set active event
            test_event = events[0]
            if uploader.set_active_event(test_event['id']):
                print(f"✅ Active event set: {test_event.get('name')}")
            else:
                print("❌ Failed to set active event")
                return
        else:
            print("❌ No events found")
            return
    except Exception as e:
        print(f"❌ Events error: {e}")
        return
    
    # Test 5: Check for test photo
    test_photos = ['test_photos/test-photo.jpg', '../test-photo.jpg', 'test-photo.jpg']
    test_photo = None
    
    for photo_path in test_photos:
        if os.path.exists(photo_path):
            test_photo = photo_path
            break
    
    if test_photo:
        print(f"✅ Found test photo: {test_photo}")
        
        # Try to install PIL if needed
        try:
            from PIL import Image
            import numpy as np
            
            # Load and test upload
            print("📸 Loading image...")
            image = Image.open(test_photo)
            image_array = np.array(image)
            
            print("🔗 Testing upload...")
            result = uploader.upload_photo(image_array, test_photo)
            
            if result['success']:
                print(f"✅ Upload successful! Photo ID: {result.get('photoId')}")
            else:
                print(f"❌ Upload failed: {result.get('error')}")
                
        except ImportError:
            print("⚠️  PIL/numpy not available - install with:")
            print("   pip3 install --user Pillow numpy")
        except Exception as e:
            print(f"❌ Upload test error: {e}")
    else:
        print("⚠️  No test photo found")
        print("   Copy a .jpg file to test_photos/ directory")
    
    uploader.close()
    print("\n🎉 Simple upload test completed!")

if __name__ == "__main__":
    test_simple_upload()
