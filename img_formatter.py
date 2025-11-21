#!/usr/bin/env python3
"""
Image Formatter Helper Functions
=================================

Clean, modular helper functions for image formatting and effects.
Provides reusable components for gradient creation, visual effects,
and brand overlays with a focus on simplicity and clarity.
"""

import math
import random
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter


def interpolate_color(
    color1: Tuple[int, int, int],
    color2: Tuple[int, int, int],
    ratio: float
) -> Tuple[int, int, int]:
    """
    Interpolate between two colors with clean linear blending.
    
    Args:
        color1: Starting RGB color tuple
        color2: Ending RGB color tuple
        ratio: Blend ratio (0.0 = color1, 1.0 = color2)
        
    Returns:
        Interpolated RGB color tuple
    """
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    return (r, g, b)


def create_linear_gradient(
    size: Tuple[int, int],
    color1: Tuple[int, int, int],
    color2: Tuple[int, int, int],
    direction: str = 'vertical',
    power: float = 1.0
) -> Image.Image:
    """
    Create a linear gradient with clean line-based rendering.
    
    Args:
        size: Tuple of (width, height)
        color1: Starting RGB color
        color2: Ending RGB color
        direction: Gradient direction ('vertical' or 'horizontal')
        power: Non-linear curve power (1.0 = linear, >1 = accelerated)
        
    Returns:
        PIL Image with gradient
    """
    width, height = size
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    if direction == 'vertical':
        for y in range(height):
            ratio = (y / height) ** power
            color = interpolate_color(color1, color2, ratio)
            draw.line([(0, y), (width, y)], fill=color)
    else:  # horizontal
        for x in range(width):
            ratio = (x / width) ** power
            color = interpolate_color(color1, color2, ratio)
            draw.line([(x, 0), (x, height)], fill=color)
    
    return gradient


def create_radial_gradient(
    size: Tuple[int, int],
    color1: Tuple[int, int, int],
    color2: Tuple[int, int, int],
    center: Tuple[float, float] = (0.5, 0.5),
    power: float = 1.0
) -> Image.Image:
    """
    Create a radial gradient from center to edges.
    
    Args:
        size: Tuple of (width, height)
        color1: Center RGB color
        color2: Edge RGB color
        center: Center point as ratio (0.5, 0.5 = middle)
        power: Non-linear curve power (1.0 = linear, >1 = accelerated)
        
    Returns:
        PIL Image with radial gradient
    """
    width, height = size
    gradient = Image.new('RGB', (width, height))
    pixels = gradient.load()
    
    cx = width * center[0]
    cy = height * center[1]
    max_dist = math.sqrt(cx**2 + cy**2)
    
    for y in range(height):
        for x in range(width):
            # Calculate distance from center
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx**2 + dy**2)
            ratio = min((dist / max_dist) ** power, 1.0)
            pixels[x, y] = interpolate_color(color1, color2, ratio)
    
    return gradient


def apply_vignette(
    image: Image.Image,
    intensity: float = 0.5,
    radius: float = 0.7
) -> Image.Image:
    """
    Apply soft edge darkening vignette effect.
    
    Args:
        image: Input PIL Image
        intensity: Darkness intensity (0.0-1.0)
        radius: Vignette radius as ratio of image size (0.0-1.0)
        
    Returns:
        Image with vignette applied
    """
    width, height = image.size
    
    # Create vignette mask
    mask = Image.new('L', (width, height), 255)
    mask_draw = ImageDraw.Draw(mask)
    
    # Calculate vignette center and dimensions
    cx, cy = width // 2, height // 2
    max_dist = math.sqrt(cx**2 + cy**2)
    
    # Draw radial gradient mask
    pixels = mask.load()
    for y in range(height):
        for x in range(width):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx**2 + dy**2)
            
            # Calculate vignette opacity
            ratio = dist / (max_dist * radius)
            if ratio < 1.0:
                opacity = 255
            else:
                fade = (ratio - 1.0) * intensity
                opacity = max(int(255 * (1 - fade)), 0)
            
            pixels[x, y] = opacity
    
    # Apply vignette by compositing with black
    vignette = Image.new('RGB', (width, height), (0, 0, 0))
    result = Image.composite(image, vignette, mask)
    
    return result


