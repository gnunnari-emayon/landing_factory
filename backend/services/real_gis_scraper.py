import urllib.request
import urllib.parse
import json
import re

def obtener_coordenadas_ciudad(ciudad: str):
    """
    Obtiene latitud y longitud reales de la ciudad usando Nominatim Geocoding API.
    """
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(ciudad)}&format=json&limit=1"
    headers = {"User-Agent": "EmayonForgeCRM/1.0 (contact@emayon.com)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    # Coordenadas por defecto (Mendoza, AR)
    return -32.8895, -68.8458

def obtener_filtro_osm_estricto(rubro: str):
    """
    Retorna el filtro de categoría OpenStreetMap estricto para evitar mezclar rubros irrelevantes.
    """
    r = rubro.lower().strip()
    if any(w in r for w in ["metalurgica", "herreria", "aluminio", "herramientas"]):
        return '["craft"~"metal_construction|blacksmith|welder"]["shop"="hardware"]'
    elif any(w in r for w in ["cafe", "cafeteria", "bar", "resto", "restaurante", "gourmet"]):
        return '["amenity"~"cafe|restaurant|bar"]'
    elif any(w in r for w in ["taller", "mecanico", "mecanica", "lubricentro", "repuestos"]):
        return '["shop"="car_repair"]'
    elif any(w in r for w in ["odontologo", "dentista", "salud dental"]):
        return '["amenity"="dentist"]'
    elif any(w in r for w in ["peluqueria", "barberia", "estetica"]):
        return '["shop"~"hairdresser|beauty"]'
    else:
        return '["shop"]'

def extraer_leads_reales_geolocalizados(tipo: str, ciudad: str, max_results: int = 50):
    """
    Motor B2B de extracción en tiempo real con filtrado categórico semántico estricto.
    """
    lat, lon = obtener_coordenadas_ciudad(ciudad)
    tag_filter = obtener_filtro_osm_estricto(tipo)

    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:15];
    node(around:8000,{lat},{lon}){tag_filter}["name"];
    out body 50;
    """

    leads = []
    seen_names = set()

    try:
        req = urllib.request.Request(
            overpass_url,
            data=overpass_query.encode("utf-8"),
            headers={"User-Agent": "EmayonForgeCRM/1.0"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elements = data.get("elements", [])

            for el in elements:
                tags = el.get("tags", {})
                nombre = tags.get("name")
                
                if not nombre or len(nombre) < 3:
                    continue

                # Filtrar nombres que no pertenezcan al rubro solicitado
                if "metalurgica" in tipo.lower() and any(bad in nombre.lower() for bad in ["restó", "cafe", "café", "bar", "pizza"]):
                    continue

                if nombre.lower() not in seen_names:
                    seen_names.add(nombre.lower())
                    sitio = tags.get("website") or tags.get("contact:website")
                    telefono = tags.get("phone") or tags.get("contact:phone") or tags.get("phone:mobile")

                    if not telefono:
                        try:
                            from backend.services.phone_enricher import enriquecer_telefono_google_maps
                            telefono = enriquecer_telefono_google_maps(nombre, ciudad)
                        except Exception:
                            telefono = None

                    leads.append({
                        "nombre": nombre,
                        "tipo_busqueda": tipo,
                        "ciudad_busqueda": ciudad,
                        "sitio_web": sitio,
                        "telefono": telefono
                    })

                    if len(leads) >= max_results:
                        break
    except Exception as e:
        print(f"Error en Overpass GIS: {e}")

    return leads
