# Creative Advertising Image Generator 🎨

A production-ready Python pipeline for generating creative advertising campaign images using text-to-image AI models, optimized for CPU execution.

## Project Structure
- `FrontEnd/` – React app (Vite) with login, products, basket/checkout, interaction tracking, and recommendation fetch.
- `personalisation_algo/` – Python recommendation engine with FastAPI wrapper.

## Prerequisites
- Node.js (18+ recommended) and npm.
- Python 3.10+.

## Setup: Frontend (React)
1) `cd FrontEnd`
2) Install deps: `npm install`
3) (Optional) Configure API paths via `.env` (Vite):
   ```
   VITE_RECO_PRODUCTS_PATH=personalisation_algo/data/products.csv
   VITE_RECO_TRANSACTIONS_PATH=personalisation_algo/data/transactions.csv
   VITE_RECO_CLICKSTREAM_PATH=personalisation_algo/data/clickstream.csv
   ```
   Defaults point to `data/*.csv`.
4) Start dev server: `npm run dev`
5) Open the shown localhost URL.

## Setup: Recommendation API (FastAPI)
1) `cd personalisation_algo`
2) Create venv and install deps:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install fastapi uvicorn pydantic pandas pyyaml
   ```
   (Add any other engine deps you need here.)
3) Run the API:
   ```
   python -m src.main
   ```
   It serves at `http://0.0.0.0:8000/recommend`.

### Recommend endpoint
`POST /recommend`
Body:
```json
{
  "customer_id": "C001",
  "products_path": "data/products.csv",
  "transactions_path": "data/transactions.csv",
  "clickstream_path": "data/clickstream.csv"
}
```
Returns a recommendation payload or 404 if none.

## Frontend → API flow
- On product view, if the user is logged in (customerId available), the frontend calls `POST /recommend` with the JSON above and surfaces the suggested item in the sidebar.
- Interaction events (view, add_to_cart, purchase) are tracked client-side with placeholders for backend wiring.

## Customer IDs & Login
- Customer IDs come from `FrontEnd/src/data/customerMap.js` (generated from `ClickStream.csv` via `FrontEnd/scripts/buildCustomerMap.js`).
- IDs are formatted `C001`, `C002`, etc.; username `kazeem` maps to `C001` for quick testing.
- Unknown usernames throw “User not found” on login.

## Basket & Checkout
- Add products to basket from list/detail. Basket counts show in nav when signed in.
- Checkout posts a purchase interaction and clears the basket.

## Scripts
- `FrontEnd/scripts/buildCustomerMap.js`: generate `src/data/customerMap.js` from `FrontEnd/ClickStream.csv` with friendly usernames. Run: `node scripts/buildCustomerMap.js` (from `FrontEnd/`).
- `FrontEnd/scripts/csvToProducts.js`: regenerate `src/data/products.js` from the CSV catalogue. Run: `node scripts/csvToProducts.js`.

## Notes
- Git commits may be blocked in this environment; run `git add/commit` locally if needed.
- Ensure file paths in the API payload match where your CSVs live; defaults assume `personalisation_algo/data`.
## ✨ Features

- **Themed Product Image Generation**: Automatic multi-theme prompt generation for products (Christmas, Studio, Supermarket, etc.)
- **Marketing Layout Formatter**: Create professional vertical, square, and horizontal branded layouts
- **Dual Generation Modes**: Fast API (HuggingFace free tier) or local CPU models
- **Advanced Post-Processing**: Automatic cropping, color adjustments, brand filters
- **Multiple Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9, Facebook cover
- **Brand Color Filters**: 6 preset filters for brand consistency
- **Pollen Swarm Branding**: Automatic branded overlays with "nectar points" badges
- **Metadata Tracking**: JSON export of all generation parameters
- **CLI Interface**: Easy command-line usage with argparse
- **Production Ready**: Type hints, structured logging, error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

**Option 1: Using Makefile (Recommended)**

```bash
# Create virtual environment and install dependencies
make venv && make install

# Run demo workflow
python demo_workflow.py
```

