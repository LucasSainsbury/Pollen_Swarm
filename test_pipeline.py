#!/usr/bin/env python3
"""
Basic tests for Pollen Swarm pipeline modules.

Run with: python3 test_pipeline.py
"""

import sys
from pathlib import Path

# Test imports
try:
    from prompt_generator import generate_prompts, get_available_themes, get_theme_description
    from creative_formatter import (
        format_vertical, format_square, format_horizontal,
        create_gradient, resize_and_crop, create_branded_panel
    )
    from PIL import Image
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)


def test_prompt_generator():
    """Test prompt generation."""
    print("\n" + "="*80)
    print("Testing Prompt Generator")
    print("="*80)
    
    # Test generate_prompts
    product = "test product (100g)"
    category = "Test Category"
    
    try:
        prompts = generate_prompts(product, category)
        assert isinstance(prompts, dict), "generate_prompts should return a dict"
        assert len(prompts) > 0, "Should generate at least one prompt"
        
        # Check that product and category appear in prompts
        for theme, prompt in prompts.items():
            assert product in prompt, f"Product name missing from {theme} prompt"
            assert category in prompt, f"Category missing from {theme} prompt"
        
        print(f"✓ Generated {len(prompts)} themed prompts")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    # Test get_available_themes
    try:
        themes = get_available_themes()
        assert isinstance(themes, list), "get_available_themes should return a list"
        assert len(themes) > 0, "Should have at least one theme"
        print(f"✓ Found {len(themes)} available themes")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    # Test get_theme_description
    try:
        for theme in themes[:3]:  # Test first 3
            desc = get_theme_description(theme)
            assert isinstance(desc, str), "Description should be a string"
            assert len(desc) > 0, "Description should not be empty"
        print(f"✓ Theme descriptions working")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    # Test error handling
    try:
        generate_prompts("", category)
        print("✗ Should have raised error for empty product name")
        return False
    except ValueError:
        print("✓ Error handling working correctly")
    
    return True


def test_creative_formatter():
    """Test creative formatter functions."""
    print("\n" + "="*80)
    print("Testing Creative Formatter")
    print("="*80)
    
    # Create a test image
    test_img = Image.new('RGB', (800, 600), color='blue')
    
    # Test create_gradient
    try:
        gradient = create_gradient(400, 300, (255, 0, 0), (0, 0, 255), vertical=True)
        assert gradient.size == (400, 300), "Gradient size mismatch"
        print("✓ Gradient creation working")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    # Test resize_and_crop
    try:
        cropped = resize_and_crop(test_img, 400, 400)
        assert cropped.size == (400, 400), "Resize/crop size mismatch"
        print("✓ Resize and crop working")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    # Test create_branded_panel
    try:
        panel = create_branded_panel(400, 300, nectar_points=10)
        assert panel.size == (400, 300), "Panel size mismatch"
        print("✓ Branded panel creation working")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    # Test format functions
    try:
        vertical = format_vertical(test_img, nectar_points=10)
        assert vertical.size == (1080, 1920), "Vertical format size mismatch"
        print("✓ Vertical formatting working")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    try:
        square = format_square(test_img, nectar_points=15)
        assert square.size == (1080, 1080), "Square format size mismatch"
        print("✓ Square formatting working")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    try:
        horizontal = format_horizontal(test_img, nectar_points=20)
        assert horizontal.size == (1920, 1080), "Horizontal format size mismatch"
        print("✓ Horizontal formatting working")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("Pollen Swarm Pipeline - Module Tests")
    print("="*80)
    
    tests = [
        ("Prompt Generator", test_prompt_generator),
        ("Creative Formatter", test_creative_formatter),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✓ {name} tests PASSED")
            else:
                failed += 1
                print(f"\n✗ {name} tests FAILED")
        except Exception as e:
            failed += 1
            print(f"\n✗ {name} tests FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*80 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
