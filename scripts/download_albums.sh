#!/bin/bash
# Download album covers from various sources

OUTPUT_DIR="/Users/l/roam/hugo/static/media/images/music-images"
mkdir -p "$OUTPUT_DIR"

echo "Downloading album covers..."
echo ""

# Function to download and save
download_album() {
    local filename="$1"
    local search_query="$2"
    local output="$OUTPUT_DIR/$filename"
    
    echo -n "Fetching $filename... "
    
    # Try to get album cover from iTunes API (high quality, no auth needed)
    local itunes_result=$(curl -s "https://itunes.apple.com/search?term=${search_query}&media=music&entity=album&limit=1" \
        | grep -o '"artworkUrl100":"[^"]*"' | head -1 | sed 's/"artworkUrl100":"//;s/"$//')
    
    if [ -n "$itunes_result" ]; then
        # Replace 100x100 with 600x600 for higher resolution
        local hires_url=$(echo "$itunes_result" | sed 's/100x100/600x600/')
        curl -s -o "$output" "$hires_url"
        local size=$(ls -lh "$output" 2>/dev/null | awk '{print $5}')
        echo "OK ($size)"
        return 0
    fi
    
    echo "NOT FOUND"
    return 1
}

# Download each album
download_album "carmen_dragon_romantic_harp.jpg" "carmen+dragon+romantic+harp"
download_album "david_garrett_14.jpg" "david+garrett+14"
download_album "death_in_june_symbols_shatter.jpg" "death+in+june+but+what+ends"
download_album "death_in_june_discriminate.jpg" "death+in+june+discriminate"
download_album "shostakovich_orchestral_works.jpg" "shostakovich+orchestral+works"
download_album "elliott_smith_either_or.jpg" "elliott+smith+either+or"
download_album "elliott_smith_introduction.jpg" "elliott+smith+introduction"
download_album "elliott_smith_xo.jpg" "elliott+smith+xo"
download_album "ghada_ghanem_come_ready.jpg" "ghada+ghanem+come+ready"
download_album "i_monster_neveroddoreven.jpg" "i+monster+neveroddoreven"
download_album "julia_boutros_la_bahlamak.jpg" "julia+boutros"
download_album "leon_fleisher_two_hands.jpg" "leon+fleisher+two+hands"
download_album "leonard_cohen_the_future.jpg" "leonard+cohen+the+future"
download_album "leonard_cohen_various_positions.jpg" "leonard+cohen+various+positions"
download_album "lu_siqing_beauty_violin.jpg" "lu+siqing+violin"
download_album "marcel_khalife_caress.jpg" "marcel+khalife"
download_album "martin_james_bartlett_love_death.jpg" "martin+james+bartlett+love+death"
download_album "mashrou_leila_beirut_school.jpg" "mashrou+leila+beirut+school"
download_album "mashrou_leila_ibn_el_leil.jpg" "mashrou+leila+ibn+el+leil"
download_album "rachid_taha_diwan_2.jpg" "rachid+taha+diwan"
download_album "rene_aubry_plaisirs_damour.jpg" "rene+aubry+plaisirs"
download_album "soheil_peyghambari_assumptions.jpg" "soheil+peyghambari"

echo ""
echo "Done!"
