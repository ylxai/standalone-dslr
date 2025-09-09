#!/usr/bin/env python3
"""
🔗 Robust Upload Client
Real database integration dengan HafiPortrait web project
Uses REAL API endpoints and Supabase database
"""

import os
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Optional, Any, List
from io import BytesIO

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables
except ImportError:
    pass


class RobustHafiPortraitUploader:
    """Robust upload client dengan real database integration"""
    
    def __init__(self, config: Dict = None):
        # Load environment variables
        self.base_url = os.getenv('NEXT_PUBLIC_APP_URL', 'http://localhost:3002')
        self.timeout = 30
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Session untuk connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HafiPortrait-DSLR-Client/2.0',
            'Content-Type': 'application/json'
        })
        
        # Current event context
        self.current_event = None
        self.active_config = None
        
        # Load any existing active config
        self._load_active_config()
    
    def _load_active_config(self):
        """Load active DSLR configuration"""
        try:
            config_file = os.getenv('CONFIG_FILE', './dslr_active_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.active_config = json.load(f)
                    self.current_event = self.active_config.get('activeEvent')
                    self.logger.info(f"Loaded active config: {self.current_event.get('name') if self.current_event else 'None'}")
        except Exception as e:
            self.logger.warning(f"Could not load active config: {e}")
    
    def test_connection(self) -> bool:
        """Test connection ke web project"""
        try:
            url = f"{self.base_url}/api/health"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f"✅ Connection to {self.base_url} successful")
                return True
            else:
                self.logger.error(f"❌ Connection failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Connection error: {e}")
            return False
    
    def get_all_events(self) -> List[Dict]:
        """Get all events dari real database"""
        try:
            url = f"{self.base_url}/api/admin/events"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                events = response.json()
                self.logger.info(f"✅ Retrieved {len(events)} events from database")
                return events
            else:
                self.logger.error(f"❌ Failed to get events: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"❌ Error getting events: {e}")
            return []
    
    def set_active_event(self, event_id: str, album_name: str = "Official", 
                        preset_name: str = None, auto_upload: bool = True,
                        watermark_enabled: bool = True) -> bool:
        """Set active event menggunakan real API"""
        try:
            # Use environment default if not specified
            if preset_name is None:
                preset_name = os.getenv('DSLR_DEFAULT_PRESET', 'wedding_warm')
            
            url = f"{self.base_url}/api/admin/dslr/set-active-event"
            data = {
                'eventId': event_id,
                'albumName': album_name,
                'presetName': preset_name,
                'autoUpload': auto_upload,
                'watermarkEnabled': watermark_enabled
            }
            
            # Remove Content-Type header for this request
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = self.session.post(url, json=data, timeout=self.timeout, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.active_config = result.get('config')
                self.current_event = self.active_config.get('activeEvent') if self.active_config else None
                
                self.logger.info(f"✅ Active event set: {event_id}")
                return True
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('error', '')
                    if 'availableEvents' in error_data:
                        available = error_data['availableEvents']
                        self.logger.info(f"Available events: {[e['name'] for e in available]}")
                except:
                    pass
                
                self.logger.error(f"❌ Failed to set active event: HTTP {response.status_code} - {error_detail}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error setting active event: {e}")
            return False
    
    def upload_photo(self, image_data: np.ndarray, original_file_path: str, 
                    metadata: Dict = None) -> Dict[str, Any]:
        """Upload processed photo menggunakan real API endpoint"""
        
        if not self.current_event:
            self.logger.error("❌ No active event set")
            return {
                'success': False,
                'error': 'No active event configured'
            }
        
        try:
            event_id = self.current_event.get('id')
            album_name = self.current_event.get('albumName', 'Official')
            uploader_name = os.getenv('DSLR_UPLOADER_NAME', 'DSLR Auto')
            
            # Convert numpy array to file-like object
            jpeg_bytes = self._convert_to_jpeg_bytes(image_data)
            
            # Use real upload endpoint
            url = f"{self.base_url}/api/events/{event_id}/photos"
            
            # Prepare multipart form data
            files = {
                'photo': ('dslr_photo.jpg', BytesIO(jpeg_bytes), 'image/jpeg')
            }
            
            data = {
                'albumName': album_name,
                'uploaderName': uploader_name
            }
            
            # Add metadata if provided
            if metadata:
                for key, value in metadata.items():
                    if key not in data:  # Don't override required fields
                        data[key] = str(value)
            
            # Remove Content-Type header for multipart upload
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            # Upload
            response = self.session.post(
                url, 
                files=files, 
                data=data, 
                timeout=60,  # Longer timeout for upload
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                photo_id = result.get('id', 'unknown')
                self.logger.info(f"✅ Upload successful: Photo ID {photo_id}")
                
                return {
                    'success': True,
                    'photoId': photo_id,
                    'url': result.get('url'),
                    'message': 'Upload successful',
                    'eventId': event_id,
                    'albumName': album_name
                }
            else:
                error_msg = f"Upload failed: HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('message', 'Unknown error')
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = f"Upload error: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def _convert_to_jpeg_bytes(self, image_data: np.ndarray) -> bytes:
        """Convert numpy array to JPEG bytes"""
        
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL required untuk image conversion")
        
        # Ensure uint8 format
        if image_data.dtype != np.uint8:
            if image_data.max() <= 1.0:
                image_data = (image_data * 255).astype(np.uint8)
            else:
                image_data = image_data.astype(np.uint8)
        
        # Convert to PIL Image
        image = Image.fromarray(image_data)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save to bytes
        buffer = BytesIO()
        quality = int(os.getenv('DSLR_JPEG_QUALITY', '95'))
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        return buffer.getvalue()
    
    def get_dslr_status(self) -> Dict[str, Any]:
        """Get DSLR status dari real API"""
        try:
            url = f"{self.base_url}/api/admin/dslr/status"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f"Status check failed: HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Status check error: {e}"
            }
    
    def retry_upload(self, image_data: np.ndarray, original_file_path: str, 
                    max_retries: int = None, retry_delay: int = None) -> Dict[str, Any]:
        """Upload dengan retry mechanism"""
        
        if max_retries is None:
            max_retries = int(os.getenv('DSLR_MAX_RETRIES', '3'))
        if retry_delay is None:
            retry_delay = int(os.getenv('DSLR_RETRY_DELAY', '5'))
        
        for attempt in range(max_retries):
            try:
                result = self.upload_photo(image_data, original_file_path)
                
                if result['success']:
                    if attempt > 0:
                        self.logger.info(f"✅ Upload successful on attempt {attempt + 1}")
                    return result
                
                if attempt < max_retries - 1:
                    self.logger.warning(f"Upload attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Upload attempt {attempt + 1} error: {e}, retrying...")
                    time.sleep(retry_delay)
                else:
                    return {
                        'success': False,
                        'error': f"All retry attempts failed: {e}"
                    }
        
        return {
            'success': False,
            'error': f"Upload failed after {max_retries} attempts"
        }
    
    def close(self):
        """Close session"""
        self.session.close()


# Test functions
def test_robust_uploader():
    """Test robust uploader functionality"""
    print("🔗 Testing Robust Upload Client...")
    
    uploader = RobustHafiPortraitUploader()
    
    # Test connection
    print("\n1. Testing connection...")
    if uploader.test_connection():
        print("✅ Connection test successful")
    else:
        print("❌ Connection test failed")
        return
    
    # Test getting events
    print("\n2. Testing events retrieval...")
    events = uploader.get_all_events()
    if events:
        print(f"✅ Retrieved {len(events)} events:")
        for event in events[:3]:  # Show first 3
            print(f"   - {event.get('name', 'Unknown')} (ID: {event.get('id')})")
    else:
        print("❌ No events retrieved")
        return
    
    # Test setting active event
    if events:
        print("\n3. Testing set active event...")
        test_event = events[0]
        if uploader.set_active_event(test_event['id']):
            print(f"✅ Active event set: {test_event.get('name')}")
        else:
            print("❌ Failed to set active event")
    
    # Test DSLR status
    print("\n4. Testing DSLR status...")
    status = uploader.get_dslr_status()
    if status.get('success'):
        print("✅ DSLR status retrieved")
        print(f"   Status: {status.get('status', {})}")
    else:
        print(f"❌ DSLR status failed: {status.get('error')}")
    
    uploader.close()
    print("\n🎉 Robust uploader test completed!")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_robust_uploader()