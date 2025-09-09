#!/usr/bin/env python3
"""
🧪 Complete System Test
Test semua komponen DSLR system secara comprehensive
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path

# Add lib directory to path
sys.path.append(str(Path(__file__).parent / 'lib'))

try:
    from utils import setup_logging, load_config, create_status_file
    from camera import CameraDetector, DSLRMonitor
    from preset_processor import PresetProcessor, AdobePresetParser
    from watermark_manager import WatermarkManager
    from uploader_robust import RobustHafiPortraitUploader as HafiPortraitUploader
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
    import requests
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class SystemTester:
    """Complete system testing class"""
    
    def __init__(self):
        self.logger = setup_logging("INFO")
        self.test_results = {}
        
        # Load config if available
        try:
            self.config = load_config()
        except:
            self.config = self._create_test_config()
    
    def _create_test_config(self) -> dict:
        """Create test configuration"""
        return {
            "camera": {
                "model": "Nikon D7100",
                "watch_directory": "./test_photos/",
                "file_extensions": [".NEF", ".JPG", ".JPEG"]
            },
            "presets": {
                "directory": "./presets/",
                "default": "wedding_warm"
            },
            "watermark": {
                "file": "./watermark.png",
                "position": "bottom_center",
                "size_percentage": 15,
                "margin_bottom": 10
            },
            "web_project": {
                "base_url": "http://localhost:3002",
                "upload_endpoint": "/api/dslr/upload",
                "timeout": 30
            }
        }
    
    def run_all_tests(self) -> bool:
        """Run all system tests"""
        
        print("🧪 HafiPortrait DSLR Complete System Test")
        print("=" * 50)
        
        tests = [
            ("Configuration", self.test_configuration),
            ("Dependencies", self.test_dependencies),
            ("Camera Detection", self.test_camera_detection),
            ("Preset System", self.test_preset_system),
            ("Watermark System", self.test_watermark_system),
            ("Upload Client", self.test_upload_client),
            ("File Processing", self.test_file_processing),
            ("Integration", self.test_integration)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            print("-" * 30)
            
            try:
                result = test_func()
                self.test_results[test_name] = result
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                self.test_results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! System ready untuk production.")
            self._print_next_steps()
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Fix issues sebelum continue.")
            self._print_troubleshooting()
        
        return passed == total
    
    def test_configuration(self) -> bool:
        """Test configuration loading"""
        
        try:
            # Test config file exists
            if not os.path.exists("config.json"):
                print("⚠️  config.json tidak ditemukan, menggunakan test config")
                return True
            
            # Test config loading
            config = load_config()
            print(f"✅ Configuration loaded: {len(config)} sections")
            
            # Validate required sections
            required_sections = ['camera', 'presets', 'watermark', 'web_project']
            for section in required_sections:
                if section not in config:
                    print(f"❌ Missing config section: {section}")
                    return False
                print(f"  ✅ {section}: OK")
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False
    
    def test_dependencies(self) -> bool:
        """Test Python dependencies"""
        
        dependencies = [
            ("PIL (Pillow)", "PIL"),
            ("NumPy", "numpy"),
            ("Requests", "requests"),
            ("Watchdog", "watchdog"),
            ("RawPy", "rawpy"),
            ("gphoto2", "gphoto2")
        ]
        
        missing = []
        
        for name, module in dependencies:
            try:
                __import__(module)
                print(f"  ✅ {name}: Available")
            except ImportError:
                print(f"  ❌ {name}: Missing")
                missing.append(name)
        
        if missing:
            print(f"\n❌ Missing dependencies: {', '.join(missing)}")
            print("Install dengan: pip install -r requirements.txt")
            return False
        
        return True
    
    def test_camera_detection(self) -> bool:
        """Test camera detection"""
        
        try:
            detector = CameraDetector()
            cameras = detector.detect_cameras()
            
            print(f"📷 Detected {len(cameras)} camera(s)")
            
            if cameras:
                for camera in cameras:
                    print(f"  📷 {camera['name']} ({camera['address']})")
                
                # Test Nikon connection
                if detector.connect_nikon_d7100():
                    print("✅ Nikon D7100 connection successful")
                    detector.disconnect()
                    return True
                else:
                    print("⚠️  Nikon D7100 tidak terdeteksi, tapi camera detection working")
                    return True
            else:
                print("⚠️  No cameras detected (normal jika tidak ada camera connected)")
                return True
                
        except Exception as e:
            print(f"❌ Camera detection error: {e}")
            return False
    
    def test_preset_system(self) -> bool:
        """Test Adobe preset system"""
        
        try:
            processor = PresetProcessor(self.config['presets'])
            
            # Test preset loading
            presets = processor.get_available_presets()
            print(f"🎨 Loaded {len(presets)} presets")
            
            if presets:
                for preset in presets:
                    print(f"  🎨 {preset}")
                
                # Test preset parsing
                test_preset = presets[0]
                preset_info = processor.get_preset_info(test_preset)
                
                if preset_info and 'settings' in preset_info:
                    settings_count = len(preset_info['settings'])
                    print(f"✅ Preset '{test_preset}' parsed: {settings_count} settings")
                    return True
                else:
                    print(f"❌ Failed to parse preset '{test_preset}'")
                    return False
            else:
                print("⚠️  No presets found. Add .xmp files ke folder presets/")
                return True
                
        except Exception as e:
            print(f"❌ Preset system error: {e}")
            return False
    
    def test_watermark_system(self) -> bool:
        """Test watermark system"""
        
        try:
            # Create test watermark if not exists
            if not os.path.exists("watermark.png"):
                self._create_test_watermark()
            
            manager = WatermarkManager(self.config['watermark'])
            
            # Test watermark info
            info = manager.get_watermark_info()
            print(f"🏷️ Watermark info:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            
            if info.get('exists'):
                # Test watermark application
                test_image = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
                watermarked = manager.apply_watermark(test_image)
                
                if watermarked.shape == test_image.shape:
                    print("✅ Watermark application successful")
                    return True
                else:
                    print("❌ Watermark application failed")
                    return False
            else:
                print("⚠️  Watermark file tidak ditemukan")
                return True
                
        except Exception as e:
            print(f"❌ Watermark system error: {e}")
            return False
    
    def test_upload_client(self) -> bool:
        """Test upload client"""
        
        try:
            uploader = HafiPortraitUploader(self.config['web_project'])
            
            # Test connection
            if uploader.test_connection():
                print("✅ Web project connection successful")
                
                # Test getting current event
                event = uploader.get_current_event()
                if event:
                    print(f"✅ Current event: {event.get('name', 'Unknown')}")
                else:
                    print("⚠️  No current event (normal untuk testing)")
                
                uploader.close()
                return True
            else:
                print("❌ Web project connection failed")
                print("  Check if web project running di:", self.config['web_project']['base_url'])
                return False
                
        except Exception as e:
            print(f"❌ Upload client error: {e}")
            return False
    
    def test_file_processing(self) -> bool:
        """Test file processing pipeline"""
        
        try:
            # Create test image
            test_image = self._create_test_image()
            
            if not test_image:
                print("❌ Failed to create test image")
                return False
            
            # Test preset processing (if available)
            processor = PresetProcessor(self.config['presets'])
            presets = processor.get_available_presets()
            
            if presets:
                try:
                    processed = processor.apply_preset(test_image, presets[0])
                    print(f"✅ Preset processing: {processed.shape}")
                except Exception as e:
                    print(f"⚠️  Preset processing failed: {e}")
            
            # Test watermark
            if os.path.exists("watermark.png"):
                manager = WatermarkManager(self.config['watermark'])
                test_array = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
                watermarked = manager.apply_watermark(test_array)
                print(f"✅ Watermark processing: {watermarked.shape}")
            
            return True
            
        except Exception as e:
            print(f"❌ File processing error: {e}")
            return False
    
    def test_integration(self) -> bool:
        """Test system integration"""
        
        try:
            # Test status file creation
            status_data = {
                'test': True,
                'timestamp': time.time()
            }
            
            if create_status_file(status_data, "test_status.json"):
                print("✅ Status file creation successful")
                
                # Cleanup
                if os.path.exists("test_status.json"):
                    os.remove("test_status.json")
            else:
                print("❌ Status file creation failed")
                return False
            
            # Test directory creation
            test_dir = "./test_temp/"
            from utils import ensure_directory
            
            if ensure_directory(test_dir):
                print("✅ Directory creation successful")
                
                # Cleanup
                if os.path.exists(test_dir):
                    os.rmdir(test_dir)
            else:
                print("❌ Directory creation failed")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Integration test error: {e}")
            return False
    
    def _create_test_watermark(self):
        """Create test watermark file"""
        
        if not PIL_AVAILABLE:
            return
        
        try:
            # Create watermark image
            watermark = Image.new('RGBA', (300, 80), (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # Try to load font
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            # Draw text with shadow
            text = "HafiPortrait"
            draw.text((2, 2), text, font=font, fill=(0, 0, 0, 128))  # Shadow
            draw.text((0, 0), text, font=font, fill=(255, 255, 255, 200))  # Main text
            
            watermark.save("watermark.png")
            print("✅ Test watermark created: watermark.png")
            
        except Exception as e:
            print(f"⚠️  Could not create test watermark: {e}")
    
    def _create_test_image(self) -> str:
        """Create test image file"""
        
        if not PIL_AVAILABLE:
            return None
        
        try:
            # Create test image
            image = Image.new('RGB', (800, 600), (100, 150, 200))
            draw = ImageDraw.Draw(image)
            
            # Add some content
            draw.rectangle([100, 100, 700, 500], fill=(200, 200, 200))
            draw.text((200, 250), "Test Image", fill=(0, 0, 0))
            
            test_file = "test_image.jpg"
            image.save(test_file, 'JPEG')
            
            return test_file
            
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None
    
    def _print_next_steps(self):
        """Print next steps after successful test"""
        
        print("\n📋 Next Steps:")
        print("1. Connect Nikon D7100 via USB")
        print("2. Add your Adobe Lightroom presets (.xmp) ke folder presets/")
        print("3. Add your watermark.png file")
        print("4. Edit config.json (set watch_directory dan web_project_url)")
        print("5. Start web project di VPS")
        print("6. Run: python run.py")
    
    def _print_troubleshooting(self):
        """Print troubleshooting info"""
        
        print("\n🔧 Troubleshooting:")
        print("- Dependencies: pip install -r requirements.txt")
        print("- gphoto2: ./setup.sh (Linux/Mac) atau setup.bat (Windows)")
        print("- Camera: Check USB connection dan PTP mode")
        print("- Web project: Check if running di configured URL")
        print("- Config: Validate config.json format")


def main():
    """Main test function"""
    
    tester = SystemTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()