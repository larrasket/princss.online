#!/bin/bash
# Download album covers for discoveries section and resize to 118x118

OUTPUT_DIR="/Users/l/roam/hugo/static/media/images/music-images"
mkdir -p "$OUTPUT_DIR"

echo "Downloading discovery album covers..."
echo ""

download_album() {
    local filename="$1"
    local search_query="$2"
    local output="$OUTPUT_DIR/$filename"
    
    echo -n "Fetching $filename... "
    
    # Try iTunes API
    local itunes_result=$(curl -s "https://itunes.apple.com/search?term=${search_query}&media=music&entity=album&limit=1" \
        | grep -o '"artworkUrl100":"[^"]*"' | head -1 | sed 's/"artworkUrl100":"//;s/"$//')
    
    if [ -n "$itunes_result" ]; then
        local hires_url=$(echo "$itunes_result" | sed 's/100x100/600x600/')
        curl -s -o "/tmp/temp_album.jpg" "$hires_url"
        # Resize to 118x118 and convert to PNG
        sips -z 118 118 "/tmp/temp_album.jpg" --out "$output" >/dev/null 2>&1
        rm -f "/tmp/temp_album.jpg"
        local size=$(ls -lh "$output" 2>/dev/null | awk '{print $5}')
        echo "OK ($size)"
        return 0
    fi
    
    echo "NOT FOUND"
    return 1
}

# Matt Elliott albums
download_album "matt_elliott_drinking_songs.png" "matt+elliott+drinking+songs"
download_album "matt_elliott_howling_songs.png" "matt+elliott+howling+songs"

# Leonard Cohen
download_album "leonard_cohen_songs_of_love_and_hate.png" "leonard+cohen+songs+of+love+and+hate"
download_album "leonard_cohen_thanks_for_dance.png" "leonard+cohen+thanks+for+the+dance"

# Death in June (already have some)
download_album "death_in_june_nada.png" "death+in+june+nada"

# Fairuz
download_album "fairuz_legendary.png" "fairuz+legendary"

# Bach
download_album "bach_toccata_fugue.png" "bach+toccata+fugue+organ"
download_album "bach_goldberg_variations.png" "bach+goldberg+variations+gould"

# Elliott Smith (already have)

# Black Hill
download_album "black_hill_silent_watcher.png" "black+hill+silent+watcher"

# Stranger on a Train
download_album "stranger_train_shadowland.png" "stranger+on+a+train"

# Classical pieces
download_album "beethoven_moonlight_sonata.png" "beethoven+moonlight+sonata"
download_album "tchaikovsky_1812_overture.png" "tchaikovsky+1812+overture"

# TSU!
download_album "tsu_prince_gumbay.png" "tsu+prince+gumbay"

# Nostalgic
download_album "ahmed_mounib_best.png" "ahmed+mounib"
download_album "idir_vava_inouva.png" "idir+vava+inouva"

echo ""
echo "Done!"
