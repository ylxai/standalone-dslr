#!/usr/bin/env python3
"""
🎯 HafiPortrait DSLR Auto-Upload System
Main script untuk complete workflow: gphoto2 → preset → watermark → upload
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path

# Add lib directory to path
sys.path.append(str(Path(__file__).parent / 'lib'))

# Import our modules
try:
    from utils import setup_logging, load_config, PerformanceTimer, create_status_file
    from camera import DSLRMonitor
    from preset_processor import PresetProcessor
    from watermark_manager import WatermarkManager
    from uploader import HafiPortraitUploader
    from interactive_selector import InteractiveSelector
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


class HafiPortraitDSLR:
    """Main DSLR auto-upload system"""
    
    def __init__(self, config_file: str = "config.json"):
        # Load configuration
        try:
            self.config = load_config(config_file)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
        
        # Setup logging
        log_level = self.config.get('monitoring', {}).get('log_level', 'INFO')
        log_file = './logs/dslr_system.log'
        self.logger = setup_logging(log_level, log_file)
        
        # Initialize components
        self.camera_monitor = None
        self.preset_processor = None
        self.watermark_manager = None
        self.uploader = None
        
        # System state
        self.running = False
        self.stats = {
            'photos_processed': 0,
            'photos_uploaded': 0,
            'errors': 0,
            'start_time': None
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def initialize_components(self) -> bool:
        """Initialize all system components"""
        
        self.logger.info("🎯 Initializing HafiPortrait DSLR System...")
        
        try:
            # Initialize camera monitor
            self.logger.info("📷 Initializing camera monitor...")
            self.camera_monitor = DSLRMonitor(self.config['camera'])
            self.camera_monitor.set_photo_callback(self._handle_new_photo)
            
            # Initialize preset processor
            self.logger.info("🎨 Initializing preset processor...")
            self.preset_processor = PresetProcessor(self.config['presets'])
            
            # Initialize watermark manager
            self.logger.info("🏷️ Initializing watermark manager...")
            self.watermark_manager = WatermarkManager(self.config['watermark'])
            
            # Initialize uploader
            self.logger.info("🔗 Initializing uploader...")
            self.uploader = HafiPortraitUploader(self.config['web_project'])
            
            # Test connections
            if not self._test_connections():
                return False
            
            self.logger.info("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing components: {e}")
            return False
    
    def _test_connections(self) -> bool:
        """Test all connections"""
        
        self.logger.info("🔍 Testing connections...")
        
        # Test web project connection
        if not self.uploader.test_connection():
            self.logger.error("❌ Web project connection failed")
            return False
        
        # Test watermark file
        if not self.watermark_manager.validate_watermark_file():
            self.logger.warning("⚠️  Watermark file tidak valid, akan skip watermark")
        
        # Check preset availability
        presets = self.preset_processor.get_available_presets()
        if not presets:
            self.logger.warning("⚠️  No presets available, akan gunakan default processing")
        else:
            self.logger.info(f"📋 Available presets: {', '.join(presets)}")
        
        return True
    
    def start(self) -> bool:
        """Start DSLR monitoring system"""
        
        if not self.initialize_components():
            return False
        
        # Run interactive selection if no saved configuration
        selection_config = self._load_or_run_interactive_selection()
        if not selection_config:
            self.logger.error("❌ No configuration selected")
            return False
        
        # Apply selected configuration
        self._apply_selection_config(selection_config)
        
        self.logger.info("🚀 Starting DSLR monitoring...")
        
        # Start camera monitoring
        if not self.camera_monitor.start_monitoring():
            self.logger.error("❌ Failed to start camera monitoring")
            return False
        
        # Update system state
        self.running = True
        self.stats['start_time'] = time.time()
        
        # Create initial status file
        self._update_status_file()
        
        self.logger.info("✅ DSLR system started successfully")
        self._print_status()
        
        return True
    
    def _handle_new_photo(self, file_path: str):
        """Handle new photo detection"""
        
        self.logger.info(f"📸 New photo detected: {Path(file_path).name}")
        
        # Process in separate thread untuk avoid blocking
        thread = threading.Thread(
            target=self._process_photo_thread,
            args=(file_path,),
            daemon=True
        )
        thread.start()
    
    def _process_photo_thread(self, file_path: str):
        """Process photo dalam separate thread"""
        
        try:
            with PerformanceTimer(f"Processing {Path(file_path).name}"):
                self._process_single_photo(file_path)
        except Exception as e:
            self.logger.error(f"❌ Error processing {file_path}: {e}")
            self.stats['errors'] += 1
            self._update_status_file()
    
    def _process_single_photo(self, file_path: str):
        """Process single photo through complete pipeline"""
        
        file_name = Path(file_path).name
        
        try:
            # Step 1: Apply preset
            self.logger.info(f"🎨 Applying preset to {file_name}...")
            default_preset = self.config['processing']['default_preset']
            processed_image = self.preset_processor.apply_preset(file_path, default_preset)
            
            # Step 2: Apply watermark
            if self.config['processing']['auto_watermark']:
                self.logger.info(f"🏷️ Applying watermark to {file_name}...")
                watermarked_image = self.watermark_manager.apply_watermark(processed_image)
            else:
                watermarked_image = processed_image
            
            # Step 3: Upload to web project
            self.logger.info(f"🔗 Uploading {file_name}...")
            
            metadata = {
                'original_file': file_name,
                'preset_applied': default_preset,
                'watermark_applied': self.config['processing']['auto_watermark'],
                'processing_timestamp': time.time()
            }
            
            # Upload dengan retry
            max_retries = self.config['monitoring']['max_retries']
            upload_result = self.uploader.retry_upload(
                watermarked_image, 
                file_path, 
                max_retries=max_retries
            )
            
            if upload_result['success']:
                self.logger.info(f"✅ Successfully processed and uploaded {file_name}")
                self.stats['photos_uploaded'] += 1
                
                # Optional: Backup original file
                if self.config['processing']['backup_originals']:
                    self._backup_original_file(file_path)
                
            else:
                self.logger.error(f"❌ Upload failed for {file_name}: {upload_result['error']}")
                self.stats['errors'] += 1
            
            self.stats['photos_processed'] += 1
            self._update_status_file()
            
        except Exception as e:
            self.logger.error(f"❌ Processing failed for {file_name}: {e}")
            self.stats['errors'] += 1
            self._update_status_file()
    
    def _backup_original_file(self, file_path: str):
        """Backup original file"""
        
        try:
            backup_result = self.uploader.upload_original_backup(file_path)
            if backup_result['success']:
                self.logger.info(f"✅ Original file backed up: {Path(file_path).name}")
            else:
                self.logger.warning(f"⚠️  Original backup failed: {backup_result['error']}")
        except Exception as e:
            self.logger.error(f"❌ Backup error: {e}")
    
    def _update_status_file(self):
        """Update status file untuk monitoring"""
        
        status_data = {
            'system_status': 'running' if self.running else 'stopped',
            'stats': self.stats.copy(),
            'camera_status': self.camera_monitor.get_camera_status() if self.camera_monitor else {},
            'uploader_status': self.uploader.get_upload_status() if self.uploader else {},
            'config': {
                'watch_directory': self.config['camera']['watch_directory'],
                'web_project_url': self.config['web_project']['base_url'],
                'default_preset': self.config['processing']['default_preset']
            }
        }
        
        create_status_file(status_data)
    
    def _print_status(self):
        """Print current system status"""
        
        print("\n" + "="*60)
        print("🎯 HafiPortrait DSLR System Status")
        print("="*60)
        print(f"📷 Camera: {self.config['camera']['model']}")
        print(f"📁 Watch Directory: {self.config['camera']['watch_directory']}")
        print(f"🎨 Default Preset: {self.config['processing']['default_preset']}")
        print(f"🔗 Web Project: {self.config['web_project']['base_url']}")
        print(f"🏷️ Watermark: {'Enabled' if self.config['processing']['auto_watermark'] else 'Disabled'}")
        print("="*60)
        print("📊 Statistics:")
        print(f"  Photos Processed: {self.stats['photos_processed']}")
        print(f"  Photos Uploaded: {self.stats['photos_uploaded']}")
        print(f"  Errors: {self.stats['errors']}")
        print("="*60)
        print("⏳ Monitoring for new photos... Press Ctrl+C to stop")
        print()
    
    def run(self):
        """Main run loop"""
        
        if not self.start():
            sys.exit(1)
        
        try:
            # Main monitoring loop
            while self.running:
                time.sleep(5)  # Check every 5 seconds
                
                # Update status periodically
                self._update_status_file()
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.stop()
    
    def stop(self):
        """Stop DSLR system"""
        
        if not self.running:
            return
        
        self.logger.info("🛑 Stopping DSLR system...")
        
        self.running = False
        
        # Stop camera monitoring
        if self.camera_monitor:
            self.camera_monitor.stop_monitoring()
        
        # Close uploader
        if self.uploader:
            self.uploader.close()
        
        # Final status update
        self._update_status_file()
        
        # Print final statistics
        runtime = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        
        print("\n" + "="*60)
        print("📊 Final Statistics")
        print("="*60)
        print(f"Runtime: {runtime:.1f} seconds")
        print(f"Photos Processed: {self.stats['photos_processed']}")
        print(f"Photos Uploaded: {self.stats['photos_uploaded']}")
        print(f"Errors: {self.stats['errors']}")
        
        if self.stats['photos_processed'] > 0:
            success_rate = (self.stats['photos_uploaded'] / self.stats['photos_processed']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("="*60)
        print("👋 HafiPortrait DSLR System stopped")
        
        self.logger.info("✅ DSLR system stopped successfully")
    
    def _load_or_run_interactive_selection(self) -> dict:
        """Load saved selection or run interactive selection"""
        
        # Check for saved selection
        selection_file = "dslr_selection.json"
        
        if os.path.exists(selection_file):
            try:
                with open(selection_file, 'r') as f:
                    saved_config = json.load(f)
                
                # Ask if user wants to use saved config
                print(f"\n📋 Found saved configuration from {saved_config.get('timestamp', 'unknown time')}")
                
                if saved_config.get('event'):
                    print(f"🎯 Event: {saved_config['event']['name']}")
                if saved_config.get('preset'):
                    print(f"🎨 Preset: {saved_config['preset']}")
                if saved_config.get('watermark', {}).get('enabled'):
                    print(f"🏷️ Watermark: Enabled")
                
                use_saved = input("\n✅ Use saved configuration? (Y/n): ").strip().lower()
                
                if use_saved in ['', 'y', 'yes']:
                    self.logger.info("Using saved configuration")
                    return saved_config
                
            except Exception as e:
                self.logger.warning(f"Error loading saved config: {e}")
        
        # Run interactive selection
        print("\n🎯 Running Interactive Selection...")
        selector = InteractiveSelector(self.config)
        return selector.run_interactive_selection()
    
    def _apply_selection_config(self, selection_config: dict):
        """Apply selected configuration to system"""
        
        # Apply event configuration
        if selection_config.get('event'):
            event = selection_config['event']
            self.uploader.set_event_context(
                event['id'], 
                album_name="Official",
                preset_name=selection_config.get('preset', 'wedding_warm')
            )
            self.logger.info(f"🎯 Active event: {event['name']}")
        
        # Apply preset configuration
        if selection_config.get('preset'):
            self.config['processing']['default_preset'] = selection_config['preset']
            self.logger.info(f"🎨 Default preset: {selection_config['preset']}")
        
        # Apply watermark configuration
        if selection_config.get('watermark'):
            watermark_config = selection_config['watermark']
            
            if watermark_config.get('enabled'):
                self.config['processing']['auto_watermark'] = True
                
                if watermark_config.get('file'):
                    self.config['watermark']['file'] = watermark_config['file']
                
                self.logger.info(f"🏷️ Watermark: {watermark_config.get('file', 'Enabled')}")
            else:
                self.config['processing']['auto_watermark'] = False
                self.logger.info("🏷️ Watermark: Disabled")


def main():
    """Main entry point"""
    
    print("🎯 HafiPortrait DSLR Auto-Upload System")
    print("======================================")
    
    # Check if config exists
    if not os.path.exists("config.json"):
        print("❌ config.json not found!")
        print("Copy config.json.example dan edit sesuai setup Anda")
        sys.exit(1)
    
    # Create DSLR system
    try:
        dslr_system = HafiPortraitDSLR()
        dslr_system.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()