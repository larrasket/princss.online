#!/usr/bin/env python3
"""
Download movie posters from TMDB API.
Uses the free TMDB API - requires an API key from https://www.themoviedb.org/settings/api
"""

import requests
import os
from pathlib import Path
import sys
import time

# TMDB API configuration
# Get your free API key from: https://www.themoviedb.org/settings/api
API_KEY = os.environ.get("TMDB_API_KEY", "")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

# Movies to download (name, year, output_filename)
MOVIES = [
    ("The Banshees of Inisherin", 2022, "banshees-of-inisherin.jpg"),
    ("3-Iron", 2004, "3-iron.jpg"),
    ("Being There", 1979, "being-there.jpg"),
    ("Detachment", 2011, "detachment.jpg"),
    ("Falling Down", 1993, "falling-down.jpg"),
    ("The House That Jack Built", 2018, "house-that-jack-built.jpg"),
    ("Phantom Thread", 2017, "phantom-thread.jpg"),
    ("Roger Dodger", 2002, "roger-dodger.jpg"),
    ("The Royal Tenenbaums", 2001, "royal-tenenbaums.jpg"),
    ("Ted K", 2021, "ted-k.jpg"),
]

OUTPUT_DIR = Path(__file__).parent.parent / "static/media/images/films-images"


def search_movie(title: str, year: int) -> dict | None:
    """Search for a movie on TMDB."""
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "year": year,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[0] if results else None


def download_poster(poster_path: str, output_file: Path) -> bool:
    """Download a poster image."""
    if not poster_path:
        return False
    
    url = f"{IMAGE_BASE_URL}{poster_path}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    output_file.write_bytes(response.content)
    return True


def main():
    if not API_KEY:
        print("Error: TMDB_API_KEY environment variable not set")
        print("Get a free API key from: https://www.themoviedb.org/settings/api")
        print("Then run: export TMDB_API_KEY='your_key_here'")
        sys.exit(1)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    for title, year, filename in MOVIES:
        output_file = OUTPUT_DIR / filename
        print(f"Searching: {title} ({year})...", end=" ", flush=True)
        
        try:
            movie = search_movie(title, year)
            if not movie:
                print("NOT FOUND")
                continue
            
            poster_path = movie.get("poster_path")
            if download_poster(poster_path, output_file):
                size = output_file.stat().st_size / 1024
                print(f"OK ({size:.1f} KB)")
                success_count += 1
            else:
                print("NO POSTER")
            
            time.sleep(0.25)  # Rate limiting
            
        except Exception as e:
            print(f"ERROR: {e}")
    
    print(f"\nDownloaded {success_count}/{len(MOVIES)} posters")


if __name__ == "__main__":
    main()
