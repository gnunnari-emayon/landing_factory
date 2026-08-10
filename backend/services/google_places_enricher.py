import json
import urllib.request
import urllib.parse
from backend.core.config import config

def enriquecer_prospecto_con_google_places(db, prospecto_model):
    """
    Enriquece un prospecto de la BD trayendo sus últimas 5 reseñas reales y mejores fotos desde Google Places API.
    Guarda URLs de fotos procesadas mediante el proxy interno /api/v1/agencia/foto_proxy?ref=...
    """
    if not prospecto_model:
        return None

    api_key = config.GOOGLE_PLACES_API_KEY
    if not api_key or len(api_key) < 5:
        return prospecto_model

    try:
        place_id = prospecto_model.place_id
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://crm.emayonforge.com/"
        }

        # Si el place_id no es un Place ID real de Google, buscamos en Places Text Search por nombre y ciudad
        if not place_id or place_id.startswith("real_") or place_id.startswith("pyme_") or place_id.startswith("misano_"):
            query_str = f"{prospecto_model.nombre} en {prospecto_model.ciudad_busqueda or 'Cordoba, AR'}"
            url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query_str)}&key={api_key}"
            req_search = urllib.request.Request(url_search, headers=headers)
            with urllib.request.urlopen(req_search) as resp_search:
                search_data = json.loads(resp_search.read().decode())
                results = search_data.get("results", [])
                if results:
                    place_id = results[0].get("place_id")
                    prospecto_model.place_id = place_id

        if place_id and not (place_id.startswith("real_") or place_id.startswith("pyme_")):
            url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,website,formatted_phone_number,rating,user_ratings_total,reviews,photos,formatted_address,editorial_summary&language=es&key={api_key}"
            req_det = urllib.request.Request(url_details, headers=headers)
            with urllib.request.urlopen(req_det) as resp_det:
                det_data = json.loads(resp_det.read().decode()).get("result", {})
                
                if det_data:
                    if det_data.get("rating"):
                        prospecto_model.rating = str(det_data.get("rating"))
                    if det_data.get("editorial_summary", {}).get("overview"):
                        prospecto_model.descripcion_gmaps = det_data["editorial_summary"]["overview"]
                    if det_data.get("user_ratings_total"):
                        prospecto_model.total_reseñas = int(det_data.get("user_ratings_total"))

                    # Fotos reales del establecimiento mediante Proxy backend seguro
                    photos_raw = det_data.get("photos", [])
                    photo_urls = []
                    for p in photos_raw[:6]:
                        pref = p.get("photo_reference")
                        if pref:
                            photo_urls.append(f"/api/v1/agencia/foto_proxy?ref={pref}")
                    if photo_urls:
                        prospecto_model.photos_json = json.dumps(photo_urls, ensure_ascii=False)

                    # Top 5 Reseñas reales escritas por clientes
                    reviews_raw = det_data.get("reviews", [])
                    top_reviews = []
                    for r in reviews_raw[:5]:
                        top_reviews.append({
                            "autor": r.get("author_name"),
                            "rating": r.get("rating"),
                            "texto": r.get("text"),
                            "tiempo": r.get("relative_time_description")
                        })
                    if top_reviews:
                        prospecto_model.reviews_json = json.dumps(top_reviews, ensure_ascii=False)

                    db.commit()
    except Exception as e:
        print(f"⚠️ Error enriqueciendo prospecto {prospecto_model.nombre} con Google Places API: {e}")

    return prospecto_model