**Option 2: Manual Installation**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run demo workflow
python demo_workflow.py
```

### Quick Demo

Try the complete workflow with the demo script:

```bash
python demo_workflow.py
```

This will:
1. Generate themed prompts for a sample product
2. Create sample images (simulated)
3. Format images into all three marketing layouts
4. Show you the complete output structure

## 📖 Usage

### Part 1: Themed Product Image Generation

Generate marketing images across multiple creative themes for any product.

#### Basic Product Image Generation

```bash
# Generate all themed images for a product
python generate_product_images.py \
  --product "dairy butter no salt (120g)" \
  --category "Dairy" \
  --output ./output/butter/

# Generate specific themes only
python generate_product_images.py \
  --product "organic honey (250g)" \
  --category "Condiments" \
  --themes christmas_festive studio_product supermarket_shelf \
  --output ./output/honey/

# List all available themes
python generate_product_images.py --list-themes
```

#### Available Themes

The system automatically generates prompts for 10+ creative themes:
- **christmas_festive** - Christmas / Holiday / Festive scenes
- **studio_product** - Clean studio product shots
- **supermarket_shelf** - In-store shelf displays
- **back_to_school** - Back to school themes
- **cooked_prepared** - Prepared / plated food presentations
- **summer_outdoor** - Summer outdoor / seasonal
- **healthy_lifestyle** - Health and fitness contexts
- **family_home** - Family kitchen / home scenes
- **premium_luxury** - Luxury / high-end presentations
- **easter_spring** - Easter / spring seasonal themes

### Part 2: Marketing Layout Formatting

Format generated images into professional marketing layouts with branded themes.

#### Basic Formatting

```bash
# Vertical banner (portrait)
python creative_formatter.py \
  -i input_image.jpg \
  -l vertical \
  -n 10

# Square format (1:1)
python creative_formatter.py \
  -i input_image.jpg \
  -l square \
  -n 15

# Horizontal format (landscape)
python creative_formatter.py \
  -i input_image.jpg \
  -l horizontal \
  -n 20 \
  -p right
```

#### Batch Formatting

```bash
# Format all images in a directory
python creative_formatter.py \
  -i ./generated_images/ \
  -l vertical \
  -n 10
```

### Original Single-Image Generation

Generate single advertising images with custom prompts:

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Generate a single image
python creative_ad_generator.py \
  --prompt "summer sale campaign with fresh produce" \
  --out ./output/summer.jpg
```

### Using Makefile Commands

```bash
# Generate single example
make run-example

# Generate all 8 built-in examples
make run-batch

# Generate with custom prompt
make run-custom PROMPT="luxury car advertisement with gold accents"

# Generate with specific aspect ratio
make run-custom PROMPT="tech product launch" ASPECT=1:1
```

### Advanced Options

```bash
# With brand color filter
python creative_ad_generator.py \
  --prompt "organic food brand" \
  --out ./output/ \
  --aspect 16:9 \
  --filter fresh_green

# With custom adjustments
python creative_ad_generator.py \
  --prompt "luxury winter campaign" \
  --out ./output/ \
  --brightness 1.2 \
  --contrast 1.3 \
  --saturation 1.1 \
  --filter warm_gold

# With reproducible seed
python creative_ad_generator.py \
  --prompt "back to school theme" \
  --out ./output/ \
  --seed 42

# Batch generate all examples
python creative_ad_generator.py \
  --batch \
  --out ./output/batch/
```

## 🎨 Available Options

### Aspect Ratios
- `1:1` - Square (1024x1024) - Instagram, Facebook posts
- `16:9` - Landscape (1024x576) - YouTube thumbnails, presentations
- `9:16` - Portrait (576x1024) - Instagram Stories, TikTok
- `4:3` - Classic landscape (1024x768)
- `3:4` - Classic portrait (768x1024)
- `21:9` - Ultra-wide (1024x439) - Website banners
- `facebook_cover` - Facebook cover (820x312)

### Brand Color Filters
- `warm_gold` - Golden overlay for luxury brands
- `cool_blue` - Corporate professional blue
- `fresh_green` - Natural/organic green
- `luxury_purple` - Premium purple tone
- `energetic_red` - Bold energetic red
- `modern_teal` - Contemporary teal

### Command-Line Arguments

```
--prompt, -p        Text description of the desired image
--out, -o          Output path (file or directory)
--seed, -s         Random seed for reproducibility
--aspect, -a       Target aspect ratio (default: 16:9)
--filter, -f       Brand color filter to apply
--brightness       Brightness adjustment (default: 1.1)
--contrast         Contrast adjustment (default: 1.15)
--saturation       Color saturation (default: 1.2)
--batch            Generate all example prompts
--local            Use local model instead of API (slower)
--hf-token         HuggingFace API token for higher rate limits
```

