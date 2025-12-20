#!/bin/bash

# Script to compress and resize all JPEG images in the current directory
# Target dimensions: ~230x345 pixels (maintaining aspect ratio)

echo "Starting image compression..."

# Check if ImageMagick is available
if ! command -v magick &> /dev/null && ! command -v convert &> /dev/null; then
    echo "Error: ImageMagick is not installed. Please install it first:"
    echo "  brew install imagemagick"
    exit 1
fi

# Determine which command to use
if command -v magick &> /dev/null; then
    MAGICK_CMD="magick"
else
    MAGICK_CMD="convert"
fi

# Create backup directory
mkdir -p backup
echo "Created backup directory"

# Counter for processed files
processed=0

# Process all JPG files
for file in *.jpg; do
    if [ -f "$file" ]; then
        echo "Processing: $file"

        # Create backup
        cp "$file" "backup/$file"

        # Get current dimensions
        current_width=$($MAGICK_CMD identify -format "%w" "$file" 2>/dev/null)
        current_height=$($MAGICK_CMD identify -format "%h" "$file" 2>/dev/null)

        echo "  Current size: ${current_width}x${current_height}"

        # Calculate target dimensions
        # If image is portrait (taller than wide), use 345 as max height
        # If image is landscape or square, use 230 as max width
        if [ "$current_height" -gt "$current_width" ]; then
            # Portrait - target height 345
            target_height=345
            $MAGICK_CMD "$file" -resize x$target_height -quality 85 -strip "$file"
        else
            # Landscape/square - target width 230
            target_width=230
            $MAGICK_CMD "$file" -resize $target_width -quality 85 -strip "$file"
        fi

        # Get new dimensions
        new_width=$($MAGICK_CMD identify -format "%w" "$file" 2>/dev/null)
        new_height=$($MAGICK_CMD identify -format "%h" "$file" 2>/dev/null)

        echo "  New size: ${new_width}x${new_height}"

        processed=$((processed + 1))
    fi
done

echo ""
echo "Compression complete!"
echo "Processed $processed images"
echo "Original files backed up in 'backup' directory"