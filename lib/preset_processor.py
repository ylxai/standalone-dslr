#!/usr/bin/env python3
"""
🎨 Adobe Preset Processor
Handles Adobe Lightroom XMP preset parsing and application
"""

import os
import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import rawpy
    import numpy as np
    from PIL import Image, ImageEnhance
    PROCESSING_AVAILABLE = True
except ImportError as e:
    PROCESSING_AVAILABLE = False
    print(f"⚠️  Image processing libraries tidak tersedia: {e}")


class AdobePresetParser:
    """Parse Adobe Lightroom XMP preset files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Adobe Camera Raw namespace
        self.namespaces = {
            'x': 'adobe:ns:meta/',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'crs': 'http://ns.adobe.com/camera-raw-settings/1.0/'
        }
    
    def parse_xmp_preset(self, xmp_file_path: str) -> Dict[str, Any]:
        """Parse Adobe Lightroom XMP preset file"""
        try:
            tree = ET.parse(xmp_file_path)
            root = tree.getroot()
            
            # Register namespaces
            for prefix, uri in self.namespaces.items():
                ET.register_namespace(prefix, uri)
            
            preset_settings = {}
            
            # Find RDF Description elements
            for desc in root.findall('.//rdf:Description', self.namespaces):
                # Extract Camera Raw settings
                for attr_name, attr_value in desc.attrib.items():
                    if attr_name.startswith('{http://ns.adobe.com/camera-raw-settings/1.0/}'):
                        setting_name = attr_name.split('}')[1]
                        converted_value = self._convert_adobe_value(setting_name, attr_value)
                        preset_settings[setting_name] = converted_value
            
            self.logger.info(f"Parsed preset: {len(preset_settings)} settings from {Path(xmp_file_path).name}")
            return preset_settings
            
        except Exception as e:
            self.logger.error(f"Error parsing XMP preset {xmp_file_path}: {e}")
            return {}
    
    def _convert_adobe_value(self, setting_name: str, value: str) -> Any:
        """Convert Adobe setting values to appropriate types"""
        
        # Numeric settings
        numeric_settings = {
            'Exposure2012', 'Contrast2012', 'Highlights2012', 'Shadows2012',
            'Whites2012', 'Blacks2012', 'Vibrance', 'Saturation',
            'Temperature', 'Tint', 'Clarity2012', 'Dehaze',
            'LuminanceSmoothing', 'ColorNoiseReduction'
        }
        
        # Boolean settings
        boolean_settings = {
            'AutoLateralCA', 'LensProfileEnable', 'PerspectiveUpright'
        }
        
        try:
            if setting_name in numeric_settings:
                return float(value)
            elif setting_name in boolean_settings:
                return value.lower() in ('true', '1', 'yes')
            else:
                return str(value)
        except ValueError:
            return str(value)


class PresetProcessor:
    """Main preset processing class"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize parser
        self.parser = AdobePresetParser()
        
        # Preset directory
        self.preset_dir = Path(config.get('directory', './presets/'))
        
        # Load available presets
        self.presets = self._scan_presets()
        
        if not PROCESSING_AVAILABLE:
            self.logger.warning("Image processing libraries tidak tersedia")
    
    def _scan_presets(self) -> Dict[str, Dict]:
        """Scan preset directory untuk available presets"""
        presets = {}
        
        if not self.preset_dir.exists():
            self.logger.warning(f"Preset directory tidak ditemukan: {self.preset_dir}")
            return presets
        
        # Scan for XMP files
        for xmp_file in self.preset_dir.glob('*.xmp'):
            preset_name = xmp_file.stem
            
            try:
                settings = self.parser.parse_xmp_preset(str(xmp_file))
                if settings:
                    presets[preset_name] = {
                        'file': str(xmp_file),
                        'type': 'lightroom_xmp',
                        'settings': settings,
                        'name': preset_name.replace('_', ' ').title()
                    }
                    self.logger.info(f"Loaded preset: {preset_name}")
            except Exception as e:
                self.logger.error(f"Error loading preset {preset_name}: {e}")
        
        self.logger.info(f"Loaded {len(presets)} presets")
        return presets
    
    def get_available_presets(self) -> List[str]:
        """Get list of available preset names"""
        return list(self.presets.keys())
    
    def get_preset_info(self, preset_name: str) -> Optional[Dict]:
        """Get preset information"""
        return self.presets.get(preset_name)
    
    def apply_preset(self, image_file: str, preset_name: str = None) -> np.ndarray:
        """Apply preset to image file"""
        
        if not PROCESSING_AVAILABLE:
            raise RuntimeError("Image processing libraries tidak tersedia")
        
        # Use default preset if none specified
        if not preset_name:
            preset_name = self.config.get('default', 'wedding_warm')
        
        # Check if preset exists
        if preset_name not in self.presets:
            self.logger.warning(f"Preset '{preset_name}' tidak ditemukan, menggunakan default processing")
            return self._process_without_preset(image_file)
        
        preset_info = self.presets[preset_name]
        settings = preset_info['settings']
        
        self.logger.info(f"Applying preset '{preset_name}' to {Path(image_file).name}")
        
        # Process based on file type
        if image_file.upper().endswith('.NEF'):
            return self._process_raw_with_preset(image_file, settings)
        else:
            return self._process_jpeg_with_preset(image_file, settings)
    
    def _process_raw_with_preset(self, nef_file: str, settings: Dict) -> np.ndarray:
        """Process RAW file dengan Adobe preset settings"""
        
        try:
            with rawpy.imread(nef_file) as raw:
                # Convert Adobe settings to rawpy parameters
                rawpy_params = self._convert_to_rawpy_params(settings)
                
                # Process RAW
                rgb = raw.postprocess(**rawpy_params)
                
                # Apply additional adjustments yang tidak bisa di rawpy
                rgb = self._apply_additional_adjustments(rgb, settings)
                
                return rgb
                
        except Exception as e:
            self.logger.error(f"Error processing RAW file {nef_file}: {e}")
            # Fallback to basic processing
            return self._process_without_preset(nef_file)
    
    def _process_jpeg_with_preset(self, jpeg_file: str, settings: Dict) -> np.ndarray:
        """Process JPEG file dengan preset adjustments"""
        
        try:
            # Load JPEG
            image = Image.open(jpeg_file)
            rgb = np.array(image)
            
            # Apply adjustments
            rgb = self._apply_additional_adjustments(rgb, settings)
            
            return rgb
            
        except Exception as e:
            self.logger.error(f"Error processing JPEG file {jpeg_file}: {e}")
            return self._process_without_preset(jpeg_file)
    
    def _convert_to_rawpy_params(self, settings: Dict) -> Dict:
        """Convert Adobe settings to rawpy parameters"""
        
        params = {
            'use_camera_wb': True,
            'output_color': rawpy.ColorSpace.sRGB,
            'output_bps': 16,
            'no_auto_bright': True,
            'auto_bright_thr': 0.01,
            'user_qual': 3  # High quality
        }
        
        # Exposure
        if 'Exposure2012' in settings:
            params['exposure_shift'] = settings['Exposure2012']
        
        # Brightness (approximate)
        if 'Highlights2012' in settings or 'Shadows2012' in settings:
            highlights = settings.get('Highlights2012', 0)
            shadows = settings.get('Shadows2012', 0)
            # Approximate brightness adjustment
            brightness = (shadows - highlights) / 200.0
            params['bright'] = max(-2.0, min(2.0, brightness))
        
        # White balance
        if 'Temperature' in settings:
            # This is approximate - rawpy uses multipliers, not temperature
            temp = settings['Temperature']
            if temp != 5500:  # 5500K is roughly neutral
                # Very rough conversion
                if temp > 5500:
                    params['user_wb'] = [1.0, 1.0, 0.8, 1.0]  # Warmer
                else:
                    params['user_wb'] = [0.8, 1.0, 1.0, 1.0]  # Cooler
        
        return params
    
    def _apply_additional_adjustments(self, rgb: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply adjustments yang tidak bisa di rawpy"""
        
        try:
            # Convert to PIL Image untuk easier processing
            image = Image.fromarray(rgb.astype('uint8'))
            
            # Contrast
            if 'Contrast2012' in settings:
                contrast_value = settings['Contrast2012']
                if contrast_value != 0:
                    factor = 1.0 + (contrast_value / 100.0)
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(factor)
            
            # Saturation
            if 'Saturation' in settings:
                saturation_value = settings['Saturation']
                if saturation_value != 0:
                    factor = 1.0 + (saturation_value / 100.0)
                    enhancer = ImageEnhance.Color(image)
                    image = enhancer.enhance(factor)
            
            # Vibrance (approximate dengan saturation)
            if 'Vibrance' in settings:
                vibrance_value = settings['Vibrance']
                if vibrance_value != 0:
                    # Vibrance is more subtle than saturation
                    factor = 1.0 + (vibrance_value / 200.0)
                    enhancer = ImageEnhance.Color(image)
                    image = enhancer.enhance(factor)
            
            return np.array(image)
            
        except Exception as e:
            self.logger.error(f"Error applying additional adjustments: {e}")
            return rgb
    
    def _process_without_preset(self, image_file: str) -> np.ndarray:
        """Process image without preset (fallback)"""
        
        try:
            if image_file.upper().endswith('.NEF'):
                # Basic RAW processing
                with rawpy.imread(image_file) as raw:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        output_color=rawpy.ColorSpace.sRGB,
                        output_bps=8
                    )
                return rgb
            else:
                # Load JPEG as-is
                image = Image.open(image_file)
                return np.array(image)
                
        except Exception as e:
            self.logger.error(f"Error in fallback processing: {e}")
            raise
    
    def create_preset_preview(self, preset_name: str, sample_image: str = None) -> Optional[str]:
        """Create preview image dengan preset applied"""
        
        if not sample_image or not os.path.exists(sample_image):
            self.logger.warning("Sample image tidak tersedia untuk preview")
            return None
        
        try:
            # Apply preset
            processed = self.apply_preset(sample_image, preset_name)
            
            # Create thumbnail
            image = Image.fromarray(processed.astype('uint8'))
            image.thumbnail((400, 300), Image.Resampling.LANCZOS)
            
            # Save preview
            preview_path = self.preset_dir / f"{preset_name}_preview.jpg"
            image.save(preview_path, 'JPEG', quality=85)
            
            return str(preview_path)
            
        except Exception as e:
            self.logger.error(f"Error creating preset preview: {e}")
            return None


# Test functions
def test_preset_parsing():
    """Test preset parsing"""
    print("🎨 Testing Adobe preset parsing...")
    
    parser = AdobePresetParser()
    
    # Create sample XMP for testing
    sample_xmp = """<?xml version="1.0" encoding="UTF-8"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
      xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
      crs:Version="15.0"
      crs:Exposure2012="+0.50"
      crs:Contrast2012="+25"
      crs:Highlights2012="-50"
      crs:Shadows2012="+30"
      crs:Whites2012="+20"
      crs:Blacks2012="-10"
      crs:Vibrance="+15"
      crs:Saturation="+5"
      crs:Temperature="5500"
      crs:Tint="+5"/>
  </rdf:RDF>
</x:xmpmeta>"""
    
    # Save sample XMP
    test_xmp_path = "test_preset.xmp"
    with open(test_xmp_path, 'w') as f:
        f.write(sample_xmp)
    
    # Parse it
    settings = parser.parse_xmp_preset(test_xmp_path)
    
    if settings:
        print("✅ XMP parsing successful")
        print("Settings found:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    else:
        print("❌ XMP parsing failed")
    
    # Cleanup
    os.remove(test_xmp_path)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_preset_parsing()