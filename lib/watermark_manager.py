#!/usr/bin/env python3
"""
🏷️ Watermark Manager
Handles transparent PNG watermark application dengan positioning
"""

import os
import logging
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL (Pillow) tidak tersedia untuk watermark processing")


class WatermarkManager:
    """Manage watermark application to images"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL (Pillow) required untuk watermark processing")
        
        # Watermark file
        self.watermark_file = config.get('file', './watermark.png')
        
        # Position settings
        self.position = config.get('position', 'bottom_center')
        self.size_percentage = config.get('size_percentage', 15)
        self.margin_bottom = config.get('margin_bottom', 10)
        self.opacity = config.get('opacity', 100)
        
        # Load watermark
        self.watermark_image = self._load_watermark()
    
    def _load_watermark(self) -> Optional[Image.Image]:
        """Load watermark PNG file"""
        
        if not os.path.exists(self.watermark_file):
            self.logger.warning(f"Watermark file tidak ditemukan: {self.watermark_file}")
            return None
        
        try:
            watermark = Image.open(self.watermark_file).convert("RGBA")
            self.logger.info(f"Watermark loaded: {watermark.size[0]}x{watermark.size[1]}")
            return watermark
            
        except Exception as e:
            self.logger.error(f"Error loading watermark: {e}")
            return None
    
    def apply_watermark(self, image: np.ndarray) -> np.ndarray:
        """Apply watermark to image"""
        
        if self.watermark_image is None:
            self.logger.warning("No watermark available, returning original image")
            return image
        
        try:
            # Convert numpy array to PIL Image
            if image.dtype != np.uint8:
                # Convert to uint8 if needed
                if image.max() <= 1.0:
                    image = (image * 255).astype(np.uint8)
                else:
                    image = image.astype(np.uint8)
            
            base_image = Image.fromarray(image)
            
            # Apply watermark
            watermarked = self._apply_watermark_to_pil(base_image)
            
            # Convert back to numpy array
            return np.array(watermarked)
            
        except Exception as e:
            self.logger.error(f"Error applying watermark: {e}")
            return image
    
    def _apply_watermark_to_pil(self, base_image: Image.Image) -> Image.Image:
        """Apply watermark to PIL Image"""
        
        # Get image dimensions
        img_width, img_height = base_image.size
        
        # Calculate watermark size
        watermark_width = int(img_width * (self.size_percentage / 100))
        watermark_height = int(watermark_width * (self.watermark_image.size[1] / self.watermark_image.size[0]))
        
        # Resize watermark
        watermark_resized = self.watermark_image.resize(
            (watermark_width, watermark_height), 
            Image.Resampling.LANCZOS
        )
        
        # Calculate position
        x_pos, y_pos = self._calculate_position(
            img_width, img_height, 
            watermark_width, watermark_height
        )
        
        # Apply opacity if needed
        if self.opacity < 100:
            watermark_resized = self._apply_opacity(watermark_resized, self.opacity)
        
        # Create a copy of base image
        result = base_image.copy()
        
        # Paste watermark
        if watermark_resized.mode == 'RGBA':
            # Use alpha channel for transparency
            result.paste(watermark_resized, (x_pos, y_pos), watermark_resized)
        else:
            # No transparency
            result.paste(watermark_resized, (x_pos, y_pos))
        
        self.logger.info(f"Watermark applied at position ({x_pos}, {y_pos})")
        return result
    
    def _calculate_position(self, img_width: int, img_height: int, 
                          wm_width: int, wm_height: int) -> Tuple[int, int]:
        """Calculate watermark position based on configuration"""
        
        margin_bottom_px = int(img_height * (self.margin_bottom / 100))
        
        if self.position == 'bottom_center':
            # Bottom center, not too low
            x_pos = (img_width - wm_width) // 2
            y_pos = img_height - wm_height - margin_bottom_px
            
        elif self.position == 'bottom_right':
            # Bottom right corner
            margin_right_px = int(img_width * 0.05)  # 5% margin from right
            x_pos = img_width - wm_width - margin_right_px
            y_pos = img_height - wm_height - margin_bottom_px
            
        elif self.position == 'bottom_left':
            # Bottom left corner
            margin_left_px = int(img_width * 0.05)  # 5% margin from left
            x_pos = margin_left_px
            y_pos = img_height - wm_height - margin_bottom_px
            
        elif self.position == 'center':
            # Center of image
            x_pos = (img_width - wm_width) // 2
            y_pos = (img_height - wm_height) // 2
            
        elif self.position == 'top_right':
            # Top right corner
            margin_right_px = int(img_width * 0.05)
            margin_top_px = int(img_height * 0.05)
            x_pos = img_width - wm_width - margin_right_px
            y_pos = margin_top_px
            
        else:
            # Default to bottom center
            x_pos = (img_width - wm_width) // 2
            y_pos = img_height - wm_height - margin_bottom_px
        
        # Ensure watermark stays within image bounds
        x_pos = max(0, min(x_pos, img_width - wm_width))
        y_pos = max(0, min(y_pos, img_height - wm_height))
        
        return x_pos, y_pos
    
    def _apply_opacity(self, watermark: Image.Image, opacity: int) -> Image.Image:
        """Apply opacity to watermark"""
        
        if watermark.mode != 'RGBA':
            watermark = watermark.convert('RGBA')
        
        # Create a copy
        watermark_copy = watermark.copy()
        
        # Adjust alpha channel
        alpha = watermark_copy.split()[3]  # Get alpha channel
        alpha = alpha.point(lambda p: int(p * (opacity / 100)))  # Apply opacity
        watermark_copy.putalpha(alpha)
        
        return watermark_copy
    
    def create_text_watermark(self, text: str, font_size: int = None) -> Image.Image:
        """Create text watermark as fallback"""
        
        if not font_size:
            font_size = 48
        
        try:
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Calculate text size
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Create image with text
            watermark = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # Draw text with shadow effect
            shadow_offset = 2
            draw.text((10 + shadow_offset, 10 + shadow_offset), text, font=font, fill=(0, 0, 0, 128))  # Shadow
            draw.text((10, 10), text, font=font, fill=(255, 255, 255, 200))  # Main text
            
            return watermark
            
        except Exception as e:
            self.logger.error(f"Error creating text watermark: {e}")
            return None
    
    def validate_watermark_file(self) -> bool:
        """Validate watermark file"""
        
        if not os.path.exists(self.watermark_file):
            return False
        
        try:
            with Image.open(self.watermark_file) as img:
                # Check if it's a valid image
                img.verify()
                return True
        except:
            return False
    
    def get_watermark_info(self) -> Dict:
        """Get watermark information"""
        
        info = {
            'file': self.watermark_file,
            'exists': os.path.exists(self.watermark_file),
            'position': self.position,
            'size_percentage': self.size_percentage,
            'margin_bottom': self.margin_bottom,
            'opacity': self.opacity
        }
        
        if self.watermark_image:
            info.update({
                'width': self.watermark_image.size[0],
                'height': self.watermark_image.size[1],
                'mode': self.watermark_image.mode,
                'has_transparency': self.watermark_image.mode in ('RGBA', 'LA')
            })
        
        return info


# Test functions
def test_watermark_creation():
    """Test watermark creation and application"""
    print("🏷️ Testing watermark system...")
    
    # Create test configuration
    config = {
        'file': './test_watermark.png',
        'position': 'bottom_center',
        'size_percentage': 15,
        'margin_bottom': 10,
        'opacity': 80
    }
    
    # Create a simple test watermark
    test_watermark = Image.new('RGBA', (200, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(test_watermark)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    draw.text((10, 10), "HafiPortrait", font=font, fill=(255, 255, 255, 200))
    test_watermark.save('./test_watermark.png')
    
    # Test watermark manager
    try:
        manager = WatermarkManager(config)
        
        # Create test image
        test_image = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
        
        # Apply watermark
        watermarked = manager.apply_watermark(test_image)
        
        print("✅ Watermark application successful")
        print(f"Original shape: {test_image.shape}")
        print(f"Watermarked shape: {watermarked.shape}")
        
        # Get watermark info
        info = manager.get_watermark_info()
        print("Watermark info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Watermark test failed: {e}")
    
    # Cleanup
    if os.path.exists('./test_watermark.png'):
        os.remove('./test_watermark.png')


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_watermark_creation()