## 💡 Generation Modes

### API Mode (Default - Recommended)

Uses HuggingFace Inference API - fast, no GPU needed, free tier available.

**Setup:**
1. Get a free HuggingFace account: https://huggingface.co/join
2. Create an access token: https://huggingface.co/settings/tokens
3. Set environment variable:
   ```bash
   export HF_TOKEN=your_huggingface_token
   ```

**Generate images:**
```bash
# Single themed product generation
python generate_product_images.py \
  --product "dairy butter no salt (120g)" \
  --category "Dairy" \
  --output ./output/butter/

# Custom single image
python creative_ad_generator.py \
  --prompt "your custom prompt" \
  --out ./output/
```

### Local Mode (Slower, More Control)

Runs Stable Diffusion locally on CPU. ⚠️ **Warning**: Very slow on CPU, 4GB+ download.

```bash
# Install heavy dependencies
make install-local

# Generate with local model
python generate_product_images.py \
  --product "your product" \
  --category "category" \
  --output ./output/ \
  --local
```

## 🎨 Complete Workflow Example

Here's a complete end-to-end workflow for creating product marketing materials:

```bash
# Step 1: Set your HuggingFace token
export HF_TOKEN=your_token_here

# Step 2: Generate all themed images for a product
python generate_product_images.py \
  --product "organic honey (250g)" \
  --category "Condiments" \
  --output ./images/honey/ \
  --aspect 16:9

# This will generate 10+ themed images:
# - Christmas/festive scene
# - Clean studio product shot
# - Supermarket shelf display
# - Back to school theme
# - Cooked/prepared presentation
# - Summer outdoor scene
# - Healthy lifestyle context
# - Family home/kitchen
# - Premium luxury presentation
# - Easter/spring theme

# Step 3: Format the best images into marketing layouts
python creative_formatter.py \
  -i ./images/honey/organic_honey_christmas_festive.jpg \
  -l vertical \
  -n 15 \
  -o ./marketing/honey_christmas_banner.png

python creative_formatter.py \
  -i ./images/honey/organic_honey_studio_product.jpg \
  -l square \
  -n 10 \
  -o ./marketing/honey_instagram.png

python creative_formatter.py \
  -i ./images/honey/organic_honey_supermarket_shelf.jpg \
  -l horizontal \
  -n 20 \
  -o ./marketing/honey_website_banner.png
```

## 📋 Built-in Example Prompts

The pipeline includes 8 optimized advertising prompts:

1. Bright summer supermarket sale with fresh produce
2. Luxury winter campaign with gold typography
3. Back-to-school energetic colorful theme
4. Modern tech product launch
5. Organic natural food brand
6. Fitness and wellness campaign
7. Holiday shopping season
8. Artisan coffee shop promotion

Generate all examples:
```bash
make run-batch
# or
python creative_ad_generator.py --batch --out ./output/
```

## 📁 Output Structure

### Product Image Generation

Each theme generates two files:

```
output/
├── product_name_theme.jpg       # Generated image
└── product_name_theme.json      # Metadata file
```

**Metadata includes:**
- Original prompt
- Theme information (name, description)
- Product details (name, category)
- Generation seed (for reproducibility)
- Timestamp
- Processing parameters
- Final image dimensions
- Generation time

A summary file is also created:
```
output/
└── product_name_generation_summary.json  # Overall generation summary
```

### Formatted Marketing Layouts

Each formatted image creates:

```
output/
├── image_layout.png             # Formatted marketing image
└── image_layout.json            # Layout metadata
```

**Layout metadata includes:**
- Input image path
- Layout type (vertical/square/horizontal)
- Nectar points value
- Image position (for horizontal)
- Final dimensions
- Timestamp
- Original generation metadata (if available)

## 🛠️ Makefile Commands

```bash
make help          # Show all available commands
make venv          # Create virtual environment
make install       # Install dependencies (API mode)
make install-local # Install with local model support
make run-example   # Generate single example
make run-batch     # Generate all 8 examples
make run-custom    # Generate with custom prompt
make clean         # Remove generated files
make clean-all     # Remove everything including venv
```

