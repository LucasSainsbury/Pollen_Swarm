#!/usr/bin/env python3
"""
Creative Image Formatter for Marketing Layouts
===============================================

Format generated images into professional marketing layouts with branded themes.
Supports three layout types: vertical banner, square, and horizontal formats.

Features:
- Purple and orange branded theme
- "Pollen Swarm" branding element
- "X nectar points" badge
- Automatic resizing and cropping
- Gradient backgrounds
- PNG output with metadata

Usage:
------
    from creative_formatter import format_creative
    
    # Vertical banner
    format_creative(
        "input.jpg",
        layout="vertical",
        nectar_points=10,
        output_path="output_vertical.png"
    )
    
    # Square format
    format_creative(
        "input.jpg",
        layout="square",
        nectar_points=15,
        output_path="output_square.png"
    )

Author: Pollen Swarm Creative Pipeline
License: MIT
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Brand colors
BRAND_COLORS = {
    'purple': (106, 27, 154),      # Deep purple
    'purple_light': (156, 39, 176), # Light purple
    'orange': (255, 152, 0),        # Vibrant orange
    'orange_light': (255, 183, 77), # Light orange
    'white': (255, 255, 255),
    'black': (0, 0, 0),
}


# Layout dimensions
LAYOUT_SIZES = {
    'vertical': (1080, 1920),   # Portrait (9:16)
    'square': (1080, 1080),     # Square (1:1)
    'horizontal': (1920, 1080), # Landscape (16:9)
}


def create_gradient(
    width: int,
    height: int,
    color1: Tuple[int, int, int],
    color2: Tuple[int, int, int],
    vertical: bool = True
) -> Image.Image:
    """
    Create a gradient image.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        color1: Starting RGB color
        color2: Ending RGB color
        vertical: If True, gradient is vertical; if False, horizontal
        
    Returns:
        PIL Image with gradient
    """
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    if vertical:
        # Vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        # Horizontal gradient
        for x in range(width):
            ratio = x / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    
    return gradient


def resize_and_crop(
    image: Image.Image,
    target_width: int,
    target_height: int,
    crop_position: str = 'center'
) -> Image.Image:
    """
    Resize and crop image to exact dimensions.
    
    Args:
        image: Input PIL Image
        target_width: Target width in pixels
        target_height: Target height in pixels
        crop_position: 'center', 'top', 'bottom', 'left', 'right'
        
    Returns:
        Resized and cropped PIL Image
    """
    # Calculate aspect ratios
    img_aspect = image.width / image.height
    target_aspect = target_width / target_height
    
    # Resize to cover target dimensions
    if img_aspect > target_aspect:
        # Image is wider, scale to height
        new_height = target_height
        new_width = int(image.width * (target_height / image.height))
    else:
        # Image is taller, scale to width
        new_width = target_width
        new_height = int(image.height * (target_width / image.width))
    
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Calculate crop coordinates
    if crop_position == 'center':
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
    elif crop_position == 'top':
        left = (new_width - target_width) // 2
        top = 0
    elif crop_position == 'bottom':
        left = (new_width - target_width) // 2
        top = new_height - target_height
    elif crop_position == 'left':
        left = 0
        top = (new_height - target_height) // 2
    elif crop_position == 'right':
        left = new_width - target_width
        top = (new_height - target_height) // 2
    else:
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
    
    # Crop to target size
    cropped = resized.crop((
        left,
        top,
        left + target_width,
        top + target_height
    ))
    
    return cropped


def draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    text: str,
    font,
    fill_color: Tuple[int, int, int],
    outline_color: Tuple[int, int, int],
    outline_width: int = 2
) -> None:
    """
    Draw text with outline for better readability.
    
    Args:
        draw: ImageDraw object
        position: (x, y) position for text
        text: Text to draw
        font: PIL ImageFont object
        fill_color: RGB color for text fill
        outline_color: RGB color for outline
        outline_width: Width of outline in pixels
    """
    x, y = position
    
    # Draw outline
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text(
                    (x + offset_x, y + offset_y),
                    text,
                    font=font,
                    fill=outline_color
                )
    
    # Draw text
    draw.text(position, text, font=font, fill=fill_color)


def get_default_font(size: int):
    """
    Get a default font or fallback to PIL default.
    
    Args:
        size: Font size in points
        
    Returns:
        PIL ImageFont object
    """
    try:
        # Try to load a nice font
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except:
            try:
                return ImageFont.truetype("arial.ttf", size)
            except:
                # Fallback to default
                logger.warning("Could not load TrueType font, using default")
                return ImageFont.load_default()


def create_branded_panel(
    width: int,
    height: int,
    nectar_points: int = 10,
    include_logo: bool = True
) -> Image.Image:
    """
    Create a branded panel with purple/orange theme and badges.
    
    Args:
        width: Panel width in pixels
        height: Panel height in pixels
        nectar_points: Number of nectar points to display
        include_logo: Whether to include "Pollen Swarm" branding
        
    Returns:
        PIL Image of branded panel
    """
    # Create gradient background
    panel = create_gradient(
        width,
        height,
        BRAND_COLORS['purple'],
        BRAND_COLORS['purple_light'],
        vertical=True
    )
    
    draw = ImageDraw.Draw(panel)
    
    if include_logo:
        # Draw white half-dome for "Pollen Swarm" branding
        dome_radius = min(width, height) // 4
        dome_x = width - dome_radius - 20
        dome_y = 20
        
        # Draw white circle (half-dome effect)
        draw.ellipse(
            [dome_x - dome_radius, dome_y - dome_radius,
             dome_x + dome_radius, dome_y + dome_radius],
            fill=BRAND_COLORS['white']
        )
        
        # Add "Pollen Swarm" text
        font_size = max(24, dome_radius // 3)
        font = get_default_font(font_size)
        text = "Pollen\nSwarm"
        
        # Calculate text position (centered in dome)
        lines = text.split('\n')
        line_height = font_size + 5
        total_height = line_height * len(lines)
        start_y = dome_y - total_height // 2
        
        for i, line in enumerate(lines):
            # Get text bounding box for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = dome_x - text_width // 2
            text_y = start_y + i * line_height
            draw.text((text_x, text_y), line, font=font, fill=BRAND_COLORS['purple'])
    
    # Draw nectar points badge (purple bubble with orange accent)
    badge_width = min(width - 40, 300)
    badge_height = 80
    badge_x = (width - badge_width) // 2
    badge_y = height - badge_height - 30
    
    # Draw orange background (rounded rectangle)
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
        radius=badge_height // 2,
        fill=BRAND_COLORS['orange']
    )
    
    # Add nectar points text
    font_size = 36
    font = get_default_font(font_size)
    text = f"{nectar_points} nectar points"
    
    # Center text in badge
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = badge_x + (badge_width - text_width) // 2
    text_y = badge_y + (badge_height - text_height) // 2
    
    draw.text((text_x, text_y), text, font=font, fill=BRAND_COLORS['white'])
    
    return panel


def format_vertical(
    image: Image.Image,
    nectar_points: int = 10
) -> Image.Image:
    """
    Format image in vertical banner layout (portrait).
    
    Image takes up top 50%, branded panel takes bottom 50%.
    
    Args:
        image: Input PIL Image
        nectar_points: Number of nectar points to display
        
    Returns:
        Formatted PIL Image
    """
    width, height = LAYOUT_SIZES['vertical']
    
    # Create output canvas
    output = Image.new('RGB', (width, height))
    
    # Resize and crop image to top half
    img_height = height // 2
    processed_img = resize_and_crop(image, width, img_height)
    output.paste(processed_img, (0, 0))
    
    # Create and paste branded panel to bottom half
    panel = create_branded_panel(width, img_height, nectar_points)
    output.paste(panel, (0, img_height))
    
    return output


def format_square(
    image: Image.Image,
    nectar_points: int = 10
) -> Image.Image:
    """
    Format image in square layout (1:1).
    
    Image takes up top 80%, branded panel takes bottom 20%.
    
    Args:
        image: Input PIL Image
        nectar_points: Number of nectar points to display
        
    Returns:
        Formatted PIL Image
    """
    width, height = LAYOUT_SIZES['square']
    
    # Create output canvas
    output = Image.new('RGB', (width, height))
    
    # Resize and crop image to top 80%
    img_height = int(height * 0.8)
    processed_img = resize_and_crop(image, width, img_height)
    output.paste(processed_img, (0, 0))
    
    # Create and paste branded panel to bottom 20%
    panel_height = height - img_height
    panel = create_branded_panel(width, panel_height, nectar_points, include_logo=True)
    output.paste(panel, (0, img_height))
    
    return output


def format_horizontal(
    image: Image.Image,
    nectar_points: int = 10,
    image_position: str = 'left'
) -> Image.Image:
    """
    Format image in horizontal layout (landscape).
    
    Image takes up 50%, branded panel takes other 50%.
    
    Args:
        image: Input PIL Image
        nectar_points: Number of nectar points to display
        image_position: 'left' or 'right' for image placement
        
    Returns:
        Formatted PIL Image
    """
    width, height = LAYOUT_SIZES['horizontal']
    
    # Create output canvas
    output = Image.new('RGB', (width, height))
    
    # Resize and crop image to half width
    img_width = width // 2
    processed_img = resize_and_crop(image, img_width, height)
    
    # Create branded panel for other half
    panel = create_branded_panel(img_width, height, nectar_points)
    
    # Paste based on position
    if image_position == 'left':
        output.paste(processed_img, (0, 0))
        output.paste(panel, (img_width, 0))
    else:
        output.paste(panel, (0, 0))
        output.paste(processed_img, (img_width, 0))
    
    return output


def format_creative(
    input_image_path: str,
    layout: str = "vertical",
    nectar_points: int = 10,
    output_path: Optional[str] = None,
    image_position: str = 'left'
) -> Tuple[str, str]:
    """
    Format a generated image into a marketing layout.
    
    Args:
        input_image_path: Path to input image file
        layout: Layout type - "vertical", "square", or "horizontal"
        nectar_points: Number of nectar points to display
        output_path: Path for output file (default: auto-generated)
        image_position: For horizontal layout, 'left' or 'right'
        
    Returns:
        Tuple of (output_image_path, metadata_path)
        
    Raises:
        FileNotFoundError: If input image doesn't exist
        ValueError: If layout type is invalid
    """
    # Validate inputs
    input_path = Path(input_image_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_image_path}")
    
    if layout not in ['vertical', 'square', 'horizontal']:
        raise ValueError(f"Invalid layout: {layout}. Must be 'vertical', 'square', or 'horizontal'")
    
    logger.info(f"Formatting image: {input_path}")
    logger.info(f"Layout: {layout}")
    logger.info(f"Nectar points: {nectar_points}")
    
    # Load input image
    try:
        image = Image.open(input_path)
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as e:
        raise ValueError(f"Failed to load image: {e}")
    
    # Format based on layout
    if layout == 'vertical':
        formatted = format_vertical(image, nectar_points)
    elif layout == 'square':
        formatted = format_square(image, nectar_points)
    elif layout == 'horizontal':
        formatted = format_horizontal(image, nectar_points, image_position)
    
    # Determine output path
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_{layout}.png"
    else:
        output_path = Path(output_path)
        # Ensure .png extension
        if output_path.suffix.lower() != '.png':
            output_path = output_path.with_suffix('.png')
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save formatted image as PNG
    formatted.save(output_path, format='PNG', optimize=True)
    logger.info(f"✓ Saved formatted image: {output_path}")
    
    # Create metadata
    metadata = {
        'input_image': str(input_path),
        'output_image': str(output_path),
        'layout': layout,
        'nectar_points': nectar_points,
        'image_position': image_position if layout == 'horizontal' else None,
        'dimensions': {
            'width': formatted.width,
            'height': formatted.height,
        },
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    
    # Load original metadata if available
    original_metadata_path = input_path.with_suffix('.json')
    if original_metadata_path.exists():
        try:
            with open(original_metadata_path, 'r') as f:
                original_metadata = json.load(f)
            metadata['original_generation'] = original_metadata
        except:
            pass
    
    # Save metadata
    metadata_path = output_path.with_suffix('.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info(f"✓ Saved metadata: {metadata_path}")
    
    return str(output_path), str(metadata_path)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Format images into marketing layouts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Vertical banner format
  python creative_formatter.py -i input.jpg -l vertical -n 10
  
  # Square format with custom output
  python creative_formatter.py -i input.jpg -l square -n 15 -o output_square.png
  
  # Horizontal format with image on right
  python creative_formatter.py -i input.jpg -l horizontal -p right -n 20
  
  # Batch process all images in a directory
  python creative_formatter.py -i ./images/ -l vertical -n 10
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Input image file or directory"
    )
    
    parser.add_argument(
        "--layout", "-l",
        type=str,
        default="vertical",
        choices=['vertical', 'square', 'horizontal'],
        help="Layout type (default: vertical)"
    )
    
    parser.add_argument(
        "--nectar-points", "-n",
        type=int,
        default=10,
        help="Number of nectar points to display (default: 10)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output path (default: auto-generated)"
    )
    
    parser.add_argument(
        "--position", "-p",
        type=str,
        default="left",
        choices=['left', 'right'],
        help="Image position for horizontal layout (default: left)"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # Handle single file
    if input_path.is_file():
        try:
            output_path, metadata_path = format_creative(
                input_image_path=str(input_path),
                layout=args.layout,
                nectar_points=args.nectar_points,
                output_path=args.output,
                image_position=args.position
            )
            logger.info(f"\n✅ Success!")
            logger.info(f"Output: {output_path}")
            logger.info(f"Metadata: {metadata_path}")
            return 0
        except Exception as e:
            logger.error(f"✗ Failed: {e}")
            return 1
    
    # Handle directory (batch processing)
    elif input_path.is_dir():
        logger.info(f"Batch processing directory: {input_path}")
        
        # Find all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_path.glob(f'*{ext}'))
            image_files.extend(input_path.glob(f'*{ext.upper()}'))
        
        if not image_files:
            logger.error(f"No image files found in {input_path}")
            return 1
        
        logger.info(f"Found {len(image_files)} images to process")
        
        successful = 0
        failed = 0
        
        for img_file in image_files:
            try:
                logger.info(f"\nProcessing: {img_file.name}")
                format_creative(
                    input_image_path=str(img_file),
                    layout=args.layout,
                    nectar_points=args.nectar_points,
                    image_position=args.position
                )
                successful += 1
            except Exception as e:
                logger.error(f"Failed to process {img_file.name}: {e}")
                failed += 1
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Batch processing complete!")
        logger.info(f"✓ Successful: {successful}")
        logger.info(f"✗ Failed: {failed}")
        
        return 0 if failed == 0 else 1
    
    else:
        logger.error(f"Input path not found: {input_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
