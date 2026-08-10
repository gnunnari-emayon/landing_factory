import sys
import os
import requests
import re
from PIL import Image
from io import BytesIO
import urllib.parse
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from services.landing_theme_engine import THEMES_POR_CATEGORIA

BASE_DIR = os.path.dirname(__file__)
SERVICES_DIR = os.path.join(BASE_DIR, "frontend", "img", "services")
NEWS_DIR = os.path.join(BASE_DIR, "frontend", "img", "news")

os.makedirs(SERVICES_DIR, exist_ok=True)
os.makedirs(NEWS_DIR, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def get_unsplash_image(query, filepath):
    # Skip if we already downloaded a real image (file size > 50KB)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 50000:
        return True
        
    print(f"Searching Unsplash for: {query}")
    # We translate some common keywords to English for better Unsplash results
    query_en = query.replace("gastronomia", "restaurant food").replace("motos", "motorcycle mechanic").replace("automotriz", "car mechanic").replace("salud_belleza", "beauty spa medical").replace("inmobiliaria", "real estate").replace("tecnologia", "technology software").replace("retail", "retail store").replace("logistica", "logistics shipping").replace("servicios_hogar", "home repair service").replace("educacion", "education classroom").replace("corporativo", "corporate business")
    
    encoded_query = urllib.parse.quote(query_en)
    url = f"https://unsplash.com/s/photos/{encoded_query}"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Find image URLs in the page source
        # Unsplash image URLs look like: https://images.unsplash.com/photo-123456789-abcdef?
        matches = re.findall(r'https://images\.unsplash\.com/photo-[a-zA-Z0-9\-]+', r.text)
        
        # Filter unique base URLs
        unique_matches = list(dict.fromkeys(matches))
        
        if not unique_matches:
            print(f"  No images found for {query}")
            return False
            
        # Try downloading the first matching image
        for img_url in unique_matches[:3]:
            # Append high quality parameters
            download_url = f"{img_url}?w=800&h=600&fit=crop&auto=format&q=80"
            try:
                print(f"  Downloading {download_url}")
                img_resp = requests.get(download_url, headers=headers, timeout=10)
                img_resp.raise_for_status()
                
                # Verify it's a valid image
                img = Image.open(BytesIO(img_resp.content)).convert("RGB")
                img.save(filepath, "JPEG", quality=85)
                print(f"  Saved {filepath}")
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"  Failed downloading {img_url}: {e}")
                
        return False
    except Exception as e:
        print(f"  Request failed: {e}")
        return False

def main():
    total = 0
    success = 0
    for category_name, theme in THEMES_POR_CATEGORIA.items():
        print(f"\nProcessing category: {category_name}")
        
        for feature in theme.get("features", []):
            image_key = feature.get("image_key")
            title = feature.get("title", "")
            if not image_key:
                continue
            
            filepath = os.path.join(SERVICES_DIR, f"{image_key}.jpg")
            query = f"{category_name} {title}"
            total += 1
            if get_unsplash_image(query, filepath):
                success += 1

        for news_item in theme.get("news", []):
            image_key = news_item.get("image_key")
            title = news_item.get("title", "")
            if not image_key:
                continue
            
            filepath = os.path.join(NEWS_DIR, f"{image_key}.jpg")
            query = f"{category_name} {title}"
            total += 1
            if get_unsplash_image(query, filepath):
                success += 1
                
    print(f"\nDone! Successfully downloaded {success}/{total} images.")

if __name__ == "__main__":
    main()
