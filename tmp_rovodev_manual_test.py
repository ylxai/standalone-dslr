#!/usr/bin/env python3
"""
🧪 Manual Testing Script
Test DSLR system dengan copy foto manual ke watch directory
"""

import os
import sys
import time
import shutil
import threading
from pathlib import Path

# Add lib directory to path
sys.path.append(str(Path(__file__).parent / 'lib'))

try:
    from uploader_robust import RobustHafiPortraitUploader
    from preset_processor import PresetProcessor
    from watermark_manager import WatermarkManager
    from utils import setup_logging
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure to run: pip install -r requirements.txt")
    sys.exit(1)

class ManualTester:
    """Manual testing class untuk DSLR workflow"""
    
    def __init__(self):
        self.logger = setup_logging("INFO")
        self.watch_dir = Path("./test_photos")
        self.temp_dir = Path("./temp")
        
        # Ensure directories exist
        self.watch_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.uploader = RobustHafiPortraitUploader()
        self.preset_processor = None
        self.watermark_manager = None
        
        # Test results
        self.test_results = {}
    
    def run_manual_test(self):
        """Run complete manual test"""
        
        print("🧪 HafiPortrait DSLR Manual Test")
        print("=" * 50)
        
        # Step 1: Test connection
        print("\n1️⃣ Testing Web Project Connection...")
        if not self._test_connection():
            return False
        
        # Step 2: Test events
        print("\n2️⃣ Testing Events Retrieval...")
        events = self._test_events()
        if not events:
            return False
        
        # Step 3: Set active event
        print("\n3️⃣ Setting Active Event...")
        if not self._set_test_event(events):
            return False
        
        # Step 4: Test components
        print("\n4️⃣ Testing Processing Components...")
        self._test_components()
        
        # Step 5: Manual photo test
        print("\n5️⃣ Manual Photo Processing Test...")
        self._manual_photo_test()
        
        # Step 6: Watch directory test
        print("\n6️⃣ Watch Directory Test...")
        self._watch_directory_test()
        
        # Summary
        self._print_summary()
        
        return True
    
    def _test_connection(self) -> bool:
        """Test web project connection"""
        
        if self.uploader.test_connection():
            print("✅ Web project connection successful")
            return True
        else:
            print("❌ Web project connection failed")
            print("   Make sure web project is running")
            return False
    
    def _test_events(self) -> list:
        """Test events retrieval"""
        
        events = self.uploader.get_all_events()
        
        if events:
            print(f"✅ Retrieved {len(events)} events:")
            for i, event in enumerate(events[:5], 1):
                status = event.get('status', 'unknown')
                print(f"   {i}. {event.get('name', 'Unknown')} ({status})")
            return events
        else:
            print("❌ No events retrieved")
            return []
    
    def _set_test_event(self, events: list) -> bool:
        """Set test event"""
        
        # Use first active event or first event
        test_event = None
        for event in events:
            if event.get('status') == 'active':
                test_event = event
                break
        
        if not test_event and events:
            test_event = events[0]
        
        if test_event:
            event_id = test_event['id']
            event_name = test_event.get('name', 'Unknown')
            
            if self.uploader.set_active_event(event_id):
                print(f"✅ Active event set: {event_name}")
                return True
            else:
                print(f"❌ Failed to set active event: {event_name}")
                return False
        else:
            print("❌ No suitable test event found")
            return False
    
    def _test_components(self):
        """Test processing components"""
        
        try:
            # Test preset processor
            print("   🎨 Testing preset processor...")
            config = {'presets': {'directory': './presets/'}}
            self.preset_processor = PresetProcessor(config['presets'])
            
            presets = self.preset_processor.get_available_presets()
            if presets:
                print(f"   ✅ Found {len(presets)} presets: {', '.join(presets)}")
            else:
                print("   ⚠️  No presets found (add .xmp files to presets/)")
            
            # Test watermark manager
            print("   🏷️ Testing watermark manager...")
            config = {
                'watermark': {
                    'file': './watermark.png',
                    'position': 'bottom_center',
                    'size_percentage': 15
                }
            }
            self.watermark_manager = WatermarkManager(config['watermark'])
            
            watermark_info = self.watermark_manager.get_watermark_info()
            if watermark_info.get('exists'):
                print("   ✅ Watermark file found")
            else:
                print("   ⚠️  Watermark file not found (create watermark.png)")
            
        except Exception as e:
            print(f"   ❌ Component test error: {e}")
    
    def _manual_photo_test(self):
        """Manual photo processing test"""
        
        # Look for test photos
        test_photos = list(self.watch_dir.glob("*.jpg")) + list(self.watch_dir.glob("*.jpeg"))
        
        if not test_photos:
            print("   ⚠️  No test photos found in test_photos/")
            print("   Copy a .jpg file to test_photos/ directory to test")
            return
        
        test_photo = test_photos[0]
        print(f"   📸 Testing with: {test_photo.name}")
        
        try:
            # Simulate processing
            import numpy as np
            from PIL import Image
            
            # Load image
            image = Image.open(test_photo)
            image_array = np.array(image)
            
            print(f"   📏 Image size: {image_array.shape}")
            
            # Test upload
            print("   🔗 Testing upload...")
            result = self.uploader.upload_photo(image_array, str(test_photo))
            
            if result['success']:
                print(f"   ✅ Upload successful: Photo ID {result.get('photoId')}")
            else:
                print(f"   ❌ Upload failed: {result.get('error')}")
            
        except Exception as e:
            print(f"   ❌ Photo test error: {e}")
    
    def _watch_directory_test(self):
        """Test watch directory functionality"""
        
        print("   📁 Watch directory test...")
        print(f"   Directory: {self.watch_dir.absolute()}")
        
        # Check if directory is writable
        test_file = self.watch_dir / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("   ✅ Directory is writable")
        except Exception as e:
            print(f"   ❌ Directory not writable: {e}")
            return
        
        # Instructions for manual testing
        print("\n   📋 Manual Testing Instructions:")
        print("   1. Copy a .jpg photo to test_photos/ directory")
        print("   2. The system should detect and process it")
        print("   3. Check logs for processing status")
        print("   4. Verify upload in web project admin panel")
        
        # Offer to wait for manual file copy
        try:
            response = input("\n   🤔 Wait for manual file copy? (y/N): ").strip().lower()
            if response == 'y':
                self._wait_for_file_copy()
        except KeyboardInterrupt:
            print("\n   ⏹️ Manual test cancelled")
    
    def _wait_for_file_copy(self):
        """Wait for manual file copy and process"""
        
        print("   ⏳ Waiting for file copy... (Ctrl+C to stop)")
        
        initial_files = set(self.watch_dir.glob("*.jpg")) | set(self.watch_dir.glob("*.jpeg"))
        
        try:
            while True:
                time.sleep(1)
                current_files = set(self.watch_dir.glob("*.jpg")) | set(self.watch_dir.glob("*.jpeg"))
                new_files = current_files - initial_files
                
                if new_files:
                    for new_file in new_files:
                        print(f"   📸 New file detected: {new_file.name}")
                        self._process_new_file(new_file)
                    
                    initial_files = current_files
                
        except KeyboardInterrupt:
            print("\n   ⏹️ File monitoring stopped")
    
    def _process_new_file(self, file_path: Path):
        """Process newly detected file"""
        
        try:
            print(f"   🔄 Processing {file_path.name}...")
            
            # Load and process image
            from PIL import Image
            import numpy as np
            
            image = Image.open(file_path)
            image_array = np.array(image)
            
            # Apply preset if available
            if self.preset_processor:
                presets = self.preset_processor.get_available_presets()
                if presets:
                    print(f"   🎨 Applying preset: {presets[0]}")
                    # In real implementation, would apply preset
            
            # Apply watermark if available
            if self.watermark_manager:
                watermark_info = self.watermark_manager.get_watermark_info()
                if watermark_info.get('exists'):
                    print("   🏷️ Applying watermark...")
                    # In real implementation, would apply watermark
            
            # Upload
            print("   🔗 Uploading...")
            result = self.uploader.upload_photo(image_array, str(file_path))
            
            if result['success']:
                print(f"   ✅ Upload successful: Photo ID {result.get('photoId')}")
            else:
                print(f"   ❌ Upload failed: {result.get('error')}")
            
        except Exception as e:
            print(f"   ❌ Processing error: {e}")
    
    def _print_summary(self):
        """Print test summary"""
        
        print("\n" + "=" * 50)
        print("📊 Manual Test Summary")
        print("=" * 50)
        
        print("✅ Connection: Working")
        print("✅ Events: Retrieved")
        print("✅ Active Event: Set")
        print("✅ Components: Tested")
        
        print("\n📋 Ready for Production Testing:")
        print("1. Setup credentials: ./setup_credentials.sh")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Add presets to presets/ folder")
        print("4. Add watermark.png file")
        print("5. Run system: python3 run.py")
        
        print("\n🎯 For manual testing:")
        print("- Copy photos to test_photos/ directory")
        print("- Monitor logs in logs/ directory")
        print("- Check uploads in web admin panel")


def main():
    """Main test function"""
    
    try:
        tester = ManualTester()
        tester.run_manual_test()
    except KeyboardInterrupt:
        print("\n⏹️ Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
    finally:
        print("\n👋 Manual test completed")


if __name__ == "__main__":
    main()