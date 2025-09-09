#!/usr/bin/env python3
"""
📷 Camera Detection and Monitoring Module
Handles gphoto2 integration untuk Nikon D7100
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict

try:
    import gphoto2 as gp
    GPHOTO2_AVAILABLE = True
except ImportError:
    GPHOTO2_AVAILABLE = False
    print("⚠️  gphoto2 Python binding tidak tersedia")
    print("   Menggunakan alternative file monitoring")

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CameraDetector:
    """Detect dan manage camera connection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.camera = None
        self.camera_model = None
        
    def detect_cameras(self) -> List[Dict]:
        """Detect semua cameras yang terhubung"""
        cameras = []
        
        if not GPHOTO2_AVAILABLE:
            self.logger.warning("gphoto2 tidak tersedia, skip camera detection")
            return cameras
        
        try:
            # Auto-detect cameras
            camera_list = gp.Camera.autodetect()
            
            for name, addr in camera_list:
                cameras.append({
                    'name': name,
                    'address': addr,
                    'model': name.split()[0] if name else 'Unknown'
                })
                
            self.logger.info(f"Detected {len(cameras)} camera(s)")
            
        except Exception as e:
            self.logger.error(f"Error detecting cameras: {e}")
            
        return cameras
    
    def connect_nikon_d7100(self) -> bool:
        """Connect specifically ke Nikon D7100"""
        if not GPHOTO2_AVAILABLE:
            self.logger.warning("gphoto2 tidak tersedia")
            return False
        
        try:
            cameras = self.detect_cameras()
            
            # Look for Nikon D7100
            for camera_info in cameras:
                if 'nikon' in camera_info['name'].lower() and 'd7100' in camera_info['name'].lower():
                    self.logger.info(f"Found Nikon D7100: {camera_info['name']}")
                    
                    # Initialize camera
                    self.camera = gp.Camera()
                    self.camera.init()
                    self.camera_model = camera_info['name']
                    
                    # Test camera connection
                    config = self.camera.get_config()
                    self.logger.info("✅ Nikon D7100 connected successfully")
                    return True
            
            self.logger.warning("Nikon D7100 tidak ditemukan")
            return False
            
        except Exception as e:
            self.logger.error(f"Error connecting to Nikon D7100: {e}")
            return False
    
    def get_camera_info(self) -> Dict:
        """Get camera information"""
        if not self.camera:
            return {}
        
        try:
            config = self.camera.get_config()
            
            info = {
                'model': self.camera_model,
                'connected': True,
                'battery': self._get_battery_level(),
                'storage': self._get_storage_info(),
                'settings': self._get_camera_settings()
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting camera info: {e}")
            return {'connected': False, 'error': str(e)}
    
    def _get_battery_level(self) -> Optional[str]:
        """Get battery level if available"""
        try:
            config = self.camera.get_config()
            battery = config.get_child_by_name('batterylevel')
            return battery.get_value()
        except:
            return None
    
    def _get_storage_info(self) -> Dict:
        """Get storage information"""
        try:
            storage_info = self.camera.get_storageinfo()
            if storage_info:
                info = storage_info[0]
                return {
                    'free_space': info.freespaceimages,
                    'capacity': info.capacityimages
                }
        except:
            pass
        return {}
    
    def _get_camera_settings(self) -> Dict:
        """Get current camera settings"""
        settings = {}
        
        try:
            config = self.camera.get_config()
            
            # Common settings
            setting_names = ['iso', 'aperture', 'shutterspeed', 'whitebalance']
            
            for setting_name in setting_names:
                try:
                    setting = config.get_child_by_name(setting_name)
                    settings[setting_name] = setting.get_value()
                except:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error getting camera settings: {e}")
        
        return settings
    
    def disconnect(self):
        """Disconnect camera"""
        if self.camera:
            try:
                self.camera.exit()
                self.logger.info("Camera disconnected")
            except:
                pass
            finally:
                self.camera = None
                self.camera_model = None


class FileMonitorHandler(FileSystemEventHandler):
    """Handle file system events untuk new photos"""
    
    def __init__(self, callback, file_extensions=None):
        self.callback = callback
        self.file_extensions = file_extensions or ['.NEF', '.JPG', '.JPEG']
        self.logger = logging.getLogger(__name__)
        
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's a photo file
        if file_path.suffix.upper() in self.file_extensions:
            self.logger.info(f"New photo detected: {file_path.name}")
            
            # Wait a bit untuk ensure file is completely written
            time.sleep(2)
            
            # Call callback function
            try:
                self.callback(str(file_path))
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")


class DSLRMonitor:
    """Main DSLR monitoring class"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize camera detector
        self.camera_detector = CameraDetector()
        
        # File monitoring
        self.observer = None
        self.watch_directory = config.get('watch_directory')
        self.file_extensions = config.get('file_extensions', ['.NEF', '.JPG'])
        
        # Callback for new photos
        self.photo_callback = None
        
    def set_photo_callback(self, callback):
        """Set callback function untuk new photos"""
        self.photo_callback = callback
    
    def start_monitoring(self) -> bool:
        """Start monitoring untuk new photos"""
        
        # Try to connect camera first
        if self.camera_detector.connect_nikon_d7100():
            self.logger.info("✅ Camera connected via gphoto2")
        else:
            self.logger.warning("⚠️  Camera tidak terdeteksi via gphoto2")
        
        # Start file monitoring
        if self.watch_directory and os.path.exists(self.watch_directory):
            return self._start_file_monitoring()
        else:
            self.logger.error(f"Watch directory tidak ditemukan: {self.watch_directory}")
            return False
    
    def _start_file_monitoring(self) -> bool:
        """Start file system monitoring"""
        try:
            # Create event handler
            handler = FileMonitorHandler(
                callback=self._handle_new_photo,
                file_extensions=self.file_extensions
            )
            
            # Create observer
            self.observer = Observer()
            self.observer.schedule(handler, self.watch_directory, recursive=True)
            self.observer.start()
            
            self.logger.info(f"📁 Monitoring directory: {self.watch_directory}")
            self.logger.info(f"📷 File types: {', '.join(self.file_extensions)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting file monitoring: {e}")
            return False
    
    def _handle_new_photo(self, file_path: str):
        """Handle new photo detection"""
        if self.photo_callback:
            self.photo_callback(file_path)
        else:
            self.logger.warning(f"No callback set for new photo: {file_path}")
    
    def get_camera_status(self) -> Dict:
        """Get current camera status"""
        status = {
            'gphoto2_available': GPHOTO2_AVAILABLE,
            'monitoring_active': self.observer is not None and self.observer.is_alive(),
            'watch_directory': self.watch_directory,
            'camera_info': {}
        }
        
        if self.camera_detector.camera:
            status['camera_info'] = self.camera_detector.get_camera_info()
        
        return status
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("File monitoring stopped")
        
        self.camera_detector.disconnect()
        self.logger.info("DSLR monitoring stopped")


# Test functions
def test_camera_detection():
    """Test camera detection"""
    print("🔍 Testing camera detection...")
    
    detector = CameraDetector()
    cameras = detector.detect_cameras()
    
    if cameras:
        print(f"✅ Found {len(cameras)} camera(s):")
        for camera in cameras:
            print(f"  - {camera['name']} ({camera['address']})")
    else:
        print("❌ No cameras detected")
    
    # Test Nikon D7100 connection
    if detector.connect_nikon_d7100():
        print("✅ Nikon D7100 connection successful")
        
        info = detector.get_camera_info()
        print(f"Camera info: {info}")
        
        detector.disconnect()
    else:
        print("❌ Nikon D7100 connection failed")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_camera_detection()