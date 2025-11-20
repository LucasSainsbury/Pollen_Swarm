# Pollen Swarm - Implementation Summary

## Overview

This implementation provides a complete pipeline for generating and formatting themed product marketing images. The system consists of three main modules that work together to automate creative content generation.

## Modules

### 1. prompt_generator.py
**Purpose**: Generate themed advertising prompts for products

**Key Functions**:
- `generate_prompts(product_name, category)` - Returns dict of themed prompts
- `get_available_themes()` - Lists all available theme IDs
- `get_theme_description(theme_name)` - Returns human-readable theme description

**Themes Included** (10+):
- christmas_festive - Christmas/Holiday scenes
- studio_product - Clean studio shots
- supermarket_shelf - In-store displays
- back_to_school - Back to school themes
- cooked_prepared - Prepared/plated presentations
- summer_outdoor - Summer/outdoor scenes
- healthy_lifestyle - Health/fitness contexts
- family_home - Family/kitchen settings
- premium_luxury - Luxury presentations
- easter_spring - Easter/spring themes

### 2. generate_product_images.py
**Purpose**: Batch generate images for all themes via HuggingFace API

**Key Features**:
- CLI interface for batch generation
- Generates images for all themes or selected themes
- Saves images with structured JSON metadata
- Error handling with detailed logging
- Reproducible with seed parameter

**Usage Example**:
```bash
python generate_product_images.py \
  --product "dairy butter no salt (120g)" \
  --category "Dairy" \
  --output ./images/butter/
```

### 3. creative_formatter.py
**Purpose**: Format images into professional marketing layouts

**Layouts Supported**:
- **Vertical**: 1080x1920 (portrait) - 50% image, 50% branding
- **Square**: 1080x1080 (1:1) - 80% image, 20% branding  
- **Horizontal**: 1920x1080 (landscape) - 50% image, 50% branding

**Branding Elements**:
- Purple/orange gradient backgrounds
- "Pollen Swarm" logo in white half-dome
- Customizable "X nectar points" badge in orange

**Key Functions**:
- `format_creative(input_path, layout, nectar_points, output_path)` - Main formatting function
- `format_vertical(image, nectar_points)` - Vertical layout
- `format_square(image, nectar_points)` - Square layout
- `format_horizontal(image, nectar_points, position)` - Horizontal layout

**Helper Functions**:
- `create_gradient()` - Generate color gradients
- `resize_and_crop()` - Smart image resizing/cropping
- `create_branded_panel()` - Create branded decoration panels

**Usage Example**:
```bash
python creative_formatter.py \
  -i input.jpg \
  -l vertical \
  -n 15 \
  -o output.png
```

## Workflow

### Complete End-to-End Process

1. **Generate Themed Prompts**
   ```python
   from prompt_generator import generate_prompts
   prompts = generate_prompts("organic honey (250g)", "Condiments")
   ```

2. **Generate Images** (via CLI or API)
   ```bash
   python generate_product_images.py \
     --product "organic honey (250g)" \
     --category "Condiments" \
     --output ./images/honey/
   ```

3. **Format into Marketing Layouts**
   ```bash
   python creative_formatter.py \
     -i ./images/honey/organic_honey_christmas_festive.jpg \
     -l vertical \
     -n 15
   ```

## Demo Script

**demo_workflow.py** - Complete workflow demonstration
- Shows full pipeline from prompt generation to formatted outputs
- Creates sample images for testing
- Demonstrates all three layout formats
- Helpful for understanding the system

Run with: `python demo_workflow.py`

## Testing

**test_pipeline.py** - Basic module tests
- Tests prompt generation
- Tests formatting functions
- Validates error handling
- Ensures all components work correctly

Run with: `python test_pipeline.py`

## Dependencies

### Required (API Mode)
- pillow >= 10.0.0
- numpy >= 1.24.0
- huggingface_hub >= 0.20.0

### Optional (Local Mode)
- torch >= 2.0.0
- diffusers >= 0.21.0
- transformers >= 4.30.0
- accelerate >= 0.20.0

## Installation

```bash
# Install required dependencies
pip install pillow numpy huggingface_hub

# Set HuggingFace token
export HF_TOKEN=your_token_here

# Run demo
python demo_workflow.py
```

## Output Structure

### Generated Images
```
output/
├── product_theme.jpg              # Generated image
├── product_theme.json             # Image metadata
└── product_generation_summary.json # Batch summary
```

### Formatted Layouts
```
output/
├── image_vertical.png             # Vertical layout
├── image_vertical.json            # Layout metadata
├── image_square.png               # Square layout
├── image_square.json
├── image_horizontal.png           # Horizontal layout
└── image_horizontal.json
```

## Key Features

✅ **Type Hints**: All functions use type annotations
✅ **Logging**: Structured logging throughout
✅ **Error Handling**: Comprehensive error handling
✅ **Metadata**: JSON tracking for all operations
✅ **CLI Interfaces**: Easy command-line usage
✅ **Batch Processing**: Handle multiple images/themes
✅ **Extensible**: Easy to add new themes or layouts
✅ **Production Ready**: Clean, documented, tested code

## Extension Points

### Adding New Themes
Edit `prompt_generator.py`:
```python
THEME_TEMPLATES = {
    "your_theme": (
        "your template with {product_name} and {category}"
    ),
}
```

### Adding New Layouts
Edit `creative_formatter.py`:
```python
def format_your_layout(image, nectar_points):
    # Your layout logic
    return formatted_image
```

### Customizing Brand Colors
Edit `creative_formatter.py`:
```python
BRAND_COLORS = {
    'your_color': (R, G, B),
}
```

## Architecture Decisions

1. **Modular Design**: Three separate modules for clear separation of concerns
2. **CLI-First**: All tools accessible via command line for easy automation
3. **API-Preferred**: Use HuggingFace API by default for speed and no local compute
4. **Metadata Rich**: Every operation generates JSON metadata for traceability
5. **Pillow-Based**: Pure Python imaging with PIL/Pillow for portability
6. **Type Safe**: Type hints throughout for better IDE support and fewer bugs

## Performance Notes

- **API Mode**: Fast, no local compute needed (~10-30 seconds per image)
- **Local Mode**: Slow on CPU (~2-5 minutes per image), requires 8GB+ RAM
- **Formatting**: Very fast (~1-2 seconds per layout)
- **Batch Operations**: Can process dozens of themes/images efficiently

## Future Enhancements

Potential areas for expansion:
- More themes (Valentine's, Halloween, etc.)
- Additional layout formats (circular, banner sizes)
- Animation support (GIF/video outputs)
- A/B testing framework
- Web interface
- Cloud deployment
- Template customization UI

## Credits

Created for Pollen Swarm creative marketing pipeline.
License: MIT
