#!/usr/bin/env python3
"""
Enterprise Creative Image Formatter for Marketing Layouts
===========================================================

Professional-grade formatter with cohesive, polished design:
- Sophisticated gradient layering and color transitions
- Seamless transparency fade zones between sections
- Premium Pollen Swarm branding integration
- Coherent overlay systems tying all elements together
- Professional typography with visual hierarchy
- Refined spacing and composition

Features:
- Multi-layer gradient backgrounds with smooth transitions
- Transparency fade overlays for seamless transitions
- Integrated brand identity throughout
- Overlapping design elements for cohesion
- Premium accent elements and decorative details
- Professional badge and branding placement
- High-end visual polish and refinement
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
        except:
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
    """Create smooth gradient with non-linear progression."""
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)

    if vertical:
        for y in range(height):
            ratio = (y / height) ** power
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        for x in range(width):
            ratio = (x / width) ** power
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))

    return gradient


def create_transparency_fade(width: int, height: int, direction: str = 'down') -> Image.Image:
    """Create gradient transparency overlay for smooth transitions."""
    fade = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    pixels = fade.load()

    if direction == 'down':
        for y in range(height):
            alpha = int((y / height) * 255)
            for x in range(width):
                pixels[x, y] = (0, 0, 0, alpha)
    elif direction == 'up':
        for y in range(height):
            alpha = int((1 - y / height) * 255)
            for x in range(width):
                pixels[x, y] = (0, 0, 0, alpha)

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


def create_pollen_swarm_branding(width: int, height: int) -> Image.Image:
    """Create Pollen Swarm branding element."""
    branding = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(branding)

    # Draw hexagon/flower shape
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 3

    # Hexagon points
    angles = [i * 60 for i in range(6)]
    points = []
    for angle in angles:
        rad = math.radians(angle)
        x = center_x + radius * math.cos(rad)
        y = center_y + radius * math.sin(rad)
        points.append((x, y))

    # Draw hexagon with gradient effect
    draw.polygon(points, fill=(*BRAND_COLORS['orange'], 200), outline=(*BRAND_COLORS['white'], 200))

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
    text_x = center_x - text_width // 2
    text_y = center_y - (bbox[3] - bbox[1]) // 2
    draw.text((text_x, text_y), text, font=font_brand, fill=BRAND_COLORS['orange'])

    return branding


def format_vertical_premium(
        image: Image.Image,
        product_name: str = "Product",
        tagline: str = "Premium Quality",
        nectar_points: int = 10,
        flavor_text: str = "Trusted quality"
) -> Image.Image:
    """Premium vertical banner with cohesive design."""
    width, height = LAYOUT_SIZES['vertical']
    output = Image.new('RGB', (width, height), color=BRAND_COLORS['white'])

    # Image section
    img_height = int(height * 0.56)
    overlap_zone = int(height * 0.08)  # Transition zone
    text_start = img_height - overlap_zone

    processed_img = resize_and_crop(image, width, img_height, crop_position='center')
    output.paste(processed_img, (0, 0))

    # Fade overlay at bottom of image for smooth transition
    fade = create_transparency_fade(width, overlap_zone * 3, direction='down')
    fade_rgb = Image.new('RGB', (width, overlap_zone * 3), color=BRAND_COLORS['purple'])
    fade_with_trans = Image.new('RGBA', (width, overlap_zone * 3))
    fade_with_trans.paste(fade_rgb, (0, 0))
    fade_with_trans.putalpha(fade.split()[3])
    output.paste(fade_with_trans, (0, text_start), fade_with_trans)

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

    # Decorative stripe with accent
    stripe_height = 8
    stripe_y = text_start + overlap_zone
    draw.rectangle([0, stripe_y, width, stripe_y + stripe_height], fill=BRAND_COLORS['orange'])
    draw.rectangle([0, stripe_y + stripe_height, width, stripe_y + stripe_height + 3],
                   fill=BRAND_COLORS['orange_light'])

    # Product name
    font_product = get_default_font(68, bold=True)
    bbox = draw.textbbox((0, 0), product_name, font=font_product)
    product_width = bbox[2] - bbox[0]
    product_x = (width - product_width) // 2
    product_y = text_start + overlap_zone + 50

    # Glow effect behind text
    draw.text((product_x + 3, product_y + 3), product_name, font=font_product, fill=(0, 0, 0, 100))
    draw.text((product_x, product_y), product_name, font=font_product, fill=BRAND_COLORS['white'])

    # Tagline
    font_tagline = get_default_font(32, bold=False)
    bbox_tag = draw.textbbox((0, 0), tagline, font=font_tagline)
    tagline_width = bbox_tag[2] - bbox_tag[0]
    tagline_x = (width - tagline_width) // 2
    tagline_y = product_y + 80
    draw.text((tagline_x, tagline_y), tagline, font=font_tagline, fill=BRAND_COLORS['orange_light'])

    # Badge - overlapping into image
    badge_width = int(width * 0.75)
    badge_height = 170
    badge = create_premium_badge(badge_width, badge_height, nectar_points, "Earn rewards")
    badge_x = (width - badge_width) // 2
    badge_y = text_start - badge_height // 2

    badge_rgb = badge.convert('RGB')
    output.paste(badge_rgb, (badge_x, badge_y))

    # Pollen Swarm branding - top right
    branding_size = 100
    branding = create_pollen_swarm_branding(branding_size, branding_size)
    branding_rgb = branding.convert('RGB')
    output.paste(branding_rgb, (width - branding_size - 30, 30), branding)

    # Flavor text
    font_flavor = get_default_font(24, bold=False)
    bbox_flavor = draw.textbbox((0, 0), flavor_text, font=font_flavor)
    flavor_width = bbox_flavor[2] - bbox_flavor[0]
    flavor_x = (width - flavor_width) // 2
    flavor_y = height - 65
    draw.text((flavor_x, flavor_y), flavor_text, font=font_flavor, fill=BRAND_COLORS['orange_light'])

    # "Pollen Swarm" text at bottom
    font_brand = get_default_font(22, bold=True)
    draw.text((35, height - 58), "✓ Pollen Swarm", font=font_brand, fill=BRAND_COLORS['white'])

    return output


def format_square_premium(
        image: Image.Image,
        product_name: str = "Product",
        tagline: str = "Premium Quality",
        nectar_points: int = 10,
        flavor_text: str = "Trusted quality"
) -> Image.Image:
    """Premium square format with cohesive design."""
    width, height = LAYOUT_SIZES['square']
    output = Image.new('RGB', (width, height), color=BRAND_COLORS['white'])

    # Image section
    img_height = int(height * 0.68)
    overlap_zone = int(height * 0.06)
    text_start = img_height - overlap_zone

    processed_img = resize_and_crop(image, width, img_height)
    output.paste(processed_img, (0, 0))

    # Fade overlay transition
    fade = create_transparency_fade(width, overlap_zone * 2.5, direction='down')
    fade_rgb = Image.new('RGB', (width, int(overlap_zone * 2.5)), color=BRAND_COLORS['orange'])
    fade_with_trans = Image.new('RGBA', (width, int(overlap_zone * 2.5)))
    fade_with_trans.paste(fade_rgb, (0, 0))
    fade_with_trans.putalpha(fade.split()[3])
    output.paste(fade_with_trans, (0, text_start), fade_with_trans)

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
    output.paste(gradient_bg, (0, text_start + int(overlap_zone * 1.5)))

    draw = ImageDraw.Draw(output)

    # Decorative stripe
    stripe_y = text_start + int(overlap_zone * 1.5)
    draw.rectangle([0, stripe_y, width, stripe_y + 10], fill=BRAND_COLORS['purple'])
    draw.rectangle([0, stripe_y + 10, width, stripe_y + 12], fill=BRAND_COLORS['purple_light'])

    # Product name
    font_product = get_default_font(58, bold=True)
    bbox = draw.textbbox((0, 0), product_name, font=font_product)
    product_width = bbox[2] - bbox[0]
    product_x = (width - product_width) // 2
    product_y = stripe_y + 35

    draw.text((product_x + 2, product_y + 2), product_name, font=font_product, fill=(0, 0, 0, 80))
    draw.text((product_x, product_y), product_name, font=font_product, fill=BRAND_COLORS['purple_dark'])

    # Badge
    badge_width = int(width * 0.72)
    badge_height = 140
    badge = create_premium_badge(badge_width, badge_height, nectar_points, "Earn rewards")
    badge_x = (width - badge_width) // 2
    badge_y = height - badge_height - 30

    badge_rgb = badge.convert('RGB')
    output.paste(badge_rgb, (badge_x, badge_y))

    # Pollen Swarm branding - corner
    branding_size = 85
    branding = create_pollen_swarm_branding(branding_size, branding_size)
    branding_rgb = branding.convert('RGB')
    output.paste(branding_rgb, (width - branding_size - 25, 25), branding)

    return output


def format_horizontal_premium(
        image: Image.Image,
        product_name: str = "Product",
        tagline: str = "Premium Quality",
        nectar_points: int = 10,
        flavor_text: str = "Trusted quality",
        image_position: str = 'left'
) -> Image.Image:
    """Premium horizontal layout with cohesive composition."""
    width, height = LAYOUT_SIZES['horizontal']
    output = Image.new('RGB', (width, height), color=BRAND_COLORS['white'])

    img_width = int(width * 0.55)
    panel_width = width - img_width

    # Process image
    processed_img = resize_and_crop(image, img_width, height)

    # Create gradient panel
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

        # Fade transition between image and panel
        fade_width = 80
        fade = create_transparency_fade(fade_width, height, direction='up')
        fade_rgb = Image.new('RGB', (fade_width, height), color=BRAND_COLORS['purple'])
        fade_with_trans = Image.new('RGBA', (fade_width, height))
        fade_with_trans.paste(fade_rgb, (0, 0))
        fade_with_trans.putalpha(fade.split()[3])
        output.paste(fade_with_trans, (img_width - fade_width, 0), fade_with_trans)

        panel_x = img_width + 50
    else:
        output.paste(gradient_panel, (0, 0))
        output.paste(processed_img, (panel_width, 0))

        fade_width = 80
        fade = create_transparency_fade(fade_width, height, direction='down')
        fade_rgb = Image.new('RGB', (fade_width, height), color=BRAND_COLORS['purple'])
        fade_with_trans = Image.new('RGBA', (fade_width, height))
        fade_with_trans.paste(fade_rgb, (0, 0))
        fade_with_trans.putalpha(fade.split()[3])
        output.paste(fade_with_trans, (panel_width, 0), fade_with_trans)

        panel_x = 50

    draw = ImageDraw.Draw(output)

    # Vertical accent divider
    if image_position == 'left':
        draw.rectangle([img_width, 0, img_width + 6, height], fill=BRAND_COLORS['orange'])
        draw.rectangle([img_width + 6, 0, img_width + 8, height], fill=BRAND_COLORS['orange_light'])
    else:
        draw.rectangle([panel_width - 6, 0, panel_width, height], fill=BRAND_COLORS['orange'])
        draw.rectangle([panel_width - 8, 0, panel_width - 6, height], fill=BRAND_COLORS['orange_light'])

    # Typography
    font_product = get_default_font(54, bold=True)
    font_tagline = get_default_font(28, bold=False)
    font_flavor = get_default_font(22, bold=False)

    # Product name
    product_y = int(height * 0.15)
    bbox = draw.textbbox((0, 0), product_name, font=font_product)
    draw.text((panel_x + 2, product_y + 2), product_name, font=font_product, fill=(0, 0, 0, 70))
    draw.text((panel_x, product_y), product_name, font=font_product, fill=BRAND_COLORS['white'])

    # Tagline
    tagline_y = product_y + 70
    draw.text((panel_x, tagline_y), tagline, font=font_tagline, fill=BRAND_COLORS['orange_light'])

    # Badge
    badge_width = int(panel_width * 0.8)
    badge_height = 145
    badge = create_premium_badge(badge_width, badge_height, nectar_points, "Earn points")
    badge_x = panel_x + (panel_width - badge_width - 70) // 2
    badge_y = int(height * 0.48)
    badge_rgb = badge.convert('RGB')
    output.paste(badge_rgb, (badge_x, badge_y))

    # Flavor text
    flavor_y = height - 55
    draw.text((panel_x, flavor_y), flavor_text, font=font_flavor, fill=BRAND_COLORS['white'])

    # Pollen Swarm branding
    branding_size = 95
    branding = create_pollen_swarm_branding(branding_size, branding_size)
    branding_rgb = branding.convert('RGB')
    if image_position == 'left':
        output.paste(branding_rgb, (panel_x + panel_width - branding_size - 20, height - branding_size - 20), branding)
    else:
        output.paste(branding_rgb, (20, height - branding_size - 20), branding)

    return output


def format_creative(
        input_image_path: str,
        layout: str = "vertical",
        product_name: str = "Premium Product",
        tagline: str = "Exceptional Quality",
        nectar_points: int = 15,
        flavor_text: str = "Join thousands of satisfied customers",
        output_path: Optional[str] = None,
        image_position: str = 'left'
) -> Tuple[str, str]:
    """Format image into premium marketing layout."""
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
        formatted = format_vertical_premium(image, product_name, tagline, nectar_points, flavor_text)
    elif layout == 'square':
        formatted = format_square_premium(image, product_name, tagline, nectar_points, flavor_text)
    elif layout == 'horizontal':
        formatted = format_horizontal_premium(image, product_name, tagline, nectar_points, flavor_text, image_position)

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
  python creative_formatter_pro.py -i input.jpg -l vertical \\
    --product "Organic Honey" --tagline "Pure Natural Sweetness" -n 15

  python creative_formatter_pro.py -i input.jpg -l square \\
    --product "Honey" --flavor "Trusted by beekeepers"
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
                image_position=args.position
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