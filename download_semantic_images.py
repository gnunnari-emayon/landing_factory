import sys
import os
import requests
from PIL import Image
from io import BytesIO
from duckduckgo_search import DDGS
from itertools import islice
import time

# Agregar backend al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from services.landing_theme_engine import THEMES_POR_CATEGORIA

BASE_DIR = os.path.dirname(__file__)
SERVICES_DIR = os.path.join(BASE_DIR, "frontend", "img", "services")
NEWS_DIR = os.path.join(BASE_DIR, "frontend", "img", "news")

os.makedirs(SERVICES_DIR, exist_ok=True)
os.makedirs(NEWS_DIR, exist_ok=True)

ddgs = DDGS()

def fetch_image(query, filepath, max_retries=3):
    if os.path.exists(filepath):
        # Already exists, but we want real images.
        # Check if it's the synthetic one from before. 
        # Synthetic ones are small (around 10KB to 20KB maybe).
        if os.path.getsize(filepath) > 50000:
            print(f"Skipping {filepath}, already downloaded large image.")
            return True
            
    print(f"Searching: {query}")
    for attempt in range(max_retries):
        try:
            results = list(islice(ddgs.images(query, max_results=5, type_image="photo", layout="Wide", size="Large"), 5))
            if not results:
                print(f"No results for {query}")
                return False
                
            for res in results:
                url = res.get("image")
                if not url:
                    continue
                try:
                    print(f"  Downloading {url}")
                    resp = requests.get(url, timeout=10)
                    resp.raise_for_status()
                    img = Image.open(BytesIO(resp.content)).convert("RGB")
                    # Resize and crop to 800x600 for consistency
                    target_ratio = 800 / 600
                    width, height = img.size
                    ratio = width / height
                    if ratio > target_ratio:
                        new_width = int(height * target_ratio)
                        offset = (width - new_width) // 2
                        img = img.crop((offset, 0, offset + new_width, height))
                    else:
                        new_height = int(width / target_ratio)
                        offset = (height - new_height) // 2
                        img = img.crop((0, offset, width, offset + new_height))
                    img = img.resize((800, 600), Image.Resampling.LANCZOS)
                    img.save(filepath, "JPEG", quality=85)
                    print(f"  Saved {filepath}")
                    time.sleep(1) # delay to avoid rate limiting
                    return True
                except Exception as e:
                    print(f"  Failed url {url}: {e}")
                    continue
                    
            print(f"All 5 images failed for {query}")
        except Exception as e:
            print(f"DuckDuckGo error: {e}")
            time.sleep(2)
            
    return False

def main():
    total = 0
    success = 0
    for category_name, theme in THEMES_POR_CATEGORIA.items():
        print(f"\nProcessing category: {category_name}")
        
        # Services
        for feature in theme.get("features", []):
            image_key = feature.get("image_key")
            title = feature.get("title", "")
            if not image_key:
                continue
            
            filepath = os.path.join(SERVICES_DIR, f"{image_key}.jpg")
            query = f"{category_name} {title} high quality photo"
            total += 1
            if fetch_image(query, filepath):
                success += 1

        # News
        for news_item in theme.get("news", []):
            image_key = news_item.get("image_key")
            title = news_item.get("title", "")
            if not image_key:
                continue
            
            filepath = os.path.join(NEWS_DIR, f"{image_key}.jpg")
            query = f"{category_name} {title} high quality photo"
            total += 1
            if fetch_image(query, filepath):
                success += 1
                
    print(f"\nDone! Successfully downloaded {success}/{total} images.")

if __name__ == "__main__":
    main()
