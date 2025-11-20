#!/usr/bin/env python3
"""
Themed Prompt Generator for Product Marketing Images
=====================================================

A module for generating creative themed prompts for product marketing campaigns.
Automatically formats prompts across multiple creative themes incorporating product
name and category.

Usage:
------
    from prompt_generator import generate_prompts
    
    prompts = generate_prompts("dairy butter no salt (120g)", "Dairy")
    for theme, prompt in prompts.items():
        print(f"{theme}: {prompt}")

Author: Pollen Swarm Creative Pipeline
License: MIT
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


# Creative theme templates
THEME_TEMPLATES = {
    "christmas_festive": (
        "festive Christmas holiday scene featuring {product_name} from the {category} "
        "category, surrounded by warm twinkling lights, red and gold decorations, "
        "pine branches with snow, gift ribbons, cozy winter atmosphere, professional "
        "advertising photography, high quality, photorealistic"
    ),
    "studio_product": (
        "clean professional studio product shot of {product_name} from the {category} "
        "category, pristine white background, soft directional lighting, minimal shadows, "
        "commercial photography style, sharp focus, high resolution, advertising ready"
    ),
    "supermarket_shelf": (
        "{product_name} from the {category} category displayed on a vibrant supermarket "
        "shelf, surrounded by complementary products, bright store lighting, fresh and "
        "appealing arrangement, in-store retail photography, realistic shopping environment, "
        "professional quality"
    ),
    "back_to_school": (
        "energetic back-to-school theme featuring {product_name} from the {category} "
        "category, colorful notebooks and school supplies in background, bright cheerful "
        "colors, optimistic mood, young and fresh aesthetic, educational setting, "
        "professional advertising photography"
    ),
    "cooked_prepared": (
        "{product_name} from the {category} category beautifully prepared and plated, "
        "gourmet presentation on elegant dinnerware, garnished and styled by professional "
        "food stylist, natural window lighting, appetizing and delicious appearance, "
        "culinary magazine quality, photorealistic"
    ),
    "summer_outdoor": (
        "bright summer outdoor scene featuring {product_name} from the {category} category, "
        "sunshine and blue sky, fresh green grass, picnic or BBQ setting, vibrant seasonal "
        "colors, warm natural lighting, lifestyle photography, vacation mood, professional "
        "advertising quality"
    ),
    "healthy_lifestyle": (
        "{product_name} from the {category} category in a healthy active lifestyle context, "
        "fitness and wellness theme, fresh organic aesthetic, morning light, clean eating "
        "concept, natural and wholesome presentation, motivational energy, professional "
        "health magazine photography"
    ),
    "family_home": (
        "warm family home kitchen scene with {product_name} from the {category} category, "
        "cozy domestic setting, wooden table, natural light through window, comfortable "
        "family atmosphere, everyday life moment, authentic and relatable, professional "
        "lifestyle photography"
    ),
    "premium_luxury": (
        "luxury premium presentation of {product_name} from the {category} category, "
        "elegant sophisticated setting, gold and marble accents, soft dramatic lighting, "
        "high-end brand aesthetic, exclusive and refined, boutique quality, professional "
        "luxury advertising photography"
    ),
    "easter_spring": (
        "cheerful Easter spring scene featuring {product_name} from the {category} category, "
        "pastel colors, fresh flowers, spring decorations, eggs and rabbits, renewal and "
        "growth theme, bright natural light, seasonal celebration atmosphere, professional "
        "holiday advertising photography"
    ),
}


def generate_prompts(product_name: str, category: str) -> Dict[str, str]:
    """
    Generate themed advertising prompts for a product.
    
    Creates professional, brand-safe prompts across multiple creative themes,
    each incorporating the product name and category naturally within realistic
    contexts suitable for advertising campaigns.
    
    Args:
        product_name: The name of the product (e.g., "dairy butter no salt (120g)")
        category: The product category (e.g., "Dairy")
        
    Returns:
        Dictionary mapping theme names to formatted prompts
        
    Example:
        >>> prompts = generate_prompts("organic honey (250g)", "Condiments")
        >>> print(prompts["christmas_festive"])
        'festive Christmas holiday scene featuring organic honey (250g)...'
    """
    if not product_name or not product_name.strip():
        raise ValueError("product_name cannot be empty")
    
    if not category or not category.strip():
        raise ValueError("category cannot be empty")
    
    logger.info(f"Generating themed prompts for: {product_name} ({category})")
    
    prompts = {}
    for theme_name, template in THEME_TEMPLATES.items():
        prompts[theme_name] = template.format(
            product_name=product_name,
            category=category
        )
        logger.debug(f"Generated {theme_name} prompt")
    
    logger.info(f"Successfully generated {len(prompts)} themed prompts")
    return prompts


def get_available_themes() -> list:
    """
    Get list of available theme names.
    
    Returns:
        List of theme identifier strings
    """
    return list(THEME_TEMPLATES.keys())


def get_theme_description(theme_name: str) -> str:
    """
    Get a human-readable description of a theme.
    
    Args:
        theme_name: Theme identifier
        
    Returns:
        Human-readable theme description
        
    Raises:
        KeyError: If theme_name is not recognized
    """
    descriptions = {
        "christmas_festive": "Christmas / Holiday / Festive",
        "studio_product": "Clean Studio Product Shot",
        "supermarket_shelf": "Supermarket / In-Store Shelf",
        "back_to_school": "Back to School",
        "cooked_prepared": "Cooked / Prepared / Plated",
        "summer_outdoor": "Summer Outdoor / Seasonal",
        "healthy_lifestyle": "Healthy Lifestyle / Fitness",
        "family_home": "Family Home / Kitchen",
        "premium_luxury": "Premium Luxury / High-End",
        "easter_spring": "Easter / Spring / Seasonal",
    }
    
    if theme_name not in descriptions:
        raise KeyError(f"Unknown theme: {theme_name}")
    
    return descriptions[theme_name]


if __name__ == "__main__":
    # Example usage
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    # Example product
    product = "dairy butter no salt (120g)"
    cat = "Dairy"
    
    print(f"\n{'='*80}")
    print(f"Themed Prompts for: {product} ({cat})")
    print(f"{'='*80}\n")
    
    prompts = generate_prompts(product, cat)
    
    for theme_name, prompt in prompts.items():
        desc = get_theme_description(theme_name)
        print(f"🎨 {desc}")
        print(f"   Theme ID: {theme_name}")
        print(f"   Prompt: {prompt[:100]}...")
        print()
    
    print(f"Total themes available: {len(get_available_themes())}")
