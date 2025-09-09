#!/usr/bin/env python3
"""
🛠️ Utility Functions
Helper functions untuk DSLR system
"""

import os
import json
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Setup logging configuration"""
    
    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """Load configuration dari JSON file"""
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file tidak ditemukan: {config_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON dalam config file: {e}")


def save_config(config: Dict[str, Any], config_file: str = "config.json") -> bool:
    """Save configuration ke JSON file"""
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving config: {e}")
        return False


def generate_hafiportrait_filename(original_filename: str, event_name: str = None) -> str:
    """Generate HafiPortrait standard filename"""
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Get file extension
    file_path = Path(original_filename)
    extension = file_path.suffix.lower()
    
    # Generate event name if not provided
    if not event_name:
        event_name = "event"
    
    # Clean event name (remove spaces, special chars)
    clean_event_name = "".join(c for c in event_name if c.isalnum() or c in ('-', '_')).lower()
    
    # Generate filename
    filename = f"hafiportrait-{clean_event_name}-{timestamp}{extension}"
    
    return filename


def calculate_file_hash(file_path: str, algorithm: str = "md5") -> str:
    """Calculate file hash untuk duplicate detection"""
    
    hash_func = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return ""


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get comprehensive file information"""
    
    path = Path(file_path)
    
    if not path.exists():
        return {}
    
    stat = path.stat()
    
    info = {
        'name': path.name,
        'stem': path.stem,
        'suffix': path.suffix,
        'size_bytes': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'is_file': path.is_file(),
        'is_dir': path.is_dir(),
        'absolute_path': str(path.absolute())
    }
    
    # Add hash for files
    if path.is_file():
        info['md5_hash'] = calculate_file_hash(str(path))
    
    return info


def ensure_directory(directory: str) -> bool:
    """Ensure directory exists, create if needed"""
    
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {e}")
        return False


def cleanup_temp_files(temp_dir: str, max_age_hours: int = 24) -> int:
    """Cleanup old temporary files"""
    
    if not os.path.exists(temp_dir):
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned_count = 0
    
    try:
        for file_path in Path(temp_dir).rglob('*'):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                        logging.info(f"Cleaned up old temp file: {file_path.name}")
                    except Exception as e:
                        logging.error(f"Error deleting {file_path}: {e}")
        
        return cleaned_count
        
    except Exception as e:
        logging.error(f"Error during temp cleanup: {e}")
        return 0


def format_file_size(size_bytes: int) -> str:
    """Format file size untuk human readable"""
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_image_file(file_path: str, supported_formats: List[str] = None) -> bool:
    """Validate if file is supported image format"""
    
    if not supported_formats:
        supported_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.nef', '.cr2', '.arw']
    
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        return False
    
    # Check extension
    if path.suffix.lower() not in [fmt.lower() for fmt in supported_formats]:
        return False
    
    # Check if it's actually a file
    if not path.is_file():
        return False
    
    # Check file size (not empty, not too large)
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb == 0 or size_mb > 100:  # 0MB or > 100MB
        return False
    
    return True


def create_backup_filename(original_path: str, backup_dir: str) -> str:
    """Create backup filename dengan timestamp"""
    
    original = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_name = f"{original.stem}_{timestamp}{original.suffix}"
    backup_path = Path(backup_dir) / backup_name
    
    return str(backup_path)


def monitor_system_resources() -> Dict[str, Any]:
    """Monitor system resources (CPU, memory, disk)"""
    
    import psutil
    
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'available_memory_mb': psutil.virtual_memory().available / (1024 * 1024),
            'timestamp': datetime.now().isoformat()
        }
    except ImportError:
        return {
            'error': 'psutil not available',
            'timestamp': datetime.now().isoformat()
        }


def retry_operation(func, max_retries: int = 3, delay: float = 1.0, 
                   backoff_factor: float = 2.0) -> Any:
    """Retry operation dengan exponential backoff"""
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries - 1:
                wait_time = delay * (backoff_factor ** attempt)
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"All {max_retries} attempts failed")
    
    raise last_exception


def create_status_file(status_data: Dict[str, Any], status_file: str = "dslr_status.json") -> bool:
    """Create status file untuk monitoring"""
    
    try:
        status_data['last_updated'] = datetime.now().isoformat()
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        return True
    except Exception as e:
        logging.error(f"Error creating status file: {e}")
        return False


def read_status_file(status_file: str = "dslr_status.json") -> Dict[str, Any]:
    """Read status file"""
    
    try:
        with open(status_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logging.error(f"Error reading status file: {e}")
        return {}


class PerformanceTimer:
    """Context manager untuk measuring performance"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation_name}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            self.logger.info(f"✅ {self.operation_name} completed in {duration:.2f}s")
        else:
            self.logger.error(f"❌ {self.operation_name} failed after {duration:.2f}s")
    
    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


# Test functions
def test_utilities():
    """Test utility functions"""
    print("🛠️ Testing utility functions...")
    
    # Test filename generation
    filename = generate_hafiportrait_filename("IMG_1234.NEF", "Wedding Sarah")
    print(f"Generated filename: {filename}")
    
    # Test file info
    if os.path.exists("config.json"):
        info = get_file_info("config.json")
        print(f"Config file info: {info}")
    
    # Test performance timer
    with PerformanceTimer("Test operation"):
        time.sleep(1)
    
    # Test system resources
    resources = monitor_system_resources()
    print(f"System resources: {resources}")
    
    print("✅ Utility tests completed")


if __name__ == "__main__":
    test_utilities()