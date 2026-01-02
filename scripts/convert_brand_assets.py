#!/usr/bin/env python3
"""
Brand Asset Conversion Script for FindingExcellence PRO

This script converts Ayesa brand assets into the formats needed for the desktop app.

Requirements:
- Pillow (PIL) - already installed in the venv

Conversions performed:
1. Logo PNG (192x192) → Multiple sizes (16, 32, 64, 128, 256, 512px)
2. Logo → ICO file for Windows window icon
3. Header JPG → Scaled versions for app header (200px, 100px height)
4. Color extraction → Update branding.py with Ayesa colors
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import PIL
try:
    from PIL import Image
    print("✓ Pillow (PIL) available")
except ImportError:
    print("✗ Pillow not installed. Install with: pip install Pillow")
    sys.exit(1)


def ensure_directories():
    """Create necessary asset directories."""
    dirs = [
        "assets",
        "assets/icons",
        "assets/headers",
        "assets/logos",
        "frontend_desktop/assets",
        "frontend_desktop/assets/icons",
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")


def convert_logo_png():
    """Convert PNG logo to multiple sizes."""
    source = Path(".github/idVZeT5U0c_logos.png")

    if not source.exists():
        print(f"✗ Logo not found: {source}")
        return False

    try:
        img = Image.open(source)
        print(f"✓ Loaded logo: {source} ({img.size})")

        # Generate multiple sizes
        sizes = [16, 32, 64, 128, 256, 512]

        for size in sizes:
            # Resize with high quality
            resized = img.resize((size, size), Image.Resampling.LANCZOS)

            # Save as PNG
            output = Path(f"assets/icons/ayesa_logo_{size}x{size}.png")
            resized.save(output, "PNG", quality=95)
            print(f"  ✓ {size}x{size}: {output}")

        return True

    except Exception as e:
        print(f"✗ Error converting logo: {e}")
        return False


def create_ico_file():
    """Create Windows ICO file from logo."""
    source = Path(".github/idVZeT5U0c_logos.png")
    output = Path("assets/icons/ayesa_logo.ico")

    if not source.exists():
        print(f"✗ Logo not found: {source}")
        return False

    try:
        img = Image.open(source)

        # Create multiple sizes for ICO (standard Windows icon sizes)
        icon_sizes = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256)]

        # Resize all variants
        icon_images = []
        for size in icon_sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)

        # Save as ICO with all sizes
        icon_images[0].save(
            output,
            format="ICO",
            sizes=icon_sizes,
            quality=95
        )

        print(f"✓ Created Windows ICO file: {output}")
        print(f"  Included sizes: {icon_sizes}")
        return True

    except Exception as e:
        print(f"✗ Error creating ICO: {e}")
        return False


def convert_header_jpg():
    """Convert header JPG to scaled versions."""
    source = Path(".github/Cabecera-Ayesa v2.jpg")

    if not source.exists():
        print(f"✗ Header not found: {source}")
        return False

    try:
        img = Image.open(source)
        original_size = img.size
        print(f"✓ Loaded header: {source} ({original_size})")

        # Calculate scaled widths based on aspect ratio
        aspect_ratio = original_size[0] / original_size[1]

        # Target heights for different UI contexts
        heights = {
            "full": 350,      # Full height (1400x350)
            "large": 150,     # Large header
            "medium": 100,    # Medium header
            "small": 60,      # Small header
        }

        for name, target_height in heights.items():
            # Calculate width to maintain aspect ratio
            target_width = int(target_height * aspect_ratio)

            # Resize
            resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # Save as PNG (better for transparency/compression)
            output = Path(f"assets/headers/ayesa_header_{name}_{target_width}x{target_height}.png")
            resized.save(output, "PNG", quality=95, optimize=True)
            print(f"  ✓ {name} ({target_width}x{target_height}): {output}")

        # Also keep original as PNG for reference
        img.save(Path("assets/headers/ayesa_header_original.png"), "PNG", quality=95)
        print(f"  ✓ Original (reference): assets/headers/ayesa_header_original.png")

        return True

    except Exception as e:
        print(f"✗ Error converting header: {e}")
        return False


def extract_colors():
    """Extract dominant colors from logo for branding.py."""
    source = Path(".github/idVZeT5U0c_logos.png")

    if not source.exists():
        print(f"✗ Logo not found: {source}")
        return None

    try:
        img = Image.open(source).convert("RGB")

        # Resize to 10x10 for color analysis
        small_img = img.resize((10, 10), Image.Resampling.LANCZOS)

        # Get all pixels and find most common colors
        pixels = list(small_img.getdata())

        # Sort by frequency
        from collections import Counter
        color_counts = Counter(pixels)
        most_common = color_counts.most_common(5)

        print("✓ Extracted dominant colors from logo:")
        colors = {}
        for i, (color, count) in enumerate(most_common):
            hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
            print(f"  {i+1}. {hex_color} (frequency: {count})")
            colors[f"color_{i+1}"] = hex_color

        return colors

    except Exception as e:
        print(f"✗ Error extracting colors: {e}")
        return None


def create_asset_index():
    """Create an index file documenting all generated assets."""
    index_content = """# Brand Assets Index

