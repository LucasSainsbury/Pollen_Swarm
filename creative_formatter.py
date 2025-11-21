#!/usr/bin/env python3
"""
Enterprise Creative Image Formatter for Marketing Layouts
===========================================================

Professional-grade formatter with cohesive, polished design optimized for
creating stunning advertisement materials with seamless brand integration.

Key Features:
- **Smart Transparent Overlays**: Multi-layer transparency system that intelligently
  blends design elements with the product image for cohesive composition
- **Adaptive Color Matching**: Extracts dominant colors from images to create
  smart gradients that smoothly transition between image and design elements
- **Prominent Pollen Swarm Branding**: Dedicated branded section with enhanced
  visibility and professional presentation throughout all layouts
- **Smooth Gradient Transitions**: Non-linear gradient algorithms with variable
  transparency for natural, professional-looking color flows
- **Professional Polish Elements**: Corner accents, multi-layer shadows, glows,
  and decorative elements for high-end advertisement quality
- **Enhanced Typography**: Multi-layer text effects with shadows and backgrounds
  for improved readability and visual hierarchy
- **Overlapping Design System**: Strategic element placement that creates depth
  and ties the composition together
- **Adaptive Transparency Fades**: Smoothness-controlled fade overlays in all
  directions for seamless image-to-design transitions

Layout Options:
- Vertical (1080x1920) - Instagram Stories, Portrait ads
- Square (1080x1080) - Social media posts, Square ads  
- Horizontal (1920x1080) - Website banners, Landscape ads

Professional Advertisement Features:
✓ Smart color-matched overlay transitions
✓ Elegant quarter-circle brand widget
✓ Decorative corner accents
✓ Multi-layer text shadows and glows
✓ Gradient accent stripes
✓ Premium nectar points badges
✓ Adaptive transparency blending
✓ High-contrast text with subtle backgrounds
✓ Brand-consistent color palette integration
"""

import argparse
import json
import logging
import os
import sys
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Import clean helper functions from img_formatter
from img_formatter import (
    interpolate_color,
    create_linear_gradient,
    create_radial_gradient,
    apply_vignette,
    add_noise_overlay,
    add_geometric_pattern,
    draw_brand_widget
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Brand colors
BRAND_COLORS = {
    'purple': (106, 27, 154),
    'purple_light': (156, 39, 176),
    'purple_dark': (75, 0, 130),
    'orange': (255, 152, 0),
    'orange_light': (255, 183, 77),
    'orange_dark': (230, 124, 0),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray_dark': (40, 40, 40),
    'gray_light': (245, 245, 245),
}

# Fallback color for edge cases
FALLBACK_NEUTRAL_COLOR = (128, 128, 128)

# Layout dimensions
LAYOUT_SIZES = {
    'vertical': (1080, 1920),
    'square': (1080, 1080),
    'horizontal': (1920, 1080),
}


def get_default_font(size: int, bold: bool = False):
    """Get system font with fallback."""
    font_names = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "arial.ttf" if not bold else "arialbd.ttf",
    ]

    for font_path in font_names:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue

    return ImageFont.load_default()


def create_gradient(
        width: int,
        height: int,
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        vertical: bool = True,
        power: float = 1.0
) -> Image.Image:
    """
    Create smooth gradient with non-linear progression.
    
    This function now wraps the cleaner create_linear_gradient from img_formatter
    for backward compatibility while using the improved implementation.
    """
    direction = 'vertical' if vertical else 'horizontal'
    return create_linear_gradient((width, height), color1, color2, direction, power)


