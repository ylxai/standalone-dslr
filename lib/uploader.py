#!/usr/bin/env python3
"""
🔗 Upload Client
Handles upload ke HafiPortrait web project via API
"""

import os
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Optional, Any
from io import BytesIO

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class HafiPortraitUploader:
    """Upload client untuk HafiPortrait web project"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.base_url = config.get('base_url', 'http://localhost:3002')
        self.upload_endpoint = config.get('upload_endpoint', '/api/dslr/upload')
        self.status_endpoint = config.get('status_endpoint', '/api/dslr/status')
        self.timeout = config.get('timeout', 30)
        
        # Session untuk connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HafiPortrait-DSLR-Client/1.0'
        })
        
        # Current event context
        self.current_event = None
        
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
    
    def get_current_event(self) -> Optional[Dict]:
        """Get current active event dari web project"""
        
        try:
            url = f"{self.base_url}/api/admin/events/current"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                event_data = response.json()
                self.current_event = event_data
                self.logger.info(f"Current event: {event_data.get('name', 'Unknown')}")
                return event_data
            else:
                self.logger.warning(f"No current event found: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting current event: {e}")
            return None
    
    def set_event_context(self, event_id: str, album_name: str = "Official", 
                         preset_name: str = "wedding_warm") -> bool:
        """Set event context untuk uploads"""
        
        try:
            url = f"{self.base_url}/api/dslr/set-event"
            data = {
                'eventId': event_id,
                'albumName': album_name,
                'presetName': preset_name,
                'autoUpload': True
            }
            
            response = self.session.post(url, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                self.current_event = {
                    'id': event_id,
                    'albumName': album_name,
                    'presetName': preset_name
                }
                self.logger.info(f"Event context set: {event_id}")
                return True
            else:
                self.logger.error(f"Failed to set event context: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting event context: {e}")
            return False
    
    def upload_photo(self, image_data: np.ndarray, original_file_path: str, 
                    metadata: Dict = None) -> Dict[str, Any]:
        """Upload processed photo ke web project"""
        
        if not self.current_event:
            # Try to get current event
            if not self.get_current_event():
                return {
                    'success': False,
                    'error': 'No active event found'
                }
        
        try:
            # Convert numpy array to JPEG bytes
            jpeg_bytes = self._convert_to_jpeg_bytes(image_data)
            
            # Prepare upload data
            upload_data = self._prepare_upload_data(original_file_path, metadata)
            
            # Upload file
            return self._upload_file(jpeg_bytes, upload_data)
            
        except Exception as e:
            self.logger.error(f"Error uploading photo: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_to_jpeg_bytes(self, image_data: np.ndarray, quality: int = 95) -> bytes:
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
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        return buffer.getvalue()
    
    def _prepare_upload_data(self, original_file_path: str, metadata: Dict = None) -> Dict:
        """Prepare upload data"""
        
        file_path = Path(original_file_path)
        
        upload_data = {
            'eventId': self.current_event.get('id'),
            'albumName': self.current_event.get('albumName', 'Official'),
            'originalFileName': file_path.name,
            'source': 'dslr_auto_upload',
            'camera': 'Nikon D7100',
            'presetApplied': self.current_event.get('presetName', 'unknown'),
            'watermarkApplied': True,
            'timestamp': int(time.time())
        }
        
        # Add metadata if provided
        if metadata:
            upload_data.update(metadata)
        
        return upload_data
    
    def _upload_file(self, jpeg_bytes: bytes, upload_data: Dict) -> Dict[str, Any]:
        """Upload file ke web project"""
        
        try:
            url = f"{self.base_url}{self.upload_endpoint}"
            
            # Prepare multipart form data
            files = {
                'photo': ('processed_photo.jpg', jpeg_bytes, 'image/jpeg')
            }
            
            # Upload
            response = self.session.post(
                url, 
                files=files, 
                data=upload_data, 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"✅ Upload successful: {result.get('photoId', 'unknown')}")
                return {
                    'success': True,
                    'photoId': result.get('photoId'),
                    'url': result.get('url'),
                    'message': 'Upload successful'
                }
            else:
                error_msg = f"Upload failed: HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('error', 'Unknown error')
                    error_msg += f" - {error_detail}"
                except:
                    pass
                
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = "Upload timeout"
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
    
    def upload_original_backup(self, original_file_path: str) -> Dict[str, Any]:
        """Upload original file untuk backup"""
        
        try:
            url = f"{self.base_url}/api/dslr/backup"
            
            with open(original_file_path, 'rb') as f:
                files = {
                    'original': (Path(original_file_path).name, f, 'application/octet-stream')
                }
                
                data = {
                    'eventId': self.current_event.get('id') if self.current_event else None,
                    'source': 'dslr_backup'
                }
                
                response = self.session.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"✅ Original backup successful")
                return {
                    'success': True,
                    'backupId': result.get('backupId'),
                    'message': 'Backup successful'
                }
            else:
                return {
                    'success': False,
                    'error': f"Backup failed: HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Backup error: {e}"
            }
    
    def get_upload_status(self) -> Dict[str, Any]:
        """Get upload status dari web project"""
        
        try:
            url = f"{self.base_url}{self.status_endpoint}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'status': 'error',
                    'message': f"Status check failed: HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Status check error: {e}"
            }
    
    def retry_upload(self, image_data: np.ndarray, original_file_path: str, 
                    max_retries: int = 3, retry_delay: int = 5) -> Dict[str, Any]:
        """Upload dengan retry mechanism"""
        
        for attempt in range(max_retries):
            try:
                result = self.upload_photo(image_data, original_file_path)
                
                if result['success']:
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
def test_uploader():
    """Test uploader functionality"""
    print("🔗 Testing upload client...")
    
    config = {
        'base_url': 'http://localhost:3002',
        'upload_endpoint': '/api/dslr/upload',
        'timeout': 30
    }
    
    uploader = HafiPortraitUploader(config)
    
    # Test connection
    if uploader.test_connection():
        print("✅ Connection test successful")
    else:
        print("❌ Connection test failed")
        return
    
    # Test getting current event
    event = uploader.get_current_event()
    if event:
        print(f"✅ Current event: {event.get('name', 'Unknown')}")
    else:
        print("⚠️  No current event found")
    
    # Test upload status
    status = uploader.get_upload_status()
    print(f"Upload status: {status}")
    
    uploader.close()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_uploader()