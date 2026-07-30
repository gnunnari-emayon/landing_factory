import urllib.request
import urllib.parse
import re
from bs4 import BeautifulSoup

def enriquecer_telefono_google_maps(nombre: str, ciudad: str):
    """
    Escaneo secundario de enriquecimiento via DuckDuckGo & Google Search HTML Parser 
    para obtener el número telefónico real de la ficha comercial (ej: CAPS Belisario Roldán -> 0223 482-8871).
    """
    ciudad_clean = ciudad.split(",")[0].strip()
    query = f"{nombre} {ciudad_clean} telefono"
    
    # 1. Probar DuckDuckGo Lite / HTML para fichas comerciales
    url_ddg = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9"
    }

    try:
        req = urllib.request.Request(url_ddg, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
            # Buscar patrones telefónicos argentinos locales (ej: 0223 482-8871, 0223-4828871, 482-8871)
            # Priorizar números que coincidan con el prefijo o formato local
            matches = re.findall(r'(0?\d{3,4}[\s-]?\d{3,4}[\s-]?\d{4})', html)
            for m in matches:
                clean_num = re.sub(r'[^\d]', '', m)
                # Evitar IDs de seguimiento y 0800/0810
                if len(clean_num) in [10, 11] and not clean_num.startswith("0800") and not clean_num.startswith("0810"):
                    if clean_num.startswith("0"):
                        return "+549" + clean_num[1:]
                    return "+54" + clean_num
    except Exception as err:
        print(f"Error DDG enriqueciendo teléfono para '{nombre}': {err}")

    # 2. Fallback: Google Search
    try:
        url_google = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=es&gl=ar"
        req_g = urllib.request.Request(url_google, headers=headers)
        with urllib.request.urlopen(req_g, timeout=5) as resp_g:
            html_g = resp_g.read().decode("utf-8", errors="ignore")
            
            # Buscar en el texto visible del resultado
            soup = BeautifulSoup(html_g, "html.parser")
            text = soup.get_text()
            
            # Buscar formato explícito "0223 482-8871" o "Teléfono: ..."
            match = re.search(r'(0\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4})', text)
            if match:
                clean_num = re.sub(r'[^\d]', '', match.group(1))
                if len(clean_num) in [10, 11] and not clean_num.startswith("0800"):
                    return "+549" + clean_num[1:]
    except Exception as err:
        print(f"Error Google enriqueciendo teléfono para '{nombre}': {err}")

    return None
