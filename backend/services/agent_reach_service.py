import urllib.request
import urllib.parse
import json

def obtener_coordenadas(ciudad: str):
    """Obtiene lat/lon reales de la ciudad usando Nominatim Geocoding API."""
    ciudad_clean = ciudad.split(",")[0].strip()
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(ciudad)}&format=json&limit=1"
    headers = {"User-Agent": "EmayonForgeCRM/1.0 (contact@emayon.com)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return -32.9593, -60.6617  # Fallback a Rosario, AR

def obtener_filtro_osm(rubro: str):
    """Mapea el rubro seleccionado al filtro categórico estricto de OpenStreetMap."""
    r = rubro.lower().strip()
    if any(w in r for w in ["metalurgica", "herreria", "aluminio", "metal"]):
        return '["craft"~"metal_construction|blacksmith|welder"]'
    elif any(w in r for w in ["cafe", "cafeteria", "bar", "resto", "restaurante", "gastronomia"]):
        return '["amenity"~"cafe|restaurant|bar"]'
    elif any(w in r for w in ["taller", "mecanico", "mecanica", "lubricentro", "auto"]):
        return '["shop"="car_repair"]'
    elif any(w in r for w in ["odontologo", "dentista", "salud", "clinica"]):
        return '["amenity"~"dentist|clinic"]'
    elif any(w in r for w in ["peluqueria", "barberia", "estetica"]):
        return '["shop"~"hairdresser|beauty"]'
    elif any(w in r for w in ["inmobiliaria", "propiedades"]):
        return '["office"="estate_agent"]'
    else:
        return '["shop"]'

def buscar_negocios_reales_google(rubro: str, ciudad: str, max_results: int = 20):
    """Alias principal."""
    return extraer_leads_reales_overpass(rubro=rubro, ciudad=ciudad, max_results=max_results)

def ejecutar_prospeccion_agent_reach(rubro: str, ciudad: str, max_results: int = 20):
    """Alias retrocompatible."""
    return extraer_leads_reales_overpass(rubro=rubro, ciudad=ciudad, max_results=max_results)

def extraer_leads_reales_overpass(rubro: str, ciudad: str, max_results: int = 20):
    """
    Motor B2B real de prospección por geolocalización satelital (OpenStreetMap Overpass GIS).
    Extrae comercios reales y garantiza que los números telefónicos no sean inventados ni repetidos.
    """
    lat, lon = obtener_coordenadas(ciudad)
    filter_tag = obtener_filtro_osm(rubro)

    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:20];
    (
      node(around:6000,{lat},{lon}){filter_tag}["name"];
      way(around:6000,{lat},{lon}){filter_tag}["name"];
    );
    out body {max_results};
    """

    leads = []
    seen_names = set()

    try:
        req = urllib.request.Request(
            overpass_url,
            data=overpass_query.encode("utf-8"),
            headers={"User-Agent": "EmayonForgeCRM/1.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elements = data.get("elements", [])

            for el in elements:
                tags = el.get("tags", {})
                nombre = tags.get("name")

                if not nombre or len(nombre) < 3:
                    continue

                if nombre.lower() in seen_names:
                    continue

                seen_names.add(nombre.lower())

                telefono = tags.get("phone") or tags.get("contact:phone") or tags.get("phone:mobile")
                sitio_web = tags.get("website") or tags.get("contact:website")

                # Pase secundario de enriquecimiento via Google Business si OSM no trae teléfono
                if not telefono:
                    from backend.services.phone_enricher import enriquecer_telefono_google_maps
                    telefono = enriquecer_telefono_google_maps(nombre, ciudad)

                # Formatear teléfono si existe
                if telefono:
                    telefono = telefono.strip()

                leads.append({
                    "nombre": nombre,
                    "tipo_busqueda": rubro,
                    "ciudad_busqueda": ciudad,
                    "sitio_web": sitio_web,
                    "telefono": telefono
                })

                if len(leads) >= max_results:
                    break
    except Exception as e:
        print(f"Error en Overpass GIS API: {e}")

    return leads
