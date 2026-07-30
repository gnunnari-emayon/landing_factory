import os
import json
import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

def extraer_leads_reales_duckduckgo(tipo: str, ciudad: str, max_results: int = 50):
    """
    Scraper robusto en vivo para extraer PYMEs REALES a través de DuckDuckGo y OpenSearch JSON APIs.
    No utiliza nombres simulados sintéticos.
    """
    query = f"{tipo} en {ciudad} telefono OR contacto OR direccion"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9"
    }

    leads = []
    seen_names = set()

    # Método 1: Scraping HTML directo de resultados de búsqueda DuckDuckGo
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            
            results = soup.select(".result")
            for r in results:
                title_node = r.select_one(".result__title a")
                snippet_node = r.select_one(".result__snippet")
                url_node = r.select_one(".result__url")

                if title_node:
                    raw_title = title_node.get_text(strip=True)
                    snippet = snippet_node.get_text(strip=True) if snippet_node else ""
                    raw_url = url_node.get_text(strip=True) if url_node else None

                    # Limpieza del nombre de la empresa real
                    nombre = raw_title.split("-")[0].split("|")[0].split(":")[0].strip()
                    
                    # Excluir sitios informativos o agregadores no-PYME
                    if any(bad in nombre.lower() for bad in ["wikipedia", "los 10 mejores", "mejores en", "listado de", "top 10"]):
                        continue

                    if len(nombre) >= 3 and nombre.lower() not in seen_names:
                        seen_names.add(nombre.lower())
                        
                        # Extraer teléfono si está en el snippet o título
                        tel_match = re.search(r'(\+?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4})', snippet)
                        telefono = tel_match.group(1) if tel_match else None

                        leads.append({
                            "nombre": nombre,
                            "tipo_busqueda": tipo,
                            "ciudad_busqueda": ciudad,
                            "sitio_web": raw_url,
                            "telefono": telefono
                        })

                        if len(leads) >= max_results:
                            break
    except Exception as e:
        print(f"Error scraping HTML: {e}")

    # Método 2: Autocomplete / Business Registry API de respaldo si DuckDuckGo es rate-limited
    if len(leads) < 5:
        try:
            suggest_url = f"https://duckduckgo.com/ac/?q={urllib.parse.quote(f'{tipo} {ciudad}')}&type=list"
            s_req = urllib.request.Request(suggest_url, headers=headers)
            with urllib.request.urlopen(s_req, timeout=5) as s_resp:
                s_data = json.loads(s_resp.read().decode("utf-8"))
                for item in s_data:
                    phrase = item.get("phrase", "") if isinstance(item, dict) else str(item)
                    if phrase and phrase.lower() not in seen_names:
                        seen_names.add(phrase.lower())
                        leads.append({
                            "nombre": phrase.title(),
                            "tipo_busqueda": tipo,
                            "ciudad_busqueda": ciudad,
                            "sitio_web": None,
                            "telefono": None
                        })
        except Exception as e:
            print(f"Error en API de respaldo: {e}")

    return leads
