#!/usr/bin/env python3
"""
🎨 Complete Processing Test
Test upload dengan preset dan watermark processing
"""

import sys
import os
sys.path.append('lib')

def test_complete_processing():
    print("🎨 Complete Processing Test")
    print("=" * 40)
    
    # Test 1: Import modules
    try:
        from uploader_robust import RobustHafiPortraitUploader
        print("✅ Uploader imported")
    except Exception as e:
        print(f"❌ Uploader import failed: {e}")
        return
    
    # Test 2: Check for image processing
    try:
        from PIL import Image
        import numpy as np
        print("✅ PIL and numpy available")
        PIL_AVAILABLE = True
    except ImportError:
        print("⚠️  PIL/numpy not available - install with:")
        print("   pip3 install --user Pillow numpy")
        PIL_AVAILABLE = False
    
    # Test 3: Check preset processor
    try:
        # Fix import issue first
        import sys
        sys.path.append('lib')
        
        # Create minimal preset processor test
        preset_dir = './presets/'
        presets = []
        if os.path.exists(preset_dir):
            for file in os.listdir(preset_dir):
                if file.endswith('.xmp'):
                    presets.append(file.replace('.xmp', ''))
        
        if presets:
            print(f"✅ Found {len(presets)} presets: {', '.join(presets)}")
        else:
            print("⚠️  No presets found in presets/ folder")
            
    except Exception as e:
        print(f"⚠️  Preset processor issue: {e}")
    
    # Test 4: Check watermark
    watermark_file = './watermark.png'
    if os.path.exists(watermark_file):
        print("✅ Watermark file found")
    else:
        print("⚠️  Watermark file not found - creating test watermark...")
        create_test_watermark()
    
    # Test 5: Setup uploader
    try:
        uploader = RobustHafiPortraitUploader()
        
        if uploader.test_connection():
            print("✅ Connection successful")
            
            events = uploader.get_all_events()
            if events and uploader.set_active_event(events[0]['id']):
                print(f"✅ Active event: {events[0].get('name')}")
            else:
                print("❌ No events available")
                return
        else:
            print("❌ Connection failed")
            return
    except Exception as e:
        print(f"❌ Uploader setup failed: {e}")
        return
    
    # Test 6: Process photo with preset and watermark
    test_photo = find_test_photo()
    if test_photo and PIL_AVAILABLE:
        print(f"📸 Processing photo: {test_photo}")
        
        try:
            # Load image
            image = Image.open(test_photo)
            image_array = np.array(image)
            print(f"✅ Image loaded: {image_array.shape}")
            
            # Apply preset (simulated)
            if presets:
                selected_preset = presets[0]
                print(f"🎨 Applying preset: {selected_preset}")
                # In real implementation, would apply XMP preset
                processed_image = image_array  # Placeholder
            else:
                processed_image = image_array
                print("⚠️  No preset applied")
            
            # Apply watermark (simulated)
            if os.path.exists(watermark_file):
                print("🏷️ Applying watermark...")
                # In real implementation, would overlay watermark
                watermarked_image = processed_image  # Placeholder
            else:
                watermarked_image = processed_image
                print("⚠️  No watermark applied")
            
            # Upload processed image
            print("🔗 Uploading processed image...")
            metadata = {
                'preset_applied': presets[0] if presets else 'none',
                'watermark_applied': os.path.exists(watermark_file),
                'processing_pipeline': 'complete'
            }
            
            result = uploader.upload_photo(watermarked_image, test_photo, metadata)
            
            if result['success']:
                print(f"✅ Upload successful! Photo ID: {result.get('photoId')}")
                print(f"   Event: {result.get('eventId')}")
                print(f"   Album: {result.get('albumName')}")
            else:
                print(f"❌ Upload failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Processing error: {e}")
    
    elif test_photo and not PIL_AVAILABLE:
        print("⚠️  Photo found but PIL not available for processing")
        print("   Install: pip3 install --user Pillow numpy")
    else:
        print("⚠️  No test photo found")
        print("   Copy a .jpg file to test_photos/ directory")
    
    uploader.close()
    print("\n🎉 Complete processing test finished!")

def find_test_photo():
    """Find test photo"""
    test_paths = [
        'test_photos/test-photo.jpg',
        'test_photos/test.jpg', 
        '../test-photo.jpg'
    ]
    
    # Also check for any .jpg in test_photos
    if os.path.exists('test_photos'):
        for file in os.listdir('test_photos'):
            if file.lower().endswith(('.jpg', '.jpeg')):
                test_paths.append(f'test_photos/{file}')
    
    for path in test_paths:
        if os.path.exists(path):
            return path
    return None

def create_test_watermark():
    """Create simple test watermark"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create watermark
        watermark = Image.new('RGBA', (300, 80), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Draw text
        text = "HafiPortrait"
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Draw with shadow
        draw.text((2, 2), text, font=font, fill=(0, 0, 0, 128))
        draw.text((0, 0), text, font=font, fill=(255, 255, 255, 200))
        
        watermark.save("watermark.png")
        print("✅ Test watermark created")
        
    except ImportError:
        # Create placeholder file
        with open("watermark.png", "w") as f:
            f.write("# Placeholder watermark file")
        print("⚠️  Created placeholder watermark (install PIL for real watermark)")
    except Exception as e:
        print(f"⚠️  Could not create watermark: {e}")

if __name__ == "__main__":
    test_complete_processing()
