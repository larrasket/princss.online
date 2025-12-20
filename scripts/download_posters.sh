#!/bin/bash
# Download movie posters from IMDB using curl
# Each URL is the high-res poster image from IMDB's CDN

OUTPUT_DIR="/Users/l/roam/hugo/static/media/images/films-images"
mkdir -p "$OUTPUT_DIR"

# Array of movies: "filename|imdb_title_id"
declare -a MOVIES=(
    "banshees-of-inisherin.jpg|tt11813216"
    "3-iron.jpg|tt0423866"
    "being-there.jpg|tt0078841"
    "detachment.jpg|tt1683526"
    "falling-down.jpg|tt0106856"
    "house-that-jack-built.jpg|tt4003440"
    "phantom-thread.jpg|tt5776858"
    "roger-dodger.jpg|tt0299117"
    "royal-tenenbaums.jpg|tt0265666"
    "ted-k.jpg|tt8128276"
)

echo "Downloading movie posters from IMDB..."
echo ""

for movie in "${MOVIES[@]}"; do
    filename="${movie%|*}"
    imdb_id="${movie#*|}"
    output="$OUTPUT_DIR/$filename"
    
    echo -n "Fetching $filename... "
    
    # Get IMDB page and extract poster URL from JSON-LD data
    poster_url=$(curl -s "https://www.imdb.com/title/$imdb_id/" \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
        | grep -o '"image":"[^"]*"' | head -1 | sed 's/"image":"//;s/"$//')
    
    if [ -n "$poster_url" ]; then
        # Download the poster
        curl -s -o "$output" "$poster_url" \
            -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        
        size=$(ls -lh "$output" 2>/dev/null | awk '{print $5}')
        echo "OK ($size)"
    else
        echo "FAILED (no poster URL found)"
    fi
    
    sleep 0.3
done

echo ""
echo "Done! Check $OUTPUT_DIR"
