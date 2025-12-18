#!/usr/bin/env python3
"""
princss_style.py - Generate images in the princss.online style

Features:
- 1-bit Floyd-Steinberg dithering with exact original colors
- Text banners with Ballantines Serial ExtraBold font (with dithering)
- Horizontal compression for compact look matching original
- Reusable flourish ornament
- Combined dithered image + text headers

Usage:
    python princss_style.py text "Your Text" output.png [--size 40] [--width 442] [--height 52]
    python princss_style.py dither input.png output.png
    python princss_style.py header input.png "Your Text" output.png [--text-height 52]
"""

import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

# Exact colors from original princss.online images
COLORS = {
    'dark': (25, 5, 3),       # Original dark brown/maroon
    'light': (255, 255, 255), # White
    'dark_rgba': (25, 5, 3, 255),
    'transparent': (255, 255, 255, 0)
}

# Script directory for assets
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR / 'assets'

# Font configuration - ExtraBold preferred for matching original
FONT_PATHS = [
    '/Users/l/Library/Fonts/Ballantines-Serial-ExtraBold Regular.ttf',
    os.path.expanduser('~/Library/Fonts/Ballantines-Serial-ExtraBold Regular.ttf'),
    '/Library/Fonts/Ballantines-Serial-ExtraBold Regular.ttf',
    'Ballantines-Serial-ExtraBold Regular.ttf',
]

def find_font():
    """Find the Ballantines Serial ExtraBold font."""
    for path in FONT_PATHS:
        try:
            font = ImageFont.truetype(path, 28)
            return path
        except:
            continue
    raise FileNotFoundError(
        "Ballantines Serial ExtraBold font not found. "
        "Please install it from your font source."
    )


def load_flourish():
    """Load the flourish ornament asset."""
    flourish_path = ASSETS_DIR / 'flourish.png'
    if flourish_path.exists():
        return Image.open(flourish_path).convert('RGBA')
    return None


def floyd_steinberg_dither(gray_array):
    """Apply Floyd-Steinberg dithering to a grayscale numpy array."""
    pixels = gray_array.astype(np.float64)
    height, width = pixels.shape
    
    for y in range(height):
        for x in range(width):
            old_pixel = pixels[y, x]
            new_pixel = 255.0 if old_pixel > 128 else 0.0
            pixels[y, x] = new_pixel
            error = old_pixel - new_pixel
            
            if x + 1 < width:
                pixels[y, x + 1] += error * 7 / 16
            if y + 1 < height:
                if x > 0:
                    pixels[y + 1, x - 1] += error * 3 / 16
                pixels[y + 1, x] += error * 5 / 16
                if x + 1 < width:
                    pixels[y + 1, x + 1] += error * 1 / 16
    
    return pixels


def princss_1bit_dither(image: Image.Image, transparent_bg: bool = False) -> Image.Image:
    """
    Apply 1-bit Floyd-Steinberg dithering with exact princss.online colors.
    
    Args:
        image: Input PIL Image (will be converted to grayscale)
        transparent_bg: If True, white pixels become transparent
        
    Returns:
        Dithered image with only RGB(25,5,3) and RGB(255,255,255) or transparent
    """
    # Convert to grayscale float array
    gray = image.convert('L')
    pixels = floyd_steinberg_dither(np.array(gray))
    
    height, width = pixels.shape
    
    if transparent_bg:
        output = Image.new('RGBA', (width, height), COLORS['transparent'])
        output_pixels = output.load()
        for y in range(height):
            for x in range(width):
                if pixels[y, x] < 128:
                    output_pixels[x, y] = COLORS['dark_rgba']
    else:
        output = Image.new('RGB', (width, height))
        output_pixels = output.load()
        for y in range(height):
            for x in range(width):
                if pixels[y, x] > 128:
                    output_pixels[x, y] = COLORS['light']
                else:
                    output_pixels[x, y] = COLORS['dark']
    
    return output


