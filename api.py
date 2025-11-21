#!/usr/bin/env python3
"""
FastAPI endpoint for AI-powered product image generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import tempfile
import shutil
from typing import Optional

from generate_product_images import generate_product_images
from creative_formatter import format_creative

app = FastAPI(title="Pollen Swarm Image Generator API")


class ProductRequest(BaseModel):
    product_name: str
    product_category: str
    theme: Optional[str] = "christmas_festive"
    layout: Optional[str] = "square"
    seed: Optional[int] = 10
    hf_token: Optional[str] = "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"


@app.post("/generate-image")
async def generate_product_image(request: ProductRequest):
    """
    Generate and format a product image.

    Args:
        product_name: Name of the product (e.g., "Carrots 1kg")
        product_category: Category (e.g., "produce")
        theme: Visual theme (default: "studio_product")
        layout: Output layout - "vertical", "square", or "horizontal" (default: "square")
        seed: Random seed for generation (default: 1)
        hf_token: HuggingFace API token (default: "test")

    Returns:
        PNG image file
    """

    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        generation_dir = temp_path / "generated"
        formatted_dir = temp_path / "formatted"
        generation_dir.mkdir(exist_ok=True)
        formatted_dir.mkdir(exist_ok=True)

        try:
            # Step 1: Generate AI image
            results = generate_product_images(
                product_name=request.product_name,
                category=request.product_category,
                output_dir=str(generation_dir),
                themes=[request.theme],
                seed=request.seed,
                aspect_ratio="16:9",
                hf_token=request.hf_token,
                brightness=1.1,
                contrast=1.15,
                saturation=1.2
            )

            # Check if generation was successful
            successful_results = [r for r in results.values() if r['status'] == 'success']
            if not successful_results:
                raise HTTPException(status_code=500, detail="Image generation failed")

            # Get the first generated image
            generated_images = list(generation_dir.glob("*.jpg"))
            if not generated_images:
                raise HTTPException(status_code=500, detail="No images were generated")

            base_image = generated_images[0]

            # Step 2: Format the image
            output_path, metadata_path = format_creative(
                input_image_path=str(base_image),
                layout=request.layout,
                product_name=request.product_name.split('(')[0].strip(),
                tagline="Fresh & Premium",
                nectar_points=25,
                flavor_text=f"Premium {request.product_category}",
                output_path=str(formatted_dir / "output.png"),
                image_position='center'
            )

            # Return the formatted image
            if not Path(output_path).exists():
                raise HTTPException(status_code=500, detail="Image formatting failed")

            # Copy to a permanent location temporarily (FastAPI will serve it)
            final_output = Path("temp_output.png")
            shutil.copy(output_path, final_output)

            return FileResponse(
                path=final_output,
                media_type="image/png",
                filename=f"{request.product_name.replace(' ', '_')}.png",
                background=None
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "Pollen Swarm Image Generator API",
        "endpoints": {
            "/generate-image": "POST - Generate product image",
            "/docs": "GET - API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)