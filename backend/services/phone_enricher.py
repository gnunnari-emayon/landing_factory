import urllib.request
import urllib.parse
import re

# Diccionario de prefijos telefónicos de área comunes en Argentina para validación cruzada por ciudad
PREFIJOS_AREA = {
    "buenos aires": ["11", "221", "223", "291", "249", "236"],
    "caba": ["11"],
    "córdoba": ["351", "3541", "353", "358"],
    "rosario": ["341"],
    "santa fe": ["342", "341"],
    "mendoza": ["261", "260", "263"],
    "san juan": ["264"],
    "salta": ["387"],
    "tucumán": ["381"],
    "jujuy": ["388"],
    "neuquén": ["299"],
    "bariloche": ["294"],
    "corrientes": ["379"],
    "posadas": ["376"],
    "resistencia": ["362"],
    "paranÃ¡": ["343"],
    "mar del plata": ["223"]
}

def extraer_whatsapp_directo(html: str) -> str | None:
    """Extrae números explícitos de WhatsApp Web / API desde links o metatags."""
    # Buscar patrones wa.me/549..., api.whatsapp.com/send?phone=549...
    wa_matches = re.findall(r'(?:wa\.me|whatsapp\.com/send\?phone=)(\d{10,13})', html)
    for num in wa_matches:
        if num.startswith("54"):
            return "+" + num
        elif len(num) == 10:
            return "+549" + num
        elif len(num) == 11 and num.startswith("0"):
            return "+549" + num[1:]

    return None

def validar_y_formatear_telefono_ar(num_raw: str, ciudad: str) -> str | None:
    """Valida que un número numérico pertenezca a la estructura válida de telefonía argentina."""
    clean_num = re.sub(r'[^\d]', '', num_raw)

    # Si empieza con 54, quitar prefijo para analizar la longitud local
    if clean_num.startswith("54"):
        clean_num = clean_num[2:]
    if clean_num.startswith("9") and len(clean_num) == 11:
        clean_num = clean_num[1:]
    if clean_num.startswith("0"):
        clean_num = clean_num[1:]

    # Un número válido en Argentina (código de área + abonado) debe tener 10 dígitos exactamente
    if len(clean_num) != 10:
        return None

    # Descartar números de cobro o no geográficos
    if clean_num.startswith("800") or clean_num.startswith("810") or clean_num.startswith("178") or clean_num.startswith("000"):
        return None

    # Verificar si coincide con los prefijos conocidos de la ciudad si está en la lista
    ciudad_lower = ciudad.lower()
    prefijos_validos = []
    for c_key, p_list in PREFIJOS_AREA.items():
        if c_key in ciudad_lower:
            prefijos_validos.extend(p_list)

    if prefijos_validos:
        if not any(clean_num.startswith(p) for p in prefijos_validos):
            # Si tiene un prefijo de área diferente pero es un celular de 10 dígitos válido en AR (ej 11, 351, 264, etc.), permitirlo si es de área real argentina
            todas_las_areas = [p for sublist in PREFIJOS_AREA.values() for p in sublist]
            if not any(clean_num.startswith(p) for p in todas_las_areas):
                return None

    # Formatear E.164 estándar internacional (+54 9 AAAA BBBBBB)
    area = clean_num[:3] if clean_num.startswith(("264", "351", "341", "387", "381", "261", "223")) else (clean_num[:2] if clean_num.startswith("11") else clean_num[:4])
    local = clean_num[len(area):]
    return f"+54 9 {area} {local}"

def enriquecer_telefono_google_maps(nombre: str, ciudad: str) -> str | None:
    """
    Escaneo secundario de enriquecimiento multicanal via DuckDuckGo & Google Search
    para extraer WhatsApps verificados o teléfonos oficiales de fichas en FB/IG/Google.
    """
    ciudad_clean = ciudad.split(",")[0].strip()
    query = f'"{nombre}" {ciudad_clean} whatsapp telefono instagram facebook'
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9"
    }

    # 1. Probar DuckDuckGo HTML / Social Search
    url_ddg = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}&kl=ar-es"
    try:
        req = urllib.request.Request(url_ddg, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
            # Prioridad A: Enlace directo de WhatsApp (wa.me)
            wa = extraer_whatsapp_directo(html)
            if wa:
                return wa

            # Prioridad B: Coincidencias numéricas con regex estricto
            matches = re.findall(r'(?:tel|cel|wa|contacto|whatsapp|llamada)?[:\s]*(\+?54[\s-]?9?[\s-]?)?(0?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4})', html, re.IGNORECASE)
            for prefix, m in matches:
                valido = validar_y_formatear_telefono_ar(m, ciudad)
                if valido:
                    return valido
    except Exception:
        pass

    # 3. Fallback adicional: Bing Search (Redes Sociales & Directorios Comerciales)
    try:
        url_bing = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&cc=AR"
        req_b = urllib.request.Request(url_bing, headers=headers)
        with urllib.request.urlopen(req_b, timeout=5) as resp_b:
            html_b = resp_b.read().decode("utf-8", errors="ignore")
            
            wa_b = extraer_whatsapp_directo(html_b)
            if wa_b:
                return wa_b

            matches_b = re.findall(r'(?:tel|cel|wa|contacto|whatsapp|llamada)?[:\s]*(\+?54[\s-]?9?[\s-]?)?(0?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4})', html_b, re.IGNORECASE)
            for prefix, m in matches_b:
                valido = validar_y_formatear_telefono_ar(m, ciudad)
                if valido:
                    return valido
    except Exception as err_b:
        pass

    # 4. Fallback final Poka-Yoke: Búsqueda específica en Instagram / Facebook Business Snippets
    try:
        query_social = f'site:facebook.com OR site:instagram.com "{nombre}" {ciudad_clean} "telefono" OR "whatsapp"'
        url_social = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query_social)}"
        req_s = urllib.request.Request(url_social, headers=headers)
        with urllib.request.urlopen(req_s, timeout=5) as resp_s:
            html_s = resp_s.read().decode("utf-8", errors="ignore")
            
            wa_s = extraer_whatsapp_directo(html_s)
            if wa_s:
                return wa_s

            matches_s = re.findall(r'(?:tel|cel|wa|contacto|whatsapp)?[:\s]*(\+?54[\s-]?9?[\s-]?)?(0?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4})', html_s, re.IGNORECASE)
            for prefix, m in matches_s:
                valido = validar_y_formatear_telefono_ar(m, ciudad)
                if valido:
                    return valido
    except Exception:
        pass

    return None
