import urllib.request
import urllib.parse
import re

def enriquecer_telefono_google_maps(nombre: str, ciudad: str):
    """
    Escaneo secundario de enriquecimiento para obtener el número telefónico real
    de la ficha comercial de Google Maps / Google Business si no venía en la base inicial.
    """
    query = f"{nombre} {ciudad} telefono"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
            # Buscar patrones telefónicos argentinos/latinoamericanos (ej: 0261 336-3981, +54 261 3363981, 0261-4559000)
            matches = re.findall(r'(\+?54[\s-]?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4}|0?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4})', html)
            for m in matches:
                clean_num = m.replace(" ", "").replace("-", "")
                if len(clean_num) >= 8 and not clean_num.startswith("0800") and not clean_num.startswith("0810"):
                    if clean_num.startswith("0"):
                        clean_num = "+549" + clean_num[1:]
                    elif not clean_num.startswith("+"):
                        clean_num = "+54" + clean_num
                    return clean_num
    except Exception as err:
        print(f"Error enriqueciendo teléfono para '{nombre}': {err}")

    return None