## 🔧 Troubleshooting

### API Rate Limiting

If you hit API rate limits:
1. Get a free HuggingFace account: https://huggingface.co/join
2. Create an access token: https://huggingface.co/settings/tokens
3. Set environment variable: `export HF_TOKEN=your_token`

### Model Loading Errors

If API returns 503 errors:
- The model is loading (cold start)
- Wait 20 seconds and it will retry automatically
- Or use `--local` flag for local generation

### Out of Memory (Local Mode)

If local generation fails with OOM:
- Local mode requires significant RAM (8GB+)
- Consider using API mode instead (default)
- Reduce image size in the code if needed

## 📦 Dependencies

**Lightweight (API mode - Required)**:
- pillow >= 10.0.0
- numpy >= 1.24.0
- huggingface_hub >= 0.20.0

**Heavy (Local mode - Optional)**:
- torch >= 2.0.0
- diffusers >= 0.21.0
- transformers >= 4.30.0
- accelerate >= 0.20.0

## 🎯 Use Cases

- **Product Marketing**: Generate themed product images for campaigns
- **Seasonal Campaigns**: Automatic holiday and seasonal variations
- **Social Media**: Create branded posts in multiple formats (Stories, Posts, Banners)
- **E-commerce**: Product promotion images across multiple themes
- **A/B Testing**: Generate variations for testing
- **Retail Marketing**: In-store and online promotional materials

## 📁 Project Structure

```
Pollen_Swarm/
├── prompt_generator.py           # Themed prompt generation module
├── generate_product_images.py    # Batch product image generation
├── creative_formatter.py          # Marketing layout formatter
├── creative_ad_generator.py       # Original single image generator
├── demo_workflow.py               # Complete workflow demonstration
├── requirements.txt               # Python dependencies
├── Makefile                       # Build and run commands
└── README.md                      # This file
```

## 🔧 API Configuration

### Setting up HuggingFace API Token

For image generation, you need a HuggingFace API token:

1. Create a free account at https://huggingface.co/join
2. Generate an access token at https://huggingface.co/settings/tokens
3. Set the environment variable:
   ```bash
   export HF_TOKEN=your_token_here
   ```
4. Or pass it directly:
   ```bash
   python generate_product_images.py --hf-token your_token_here ...
   ```

## 📝 Extending the Pipeline

### Adding New Themes

Edit `prompt_generator.py` and add to `THEME_TEMPLATES`:

```python
THEME_TEMPLATES = {
    "your_theme": (
        "your template featuring {product_name} from the {category} "
        "category, your creative description here"
    ),
    # ... existing themes
}
```

### Customizing Brand Colors

Edit `creative_formatter.py` and modify `BRAND_COLORS`:

```python
BRAND_COLORS = {
    'purple': (106, 27, 154),
    'orange': (255, 152, 0),
    'your_color': (R, G, B),
    # ...
}
```

### Adding New Layouts

Add a new formatting function in `creative_formatter.py`:

```python
def format_your_layout(image: Image.Image, nectar_points: int) -> Image.Image:
    # Your custom layout logic
    return formatted_image
```

## 📝 Example Workflows

### Campaign Asset Generation

```bash
# Generate hero image
python creative_ad_generator.py \
  --prompt "summer sale campaign" \
  --aspect 21:9 \
  --out ./campaign/hero.jpg

# Generate social media assets
python creative_ad_generator.py \
  --prompt "summer sale campaign" \
  --aspect 1:1 \
  --out ./campaign/instagram.jpg

python creative_ad_generator.py \
  --prompt "summer sale campaign" \
  --aspect 9:16 \
  --out ./campaign/story.jpg
```

### Brand-Consistent Content

```bash
# Generate with brand filter
python creative_ad_generator.py \
  --prompt "new product launch" \
  --filter warm_gold \
  --brightness 1.15 \
  --contrast 1.2 \
  --out ./branded/
```

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - feel free to use in commercial projects.

## 🔗 Resources

- [HuggingFace Inference API](https://huggingface.co/inference-api)
- [Stable Diffusion](https://github.com/Stability-AI/stablediffusion)
- [Diffusers Library](https://github.com/huggingface/diffusers)

## 💬 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the log file: `creative_pipeline.log`
3. Open an issue on GitHub

---

Made with ❤️ for creative advertising workflows
