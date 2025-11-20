# Creative Advertising Image Generator 🎨

A production-ready Python pipeline for generating creative advertising campaign images using text-to-image AI models, optimized for CPU execution.

## ✨ Features

- **Dual Generation Modes**: Fast API (HuggingFace free tier) or local CPU models
- **Advanced Post-Processing**: Automatic cropping, color adjustments, brand filters
- **Multiple Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9, Facebook cover
- **Brand Color Filters**: 6 preset filters for brand consistency
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

# Generate your first image
make run-example
```

**Option 2: Manual Installation**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📖 Usage

### Basic Usage

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

```bash
# Install lightweight dependencies
make install

# Generate images
python creative_ad_generator.py --prompt "your prompt" --out ./output/
```

**Tip**: Set `HF_TOKEN` environment variable for higher rate limits:
```bash
export HF_TOKEN=your_huggingface_token
python creative_ad_generator.py --prompt "your prompt" --out ./output/
```

### Local Mode (Slower, More Control)

Runs Stable Diffusion locally on CPU. ⚠️ **Warning**: Very slow on CPU, 4GB+ download.

```bash
# Install heavy dependencies
make install-local

# Generate with local model
python creative_ad_generator.py --prompt "your prompt" --out ./output/ --local
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

Each generation creates two files:

```
output/
├── example.jpg          # Generated image
└── example.json         # Metadata file
```

**Metadata includes:**
- Original prompt
- Generation seed (for reproducibility)
- Timestamp
- Processing parameters
- Final image dimensions
- Generation time

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

**Lightweight (API mode)**:
- pillow >= 10.0.0
- numpy >= 1.24.0
- requests >= 2.31.0

**Heavy (Local mode)**:
- torch >= 2.0.0
- diffusers >= 0.21.0
- transformers >= 4.30.0
- accelerate >= 0.20.0

## 🎯 Use Cases

- **Marketing Teams**: Generate campaign visuals quickly
- **Ad Agencies**: Create concept mockups for clients
- **E-commerce**: Product promotion images
- **Social Media**: Platform-specific content (stories, posts, banners)
- **A/B Testing**: Generate variations for testing
- **Datasets**: Create labeled training datasets

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
