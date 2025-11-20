#!/usr/bin/env python3
"""
Complete Workflow Demo
======================

This script demonstrates the complete end-to-end workflow:
1. Generate themed prompts for a product
2. (Simulated) Generate images for each theme
3. Format images into marketing layouts

For demonstration, we'll create sample images instead of calling the API.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from prompt_generator import generate_prompts, get_theme_description
from creative_formatter import format_creative

def create_sample_image(theme_name: str, product_name: str, width: int = 800, height: int = 600) -> Image.Image:
    """Create a sample image for demonstration."""
    # Create a colorful sample image
    colors = {
        'christmas_festive': '#FF0000',
        'studio_product': '#FFFFFF',
        'supermarket_shelf': '#FFD700',
        'back_to_school': '#4169E1',
        'cooked_prepared': '#FF8C00',
        'summer_outdoor': '#87CEEB',
        'healthy_lifestyle': '#32CD32',
        'family_home': '#DEB887',
        'premium_luxury': '#9370DB',
        'easter_spring': '#FFB6C1',
    }
    
    # Get base color for theme
    base_color = colors.get(theme_name, '#808080')
    
    # Create image with gradient
    img = Image.new('RGB', (width, height), color=base_color)
    draw = ImageDraw.Draw(img)
    
    # Add theme and product text
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw centered text
    theme_desc = get_theme_description(theme_name)
    
    # Calculate text bounding boxes
    bbox1 = draw.textbbox((0, 0), theme_desc, font=font_large)
    bbox2 = draw.textbbox((0, 0), product_name, font=font_small)
    
    text1_width = bbox1[2] - bbox1[0]
    text2_width = bbox2[2] - bbox2[0]
    
    # Draw theme name
    x1 = (width - text1_width) // 2
    y1 = height // 2 - 40
    draw.text((x1, y1), theme_desc, fill='white', font=font_large)
    
    # Draw product name
    x2 = (width - text2_width) // 2
    y2 = height // 2 + 20
    draw.text((x2, y2), product_name, fill='white', font=font_small)
    
    return img


def demo_workflow():
    """Demonstrate the complete workflow."""
    print("="*80)
    print("Pollen Swarm - Complete Workflow Demo")
    print("="*80)
    print()
    
    # Step 1: Define product
    product_name = "organic honey (250g)"
    category = "Condiments"
    
    print(f"Product: {product_name}")
    print(f"Category: {category}")
    print()
    
    # Step 2: Generate prompts
    print("Step 1: Generating themed prompts...")
    prompts = generate_prompts(product_name, category)
    print(f"✓ Generated {len(prompts)} themed prompts")
    print()
    
    # Show first 3 prompts as examples
    print("Sample prompts:")
    for i, (theme, prompt) in enumerate(list(prompts.items())[:3], 1):
        desc = get_theme_description(theme)
        print(f"\n{i}. {desc}")
        print(f"   {prompt[:100]}...")
    print()
    
    # Step 3: Create sample images (simulating API generation)
    print("Step 2: Creating sample images (simulating API generation)...")
    output_dir = Path("/tmp/demo_workflow")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sample_images = []
    for i, (theme_name, prompt) in enumerate(list(prompts.items())[:3], 1):
        img = create_sample_image(theme_name, product_name)
        img_path = output_dir / f"honey_{theme_name}.jpg"
        img.save(img_path, quality=95)
        sample_images.append((theme_name, img_path))
        print(f"  ✓ Created: {img_path.name}")
    print()
    
    # Step 4: Format images into marketing layouts
    print("Step 3: Formatting images into marketing layouts...")
    layouts = ['vertical', 'square', 'horizontal']
    
    for theme_name, img_path in sample_images[:1]:  # Just format the first one
        print(f"\n  Processing: {theme_name}")
        for layout in layouts:
            output_path, metadata_path = format_creative(
                input_image_path=str(img_path),
                layout=layout,
                nectar_points=15,
                image_position='left'
            )
            print(f"    ✓ {layout.capitalize()} layout: {Path(output_path).name}")
    
    print()
    print("="*80)
    print("Demo Complete!")
    print("="*80)
    print(f"\nOutput directory: {output_dir}")
    print("\nFiles created:")
    for file in sorted(output_dir.glob("*")):
        print(f"  - {file.name}")
    print()
    print("Next steps:")
    print("  1. Review the generated files in:", output_dir)
    print("  2. Try with real API: python generate_product_images.py --product '...' --category '...'")
    print("  3. Format your own images: python creative_formatter.py -i image.jpg -l vertical")
    print()


if __name__ == "__main__":
    try:
        demo_workflow()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
