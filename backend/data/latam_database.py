"""
Base de datos de Rubros Comerciales y Ciudades / Provincias de Latinoamérica
para autocompletado e inferencia inteligente de búsquedas B2B.
"""

from backend.domain.rubros import RUBROS_MASTER

RUBROS_LATAM = RUBROS_MASTER


UBICACIONES_LATAM = [
    # Argentina
    {"ciudad": "Córdoba", "provincia": "Córdoba", "pais": "Argentina", "formato": "Córdoba, Córdoba, Argentina", "lat": -31.4201, "lon": -64.1888},
    {"ciudad": "Mendoza", "provincia": "Mendoza", "pais": "Argentina", "formato": "Mendoza, Mendoza, Argentina", "lat": -32.8895, "lon": -68.8458},
    {"ciudad": "Rosario", "provincia": "Santa Fe", "pais": "Argentina", "formato": "Rosario, Santa Fe, Argentina", "lat": -32.9442, "lon": -60.6505},
    {"ciudad": "Buenos Aires", "provincia": "CABA", "pais": "Argentina", "formato": "Buenos Aires, CABA, Argentina", "lat": -34.6037, "lon": -58.3816},
    {"ciudad": "Salta", "provincia": "Salta", "pais": "Argentina", "formato": "Salta, Salta, Argentina", "lat": -24.7892, "lon": -65.4103},
    {"ciudad": "San Miguel de Tucumán", "provincia": "Tucumán", "pais": "Argentina", "formato": "San Miguel de Tucumán, Tucumán, Argentina", "lat": -26.8241, "lon": -65.2226},
    {"ciudad": "Mar del Plata", "provincia": "Buenos Aires", "pais": "Argentina", "formato": "Mar del Plata, Buenos Aires, Argentina", "lat": -38.0055, "lon": -57.5426},
    {"ciudad": "Neuquén", "provincia": "Neuquén", "pais": "Argentina", "formato": "Neuquén, Neuquén, Argentina", "lat": -38.9516, "lon": -68.0591},
    {"ciudad": "San Juan", "provincia": "San Juan", "pais": "Argentina", "formato": "San Juan, San Juan, Argentina", "lat": -31.5375, "lon": -68.5364},
    {"ciudad": "Bariloche", "provincia": "Río Negro", "pais": "Argentina", "formato": "Bariloche, Río Negro, Argentina", "lat": -41.1335, "lon": -71.3103},
    {"ciudad": "Santa Fe", "provincia": "Santa Fe", "pais": "Argentina", "formato": "Santa Fe, Santa Fe, Argentina", "lat": -31.6333, "lon": -60.7000},
    {"ciudad": "Resistencia", "provincia": "Chaco", "pais": "Argentina", "formato": "Resistencia, Chaco, Argentina", "lat": -27.4606, "lon": -58.9839},

    # Chile
    {"ciudad": "Santiago", "provincia": "Región Metropolitana", "pais": "Chile", "formato": "Santiago, Región Metropolitana, Chile", "lat": -33.4489, "lon": -70.6693},
    {"ciudad": "Valparaíso", "provincia": "Valparaíso", "pais": "Chile", "formato": "Valparaíso, Valparaíso, Chile", "lat": -33.0472, "lon": -71.6127},
    {"ciudad": "Concepción", "provincia": "Biobío", "pais": "Chile", "formato": "Concepción, Biobío, Chile", "lat": -36.8201, "lon": -73.0444},
    
    # Uruguay
    {"ciudad": "Montevideo", "provincia": "Montevideo", "pais": "Uruguay", "formato": "Montevideo, Montevideo, Uruguay", "lat": -34.9011, "lon": -56.1645},
    {"ciudad": "Punta del Este", "provincia": "Maldonado", "pais": "Uruguay", "formato": "Punta del Este, Maldonado, Uruguay", "lat": -34.9626, "lon": -54.9431},

    # Colombia
    {"ciudad": "Bogotá", "provincia": "Cundinamarca", "pais": "Colombia", "formato": "Bogotá, Cundinamarca, Colombia", "lat": 4.7110, "lon": -74.0721},
    {"ciudad": "Medellín", "provincia": "Antioquia", "pais": "Colombia", "formato": "Medellín, Antioquia, Colombia", "lat": 6.2442, "lon": -75.5812},
    {"ciudad": "Cali", "provincia": "Valle del Cauca", "pais": "Colombia", "formato": "Cali, Valle del Cauca, Colombia", "lat": 3.4516, "lon": -76.5320},

    # México
    {"ciudad": "Ciudad de México", "provincia": "CDMX", "pais": "México", "formato": "Ciudad de México, CDMX, México", "lat": 19.4326, "lon": -99.1332},
    {"ciudad": "Guadalajara", "provincia": "Jalisco", "pais": "México", "formato": "Guadalajara, Jalisco, México", "lat": 20.6597, "lon": -103.3496},
    {"ciudad": "Monterrey", "provincia": "Nuevo León", "pais": "México", "formato": "Monterrey, Nuevo León, México", "lat": 25.6866, "lon": -100.3161},

    # Perú
    {"ciudad": "Lima", "provincia": "Lima", "pais": "Perú", "formato": "Lima, Lima, Perú", "lat": -12.0464, "lon": -77.0428},
    {"ciudad": "Arequipa", "provincia": "Arequipa", "pais": "Perú", "formato": "Arequipa, Arequipa, Perú", "lat": -16.4090, "lon": -71.5375}
]

def autocompletar_rubro(query: str):
    q = query.lower().strip()
    if not q:
        return RUBROS_LATAM[:5]
    res = []
    for r in RUBROS_LATAM:
        if q in r["nombre"].lower() or any(q in s for s in r["synonyms"]):
            res.append(r)
    return res if res else [{"id": q, "nombre": query.title(), "synonyms": [q]}]

def autocompletar_ubicacion(query: str):
    q = query.lower().strip()
    if not q:
        return UBICACIONES_LATAM[:5]
    res = []
    for u in UBICACIONES_LATAM:
        text = f"{u['ciudad']} {u['provincia']} {u['pais']} {u['formato']}".lower()
        if q in text:
            res.append(u)
    return res if res else [{"ciudad": query.title(), "provincia": "LATAM", "pais": "Argentina", "formato": f"{query.title()}, Argentina", "lat": -31.4201, "lon": -64.1888}]