Generated by: convert_brand_assets.py

## Logo Assets

### PNG Formats (Standard sizes)
- assets/icons/ayesa_logo_16x16.png - Toolbar icon
- assets/icons/ayesa_logo_32x32.png - Window decorator
- assets/icons/ayesa_logo_64x64.png - Dialog icon
- assets/icons/ayesa_logo_128x128.png - Large icon
- assets/icons/ayesa_logo_256x256.png - Extra large icon
- assets/icons/ayesa_logo_512x512.png - Desktop/splash icon

### Windows ICO Format
- assets/icons/ayesa_logo.ico - Multi-resolution Windows icon
  - Contains: 16x16, 32x32, 64x64, 128x128, 256x256

## Header Assets

### Scaled Variants
- assets/headers/ayesa_header_full_1400x350.png - Full original size
- assets/headers/ayesa_header_large_1400x150.png - Large app header
- assets/headers/ayesa_header_medium_1400x100.png - Medium app header
- assets/headers/ayesa_header_small_1400x60.png - Small app header
- assets/headers/ayesa_header_original.png - Original reference

## Usage in Application

### Window Icon
```python
# frontend_desktop/main.py
root.iconbitmap(default='assets/icons/ayesa_logo.ico')
```

### App Header (CustomTkinter)
```python
# frontend_desktop/ui/main_window.py
header_image = PhotoImage(file='assets/headers/ayesa_header_medium_1400x100.png')
header_label = ctk.CTkLabel(root, image=header_image)
```

### Splash Screen
```python
# Show at startup
splash_image = Image.open('assets/icons/ayesa_logo_512x512.png')
```

## Color Palette
Extract dominant colors from logo using: python scripts/convert_brand_assets.py --colors

## Notes
- All PNG files optimized for web and UI
- ICO file contains multiple sizes for Windows scaling
- Original assets preserved in .github/ folder
- All conversions use high-quality LANCZOS resampling
"""

    output = Path("assets/BRAND_ASSETS_INDEX.md")
    output.write_text(index_content)
    print(f"✓ Created asset index: {output}")


def main():
    """Run all conversions."""
    print("=" * 60)
    print("AYESA BRAND ASSET CONVERTER")
    print("=" * 60)
    print()

    # Create directories
    print("Step 1: Creating asset directories...")
    ensure_directories()
    print()

    # Convert logo
    print("Step 2: Converting logo PNG to multiple sizes...")
    logo_ok = convert_logo_png()
    print()

    # Create ICO
    print("Step 3: Creating Windows ICO file...")
    ico_ok = create_ico_file()
    print()

    # Convert header
    print("Step 4: Converting header JPG to scaled variants...")
    header_ok = convert_header_jpg()
    print()

    # Extract colors
    print("Step 5: Extracting color palette...")
    colors = extract_colors()
    print()

    # Create index
    print("Step 6: Creating asset index...")
    create_asset_index()
    print()

    # Summary
    print("=" * 60)
    print("CONVERSION SUMMARY")
    print("=" * 60)
    print(f"Logo conversion: {'✓ Success' if logo_ok else '✗ Failed'}")
    print(f"ICO creation: {'✓ Success' if ico_ok else '✗ Failed'}")
    print(f"Header conversion: {'✓ Success' if header_ok else '✗ Failed'}")
    print(f"Color extraction: {'✓ Success' if colors else '✗ Failed'}")
    print()

    if logo_ok and ico_ok and header_ok:
        print("✓ All conversions completed successfully!")
        print()
        print("Next steps:")
        print("1. Check assets/ folder for generated files")
        print("2. Update frontend_desktop/main.py to use window icon")
        print("3. Add header image to main window UI")
        print("4. Review extracted colors and update branding.py")
        return 0
    else:
        print("✗ Some conversions failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