def generate_text_banner(
    text: str,
    width: int = 442,
    height: int = 52,
    font_size: int = 60,
    with_flourish: bool = True,
    dither: bool = True,
    target_text_width: int = 252,
    target_text_height: int = 29,
    gamma: float = 2.2
) -> Image.Image:
    """
    Generate a text banner in princss.online style.
    
    Args:
        text: The text to render
        width: Image width in pixels
        height: Image height in pixels
        font_size: Base font size (rendered at 4x then scaled down)
        with_flourish: Add decorative flourish ornament below text
        dither: Apply 1-bit dithering to text (like original)
        target_text_width: Target width for text after scaling (252 = original)
        target_text_height: Target height for text after scaling (29 = original)
        gamma: Gamma correction for dithering density (2.0 = match original ~29%)
        
    Returns:
        PIL Image with rendered text (RGBA with transparent background)
    """
    font_path = find_font()
    
    # Render at 4x resolution for high-quality anti-aliasing
    render_scale = 4
    font = ImageFont.truetype(font_path, font_size * render_scale)
    
    # Calculate text area height (leave room for flourish if needed)
    text_area_height = height - 17 if with_flourish else height
    
    # Render text at high resolution
    temp = Image.new('L', (2400, 200), 255)
    draw = ImageDraw.Draw(temp)
    
    # Get text dimensions
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Render text at origin
    draw.text((0 - bbox[0], 0 - bbox[1]), text, fill=0, font=font)
    
    # Crop to just the text
    text_only = temp.crop((0, 0, text_width + 4, text_height + 4))
    
    # Scale to target dimensions (creates anti-aliased grays for dithering)
    text_scaled = text_only.resize((target_text_width, target_text_height), Image.LANCZOS)
    
    # Apply gamma correction to darken midtones for more dithering dots
    pixels_pre = np.array(text_scaled, dtype=np.float64)
    pixels_darkened = 255 * np.power(pixels_pre / 255, gamma)
    text_dark = Image.fromarray(pixels_darkened.astype(np.uint8))
    
    # Create grayscale canvas and paste text centered
    text_img = Image.new('L', (width, text_area_height), 255)
    x = (width - target_text_width) // 2
    y = 2  # Start near top like original
    text_img.paste(text_dark, (x, y))
    
    # Apply dithering if requested (use PIL's native Floyd-Steinberg)
    if dither:
        dithered = text_img.convert('1', dither=Image.FLOYDSTEINBERG)
        pixels = np.array(dithered)
        # PIL 1-bit: True=white, False=black
    else:
        pixels = np.array(text_img) > 128  # Simple threshold
    
    # Create output RGBA with transparent background
    output = Image.new('RGBA', (width, height), COLORS['transparent'])
    output_pixels = output.load()
    
    # Add dithered text (invert logic for PIL's 1-bit format)
    for yi in range(text_area_height):
        for xi in range(width):
            if not pixels[yi, xi]:  # False = black pixel
                output_pixels[xi, yi] = COLORS['dark_rgba']
    
    # Add flourish ornament if requested
    if with_flourish:
        flourish = load_flourish()
        if flourish:
            orn_x = (width - flourish.width) // 2
            orn_y = text_area_height
            output.paste(flourish, (orn_x, orn_y), flourish)
    
    return output


def generate_header(
    image_path: str,
    text: str,
    text_height: int = 52,
    font_size: int = 40
) -> Image.Image:
    """
    Generate a combined header with dithered image and text banner.
    
    Args:
        image_path: Path to source image
        text: Text for the banner
        text_height: Height of text banner
        font_size: Font size for text
        
    Returns:
        Combined PIL Image (RGB with white background)
    """
    # Load and dither the image
    source = Image.open(image_path)
    dithered = princss_1bit_dither(source, transparent_bg=False)
    
    # Generate text banner at same width
    text_banner = generate_text_banner(
        text,
        width=dithered.width,
        height=text_height,
        font_size=font_size
    )
    
    # Combine vertically (white background)
    combined_height = dithered.height + text_height
    combined = Image.new('RGB', (dithered.width, combined_height), COLORS['light'])
    combined.paste(dithered, (0, 0))
    
    # Paste text banner (convert RGBA to RGB with white bg)
    text_rgb = Image.new('RGB', text_banner.size, COLORS['light'])
    text_rgb.paste(text_banner, mask=text_banner.split()[3])  # Use alpha as mask
    combined.paste(text_rgb, (0, dithered.height))
    
    return combined


