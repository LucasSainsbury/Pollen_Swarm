#!/usr/bin/env python3
"""
Product Image Generation Pipeline
==================================

Complete pipeline for generating themed product marketing images using the
HuggingFace text-to-image API. Generates images across multiple creative themes
for a given product.

Usage:
------
    # Generate all themed images for a product
    python generate_product_images.py \
        --product "dairy butter no salt (120g)" \
        --category "Dairy" \
        --output ./output/butter/
    
    # Generate specific themes only
    python generate_product_images.py \
        --product "organic honey (250g)" \
        --category "Condiments" \
        --themes christmas_festive studio_product \
        --output ./output/honey/
    
    # Use custom settings
    python generate_product_images.py \
        --product "fresh milk (1L)" \
        --category "Dairy" \
        --output ./output/milk/ \
        --seed 42 \
        --aspect 1:1

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
from typing import Dict, List, Optional

from prompt_generator import generate_prompts, get_available_themes, get_theme_description
from creative_ad_generator import CreativeImagePipeline, ASPECT_RATIOS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('product_image_generation.log')
    ]
)
logger = logging.getLogger(__name__)


def sanitize_filename(text: str) -> str:
    """
    Convert text to a safe filename.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized filename-safe string
    """
    # Remove or replace problematic characters
    safe = text.lower()
    safe = safe.replace(' ', '_')
    safe = safe.replace('/', '_')
    safe = safe.replace('\\', '_')
    safe = safe.replace('(', '')
    safe = safe.replace(')', '')
    safe = safe.replace('[', '')
    safe = safe.replace(']', '')
    safe = ''.join(c for c in safe if c.isalnum() or c in ('_', '-', '.'))
    return safe


def generate_product_images(
    product_name: str,
    category: str,
    output_dir: str,
    themes: Optional[List[str]] = None,
    seed: Optional[int] = None,
    aspect_ratio: str = "16:9",
    use_local: bool = False,
    hf_token: Optional[str] = None,
    brightness: float = 1.1,
    contrast: float = 1.15,
    saturation: float = 1.2,
    brand_filter: Optional[str] = None
) -> Dict[str, Dict]:
    """
    Generate themed product marketing images.
    
    Args:
        product_name: Name of the product
        category: Product category
        output_dir: Directory to save generated images
        themes: List of specific themes to generate (None = all themes)
        seed: Random seed for reproducibility
        aspect_ratio: Image aspect ratio
        use_local: Use local model instead of API
        hf_token: HuggingFace API token
        brightness: Brightness adjustment
        contrast: Contrast adjustment
        saturation: Saturation adjustment
        brand_filter: Optional brand color filter
        
    Returns:
        Dictionary mapping theme names to result metadata
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Product: {product_name}")
    logger.info(f"Category: {category}")
    logger.info(f"Output directory: {output_path}")
    
    # Generate prompts for all themes
    all_prompts = generate_prompts(product_name, category)
    
    # Filter to requested themes if specified
    if themes:
        prompts_to_generate = {
            theme: all_prompts[theme] 
            for theme in themes 
            if theme in all_prompts
        }
        if not prompts_to_generate:
            raise ValueError(f"None of the requested themes are valid. Available: {list(all_prompts.keys())}")
    else:
        prompts_to_generate = all_prompts
    
    logger.info(f"Generating {len(prompts_to_generate)} themed images")
    
    # Initialize the image generation pipeline
    try:
        pipeline = CreativeImagePipeline(
            use_local=use_local,
            hf_token=hf_token,
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            aspect_ratio=aspect_ratio,
            brand_filter=brand_filter
        )
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise
    
    # Generate images for each theme
    results = {}
    successful = 0
    failed = 0
    
    for i, (theme_name, prompt) in enumerate(prompts_to_generate.items(), 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"Generating image {i}/{len(prompts_to_generate)}")
        logger.info(f"Theme: {get_theme_description(theme_name)} ({theme_name})")
        logger.info(f"{'='*80}\n")
        
        # Create filename
        product_safe = sanitize_filename(product_name)
        filename = f"{product_safe}_{theme_name}.jpg"
        output_file = output_path / filename
        
        try:
            # Generate the image
            image_path, metadata_path = pipeline.run(
                prompt=prompt,
                output_path=output_file,
                seed=seed
            )
            
            # Store theme information in metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata['product'] = {
                'name': product_name,
                'category': category,
            }
            metadata['theme'] = {
                'name': theme_name,
                'description': get_theme_description(theme_name),
            }
            
            # Save updated metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            results[theme_name] = {
                'status': 'success',
                'image_path': str(image_path),
                'metadata_path': str(metadata_path),
                'metadata': metadata
            }
            
            successful += 1
            logger.info(f"✓ Success: {image_path}\n")
            
        except Exception as e:
            logger.error(f"✗ Failed to generate {theme_name}: {e}\n")
            results[theme_name] = {
                'status': 'failed',
                'error': str(e)
            }
            failed += 1
            continue
    
    # Save summary
    summary = {
        'product_name': product_name,
        'category': category,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_themes': len(prompts_to_generate),
        'successful': successful,
        'failed': failed,
        'settings': {
            'aspect_ratio': aspect_ratio,
            'seed': seed,
            'brightness': brightness,
            'contrast': contrast,
            'saturation': saturation,
            'brand_filter': brand_filter,
            'use_local': use_local,
        },
        'results': results
    }
    
    summary_path = output_path / f"{sanitize_filename(product_name)}_generation_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Generation Complete!")
    logger.info(f"{'='*80}")
    logger.info(f"Total: {len(prompts_to_generate)}")
    logger.info(f"✓ Successful: {successful}")
    logger.info(f"✗ Failed: {failed}")
    logger.info(f"📁 Output directory: {output_path}")
    logger.info(f"📝 Summary: {summary_path}")
    
    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate themed product marketing images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all themes for a product
  python generate_product_images.py \\
    --product "dairy butter no salt (120g)" \\
    --category "Dairy" \\
    --output ./output/butter/
  
  # Generate specific themes only
  python generate_product_images.py \\
    --product "organic honey (250g)" \\
    --category "Condiments" \\
    --themes christmas_festive studio_product supermarket_shelf \\
    --output ./output/honey/
  
  # With custom settings
  python generate_product_images.py \\
    --product "fresh milk (1L)" \\
    --category "Dairy" \\
    --output ./output/milk/ \\
    --seed 42 \\
    --aspect 1:1 \\
    --filter fresh_green
        """
    )
    
    parser.add_argument(
        "--product", "-p",
        type=str,
        required=True,
        help="Product name (e.g., 'dairy butter no salt (120g)')"
    )
    
    parser.add_argument(
        "--category", "-c",
        type=str,
        required=True,
        help="Product category (e.g., 'Dairy')"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Output directory for generated images"
    )
    
    parser.add_argument(
        "--themes", "-t",
        type=str,
        nargs='+',
        default=None,
        help=f"Specific themes to generate (default: all). Available: {', '.join(get_available_themes())}"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility (default: random)"
    )
    
    parser.add_argument(
        "--aspect", "-a",
        type=str,
        default="16:9",
        choices=list(ASPECT_RATIOS.keys()),
        help="Target aspect ratio (default: 16:9)"
    )
    
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local model instead of API (slower)"
    )
    
    parser.add_argument(
        "--hf-token",
        type=str,
        default=os.getenv("HF_TOKEN"),
        help="HuggingFace API token (or set HF_TOKEN env var)"
    )
    
    parser.add_argument(
        "--brightness",
        type=float,
        default=1.1,
        help="Brightness adjustment (default: 1.1)"
    )
    
    parser.add_argument(
        "--contrast",
        type=float,
        default=1.15,
        help="Contrast adjustment (default: 1.15)"
    )
    
    parser.add_argument(
        "--saturation",
        type=float,
        default=1.2,
        help="Saturation adjustment (default: 1.2)"
    )
    
    parser.add_argument(
        "--filter", "-f",
        type=str,
        default=None,
        help="Brand color filter to apply"
    )
    
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List all available themes and exit"
    )
    
    args = parser.parse_args()
    
    # Handle --list-themes
    if args.list_themes:
        print("\nAvailable Themes:")
        print("=" * 80)
        for theme in get_available_themes():
            desc = get_theme_description(theme)
            print(f"  {theme:25s} - {desc}")
        print()
        return 0
    
    # Generate images
    try:
        results = generate_product_images(
            product_name=args.product,
            category=args.category,
            output_dir=args.output,
            themes=args.themes,
            seed=args.seed,
            aspect_ratio=args.aspect,
            use_local=args.local,
            hf_token=args.hf_token,
            brightness=args.brightness,
            contrast=args.contrast,
            saturation=args.saturation,
            brand_filter=args.filter
        )
        
        # Exit with error if any generation failed
        failed_count = sum(1 for r in results.values() if r['status'] == 'failed')
        if failed_count > 0:
            logger.warning(f"{failed_count} theme(s) failed to generate")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