def extract_dominant_color(image: Image.Image, sample_area: str = 'center') -> Tuple[int, int, int]:
    """Extract dominant color from image for smart gradient matching."""
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Sample a region of the image
    w, h = image.size
    if sample_area == 'center':
        box = (w//4, h//4, 3*w//4, 3*h//4)
    elif sample_area == 'bottom':
        box = (0, 3*h//4, w, h)
    elif sample_area == 'top':
        box = (0, 0, w, h//4)
    elif sample_area == 'right':
        box = (3*w//4, 0, w, h)
    elif sample_area == 'left':
        box = (0, 0, w//4, h)
    else:
        box = (0, 0, w, h)
    
    region = image.crop(box)
    region = region.resize((50, 50), Image.Resampling.LANCZOS)
    
    # Get average color - safely handle all pixel data
    pixels = list(region.getdata())
    if not pixels:
        # Fallback to neutral color if no pixels
        return FALLBACK_NEUTRAL_COLOR
    
    # Check if pixels have RGB channels
    first_pixel = pixels[0]
    if not isinstance(first_pixel, tuple) or len(first_pixel) < 3:
        # Fallback to neutral color for non-RGB data
        return FALLBACK_NEUTRAL_COLOR
    
    r_avg = sum(p[0] for p in pixels) // len(pixels)
    g_avg = sum(p[1] for p in pixels) // len(pixels)
    b_avg = sum(p[2] for p in pixels) // len(pixels)
    
    # Slightly desaturate for better overlay blending
    avg = (r_avg + g_avg + b_avg) // 3
    r_avg = int(r_avg * 0.7 + avg * 0.3)
    g_avg = int(g_avg * 0.7 + avg * 0.3)
    b_avg = int(b_avg * 0.7 + avg * 0.3)
    
    return (r_avg, g_avg, b_avg)


def create_smart_overlay(
        width: int,
        height: int,
        base_color: Tuple[int, int, int],
        brand_color: Tuple[int, int, int],
        alpha: int = 180
) -> Image.Image:
    """
    Create a smart overlay that blends image colors with brand colors efficiently.
    
    Now uses the cleaner interpolate_color function for better code clarity.
    """
    overlay = Image.new('RGBA', (width, height))
    
    # Use ImageDraw for more efficient rendering
    draw = ImageDraw.Draw(overlay)
    
    # Create a gradient from extracted color to brand color using cleaner helper
    for y in range(height):
        ratio = (y / height) ** 1.2
        color = interpolate_color(base_color, brand_color, ratio)
        
        # Vary alpha for smoother transitions
        line_alpha = int(alpha * (0.3 + 0.7 * ratio))
        
        # Draw entire line at once instead of pixel by pixel
        draw.line([(0, y), (width, y)], fill=color + (line_alpha,))
    
    return overlay


def create_transparency_fade(width: int, height: int, direction: str = 'down', smoothness: float = 1.5) -> Image.Image:
    """Create gradient transparency overlay for smooth transitions with enhanced blending."""
    fade = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(fade)

    if direction == 'down':
        for y in range(height):
            # Use power function for smoother, more natural fade
            ratio = (y / height) ** smoothness
            alpha = int(ratio * 255)
            # Draw entire line at once for better performance
            draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    elif direction == 'up':
        for y in range(height):
            ratio = (1 - y / height) ** smoothness
            alpha = int(ratio * 255)
            draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    elif direction == 'left':
        for x in range(width):
            ratio = (x / width) ** smoothness
            alpha = int(ratio * 255)
            draw.line([(x, 0), (x, height)], fill=(0, 0, 0, alpha))
    elif direction == 'right':
        for x in range(width):
            ratio = (1 - x / width) ** smoothness
            alpha = int(ratio * 255)
            draw.line([(x, 0), (x, height)], fill=(0, 0, 0, alpha))

    return fade


def resize_and_crop(
        image: Image.Image,
        target_width: int,
        target_height: int,
        crop_position: str = 'center'
) -> Image.Image:
    """Resize and crop image to exact dimensions."""
    img_aspect = image.width / image.height
    target_aspect = target_width / target_height

    if img_aspect > target_aspect:
        new_height = target_height
        new_width = int(image.width * (target_height / image.height))
    else:
        new_width = target_width
        new_height = int(image.height * (target_width / image.width))

    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    if crop_position == 'center':
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
    elif crop_position == 'top':
        left = (new_width - target_width) // 2
        top = 0
    else:
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2

    cropped = resized.crop((left, top, left + target_width, top + target_height))
    return cropped


def create_premium_badge(
        width: int,
        height: int,
        points: int = 10,
        tagline: str = "Get rewarded"
) -> Image.Image:
    """Create sophisticated badge with advanced styling."""
    badge = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)

    corner_radius = height // 4

    # Outer shadow effect
    shadow_offset = 8
    shadow_color = (0, 0, 0, 60)
    draw.rounded_rectangle(
        [shadow_offset, shadow_offset, width + shadow_offset, height + shadow_offset],
        radius=corner_radius,
        fill=shadow_color
    )

    # Main badge body gradient
    gradient = create_gradient(
        width, height,
        BRAND_COLORS['orange'],
        BRAND_COLORS['orange_dark'],
        vertical=True,
        power=1.2
    )
    gradient_rgba = gradient.convert('RGBA')

    # Create rounded mask
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, width, height], radius=corner_radius, fill=255)

    # Apply mask
    badge_with_grad = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    badge_with_grad.paste(gradient_rgba, (0, 0), mask)

    # Add shine layer
    shine = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shine_draw = ImageDraw.Draw(shine)
    shine_height = height // 3
    shine_draw.rounded_rectangle(
        [2, 2, width - 2, shine_height],
        radius=corner_radius,
        fill=(*BRAND_COLORS['white'], 120)
    )
    badge_with_grad.paste(shine, (0, 0), shine)

    # Subtle inner border
    border_draw = ImageDraw.Draw(badge_with_grad)
    border_draw.rounded_rectangle(
        [3, 3, width - 3, height - 3],
        radius=corner_radius,
        outline=(*BRAND_COLORS['white'], 180),
        width=2
    )

    # Points number
    font_points = get_default_font(int(height * 0.5), bold=True)
    font_text = get_default_font(int(height * 0.24), bold=False)

    points_text = str(points)
    bbox = draw.textbbox((0, 0), points_text, font=font_points)
    points_width = bbox[2] - bbox[0]
    points_x = (width - points_width) // 2
    points_y = int(height * 0.10)

    draw.text((points_x, points_y), points_text, font=font_points, fill=BRAND_COLORS['white'])

    # "nectar points" label
    label_text = "nectar points"
    bbox_label = draw.textbbox((0, 0), label_text, font=font_text)
    label_width = bbox_label[2] - bbox_label[0]
    label_x = (width - label_width) // 2
    label_y = int(height * 0.58)

    draw.text((label_x, label_y), label_text, font=font_text, fill=BRAND_COLORS['white'])

    # Tagline
    if tagline:
        font_tagline = get_default_font(int(height * 0.18), bold=False)
        bbox_tag = draw.textbbox((0, 0), tagline, font=font_tagline)
        tag_width = bbox_tag[2] - bbox_tag[0]
        tag_x = (width - tag_width) // 2
        tag_y = int(height * 0.77)
        draw.text((tag_x, tag_y), tagline, font=font_tagline, fill=(*BRAND_COLORS['white'], 245))

    return badge_with_grad


def create_corner_accent(size: int, color: Tuple[int, int, int]) -> Image.Image:
    """Create decorative corner accent for professional polish."""
    accent = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(accent)
    
    # Create a subtle corner design
    thickness = max(3, size // 30)
    
    # L-shaped corner
    draw.line([(0, 0), (size, 0)], fill=(*color, 200), width=thickness)
    draw.line([(0, 0), (0, size)], fill=(*color, 200), width=thickness)
    
    # Additional accent lines for depth
    offset = thickness + 2
    draw.line([(0, offset), (size - offset, offset)], fill=(*color, 120), width=thickness - 1)
    draw.line([(offset, 0), (offset, size - offset)], fill=(*color, 120), width=thickness - 1)
    
    return accent


def create_pollen_swarm_branding(width: int, height: int, style: str = 'logo') -> Image.Image:
    """Create enhanced Pollen Swarm branding element with multiple styles."""
    branding = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(branding)

    center_x, center_y = width // 2, height // 2
    
    if style == 'logo':
        # Hexagon/flower logo
        radius = min(width, height) // 3
        angles = [i * 60 for i in range(6)]
        points = []
        for angle in angles:
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            points.append((x, y))
        
        # Draw hexagon with gradient effect and glow
        draw.polygon(points, fill=(*BRAND_COLORS['orange'], 220), outline=(*BRAND_COLORS['white'], 255))
        
        # Add center circle
        circle_radius = radius // 2
        draw.ellipse(
            [center_x - circle_radius, center_y - circle_radius,
             center_x + circle_radius, center_y + circle_radius],
            fill=(*BRAND_COLORS['white'], 255)
        )
        
        # Add text
        font_brand = get_default_font(int(height * 0.35), bold=True)
        text = "PS"
        bbox = draw.textbbox((0, 0), text, font=font_brand)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2
        draw.text((text_x, text_y), text, font=font_brand, fill=BRAND_COLORS['orange'])
    
    elif style == 'badge':
        # Full branded badge with text
        padding = int(width * 0.1)
        
        # Background with rounded corners
        draw.rounded_rectangle(
            [padding, padding, width - padding, height - padding],
            radius=height // 6,
            fill=(*BRAND_COLORS['purple'], 230)
        )
        
        # Border accent
        draw.rounded_rectangle(
            [padding + 3, padding + 3, width - padding - 3, height - padding - 3],
            radius=height // 6,
            outline=(*BRAND_COLORS['orange'], 200),
            width=3
        )
        
        # Pollen Swarm text
        font_brand = get_default_font(int(height * 0.28), bold=True)
        text = "POLLEN"
        bbox = draw.textbbox((0, 0), text, font=font_brand)
        text_width = bbox[2] - bbox[0]
        text_x = center_x - text_width // 2
        text_y = int(height * 0.25)
        draw.text((text_x, text_y), text, font=font_brand, fill=BRAND_COLORS['white'])
        
        font_swarm = get_default_font(int(height * 0.28), bold=True)
        text2 = "SWARM"
        bbox2 = draw.textbbox((0, 0), text2, font=font_swarm)
        text2_width = bbox2[2] - bbox2[0]
        text2_x = center_x - text2_width // 2
        text2_y = int(height * 0.55)
        draw.text((text2_x, text2_y), text2, font=font_swarm, fill=BRAND_COLORS['orange'])

    return branding


def format_vertical_premium(
        image: Image.Image,
        product_name: str = "Product",
        tagline: str = "Premium Quality",
        nectar_points: int = 10,
        flavor_text: str = "Trusted quality",
        add_vignette: bool = False,
        add_noise: bool = False,
        add_pattern: bool = False
) -> Image.Image:
    """
    Premium vertical banner with enhanced cohesive design and prominent branding.
    
    Args:
        image: Product image to format
        product_name: Product name text
        tagline: Tagline text
        nectar_points: Reward points value
        flavor_text: Descriptive flavor text
        add_vignette: Apply soft edge darkening (optional)
        add_noise: Add subtle texture overlay (optional)
        add_pattern: Add geometric pattern overlay (optional)
    
    Returns:
        Formatted image in vertical layout (1080x1920)
    """
    width, height = LAYOUT_SIZES['vertical']
    output = Image.new('RGB', (width, height), color=BRAND_COLORS['white'])

    # Image section
    img_height = int(height * 0.55)
    overlap_zone = int(height * 0.10)  # Larger transition zone
    text_start = img_height - overlap_zone

    processed_img = resize_and_crop(image, width, img_height, crop_position='center')
    output.paste(processed_img, (0, 0))
    
    # Extract dominant color from bottom of image for smart blending
    dominant_color = extract_dominant_color(processed_img, 'bottom')

    # Apply subtle darkening overlay on bottom of image for better text contrast
    dark_overlay = Image.new('RGBA', (width, overlap_zone * 2), (0, 0, 0, 0))
    dark_draw = ImageDraw.Draw(dark_overlay)
    for y in range(overlap_zone * 2):
        alpha = int((y / (overlap_zone * 2)) * 100)
        dark_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    output.paste(dark_overlay, (0, img_height - overlap_zone * 2), dark_overlay)

    # Smart color-matched overlay for smooth transition
    smart_overlay = create_smart_overlay(
        width, 
        overlap_zone * 3, 
        dominant_color, 
        BRAND_COLORS['purple'],
        alpha=160
    )
    output.paste(smart_overlay, (0, text_start - overlap_zone), smart_overlay)

    # Main background gradient for text area
    gradient_height = height - text_start
    gradient_bg = create_gradient(
        width,
        gradient_height,
        BRAND_COLORS['purple'],
        BRAND_COLORS['purple_dark'],
        vertical=True,
        power=0.9
    )
    output.paste(gradient_bg, (0, text_start + overlap_zone))

    draw = ImageDraw.Draw(output)

    # Decorative accent stripe with gradient
    stripe_height = 6
    stripe_y = text_start + overlap_zone
    for i in range(stripe_height):
        alpha_val = int(255 - (i / stripe_height) * 100)
        color = (*BRAND_COLORS['orange'], alpha_val) if i < stripe_height // 2 else (*BRAND_COLORS['orange_light'], alpha_val)
        draw.line([(0, stripe_y + i), (width, stripe_y + i)], fill=color)

    # Corner accents for professional polish
    corner_size = 60
    corner_accent_tl = create_corner_accent(corner_size, BRAND_COLORS['orange'])
    corner_accent_br = create_corner_accent(corner_size, BRAND_COLORS['orange']).rotate(180)
    output.paste(corner_accent_tl, (15, 15), corner_accent_tl)
    output.paste(corner_accent_br, (width - corner_size - 15, height - corner_size - 15), corner_accent_br)

    # Product name with glow effect
    font_product = get_default_font(70, bold=True)
    bbox = draw.textbbox((0, 0), product_name, font=font_product)
    product_width = bbox[2] - bbox[0]
    product_x = (width - product_width) // 2
    product_y = text_start + overlap_zone + 60

    # Multi-layer glow for depth
    for offset in [(4, 4), (3, 3), (2, 2)]:
        draw.text((product_x + offset[0], product_y + offset[1]), product_name, 
                 font=font_product, fill=(0, 0, 0, 80))
    draw.text((product_x, product_y), product_name, font=font_product, fill=BRAND_COLORS['white'])

    # Tagline with subtle background
    font_tagline = get_default_font(34, bold=False)
    bbox_tag = draw.textbbox((0, 0), tagline, font=font_tagline)
    tagline_width = bbox_tag[2] - bbox_tag[0]
    tagline_x = (width - tagline_width) // 2
    tagline_y = product_y + 90
    
    # Tagline background bar
    tag_bg_padding = 15
    draw.rounded_rectangle(
        [tagline_x - tag_bg_padding, tagline_y - 8, 
         tagline_x + tagline_width + tag_bg_padding, tagline_y + 42],
        radius=8,
        fill=(*BRAND_COLORS['orange'], 100)
    )
    draw.text((tagline_x, tagline_y), tagline, font=font_tagline, fill=BRAND_COLORS['white'])

    # Badge - overlapping design
    badge_width = int(width * 0.78)
    badge_height = 180
    badge = create_premium_badge(badge_width, badge_height, nectar_points, "Earn rewards")
    badge_x = (width - badge_width) // 2
    badge_y = text_start - badge_height // 2

    badge_rgb = badge.convert('RGB')
    output.paste(badge_rgb, (badge_x, badge_y))

    # Flavor text below badge
    font_flavor = get_default_font(26, bold=False)
    bbox_flavor = draw.textbbox((0, 0), flavor_text, font=font_flavor)
    flavor_width = bbox_flavor[2] - bbox_flavor[0]
    flavor_x = (width - flavor_width) // 2
    flavor_y = badge_y + badge_height + 40
    
    # Flavor text with shadow
    draw.text((flavor_x + 1, flavor_y + 1), flavor_text, font=font_flavor, fill=(0, 0, 0, 120))
    draw.text((flavor_x, flavor_y), flavor_text, font=font_flavor, fill=BRAND_COLORS['white'])

    # Clean brand widget in bottom-right corner (replaces branding bar)
    output = draw_brand_widget(
        output,
        text="Pollen Swarm",
        size_ratio=0.25,
        bg_color=BRAND_COLORS['purple'],
        accent_color=BRAND_COLORS['orange']
    )

    # Additional small logo in top right for brand consistency
    small_logo_size = 80
    small_logo = create_pollen_swarm_branding(small_logo_size, small_logo_size, style='logo')
    output.paste(small_logo, (width - small_logo_size - 25, 25), small_logo)

    # Apply optional effects
    if add_vignette:
        output = apply_vignette(output, intensity=0.5, radius=0.7)
    if add_noise:
        output = add_noise_overlay(output, intensity=10, grain_size=1)
    if add_pattern:
        output = add_geometric_pattern(output, pattern_type='lines', 
                                      color=BRAND_COLORS['white'], opacity=15, spacing=60)

    return output


def format_square_premium(
        image: Image.Image,
        product_name: str = "Product",
        tagline: str = "Premium Quality",
        nectar_points: int = 10,
        flavor_text: str = "Trusted quality",
        add_vignette: bool = False,
        add_noise: bool = False,
        add_pattern: bool = False
) -> Image.Image:
    """
    Premium square format with enhanced cohesive design and branding.
    
    Args:
        image: Product image to format
        product_name: Product name text
        tagline: Tagline text
        nectar_points: Reward points value
        flavor_text: Descriptive flavor text
        add_vignette: Apply soft edge darkening (optional)
        add_noise: Add subtle texture overlay (optional)
        add_pattern: Add geometric pattern overlay (optional)
    
    Returns:
        Formatted image in square layout (1080x1080)
    """
    width, height = LAYOUT_SIZES['square']
    output = Image.new('RGB', (width, height), color=BRAND_COLORS['white'])

    # Image section
    img_height = int(height * 0.66)
    overlap_zone = int(height * 0.08)
    text_start = img_height - overlap_zone

    processed_img = resize_and_crop(image, width, img_height)
    output.paste(processed_img, (0, 0))
    
    # Extract dominant color for smart blending
    dominant_color = extract_dominant_color(processed_img, 'bottom')

    # Darkening overlay for better contrast
    dark_overlay = Image.new('RGBA', (width, overlap_zone * 2), (0, 0, 0, 0))
    dark_draw = ImageDraw.Draw(dark_overlay)
    for y in range(overlap_zone * 2):
        alpha = int((y / (overlap_zone * 2)) * 90)
        dark_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    output.paste(dark_overlay, (0, img_height - overlap_zone * 2), dark_overlay)

    # Smart overlay transition
    smart_overlay = create_smart_overlay(
        width, 
        overlap_zone * 3, 
        dominant_color, 
        BRAND_COLORS['orange'],
        alpha=150
    )
    output.paste(smart_overlay, (0, text_start - overlap_zone), smart_overlay)

    # Background gradient
    gradient_height = height - text_start
    gradient_bg = create_gradient(
        width,
        gradient_height,
        BRAND_COLORS['orange'],
        BRAND_COLORS['orange_dark'],
        vertical=True,
        power=1.1
    )
    output.paste(gradient_bg, (0, text_start + int(overlap_zone * 1.3)))

    draw = ImageDraw.Draw(output)

    # Decorative stripe with gradient effect
    stripe_y = text_start + int(overlap_zone * 1.3)
    for i in range(8):
        alpha_val = int(255 - (i / 8) * 100)
        color = (*BRAND_COLORS['purple'], alpha_val) if i < 4 else (*BRAND_COLORS['purple_light'], alpha_val)
        draw.line([(0, stripe_y + i), (width, stripe_y + i)], fill=color)

    # Corner accents
    corner_size = 55
    corner_accent_tl = create_corner_accent(corner_size, BRAND_COLORS['purple'])
    corner_accent_br = create_corner_accent(corner_size, BRAND_COLORS['purple']).rotate(180)
    output.paste(corner_accent_tl, (12, 12), corner_accent_tl)
    output.paste(corner_accent_br, (width - corner_size - 12, height - corner_size - 12), corner_accent_br)

    # Product name with enhanced styling
    font_product = get_default_font(62, bold=True)
    bbox = draw.textbbox((0, 0), product_name, font=font_product)
    product_width = bbox[2] - bbox[0]
    product_x = (width - product_width) // 2
    product_y = stripe_y + 45

    # Multi-layer shadow
    for offset in [(3, 3), (2, 2), (1, 1)]:
        draw.text((product_x + offset[0], product_y + offset[1]), product_name, 
                 font=font_product, fill=(0, 0, 0, 100))
    draw.text((product_x, product_y), product_name, font=font_product, fill=BRAND_COLORS['white'])

    # Badge positioned in center
    badge_width = int(width * 0.75)
    badge_height = 150
    badge = create_premium_badge(badge_width, badge_height, nectar_points, "Earn rewards")
    badge_x = (width - badge_width) // 2
    badge_y = product_y + 100

    badge_rgb = badge.convert('RGB')
    output.paste(badge_rgb, (badge_x, badge_y))

    # Clean brand widget in bottom-right corner (replaces branding bar)
    output = draw_brand_widget(
        output,
        text="Pollen Swarm",
        size_ratio=0.25,
        bg_color=BRAND_COLORS['purple'],
        accent_color=BRAND_COLORS['orange']
    )

    # Small logo in corner
    small_logo_size = 75
    small_logo = create_pollen_swarm_branding(small_logo_size, small_logo_size, style='logo')
    output.paste(small_logo, (width - small_logo_size - 20, 20), small_logo)

    # Apply optional effects
    if add_vignette:
        output = apply_vignette(output, intensity=0.5, radius=0.7)
    if add_noise:
        output = add_noise_overlay(output, intensity=10, grain_size=1)
    if add_pattern:
        output = add_geometric_pattern(output, pattern_type='lines', 
                                      color=BRAND_COLORS['white'], opacity=15, spacing=60)

    return output


def format_horizontal_premium(
        image: Image.Image,
        product_name: str = "Product",
        tagline: str = "Premium Quality",
        nectar_points: int = 10,
        flavor_text: str = "Trusted quality",
        image_position: str = 'left',
        add_vignette: bool = False,
        add_noise: bool = False,
        add_pattern: bool = False
) -> Image.Image:
    """
    Premium horizontal layout with enhanced cohesive composition and branding.
    
    Args:
        image: Product image to format
        product_name: Product name text
        tagline: Tagline text
        nectar_points: Reward points value
        flavor_text: Descriptive flavor text
        image_position: Image position ('left' or 'right')
        add_vignette: Apply soft edge darkening (optional)
        add_noise: Add subtle texture overlay (optional)
        add_pattern: Add geometric pattern overlay (optional)
    
    Returns:
        Formatted image in horizontal layout (1920x1080)
    """
    width, height = LAYOUT_SIZES['horizontal']
    output = Image.new('RGB', (width, height), color=BRAND_COLORS['white'])

    img_width = int(width * 0.54)
    panel_width = width - img_width

    # Process image
    processed_img = resize_and_crop(image, img_width, height)
    
    # Extract dominant color for smart overlay
    dominant_color = extract_dominant_color(processed_img, 'right' if image_position == 'left' else 'left')

    # Create enhanced gradient panel
    gradient_panel = create_gradient(
        panel_width,
        height,
        BRAND_COLORS['purple'],
        BRAND_COLORS['purple_dark'],
        vertical=False,
        power=0.85
    )

    # Place sections
    if image_position == 'left':
        output.paste(processed_img, (0, 0))
        output.paste(gradient_panel, (img_width, 0))

        # Enhanced fade transition with smart color matching
        fade_width = 120
        smart_fade = create_smart_overlay(
            fade_width, 
            height, 
            dominant_color, 
            BRAND_COLORS['purple'],
            alpha=180
        )
        output.paste(smart_fade, (img_width - fade_width + 20, 0), smart_fade)

        panel_x = img_width + 60
        accent_x = img_width
    else:
        output.paste(gradient_panel, (0, 0))
        output.paste(processed_img, (panel_width, 0))

        fade_width = 120
        smart_fade = create_smart_overlay(
            fade_width, 
            height, 
            dominant_color, 
            BRAND_COLORS['purple'],
            alpha=180
        )
        output.paste(smart_fade, (panel_width - 20, 0), smart_fade)

        panel_x = 60
        accent_x = panel_width - 6

    draw = ImageDraw.Draw(output)

    # Enhanced vertical accent divider with gradient
    divider_width = 8
    for i in range(divider_width):
        if image_position == 'left':
            alpha_val = int(255 - (i / divider_width) * 100)
            color = (*BRAND_COLORS['orange'], alpha_val) if i < divider_width // 2 else (*BRAND_COLORS['orange_light'], alpha_val)
            draw.line([(accent_x + i, 0), (accent_x + i, height)], fill=color)
        else:
            alpha_val = int(255 - (i / divider_width) * 100)
            color = (*BRAND_COLORS['orange'], alpha_val) if i < divider_width // 2 else (*BRAND_COLORS['orange_light'], alpha_val)
            draw.line([(accent_x - i, 0), (accent_x - i, height)], fill=color)

    # Corner accents
    corner_size = 50
    corner_accent_tl = create_corner_accent(corner_size, BRAND_COLORS['orange'])
    corner_accent_br = create_corner_accent(corner_size, BRAND_COLORS['orange']).rotate(180)
    
    if image_position == 'left':
        output.paste(corner_accent_br, (width - corner_size - 12, height - corner_size - 12), corner_accent_br)
    else:
        output.paste(corner_accent_tl, (12, 12), corner_accent_tl)

    # Typography
    font_product = get_default_font(58, bold=True)
    font_tagline = get_default_font(30, bold=False)
    font_flavor = get_default_font(24, bold=False)

    # Product name with enhanced styling
    product_y = int(height * 0.12)
    bbox = draw.textbbox((0, 0), product_name, font=font_product)
    
    # Multi-layer shadow for depth
    for offset in [(3, 3), (2, 2)]:
        draw.text((panel_x + offset[0], product_y + offset[1]), product_name, 
                 font=font_product, fill=(0, 0, 0, 90))
    draw.text((panel_x, product_y), product_name, font=font_product, fill=BRAND_COLORS['white'])

    # Tagline with background
    tagline_y = product_y + 75
    bbox_tag = draw.textbbox((0, 0), tagline, font=font_tagline)
    tagline_width = bbox_tag[2] - bbox_tag[0]
    
    # Subtle background bar for tagline
    tag_padding = 12
    draw.rounded_rectangle(
        [panel_x - tag_padding, tagline_y - 6, 
         panel_x + tagline_width + tag_padding, tagline_y + 36],
        radius=6,
        fill=(*BRAND_COLORS['orange'], 80)
    )
    draw.text((panel_x, tagline_y), tagline, font=font_tagline, fill=BRAND_COLORS['white'])

    # Badge
    badge_width = int(panel_width * 0.82)
    badge_height = 155
    badge = create_premium_badge(badge_width, badge_height, nectar_points, "Earn points")
    badge_x = panel_x + (panel_width - badge_width - 80) // 2
    badge_y = int(height * 0.45)
    badge_rgb = badge.convert('RGB')
    output.paste(badge_rgb, (badge_x, badge_y))

    # Flavor text below badge
    font_flavor = get_default_font(24, bold=False)
    flavor_y = badge_y + badge_height + 40
    bbox_flavor = draw.textbbox((0, 0), flavor_text, font=font_flavor)
    draw.text((panel_x + 1, flavor_y + 1), flavor_text, font=font_flavor, fill=(0, 0, 0, 100))
    draw.text((panel_x, flavor_y), flavor_text, font=font_flavor, fill=BRAND_COLORS['orange_light'])

    # Clean brand widget in bottom-right corner (replaces branding bar)
    output = draw_brand_widget(
        output,
        text="Pollen Swarm",
        size_ratio=0.22,  # Slightly smaller for horizontal layout
        bg_color=BRAND_COLORS['purple'],
        accent_color=BRAND_COLORS['orange']
    )

    # Small logo on image side
    small_logo_size = 85
    small_logo = create_pollen_swarm_branding(small_logo_size, small_logo_size, style='logo')
    if image_position == 'left':
        output.paste(small_logo, (25, height - small_logo_size - 25), small_logo)
    else:
        output.paste(small_logo, (width - small_logo_size - 25, 25), small_logo)

    # Apply optional effects
    if add_vignette:
        output = apply_vignette(output, intensity=0.5, radius=0.7)
    if add_noise:
        output = add_noise_overlay(output, intensity=10, grain_size=1)
    if add_pattern:
        output = add_geometric_pattern(output, pattern_type='lines', 
                                      color=BRAND_COLORS['white'], opacity=15, spacing=60)

    return output


def format_creative(
        input_image_path: str,
        layout: str = "vertical",
        product_name: str = "Premium Product",
        tagline: str = "Exceptional Quality",
        nectar_points: int = 15,
        flavor_text: str = "Join thousands of satisfied customers",
        output_path: Optional[str] = None,
        image_position: str = 'left',
        add_vignette: bool = False,
        add_noise: bool = False,
        add_pattern: bool = False
) -> Tuple[str, str]:
    """
    Format image into premium marketing layout with optional visual effects.
    
    Args:
        input_image_path: Path to input image
        layout: Layout format ('vertical', 'square', or 'horizontal')
        product_name: Product name text
        tagline: Tagline text
        nectar_points: Reward points value
        flavor_text: Descriptive flavor text
        output_path: Optional output path (auto-generated if None)
        image_position: Image position for horizontal layout ('left' or 'right')
        add_vignette: Apply soft edge darkening (optional)
        add_noise: Add subtle texture overlay (optional)
        add_pattern: Add geometric pattern overlay (optional)
        
    Returns:
        Tuple of (output_path, metadata_json)
    """
    input_path = Path(input_image_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_image_path}")

    if layout not in ['vertical', 'square', 'horizontal']:
        raise ValueError(f"Invalid layout: {layout}")

    logger.info(f"Formatting: {input_path.name} | Layout: {layout} | Product: {product_name}")

    try:
        image = Image.open(input_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as e:
        raise ValueError(f"Failed to load image: {e}")

    # Format based on layout
    if layout == 'vertical':
        formatted = format_vertical_premium(
            image, product_name, tagline, nectar_points, flavor_text,
            add_vignette, add_noise, add_pattern
        )
    elif layout == 'square':
        formatted = format_square_premium(
            image, product_name, tagline, nectar_points, flavor_text,
            add_vignette, add_noise, add_pattern
        )
    elif layout == 'horizontal':
        formatted = format_horizontal_premium(
            image, product_name, tagline, nectar_points, flavor_text, image_position,
            add_vignette, add_noise, add_pattern
        )

    # Determine output path
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_{layout}.png"
    else:
        output_path = Path(output_path)
        if output_path.suffix.lower() != '.png':
            output_path = output_path.with_suffix('.png')

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save with high quality
    formatted.save(output_path, format='PNG', optimize=False, quality=95)
    logger.info(f"✓ Saved: {output_path}")

    # Create metadata
    metadata = {
        'input_image': str(input_path),
        'output_image': str(output_path),
        'layout': layout,
        'product_name': product_name,
        'tagline': tagline,
        'nectar_points': nectar_points,
        'flavor_text': flavor_text,
        'dimensions': {'width': formatted.width, 'height': formatted.height},
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

    metadata_path = output_path.with_suffix('.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info(f"✓ Metadata: {metadata_path}")

    return str(output_path), str(metadata_path)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Premium image formatter for marketing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python creative_formatter.py -i input.jpg -l vertical \\
    --product "Organic Honey" --tagline "Pure Natural Sweetness" -n 15

  python creative_formatter.py -i input.jpg -l square \\
    --product "Honey" --flavor "Trusted by beekeepers"
  
  python creative_formatter.py -i input.jpg -l horizontal \\
    --product "Premium Honey" --vignette --noise
        """
    )

    parser.add_argument("--input", "-i", type=str, required=True, help="Input image")
    parser.add_argument("--layout", "-l", type=str, default="vertical",
                        choices=['vertical', 'square', 'horizontal'])
    parser.add_argument("--product", type=str, default="Premium Product")
    parser.add_argument("--tagline", type=str, default="Exceptional Quality")
    parser.add_argument("--nectar-points", "-n", type=int, default=15)
    parser.add_argument("--flavor", type=str, default="Join thousands of satisfied customers")
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--position", "-p", type=str, default="left", choices=['left', 'right'])
    
    # Optional visual effects
    parser.add_argument("--vignette", action="store_true", help="Apply soft edge darkening")
    parser.add_argument("--noise", action="store_true", help="Add subtle texture overlay")
    parser.add_argument("--pattern", action="store_true", help="Add geometric pattern overlay")

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        try:
            output_path, metadata_path = format_creative(
                input_image_path=str(input_path),
                layout=args.layout,
                product_name=args.product,
                tagline=args.tagline,
                nectar_points=args.nectar_points,
                flavor_text=args.flavor,
                output_path=args.output,
                image_position=args.position,
                add_vignette=args.vignette,
                add_noise=args.noise,
                add_pattern=args.pattern
            )
            logger.info(f"\n✅ Complete!\nOutput: {output_path}\nMetadata: {metadata_path}")
            return 0
        except Exception as e:
            logger.error(f"✗ Failed: {e}")
            return 1
    else:
        logger.error(f"Input not found: {input_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())