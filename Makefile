.PHONY: help venv install install-local clean run-example run-batch test

# Variables
PYTHON := python3
VENV := venv
BIN := $(VENV)/bin
PIP := $(BIN)/pip
PYTHON_VENV := $(BIN)/python
HF_TOKEN := n/a

# Export token for all commands
export HF_TOKEN

# Default target
help:
	@echo "Creative Advertising Image Generator - Makefile Commands"
	@echo "========================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make venv          - Create Python virtual environment"
	@echo "  make install       - Install dependencies (API mode - lightweight)"
	@echo "  make install-local - Install with local model support (heavy)"
	@echo ""
	@echo "Run Commands:"
	@echo "  make run-example   - Generate a single example image"
	@echo "  make run-batch     - Generate all 8 example advertising images"
	@echo "  make run-custom    - Run with custom prompt (set PROMPT variable)"
	@echo "  make run-local     - Run with local model (slow on CPU)"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean         - Remove generated files and cache"
	@echo "  make clean-all     - Remove everything including venv"
	@echo "  make test          - Run tests (if available)"
	@echo ""
	@echo "Examples:"
	@echo "  make venv && make install && make run-example"
	@echo "  make run-custom PROMPT='luxury car advertisement'"
	@echo "  HF_TOKEN=your_token make run-batch"

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "✓ Virtual environment created at ./$(VENV)/"
	@echo "  Activate with: source $(VENV)/bin/activate"

# Install dependencies (API mode - lightweight)
install: venv
	@echo "Installing dependencies (API mode - lightweight)..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Dependencies installed successfully!"
	@echo "  You can now run: make run-example"

# Install with local model support (heavy)
install-local: venv
	@echo "Installing dependencies with local model support..."
	@echo "⚠️  Warning: This will download ~4GB of packages"
	$(PIP) install --upgrade pip
	$(PIP) install pillow numpy requests
	$(PIP) install torch torchvision --index-url https://download.pytorch.org/whl/cpu
	$(PIP) install diffusers transformers accelerate
	@echo "✓ Local model dependencies installed!"
	@echo "  You can now run with --local flag"

# Add new API example command after run-example
run-api: venv
	@echo "Generating image using HuggingFace API (fast, no local model needed)..."
	@mkdir -p output
	$(PYTHON_VENV) creative_ad_generator.py \
		--prompt "bright summer supermarket sale with fresh produce, vibrant colors, photorealistic" \
		--out output/api_example.jpg \
		--aspect 16:9 \
		--hf-token $(HF_TOKEN)
	@echo "✓ Check output/api_example.jpg"

# Update run-example to use API with token
run-example: venv
	@echo "Generating example advertising image with API..."
	@mkdir -p output
	$(PYTHON_VENV) creative_ad_generator.py \
		--prompt "bright summer supermarket sale with fresh produce, vibrant colors" \
		--out output/example.jpg \
		--aspect 16:9 \
		--hf-token $(HF_TOKEN)
	@echo "✓ Check output/example.jpg"

# Update run-batch to use token
run-batch: venv
	@echo "Generating all 8 example advertising images with API..."
	@mkdir -p output/batch
	$(PYTHON_VENV) creative_ad_generator.py \
		--batch \
		--out output/batch/ \
		--hf-token $(HF_TOKEN)
	@echo "✓ Check output/batch/ directory"

# Run with custom prompt
run-custom: venv
	@if [ -z "$(PROMPT)" ]; then \
		echo "Error: PROMPT variable not set"; \
		echo "Usage: make run-custom PROMPT='your prompt here'"; \
		exit 1; \
	fi
	@mkdir -p output
	$(PYTHON_VENV) creative_ad_generator.py \
		--prompt "$(PROMPT)" \
		--out output/custom.jpg \
		--aspect $(ASPECT)
	@echo "✓ Check output/custom.jpg"

# Run with local model (slow on CPU)
run-local: venv
	@echo "⚠️  Running with local model - this will be slow on CPU!"
	@mkdir -p output
	$(PYTHON_VENV) creative_ad_generator.py \
		--prompt "luxury advertising campaign" \
		--out output/local.jpg \
		--local
	@echo "✓ Check output/local.jpg"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf output/
	rm -rf ads/
	rm -rf __pycache__/
	rm -f *.pyc
	rm -f *.log
	@echo "✓ Cleaned!"

# Clean everything including venv
clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf $(VENV)/
	@echo "✓ Everything cleaned!"

# Run tests
test: venv
	@echo "Running tests..."
	$(PYTHON_VENV) -m pytest tests/ -v || echo "No tests found"

# Default aspect ratio for custom runs
ASPECT ?= 16:9