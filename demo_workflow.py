#!/usr/bin/env python3
"""
Complete Professional Workflow Demo
====================================

Enhanced end-to-end workflow demonstrating:
1. Direct function imports from generate_product_images.py
2. Professional marketing layout formatting with real generated images
3. Multiple layout variations with custom copy
4. Direct API integration for AI image generation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generate_product_images import generate_product_images
from creative_formatter import format_creative

# Demo product configurations
DEMO_PRODUCTS = [
    {
        'product': 'organic honey (250g)',
        'category': 'Condiments',
        'themes': ['christmas_festive', 'studio_product', 'supermarket_shelf'],
        'name': 'Organic Honey',
        'tagline': 'Pure Natural Sweetness',
        'flavor_vertical': 'Ethically sourced from local beekeepers',
        'flavor_square': 'Nature\'s golden treasure',
        'flavor_horizontal': '100% pure, never heated',
        'points': 25,
    },
]

'''
    {
        'product': 'premium butter no salt (120g)',
        'category': 'Dairy',
        'themes': ['studio_product', 'family_home', 'healthy_lifestyle'],
        'name': 'Premium Butter',
        'tagline': 'Crafted Perfection',
        'flavor_vertical': 'Rich, creamy, and sustainably made',
        'flavor_square': 'Taste the difference',
        'flavor_horizontal': 'From grass-fed dairy',
        'points': 20,
    },
    '''

# API Configuration
HF_TOKEN = "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"
SEED = 1
OUTPUT_BASE = Path("./demo_workflow_output")


def format_generated_images(
        images_dir: Path,
        product_data: dict,
        output_dir: Path
) -> list:
    """
    Format all generated images into professional marketing layouts.

    Args:
        images_dir: Directory containing generated images
        product_data: Product metadata (name, tagline, flavor texts, etc.)
        output_dir: Output directory for formatted images

    Returns:
        List of formatted image paths
    """
    formatted_images = []

    # Find all generated JPG images
    generated_images = list(images_dir.glob("*.jpg"))

    if not generated_images:
        print(f"  ⚠️  No generated images found in {images_dir}")
        return formatted_images

    print(f"  Found {len(generated_images)} generated images")
    print(f"\n  Formatting into professional layouts:\n")

    # Use first image for multi-format demonstration
    base_image = generated_images[0]
    theme_name = base_image.stem.split('_', 1)[1] if '_' in base_image.stem else 'base'

    # Layout configurations
    layouts_config = [
        {
            'layout': 'vertical',
            'flavor': product_data['flavor_vertical'],
            'description': 'Portrait (9:16)',
        },
        {
            'layout': 'square',
            'flavor': product_data['flavor_square'],
            'description': 'Square (1:1)',
        },
        {
            'layout': 'horizontal',
            'flavor': product_data['flavor_horizontal'],
            'description': 'Landscape (16:9)',
        }
    ]

    print(f"  Base image: {base_image.stem}\n")

    for config in layouts_config:
        try:
            output_path, metadata_path = format_creative(
                input_image_path=str(base_image),
                layout=config['layout'],
                product_name=product_data['name'],
                tagline=product_data['tagline'],
                nectar_points=product_data['points'],
                flavor_text=config['flavor'],
                output_path=str(output_dir / f"{base_image.stem}_{config['layout']}_formatted.png"),
                image_position='left' if config['layout'] == 'horizontal' else 'center'
            )

            formatted_images.append(output_path)
            print(f"    ✓ {config['layout'].upper():12} → {Path(output_path).name}")

        except Exception as e:
            print(f"    ❌ {config['layout'].upper():12} → Failed: {e}")

    return formatted_images


def demo_complete_workflow():
    """Run complete professional workflow with real AI image generation."""
    print("\n" + "=" * 100)
    print("🎨 POLLEN SWARM - PROFESSIONAL WORKFLOW WITH AI GENERATION 🎨".center(100))
    print("=" * 100 + "\n")

    output_base = OUTPUT_BASE
    output_base.mkdir(parents=True, exist_ok=True)

    all_results = []

    # Process each product
    for idx, product_data in enumerate(DEMO_PRODUCTS, 1):
        print(f"\n{'─' * 100}")
        print(f"📦 PRODUCT {idx}/{len(DEMO_PRODUCTS)}: {product_data['name'].upper()}")
        print(f"{'─' * 100}\n")

        product = product_data['product']
        category = product_data['category']
        themes = product_data['themes']

        # Create product-specific directory
        product_key = product.split('(')[0].strip().lower().replace(' ', '_')
        product_output = output_base / product_key
        product_output.mkdir(exist_ok=True)

        generation_output = product_output / "generated"
        generation_output.mkdir(exist_ok=True)

        # Step 1 & 2: Generate images using direct function import
        print(f"Step 1️⃣  Generating themed product images\n")
        print(f"   Product: {product}")
        print(f"   Category: {category}")
        print(f"   Themes: {', '.join(themes)}")
        print(f"   Seed: {SEED}\n")

        try:
            results = generate_product_images(
                product_name=product,
                category=category,
                output_dir=str(generation_output),
                themes=themes,
                seed=SEED,
                aspect_ratio="16:9",
                hf_token=HF_TOKEN,
                brightness=1.1,
                contrast=1.15,
                saturation=1.2
            )

            successful = sum(1 for r in results.values() if r['status'] == 'success')
            failed = sum(1 for r in results.values() if r['status'] == 'failed')

            print(f"\n   ✓ Generation complete")
            print(f"     • Successful: {successful}")
            print(f"     • Failed: {failed}\n")

        except Exception as e:
            print(f"   ❌ Image generation failed: {e}")
            print(f"   ⏭️  Skipping to next product\n")
            continue

        # Step 2: Format into professional layouts
        print(f"Step 2️⃣  Formatting into professional marketing layouts\n")

        formatted_output = product_output / "formatted"
        formatted_output.mkdir(exist_ok=True)

        formatted_images = format_generated_images(
            images_dir=generation_output,
            product_data=product_data,
            output_dir=formatted_output
        )

        # Step 3: Summary
        print(f"\n  📊 Results for {product_data['name']}:")
        print(f"     • Generated images: {generation_output}")
        print(f"     • Formatted layouts: {formatted_output}")
        print(f"     • Total formatted outputs: {len(formatted_images)}")

        all_results.append({
            'product': product_data['name'],
            'category': category,
            'generation_dir': str(generation_output),
            'formatted_dir': str(formatted_output),
            'formatted_count': len(formatted_images),
            'generated_count': successful,
        })

    # Final Summary
    print(f"\n{'=' * 100}")
    print("✅ WORKFLOW COMPLETE - ALL PRODUCTS PROCESSED".center(100))
    print(f"{'=' * 100}\n")

    print(f"📁 Main Output: {output_base}\n")

    print("📊 Summary of Generated Outputs:")
    total_generated = 0
    total_formatted = 0

    for result in all_results:
        print(f"\n   {result['product']}")
        print(f"   ├─ Category: {result['category']}")
        print(f"   ├─ Generated: {result['generated_count']} images")
        print(f"   ├─ Formatted: {result['formatted_count']} layouts")
        print(f"   └─ Path: {Path(result['formatted_dir']).parent.name}/")
        total_generated += result['generated_count']
        total_formatted += result['formatted_count']

    print(f"\n   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   TOTALS: {total_generated} images → {total_formatted} layouts")

    print("\n📋 Workflow Pipeline:")
    print("   1. ✓ Prompt generation (themed creative briefs)")
    print("   2. ✓ AI image generation (HuggingFace API)")
    print("   3. ✓ Professional post-processing (brightness, contrast, saturation)")
    print("   4. ✓ Multi-format layout generation (3 variants per product)")
    print("   5. ✓ Metadata preservation (JSON tracking)")

    print("\n🎨 Professional Design Features:")
    print("   ✓ Dynamic gradient overlays")
    print("   ✓ Sophisticated typography hierarchy")
    print("   ✓ Overlapping image/panel composition")
    print("   ✓ Context-aware flavor text")
    print("   ✓ Premium nectar points badges")
    print("   ✓ Multi-format responsive layouts (9:16, 1:1, 16:9)")
    print("   ✓ Brand-consistent purple & orange color scheme")

    print("\n💡 Key Parameters Used:")
    print(f"   • HF Token: {'*' * len(HF_TOKEN[:-10]) + HF_TOKEN[-10:]}")
    print(f"   • Seed: {SEED}")
    print(f"   • Aspect Ratio: 16:9")
    print(f"   • Brightness: 1.1")
    print(f"   • Contrast: 1.15")
    print(f"   • Saturation: 1.2")

    print("\n🚀 Next Steps:")
    print("   1. Review generated files:")
    print(f"      open {output_base}")
    print("   2. Customize products in DEMO_PRODUCTS dict")
    print("   3. Adjust generation parameters as needed")
    print("   4. Integrate into your batch processing pipeline")

    print("\n" + "=" * 100 + "\n")


if __name__ == "__main__":
    try:
        demo_complete_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Workflow error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)