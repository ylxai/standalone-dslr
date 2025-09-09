#!/usr/bin/env python3
"""
🖼️ Preset Preview Generator
Generate preview images showing before/after preset application
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, Tuple

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import rawpy
    PIL_AVAILABLE = True
except ImportError as e:
    PIL_AVAILABLE = False
    print(f"⚠️  Required libraries not available: {e}")
    print("Install with: pip install pillow rawpy numpy")

# Add lib directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from preset_processor import AdobePresetParser, PresetProcessor
    from utils import setup_logging
except ImportError as e:
    print(f"❌ Error importing local modules: {e}")
    sys.exit(1)


class PresetPreviewGenerator:
    """Generate preview images for Adobe presets"""
    
    def __init__(self, output_size: Tuple[int, int] = (800, 600)):
        self.output_size = output_size
        self.logger = logging.getLogger(__name__)
        
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL and other required libraries not available")
        
        # Initialize preset processor
        self.preset_parser = AdobePresetParser()
        
    def generate_preview(self, preset_file: str, sample_image: str, 
                        output_file: str, comparison: bool = True) -> bool:
        """Generate preset preview image"""
        
        try:
            self.logger.info(f"Generating preview for preset: {Path(preset_file).name}")
            
            # Parse preset
            preset_settings = self.preset_parser.parse_xmp_preset(preset_file)
            if not preset_settings:
                self.logger.error("Failed to parse preset file")
                return False
            
            # Load and process sample image
            original_image = self._load_sample_image(sample_image)
            if original_image is None:
                self.logger.error("Failed to load sample image")
                return False
            
            # Apply preset
            processed_image = self._apply_preset_to_image(original_image, preset_settings)
            
            if comparison:
                # Create before/after comparison
                preview_image = self._create_comparison_image(original_image, processed_image, preset_settings)
            else:
                # Just the processed image
                preview_image = self._resize_image(processed_image, self.output_size)
            
            # Save preview
            preview_image.save(output_file, 'JPEG', quality=90, optimize=True)
            
            self.logger.info(f"Preview saved: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating preview: {e}")
            return False
    
    def _load_sample_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load sample image (supports RAW and standard formats)"""
        
        try:
            image_path = Path(image_path)
            
            if image_path.suffix.upper() in ['.NEF', '.CR2', '.ARW', '.DNG']:
                # RAW file
                with rawpy.imread(str(image_path)) as raw:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        output_color=rawpy.ColorSpace.sRGB,
                        output_bps=8
                    )
                return rgb
            else:
                # Standard image file
                image = Image.open(image_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                return np.array(image)
                
        except Exception as e:
            self.logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def _apply_preset_to_image(self, image: np.ndarray, settings: dict) -> np.ndarray:
        """Apply preset settings to image"""
        
        try:
            # Convert to PIL for easier processing
            pil_image = Image.fromarray(image.astype('uint8'))
            
            # Apply basic adjustments
            processed = self._apply_basic_adjustments(pil_image, settings)
            
            return np.array(processed)
            
        except Exception as e:
            self.logger.error(f"Error applying preset: {e}")
            return image
    
    def _apply_basic_adjustments(self, image: Image.Image, settings: dict) -> Image.Image:
        """Apply basic preset adjustments"""
        
        from PIL import ImageEnhance
        
        try:
            result = image.copy()
            
            # Brightness (approximate from exposure)
            if 'Exposure2012' in settings:
                exposure = settings['Exposure2012']
                if exposure != 0:
                    factor = 1.0 + (exposure * 0.3)  # Scale exposure effect
                    enhancer = ImageEnhance.Brightness(result)
                    result = enhancer.enhance(factor)
            
            # Contrast
            if 'Contrast2012' in settings:
                contrast = settings['Contrast2012']
                if contrast != 0:
                    factor = 1.0 + (contrast / 100.0)
                    enhancer = ImageEnhance.Contrast(result)
                    result = enhancer.enhance(factor)
            
            # Color/Saturation
            if 'Saturation' in settings:
                saturation = settings['Saturation']
                if saturation != 0:
                    factor = 1.0 + (saturation / 100.0)
                    enhancer = ImageEnhance.Color(result)
                    result = enhancer.enhance(factor)
            
            # Vibrance (approximate with color enhancement)
            if 'Vibrance' in settings:
                vibrance = settings['Vibrance']
                if vibrance != 0:
                    factor = 1.0 + (vibrance / 200.0)  # More subtle than saturation
                    enhancer = ImageEnhance.Color(result)
                    result = enhancer.enhance(factor)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error applying adjustments: {e}")
            return image
    
    def _create_comparison_image(self, original: np.ndarray, processed: np.ndarray, 
                               settings: dict) -> Image.Image:
        """Create before/after comparison image"""
        
        try:
            # Resize images to fit in comparison
            comparison_width, comparison_height = self.output_size
            single_width = comparison_width // 2 - 10  # Leave space for divider
            single_height = comparison_height - 80  # Leave space for labels and info
            
            # Resize both images
            original_resized = self._resize_image_array(original, (single_width, single_height))
            processed_resized = self._resize_image_array(processed, (single_width, single_height))
            
            # Create comparison canvas
            canvas = Image.new('RGB', self.output_size, (240, 240, 240))
            
            # Paste images
            canvas.paste(Image.fromarray(original_resized), (5, 40))
            canvas.paste(Image.fromarray(processed_resized), (single_width + 15, 40))
            
            # Add labels and info
            self._add_comparison_labels(canvas, settings, single_width)
            
            return canvas
            
        except Exception as e:
            self.logger.error(f"Error creating comparison: {e}")
            # Fallback to just processed image
            return self._resize_image(Image.fromarray(processed), self.output_size)
    
    def _resize_image_array(self, image_array: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """Resize numpy image array"""
        
        image = Image.fromarray(image_array.astype('uint8'))
        resized = image.resize(size, Image.Resampling.LANCZOS)
        return np.array(resized)
    
    def _resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resize PIL image maintaining aspect ratio"""
        
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create canvas and center image
        canvas = Image.new('RGB', size, (240, 240, 240))
        
        # Calculate position to center image
        x = (size[0] - image.width) // 2
        y = (size[1] - image.height) // 2
        
        canvas.paste(image, (x, y))
        return canvas
    
    def _add_comparison_labels(self, canvas: Image.Image, settings: dict, single_width: int):
        """Add labels and preset info to comparison image"""
        
        try:
            draw = ImageDraw.Draw(canvas)
            
            # Try to load a font
            try:
                title_font = ImageFont.truetype("arial.ttf", 16)
                info_font = ImageFont.truetype("arial.ttf", 12)
            except:
                title_font = ImageFont.load_default()
                info_font = ImageFont.load_default()
            
            # Add "Before" and "After" labels
            draw.text((single_width // 2 - 20, 10), "BEFORE", font=title_font, fill=(100, 100, 100))
            draw.text((single_width + single_width // 2 - 15, 10), "AFTER", font=title_font, fill=(100, 100, 100))
            
            # Add divider line
            line_x = single_width + 10
            draw.line([(line_x, 40), (line_x, canvas.height - 40)], fill=(200, 200, 200), width=2)
            
            # Add preset info at bottom
            y_pos = canvas.height - 35
            
            # Key settings info
            info_parts = []
            
            if 'Exposure2012' in settings and settings['Exposure2012'] != 0:
                exp = settings['Exposure2012']
                info_parts.append(f"Exposure: {exp:+.1f}")
            
            if 'Vibrance' in settings and settings['Vibrance'] != 0:
                vib = settings['Vibrance']
                info_parts.append(f"Vibrance: {vib:+.0f}")
            
            if 'Contrast2012' in settings and settings['Contrast2012'] != 0:
                con = settings['Contrast2012']
                info_parts.append(f"Contrast: {con:+.0f}")
            
            if 'Temperature' in settings and settings['Temperature'] != 5500:
                temp = settings['Temperature']
                info_parts.append(f"Temp: {temp:.0f}K")
            
            if info_parts:
                info_text = " | ".join(info_parts[:3])  # Limit to 3 items
                
                # Center the text
                bbox = draw.textbbox((0, 0), info_text, font=info_font)
                text_width = bbox[2] - bbox[0]
                x_pos = (canvas.width - text_width) // 2
                
                draw.text((x_pos, y_pos), info_text, font=info_font, fill=(80, 80, 80))
            
        except Exception as e:
            self.logger.error(f"Error adding labels: {e}")
    
    def generate_preset_grid(self, preset_files: list, sample_image: str, 
                           output_file: str, grid_size: Tuple[int, int] = (3, 2)) -> bool:
        """Generate grid of multiple preset previews"""
        
        try:
            cols, rows = grid_size
            total_presets = min(len(preset_files), cols * rows)
            
            if total_presets == 0:
                return False
            
            # Calculate individual preview size
            preview_width = self.output_size[0] // cols - 10
            preview_height = self.output_size[1] // rows - 30
            
            # Create grid canvas
            canvas = Image.new('RGB', self.output_size, (250, 250, 250))
            draw = ImageDraw.Draw(canvas)
            
            # Load sample image once
            original_image = self._load_sample_image(sample_image)
            if original_image is None:
                return False
            
            # Generate preview for each preset
            for i, preset_file in enumerate(preset_files[:total_presets]):
                row = i // cols
                col = i % cols
                
                # Parse preset
                preset_settings = self.preset_parser.parse_xmp_preset(preset_file)
                if not preset_settings:
                    continue
                
                # Apply preset
                processed_image = self._apply_preset_to_image(original_image, preset_settings)
                
                # Resize for grid
                preview_img = self._resize_image_array(processed_image, (preview_width, preview_height))
                
                # Calculate position
                x = col * (preview_width + 10) + 5
                y = row * (preview_height + 30) + 20
                
                # Paste preview
                canvas.paste(Image.fromarray(preview_img), (x, y))
                
                # Add preset name
                preset_name = Path(preset_file).stem.replace('_', ' ').title()
                try:
                    font = ImageFont.truetype("arial.ttf", 10)
                except:
                    font = ImageFont.load_default()
                
                draw.text((x, y - 15), preset_name, font=font, fill=(60, 60, 60))
            
            # Save grid
            canvas.save(output_file, 'JPEG', quality=85, optimize=True)
            
            self.logger.info(f"Preset grid saved: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating preset grid: {e}")
            return False


def main():
    """Main CLI function"""
    
    parser = argparse.ArgumentParser(description='Generate Adobe preset previews')
    parser.add_argument('--preset', required=True, help='Path to XMP preset file')
    parser.add_argument('--input', required=True, help='Path to sample image')
    parser.add_argument('--output', required=True, help='Output preview image path')
    parser.add_argument('--size', default='800x600', help='Output size (WIDTHxHEIGHT)')
    parser.add_argument('--no-comparison', action='store_true', help='Skip before/after comparison')
    parser.add_argument('--grid', help='Generate grid from multiple presets (comma-separated)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(log_level)
    
    # Parse output size
    try:
        width, height = map(int, args.size.split('x'))
        output_size = (width, height)
    except ValueError:
        print("❌ Invalid size format. Use WIDTHxHEIGHT (e.g., 800x600)")
        sys.exit(1)
    
    # Check if required libraries are available
    if not PIL_AVAILABLE:
        print("❌ Required libraries not available")
        sys.exit(1)
    
    # Initialize generator
    generator = PresetPreviewGenerator(output_size)
    
    try:
        if args.grid:
            # Generate grid of presets
            preset_files = [p.strip() for p in args.grid.split(',')]
            success = generator.generate_preset_grid(preset_files, args.input, args.output)
        else:
            # Generate single preset preview
            success = generator.generate_preview(
                args.preset, 
                args.input, 
                args.output, 
                comparison=not args.no_comparison
            )
        
        if success:
            print(f"✅ Preview generated successfully: {args.output}")
            sys.exit(0)
        else:
            print("❌ Failed to generate preview")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()