def add_noise_overlay(
    image: Image.Image,
    intensity: int = 10,
    grain_size: int = 1,
    blend_ratio: float = 0.1
) -> Image.Image:
    """
    Add subtle noise texture overlay for film-like quality.
    
    Args:
        image: Input PIL Image
        intensity: Noise intensity (0-255)
        grain_size: Size of noise grains (1 = fine, higher = coarser)
        blend_ratio: Noise blend ratio (0.0-1.0, default 0.1 for subtle effect)
        
    Returns:
        Image with noise overlay
    """
    FINE_GRAIN_SIZE = 1  # Threshold for fine grain rendering
    
    width, height = image.size
    noise = Image.new('RGB', (width // grain_size, height // grain_size))
    pixels = noise.load()
    
    # Generate random noise
    for y in range(height // grain_size):
        for x in range(width // grain_size):
            noise_val = random.randint(-intensity, intensity)
            gray = max(0, min(255, 128 + noise_val))  # Clamp to valid range
            pixels[x, y] = (gray, gray, gray)
    
    # Scale up noise with smoother resampling for better quality
    # Use NEAREST for fine grain, BILINEAR for larger grains
    resample_method = (Image.Resampling.NEAREST if grain_size == FINE_GRAIN_SIZE 
                      else Image.Resampling.BILINEAR)
    noise = noise.resize((width, height), resample_method)
    result = Image.blend(image, noise, blend_ratio)
    
    return result


def add_geometric_pattern(
    image: Image.Image,
    pattern_type: str = 'lines',
    color: Tuple[int, int, int] = (255, 255, 255),
    opacity: int = 20,
    spacing: int = 40
) -> Image.Image:
    """
    Add subtle geometric pattern overlay.
    
    Args:
        image: Input PIL Image
        pattern_type: Pattern style ('lines', 'grid', 'dots')
        color: Pattern RGB color
        opacity: Pattern opacity (0-255)
        spacing: Space between pattern elements
        
    Returns:
        Image with pattern overlay
    """
    width, height = image.size
    
    # Create pattern overlay
    pattern = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pattern)
    
    if pattern_type == 'lines':
        # Diagonal lines
        for i in range(0, width + height, spacing):
            draw.line([(i, 0), (0, i)], fill=color + (opacity,), width=1)
    elif pattern_type == 'grid':
        # Horizontal and vertical lines
        for y in range(0, height, spacing):
            draw.line([(0, y), (width, y)], fill=color + (opacity,), width=1)
        for x in range(0, width, spacing):
            draw.line([(x, 0), (x, height)], fill=color + (opacity,), width=1)
    elif pattern_type == 'dots':
        # Dot pattern
        for y in range(0, height, spacing):
            for x in range(0, width, spacing):
                draw.ellipse([(x-2, y-2), (x+2, y+2)], fill=color + (opacity,))
    
    # Composite pattern over image
    result = Image.alpha_composite(image.convert('RGBA'), pattern)
    return result.convert('RGB')


def draw_brand_widget(
    image: Image.Image,
    text: str = "Pollen Swarm",
    size_ratio: float = 0.25,
    bg_color: Tuple[int, int, int] = (106, 27, 154),
    text_color: Tuple[int, int, int] = (255, 255, 255),
    accent_color: Tuple[int, int, int] = (255, 152, 0)
) -> Image.Image:
    """
    Draw elegant quarter-circle brand widget in bottom-right corner.
    
    Creates a signature branding element with quarter-circle background,
    brand text, and decorative accent - cleaner alternative to branding bars.
    
    Args:
        image: Input PIL Image
        text: Brand text to display
        size_ratio: Widget size as ratio of image width (default 0.25 = 25%)
        bg_color: Widget background RGB color
        text_color: Text RGB color
        accent_color: Accent stripe RGB color
        
    Returns:
        Image with brand widget overlay
    """
    width, height = image.size
    widget_size = int(width * size_ratio)
    
    # Create widget overlay
    widget = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(widget)
    
    # Draw quarter circle background (bottom-right corner)
    x_start = width - widget_size
    y_start = height - widget_size
    
    # Draw filled quarter circle using bbox
    draw.pieslice(
        [(x_start - widget_size, y_start - widget_size),
         (width + widget_size, height + widget_size)],
        180, 270,  # Quarter circle from 180° to 270°
        fill=bg_color + (220,)  # Semi-transparent
    )
    
    # Draw accent stripe (arc)
    stripe_width = 3
    for i in range(stripe_width):
        draw.arc(
            [(x_start - widget_size + 15 + i, y_start - widget_size + 15 + i),
             (width + widget_size - 15 - i, height + widget_size - 15 - i)],
            180, 270,
            fill=accent_color + (200,),
            width=1
        )
    
    # Add brand text along the curve (simplified positioning)
    # Position text in the lower-right area of the widget
    font_size = max(int(widget_size * 0.2), 24)
    
    # Try multiple font paths for cross-platform compatibility
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "arial.ttf",
    ]
    
    font = None
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except (OSError, IOError):
            continue
    
    if font is None:
        font = ImageFont.load_default()
    
    # Calculate text position (bottom-right corner with padding)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = width - text_width - int(widget_size * 0.25)
    text_y = height - text_height - int(widget_size * 0.2)
    
    # Draw text with shadow for depth
    shadow_offset = 2
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
              fill=(0, 0, 0, 150), font=font)
    draw.text((text_x, text_y), text, fill=text_color + (255,), font=font)
    
    # Composite widget over image
    result = Image.alpha_composite(image.convert('RGBA'), widget)
    return result.convert('RGB')
