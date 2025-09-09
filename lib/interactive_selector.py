#!/usr/bin/env python3
"""
🎯 Interactive Selection System
User-friendly selection untuk event, presets, dan watermark options
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

try:
    from colorama import init, Fore, Back, Style
    init()  # Initialize colorama
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

from uploader_robust import RobustHafiPortraitUploader as HafiPortraitUploader
from preset_processor import PresetProcessor
from watermark_manager import WatermarkManager


class InteractiveSelector:
    """Interactive selection system untuk DSLR configuration"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Selection results
        self.selected_event = None
        self.selected_preset = None
        self.selected_watermark = None
        
        # Initialize components for data fetching
        self.uploader = HafiPortraitUploader(config['web_project'])
        self.preset_processor = PresetProcessor(config['presets'])
        self.watermark_manager = WatermarkManager(config['watermark'])
    
    def run_interactive_selection(self) -> Dict[str, Any]:
        """Run complete interactive selection process"""
        
        self._print_header()
        
        try:
            # Step 1: Select Event
            self._print_step("1", "Event Selection")
            self.selected_event = self._select_event()
            
            if not self.selected_event:
                self._print_error("No event selected. Exiting...")
                return {}
            
            # Step 2: Select Preset
            self._print_step("2", "Preset Selection")
            self.selected_preset = self._select_preset()
            
            # Step 3: Select Watermark
            self._print_step("3", "Watermark Configuration")
            self.selected_watermark = self._select_watermark()
            
            # Step 4: Confirmation
            self._print_step("4", "Configuration Summary")
            if self._confirm_selection():
                return self._build_configuration()
            else:
                self._print_warning("Configuration cancelled by user")
                return {}
                
        except KeyboardInterrupt:
            self._print_warning("\nSelection cancelled by user")
            return {}
        except Exception as e:
            self._print_error(f"Selection error: {e}")
            return {}
    
    def _select_event(self) -> Optional[Dict]:
        """Interactive event selection"""
        
        print("📋 Fetching available events...")
        
        try:
            # Test connection first
            if not self.uploader.test_connection():
                self._print_error("Cannot connect to web project")
                return self._fallback_event_selection()
            
            # Get events from API
            events = self._fetch_events_from_api()
            
            if not events:
                self._print_warning("No events found in web project")
                return self._fallback_event_selection()
            
            return self._display_event_menu(events)
            
        except Exception as e:
            self._print_error(f"Error fetching events: {e}")
            return self._fallback_event_selection()
    
    def _fetch_events_from_api(self) -> List[Dict]:
        """Fetch events from web project API"""
        
        try:
            # Get current event
            current_event = self.uploader.get_current_event()
            
            # For now, create mock events list
            # In real implementation, this would call /api/admin/events
            events = []
            
            if current_event:
                events.append({
                    'id': current_event.get('id', 'current'),
                    'name': current_event.get('name', 'Current Event'),
                    'date': current_event.get('date', '2024-12-01'),
                    'status': 'active',
                    'type': 'wedding'
                })
            
            # Add some example events
            example_events = [
                {
                    'id': 'evt_wedding_sarah_2024',
                    'name': 'Wedding Sarah & John',
                    'date': '2024-12-01',
                    'status': 'active',
                    'type': 'wedding'
                },
                {
                    'id': 'evt_birthday_maya_2024',
                    'name': 'Birthday Party Maya',
                    'date': '2024-12-05',
                    'status': 'upcoming',
                    'type': 'birthday'
                }
            ]
            
            # Merge and deduplicate
            all_events = events + example_events
            seen_ids = set()
            unique_events = []
            
            for event in all_events:
                if event['id'] not in seen_ids:
                    unique_events.append(event)
                    seen_ids.add(event['id'])
            
            return unique_events
            
        except Exception as e:
            self.logger.error(f"Error fetching events: {e}")
            return []
    
    def _display_event_menu(self, events: List[Dict]) -> Optional[Dict]:
        """Display event selection menu"""
        
        print("\n" + "="*60)
        print("🎯 SELECT TARGET EVENT")
        print("="*60)
        
        for i, event in enumerate(events, 1):
            status_icon = "🟢" if event['status'] == 'active' else "🟡"
            type_icon = "💒" if event['type'] == 'wedding' else "🎉"
            
            print(f"{i:2d}. {status_icon} {type_icon} {event['name']}")
            print(f"     📅 {event['date']} | Status: {event['status']}")
        
        print(f"{len(events)+1:2d}. ➕ Manual Event ID Entry")
        print(f"{len(events)+2:2d}. ❌ Skip (Use Default)")
        
        while True:
            try:
                choice = input(f"\n🎯 Select event (1-{len(events)+2}): ").strip()
                
                if not choice:
                    continue
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(events):
                    selected = events[choice_num - 1]
                    self._print_success(f"Selected: {selected['name']}")
                    return selected
                
                elif choice_num == len(events) + 1:
                    return self._manual_event_entry()
                
                elif choice_num == len(events) + 2:
                    self._print_warning("Skipping event selection")
                    return None
                
                else:
                    self._print_error("Invalid choice. Please try again.")
                    
            except ValueError:
                self._print_error("Please enter a valid number.")
            except KeyboardInterrupt:
                return None
    
    def _manual_event_entry(self) -> Optional[Dict]:
        """Manual event ID entry"""
        
        print("\n📝 Manual Event Entry")
        print("-" * 30)
        
        event_id = input("Event ID: ").strip()
        if not event_id:
            return None
        
        event_name = input("Event Name (optional): ").strip()
        if not event_name:
            event_name = event_id
        
        return {
            'id': event_id,
            'name': event_name,
            'date': '2024-12-01',
            'status': 'manual',
            'type': 'custom'
        }
    
    def _fallback_event_selection(self) -> Optional[Dict]:
        """Fallback event selection when API unavailable"""
        
        self._print_warning("Using fallback event selection")
        
        print("\n📝 Manual Event Configuration")
        print("-" * 40)
        
        event_id = input("Enter Event ID: ").strip()
        if not event_id:
            return None
        
        event_name = input("Enter Event Name: ").strip()
        if not event_name:
            event_name = event_id
        
        return {
            'id': event_id,
            'name': event_name,
            'date': '2024-12-01',
            'status': 'manual',
            'type': 'custom'
        }
    
    def _select_preset(self) -> Optional[str]:
        """Interactive preset selection"""
        
        print("\n📋 Loading available presets...")
        
        presets = self.preset_processor.get_available_presets()
        
        if not presets:
            self._print_warning("No presets found in presets/ folder")
            return self._manual_preset_entry()
        
        return self._display_preset_menu(presets)
    
    def _display_preset_menu(self, presets: List[str]) -> Optional[str]:
        """Display preset selection menu"""
        
        print("\n" + "="*60)
        print("🎨 SELECT PROCESSING PRESET")
        print("="*60)
        
        for i, preset in enumerate(presets, 1):
            preset_info = self.preset_processor.get_preset_info(preset)
            
            # Display preset with description
            preset_name = preset.replace('_', ' ').title()
            
            if preset_info and 'settings' in preset_info:
                settings_count = len(preset_info['settings'])
                print(f"{i:2d}. 🎨 {preset_name}")
                print(f"     📋 {settings_count} adjustments")
                
                # Show key settings
                settings = preset_info['settings']
                key_settings = []
                
                if 'Exposure2012' in settings:
                    key_settings.append(f"Exposure: {settings['Exposure2012']:+.1f}")
                if 'Vibrance' in settings:
                    key_settings.append(f"Vibrance: {settings['Vibrance']:+.0f}")
                if 'Temperature' in settings:
                    key_settings.append(f"Temp: {settings['Temperature']:.0f}K")
                
                if key_settings:
                    print(f"     ⚙️  {' | '.join(key_settings)}")
            else:
                print(f"{i:2d}. 🎨 {preset_name}")
        
        print(f"{len(presets)+1:2d}. ➕ Manual Preset Name")
        print(f"{len(presets)+2:2d}. ❌ No Preset (Default Processing)")
        
        while True:
            try:
                choice = input(f"\n🎨 Select preset (1-{len(presets)+2}): ").strip()
                
                if not choice:
                    continue
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(presets):
                    selected = presets[choice_num - 1]
                    self._print_success(f"Selected: {selected}")
                    return selected
                
                elif choice_num == len(presets) + 1:
                    return self._manual_preset_entry()
                
                elif choice_num == len(presets) + 2:
                    self._print_warning("No preset selected - using default processing")
                    return None
                
                else:
                    self._print_error("Invalid choice. Please try again.")
                    
            except ValueError:
                self._print_error("Please enter a valid number.")
            except KeyboardInterrupt:
                return None
    
    def _manual_preset_entry(self) -> Optional[str]:
        """Manual preset name entry"""
        
        print("\n📝 Manual Preset Entry")
        print("-" * 30)
        
        preset_name = input("Preset name (without .xmp): ").strip()
        if not preset_name:
            return None
        
        # Check if preset file exists
        preset_file = Path(self.config['presets']['directory']) / f"{preset_name}.xmp"
        
        if preset_file.exists():
            self._print_success(f"Found preset file: {preset_file.name}")
            return preset_name
        else:
            self._print_warning(f"Preset file not found: {preset_file}")
            use_anyway = input("Use anyway? (y/N): ").strip().lower()
            return preset_name if use_anyway == 'y' else None
    
    def _select_watermark(self) -> Optional[Dict]:
        """Interactive watermark selection"""
        
        print("\n" + "="*60)
        print("🏷️ WATERMARK CONFIGURATION")
        print("="*60)
        
        # Check current watermark
        watermark_info = self.watermark_manager.get_watermark_info()
        
        if watermark_info.get('exists'):
            print(f"✅ Current watermark: {watermark_info['file']}")
            print(f"   Size: {watermark_info.get('width', 0)}x{watermark_info.get('height', 0)}")
            print(f"   Transparency: {watermark_info.get('has_transparency', False)}")
        else:
            print("❌ No watermark file found")
        
        print("\nWatermark Options:")
        print("1. ✅ Use Current Watermark")
        print("2. 🏷️ Specify Different Watermark File")
        print("3. 📝 Create Text Watermark")
        print("4. ❌ Disable Watermark")
        
        while True:
            try:
                choice = input("\n🏷️ Select watermark option (1-4): ").strip()
                
                if choice == '1':
                    if watermark_info.get('exists'):
                        self._print_success("Using current watermark")
                        return self._get_watermark_config()
                    else:
                        self._print_error("No current watermark available")
                        continue
                
                elif choice == '2':
                    return self._specify_watermark_file()
                
                elif choice == '3':
                    return self._create_text_watermark()
                
                elif choice == '4':
                    self._print_warning("Watermark disabled")
                    return {'enabled': False}
                
                else:
                    self._print_error("Invalid choice. Please try again.")
                    
            except ValueError:
                self._print_error("Please enter a valid number.")
            except KeyboardInterrupt:
                return None
    
    def _specify_watermark_file(self) -> Optional[Dict]:
        """Specify different watermark file"""
        
        print("\n📝 Specify Watermark File")
        print("-" * 30)
        
        file_path = input("Watermark file path: ").strip()
        if not file_path:
            return None
        
        if os.path.exists(file_path):
            self._print_success(f"Watermark file found: {file_path}")
            return {
                'enabled': True,
                'file': file_path,
                'position': 'bottom_center',
                'size_percentage': 15
            }
        else:
            self._print_error(f"File not found: {file_path}")
            return None
    
    def _create_text_watermark(self) -> Optional[Dict]:
        """Create text watermark"""
        
        print("\n📝 Create Text Watermark")
        print("-" * 30)
        
        text = input("Watermark text: ").strip()
        if not text:
            return None
        
        try:
            # Create text watermark
            watermark_image = self.watermark_manager.create_text_watermark(text)
            
            if watermark_image:
                text_watermark_path = f"text_watermark_{text.replace(' ', '_')}.png"
                watermark_image.save(text_watermark_path)
                
                self._print_success(f"Text watermark created: {text_watermark_path}")
                
                return {
                    'enabled': True,
                    'file': text_watermark_path,
                    'position': 'bottom_center',
                    'size_percentage': 15,
                    'type': 'text',
                    'text': text
                }
            else:
                self._print_error("Failed to create text watermark")
                return None
                
        except Exception as e:
            self._print_error(f"Error creating text watermark: {e}")
            return None
    
    def _get_watermark_config(self) -> Dict:
        """Get current watermark configuration"""
        
        return {
            'enabled': True,
            'file': self.config['watermark']['file'],
            'position': self.config['watermark']['position'],
            'size_percentage': self.config['watermark']['size_percentage']
        }
    
    def _confirm_selection(self) -> bool:
        """Confirm final selection"""
        
        print("\n" + "="*60)
        print("📋 CONFIGURATION SUMMARY")
        print("="*60)
        
        # Event
        if self.selected_event:
            print(f"🎯 Event: {self.selected_event['name']}")
            print(f"   ID: {self.selected_event['id']}")
        else:
            print("🎯 Event: Not selected")
        
        # Preset
        if self.selected_preset:
            print(f"🎨 Preset: {self.selected_preset}")
        else:
            print("🎨 Preset: Default processing")
        
        # Watermark
        if self.selected_watermark and self.selected_watermark.get('enabled'):
            print(f"🏷️ Watermark: {self.selected_watermark.get('file', 'Enabled')}")
        else:
            print("🏷️ Watermark: Disabled")
        
        print("="*60)
        
        while True:
            confirm = input("\n✅ Confirm configuration? (Y/n): ").strip().lower()
            
            if confirm in ['', 'y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                self._print_error("Please enter Y or N")
    
    def _build_configuration(self) -> Dict[str, Any]:
        """Build final configuration"""
        
        config = {
            'event': self.selected_event,
            'preset': self.selected_preset,
            'watermark': self.selected_watermark,
            'timestamp': self._get_timestamp()
        }
        
        # Save to file for persistence
        self._save_selection_config(config)
        
        return config
    
    def _save_selection_config(self, config: Dict):
        """Save selection to config file"""
        
        try:
            with open('dslr_selection.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            self._print_success("Configuration saved to dslr_selection.json")
            
        except Exception as e:
            self._print_error(f"Error saving configuration: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # Utility methods for colored output
    def _print_header(self):
        """Print header"""
        print("\n" + "="*60)
        print("🎯 HAFIPORTRAIT DSLR INTERACTIVE SETUP")
        print("="*60)
        print("Configure your DSLR auto-upload system")
        print()
    
    def _print_step(self, step: str, title: str):
        """Print step header"""
        print(f"\n{'='*20} STEP {step}: {title.upper()} {'='*20}")
    
    def _print_success(self, message: str):
        """Print success message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
        else:
            print(f"✅ {message}")
    
    def _print_warning(self, message: str):
        """Print warning message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")
        else:
            print(f"⚠️  {message}")
    
    def _print_error(self, message: str):
        """Print error message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
        else:
            print(f"❌ {message}")


# Test function
def test_interactive_selector():
    """Test interactive selector"""
    
    config = {
        'web_project': {
            'base_url': 'http://localhost:3002',
            'timeout': 30
        },
        'presets': {
            'directory': './presets/'
        },
        'watermark': {
            'file': './watermark.png',
            'position': 'bottom_center',
            'size_percentage': 15
        }
    }
    
    selector = InteractiveSelector(config)
    result = selector.run_interactive_selection()
    
    if result:
        print("\n🎉 Selection completed!")
        print(json.dumps(result, indent=2))
    else:
        print("\n❌ Selection cancelled or failed")


if __name__ == "__main__":
    test_interactive_selector()