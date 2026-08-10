import sys
import os
import requests
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from services.landing_theme_engine import THEMES_POR_CATEGORIA

BASE_DIR = os.path.dirname(__file__)
SERVICES_DIR = os.path.join(BASE_DIR, "frontend", "img", "services")
NEWS_DIR = os.path.join(BASE_DIR, "frontend", "img", "news")

os.makedirs(SERVICES_DIR, exist_ok=True)
os.makedirs(NEWS_DIR, exist_ok=True)

# Map rubros to english keywords for loremflickr
CATEGORY_KEYWORDS = {
    "gastronomia": "restaurant,food,gourmet",
    "motos": "motorcycle,mechanic,workshop",
    "automotriz": "car,mechanic,auto",
    "salud_belleza": "spa,skincare,medical,clinic",
    "inmobiliaria": "house,realestate,apartment",
    "tecnologia": "technology,software,server,code",
    "retail": "retail,store,shopping",
    "logistica": "logistics,shipping,truck,warehouse",
    "servicios_hogar": "plumber,electrician,repair,home",
    "educacion": "education,university,student,classroom",
    "corporativo": "corporate,business,office,team"
}

def download_loremflickr(keywords, filepath):
    # Only skip if we already downloaded a real image (file size > 40KB)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 40000:
        return True
        
    url = f"https://loremflickr.com/800/600/{keywords}/all"
    try:
        r = requests.get(url, allow_redirects=True, timeout=15)
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(r.content)
        print(f"Downloaded {filepath} with keywords: {keywords}")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Failed to download {filepath}: {e}")
        return False

def main():
    total = 0
    success = 0
    for category_name, theme in THEMES_POR_CATEGORIA.items():
        keywords = CATEGORY_KEYWORDS.get(category_name, "business")
        
        for feature in theme.get("features", []):
            image_key = feature.get("image_key")
            if not image_key: continue
            
            filepath = os.path.join(SERVICES_DIR, f"{image_key}.jpg")
            total += 1
            if download_loremflickr(keywords, filepath):
                success += 1

        for news_item in theme.get("news", []):
            image_key = news_item.get("image_key")
            if not image_key: continue
            
            filepath = os.path.join(NEWS_DIR, f"{image_key}.jpg")
            total += 1
            if download_loremflickr(keywords, filepath):
                success += 1
                
    print(f"\nDone! Successfully downloaded {success}/{total} images.")

if __name__ == "__main__":
    main()
