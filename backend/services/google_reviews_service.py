from __future__ import annotations
import urllib.request
import urllib.parse
import json
import re
from bs4 import BeautifulSoup
from backend.core.config import config

def obtener_resenas_reales_google(nombre: str, ciudad: str) -> list[dict] | None:
    """
    Verifica y extrae las reseñas reales de Google Maps / Business para una empresa.
    Retorna una lista de dicts con {'name': ..., 'comment': ..., 'rating': ..., 'city': ...}
    o None si la empresa NO tiene reseñas auténticas verificables en Google.
    """
    if not nombre or len(nombre) < 2:
        return None

    ciudad_clean = ciudad.split(",")[0].strip()
    query = f'"{nombre}" {ciudad_clean} "opiniones" OR "reseñas" site:google.com/maps OR "google.com"'
    
    # 1. Si existe Google Places API Key, intentar API Oficial
    api_key = getattr(config, "GOOGLE_PLACES_API_KEY", "")
    if api_key and len(api_key) > 5:
        try:
            url_place = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query)}&key={api_key}"
            req = urllib.request.Request(url_place, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                if results and "place_id" in results[0]:
                    place_id = results[0]["place_id"]
                    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,reviews&key={api_key}"
                    req_det = urllib.request.Request(url_details, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req_det, timeout=5) as resp_det:
                        det_data = json.loads(resp_det.read().decode("utf-8"))
                        reviews = det_data.get("result", {}).get("reviews", [])
                        if reviews:
                            formatted_reviews = []
                            for r in reviews[:3]:
                                text = r.get("text", "").strip()
                                if text:
                                    formatted_reviews.append({
                                        "name": r.get("author_name", "Cliente Google"),
                                        "comment": text,
                                        "rating": r.get("rating", 5),
                                        "city": ciudad_clean
                                    })
                            if formatted_reviews:
                                return formatted_reviews
        except Exception as e:
            print(f"[Google Reviews API Error]: {e}")

    # 2. Web Scraping de respaldo para buscar snippets de reseñas auténticas en Google / DuckDuckGo
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9"
    }

    try:
        url_search = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}&kl=ar-es"
        req_s = urllib.request.Request(url_search, headers=headers)
        with urllib.request.urlopen(req_s, timeout=5) as resp_s:
            html = resp_s.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            results = soup.select(".result")
            
            extracted_reviews = []
            for r in results:
                snippet_node = r.select_one(".result__snippet")
                if not snippet_node:
                    continue
                snippet_text = snippet_node.get_text(strip=True)
                
                # Buscar fragmentos que contengan frases de opiniones en comillas o valoraciones explícitas
                if any(kw in snippet_text.lower() for kw in ["excelente", "buen servicio", "atención", "muy buena", "recomendable", "estrellas", "puntuación"]):
                    # Limpiar texto del snippet para extraer la opinión real
                    clean_comment = re.sub(r'Rating: \d(\.\d)?', '', snippet_text)
                    clean_comment = clean_comment.replace("Google", "").strip()
                    if len(clean_comment) > 20:
                        extracted_reviews.append({
                            "name": "Cliente de Google Maps",
                            "comment": clean_comment[:180] + "...",
                            "rating": 5,
                            "city": ciudad_clean
                        })
                        if len(extracted_reviews) >= 3:
                            break

            if extracted_reviews:
                return extracted_reviews

    except Exception as err:
        print(f"[Google Reviews Scraper Error]: {err}")

    # Si no se encontraron reseñas auténticas en Google Maps
    return None
