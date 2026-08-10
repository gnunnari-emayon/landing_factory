import os
import re
import json
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)

def construir_demo_html(
    place_id: str,
    nombre: str,
    rubro: str,
    cat_visual: str,
    theme: dict,
    ctx_web: dict,
    prospecto: dict = None,
    precio: float = 350,
    dominio: str = "miempresa.com",
    telefono_wa: str = None
) -> tuple[str, str]:
    """
    Construye y guarda el HTML de la demo comercial para un prospecto B2B.
    Retorna una tupla: (filepath, link_wa)
    """
    ciudad_prospecto = (prospecto.get("ciudad_busqueda") if prospecto else None) or "Rosario, AR"
    
    # Directorio de salida de la demo
    demos_dir = os.path.join(BASE_DIR, "frontend", "demos")
    os.makedirs(demos_dir, exist_ok=True)
    filepath = os.path.join(demos_dir, f"{place_id}.html")

    # Link de WhatsApp
    link_wa = ""
    if telefono_wa and telefono_wa != "Por verificar":
        num_clean = re.sub(r"[^\d]", "", telefono_wa)
        msg_wa = f"Hola {nombre}, preparé una demo comercial exclusiva de su nuevo sitio web ({dominio}): http://localhost:8000/static/demos/{place_id}.html"
        link_wa = f"https://wa.me/{num_clean}?text={msg_wa.replace(' ', '%20')}"

    nav_wa_link = link_wa if link_wa else "#"

    # Reseñas
    reviews_data = []
    if prospecto and prospecto.get("reviews_json"):
        try:
            reviews_data = json.loads(prospecto["reviews_json"]) if isinstance(prospecto["reviews_json"], str) else prospecto["reviews_json"]
        except Exception:
            reviews_data = []

    if not reviews_data:
        from backend.services.google_reviews_service import obtener_resenas_reales_google
        raw_fallback = obtener_resenas_reales_google(nombre, ciudad_prospecto) or []
        reviews_data = [{"autor": r.get("name", "Cliente"), "rating": 5, "texto": r.get("comment", ""), "tiempo": "Reciente"} for r in raw_fallback]

    # Formatear datos de reseñas para Jinja2
    formatted_reviews = []
    for rev in reviews_data[:6]:
        autor = rev.get("autor") or rev.get("name") or "Cliente Verificado"
        formatted_reviews.append({
            "autor": autor,
            "autor_initial": autor[0].upper() if autor else "C",
            "rating_num": int(rev.get("rating") or 5),
            "texto": rev.get("texto") or rev.get("comment") or "",
            "tiempo": rev.get("tiempo") or "Hace un mes"
        })

    # Fotos reales de Google Maps
    photos_data = []
    if prospecto and prospecto.get("photos_json"):
        try:
            photos_data = json.loads(prospecto["photos_json"]) if isinstance(prospecto["photos_json"], str) else prospecto["photos_json"]
        except Exception:
            photos_data = []

    hero_bg_img = photos_data[0] if photos_data else theme.get("hero_image", "")

    # Características / Servicios
    features_items = []
    items_features = theme.get("features", [])[:6]
    seed_hash = sum(ord(c) for c in place_id)
    services_offset = seed_hash % 6
    news_offset = (seed_hash + 3) % 6

    for idx, feat in enumerate(items_features):
        # Asignación de foto: Si existen fotos de Google Maps, usamos la foto correspondiente (partiendo de idx+1)
        if photos_data and (idx + 1) < len(photos_data):
            img_path = photos_data[idx + 1]
        elif photos_data and idx < len(photos_data):
            img_path = photos_data[idx]
        elif "image_key" in feat:
            img_path = f"/static/img/services/{feat['image_key']}.jpg"
        else:
            img_num = ((idx + services_offset) % 6) + 1
            img_path = f"/static/img/services/{cat_visual}_{img_num}.jpg"

        features_items.append({
            "img_path": img_path,
            "icon": feat.get("icon", "fa-check"),
            "tag": feat.get("tag", "Servicio"),
            "title": feat.get("title", ""),
            "desc": feat.get("desc", "")
        })

    # Noticias / Novedades
    news_items = []
    for idx, item in enumerate(theme.get("news", [])):
        if "image_key" in item:
            news_img_path = f"/static/img/news/{item['image_key']}.jpg"
        else:
            news_img_num = ((idx + news_offset) % 6) + 1
            news_img_path = f"/static/img/news/{cat_visual}_news_{news_img_num}.jpg"

        news_items.append({
            "news_img_path": news_img_path,
            "date": item.get("date", ""),
            "read_time": item.get("read_time", ""),
            "title": item.get("title", ""),
            "snippet": item.get("snippet", "")
        })

    # Rating general del prospecto
    rating_general = "4.8"
    total_reseñas = 0
    if prospecto:
        rating_general = prospecto.get("rating", "4.8") or "4.8"
        total_reseñas = prospecto.get("total_reseñas", 0) or 0

    # Descripción del negocio: cascada de fuentes (Google Maps → DuckDuckGo → theme genérico)
    descripcion_negocio = ""
    if prospecto and prospecto.get("descripcion_gmaps"):
        descripcion_negocio = prospecto["descripcion_gmaps"]
    elif ctx_web and ctx_web.get("resumen_web"):
        descripcion_negocio = ctx_web["resumen_web"]
    if not descripcion_negocio:
        descripcion_negocio = f"Especialistas en {rubro} en {ciudad_prospecto}. Compromiso, trayectoria y atención personalizada."

    # CTA contextual y horarios del rubro
    cta_rubro_text = theme.get("cta_text", "Solicitar Información")
    horarios_atencion = theme.get("hours", "Lunes a Viernes: 09:00 - 18:00 hs")

    # Renderizar plantilla
    template = env.get_template("demos/demo_landing_template.html")
    html_rendered = template.render(
        nombre=nombre,
        rubro=rubro,
        cat_visual=cat_visual,
        theme=theme,
        ciudad_prospecto=ciudad_prospecto,
        dominio=dominio,
        link_wa=link_wa,
        nav_wa_link=nav_wa_link,
        hero_bg_img=hero_bg_img,
        features_items=features_items,
        news_items=news_items,
        reviews_data=formatted_reviews,
        photos_data=photos_data,
        rating_general=rating_general,
        total_reseñas=total_reseñas,
        descripcion_negocio=descripcion_negocio,
        cta_rubro_text=cta_rubro_text,
        horarios_atencion=horarios_atencion,
        precio=precio
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_rendered)

    return filepath, link_wa