def generate_alt_image(
    input_path: str,
    gamma: float = 1.25,
    size: int = None
) -> Image.Image:
    """
    Generate a princss.online style 'alt' image.
    
    Converts an image to 1-bit dithered style with:
    - Dark color: RGB(25, 5, 3)
    - Transparent background
    - Floyd-Steinberg dithering for scattered dot effect
    
    Args:
        input_path: Path to source image
        gamma: Gamma correction (higher = more dark pixels, default 1.25 for images)
        size: Target size (width and height), preserves aspect ratio. None = keep original.
        
    Returns:
        PIL Image in RGBA format with transparent background
    """
    # Load and convert to grayscale
    img = Image.open(input_path)
    
    # Resize if specified (maintain aspect ratio, fit within size x size)
    if size:
        img.thumbnail((size, size), Image.LANCZOS)
    
    # Convert to grayscale
    gray = img.convert('L')
    
    # Apply gamma correction to darken midtones for more dithering dots
    arr = np.array(gray, dtype=np.float64)
    arr_dark = 255 * np.power(arr / 255, gamma)
    img_dark = Image.fromarray(arr_dark.astype(np.uint8))
    
    # Apply Floyd-Steinberg dithering
    dithered = img_dark.convert('1', dither=Image.FLOYDSTEINBERG)
    dithered_arr = np.array(dithered)
    
    # Create RGBA output with transparent background
    output = Image.new('RGBA', gray.size, COLORS['transparent'])
    output_pixels = output.load()
    
    # Add dark pixels (PIL 1-bit: False = black)
    for y in range(gray.height):
        for x in range(gray.width):
            if not dithered_arr[y, x]:
                output_pixels[x, y] = COLORS['dark_rgba']
    
    return output


def apply_dither_effect(input_path: str, output_path: str):
    """Apply dithering to an image and save."""
    image = Image.open(input_path)
    dithered = princss_1bit_dither(image)
    dithered.save(output_path)
    print(f"Dithered image saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate princss.online style images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Text command
    text_parser = subparsers.add_parser('text', help='Generate text banner')
    text_parser.add_argument('text', help='Text to render')
    text_parser.add_argument('output', help='Output file path')
    text_parser.add_argument('--size', type=int, default=40, help='Font size (default: 40)')
    text_parser.add_argument('--width', type=int, default=442, help='Image width')
    text_parser.add_argument('--height', type=int, default=52, help='Image height')
    text_parser.add_argument('--no-flourish', action='store_true', help='Omit flourish ornament')
    text_parser.add_argument('--no-dither', action='store_true', help='Skip dithering effect')
    
    # Dither command
    dither_parser = subparsers.add_parser('dither', help='Apply 1-bit dithering')
    dither_parser.add_argument('input', help='Input image path')
    dither_parser.add_argument('output', help='Output file path')
    dither_parser.add_argument('--transparent', action='store_true', help='Transparent background')
    
    # Header command
    header_parser = subparsers.add_parser('header', help='Generate image + text header')
    header_parser.add_argument('input', help='Input image path')
    header_parser.add_argument('text', help='Text for banner')
    header_parser.add_argument('output', help='Output file path')
    header_parser.add_argument('--text-height', type=int, default=52, help='Text banner height')
    header_parser.add_argument('--size', type=int, default=40, help='Font size')
    
    # Alt command - generate alt image effect
    alt_parser = subparsers.add_parser('alt', help='Generate alt image (1-bit dithered with transparent bg)')
    alt_parser.add_argument('input', help='Input image path')
    alt_parser.add_argument('output', help='Output file path')
    alt_parser.add_argument('--gamma', type=float, default=1.25, help='Gamma correction (higher = more dark pixels, default 1.25)')
    alt_parser.add_argument('--size', type=int, default=None, help='Resize to fit within size x size (preserves aspect ratio)')
    
    args = parser.parse_args()
    
    if args.command == 'text':
        img = generate_text_banner(
            args.text,
            width=args.width,
            height=args.height,
            font_size=args.size,
            with_flourish=not args.no_flourish,
            dither=not args.no_dither
        )
        img.save(args.output)
        print(f"Text banner saved to: {args.output}")
        
    elif args.command == 'dither':
        image = Image.open(args.input)
        dithered = princss_1bit_dither(image, transparent_bg=args.transparent)
        dithered.save(args.output)
        print(f"Dithered image saved to: {args.output}")
        
    elif args.command == 'header':
        img = generate_header(
            args.input,
            args.text,
            text_height=args.text_height,
            font_size=args.size
        )
        img.save(args.output)
        print(f"Header saved to: {args.output}")
    
    elif args.command == 'alt':
        img = generate_alt_image(
            args.input,
            gamma=args.gamma,
            size=args.size
        )
        img.save(args.output)
        print(f"Alt image saved to: {args.output}")
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
