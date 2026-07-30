import os
import json
import re
import urllib.request
import urllib.parse
from backend.services.domain_checker import es_sitio_web_propio

def extraer_leads_reales_google(tipo: str, ciudad: str, max_results: int = 50):
    """
    Motor de prospección real profunda vía Google Search / Google Maps Scraper nativo.
    Extrae directamente empresas reales publicadas en los índices de Google.
    """
    leads = []
    seen_names = set()
    ciudad_clean = ciudad.split(",")[0].strip()
    query = f"{tipo} en {ciudad_clean}"

    # Google Search URL con headers de navegador de escritorio real
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=es&gl=ar"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

            # Extraer todos los h3 (títulos de resultados) y buscar sus enlaces o nombres
            h3_matches = re.findall(r'<h3[^>]*>(.*?)</h3>', html)
            links_raw = re.findall(r'href="(https?://[^"]+)"', html)

            for idx, h3_text in enumerate(h3_matches):
                nombre = re.sub(r'<[^>]+>', '', h3_text).strip()
                nombre_clean = nombre.split("-")[0].split("|")[0].split(":")[0].strip()

                palabras_ignorar = ["google", "wikipedia", "los 10 mejores", "top 10", "guía de", "directorio", "mejores en", "mapa"]
                if any(p in nombre_clean.lower() for p in palabras_ignorar):
                    continue

                if len(nombre_clean) >= 3 and len(nombre_clean) <= 80 and nombre_clean.lower() not in seen_names:
                    seen_names.add(nombre_clean.lower())
                    site_url = links_raw[idx] if idx < len(links_raw) else None

                    leads.append({
                        "nombre": nombre_clean,
                        "tipo_busqueda": tipo,
                        "ciudad_busqueda": ciudad,
                        "sitio_web": site_url if site_url and "google" not in site_url else None,
                        "telefono": None
                    })

                    if len(leads) >= max_results:
                        break
    except Exception as err:
        print(f"Error escaneando Google Search: {err}")

    return leads
