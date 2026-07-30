"""
Base de datos de Rubros Comerciales y Ciudades / Provincias de Latinoamérica
para autocompletado e inferencia inteligente de búsquedas B2B.
"""

RUBROS_LATAM = [
    {"id": "metalurgica", "nombre": "Metalúrgica & Herrería", "synonyms": ["metalurgica", "herreria", "talleres metalurgicos", "aluminio"]},
    {"id": "cafeteria", "nombre": "Cafetería & Gastronomía", "synonyms": ["cafeteria", "cafe", "bar", "resto", "restaurante", "gourmet"]},
    {"id": "fletes", "nombre": "Fletes & Logística", "synonyms": ["fletes", "mudanzas", "logistica", "transporte", "envios"]},
    {"id": "odontologo", "nombre": "Odontología & Salud Dental", "synonyms": ["odontologo", "dentista", "clinica dental", "ortodoncia"]},
    {"id": "taller_mecanico", "nombre": "Taller Mecánico & Automotor", "synonyms": ["taller mecanico", "mecanica", "repuestos", "lubricentro"]},
    {"id": "estetica", "nombre": "Estética & Peluquería", "synonyms": ["estetica", "peluqueria", "barberia", "spa", "centro de estetica"]},
    {"id": "abogado", "nombre": "Estudio Jurídico & Abogados", "synonyms": ["abogado", "estudio juridico", "legales", "derecho"]},
    {"id": "contabilidad", "nombre": "Estudio Contable & Asesoría", "synonyms": ["contador", "estudio contable", "impuestos", "finanzas"]},
    {"id": "inmobiliaria", "nombre": "Inmobiliaria & Bienes Raíces", "synonyms": ["inmobiliaria", "propiedades", "alquileres", "bienes raices"]},
    {"id": "construccion", "nombre": "Construcción & Corralón", "synonyms": ["construccion", "corralon", "arquitectura", "reformas"]}
]

UBICACIONES_LATAM = [
    # Argentina
    {"ciudad": "Mendoza", "provincia": "Mendoza", "pais": "Argentina", "lat": -32.8895, "lon": -68.8458},
    {"ciudad": "Salta", "provincia": "Salta", "pais": "Argentina", "lat": -24.7892, "lon": -65.4103},
    {"ciudad": "Córdoba", "provincia": "Córdoba", "pais": "Argentina", "lat": -31.4201, "lon": -64.1888},
    {"ciudad": "Rosario", "provincia": "Santa Fe", "pais": "Argentina", "lat": -32.9442, "lon": -60.6505},
    {"ciudad": "Buenos Aires", "provincia": "CABA", "pais": "Argentina", "lat": -34.6037, "lon": -58.3816},
    {"ciudad": "San Miguel de Tucumán", "provincia": "Tucumán", "pais": "Argentina", "lat": -26.8241, "lon": -65.2226},
    {"ciudad": "Mar del Plata", "provincia": "Buenos Aires", "pais": "Argentina", "lat": -38.0055, "lon": -57.5426},
    {"ciudad": "Neuquén", "provincia": "Neuquén", "pais": "Argentina", "lat": -38.9516, "lon": -68.0591},
    {"ciudad": "San Juan", "provincia": "San Juan", "pais": "Argentina", "lat": -31.5375, "lon": -68.5364},
    {"ciudad": "Bariloche", "provincia": "Río Negro", "pais": "Argentina", "lat": -41.1335, "lon": -71.3103},
    
    # Chile
    {"ciudad": "Santiago", "provincia": "Región Metropolitana", "pais": "Chile", "lat": -33.4489, "lon": -70.6693},
    {"ciudad": "Valparaíso", "provincia": "Valparaíso", "pais": "Chile", "lat": -33.0472, "lon": -71.6127},
    {"ciudad": "Concepción", "provincia": "Biobío", "pais": "Chile", "lat": -36.8201, "lon": -73.0444},
    
    # Uruguay
    {"ciudad": "Montevideo", "provincia": "Montevideo", "pais": "Uruguay", "lat": -34.9011, "lon": -56.1645},
    {"ciudad": "Punta del Este", "provincia": "Maldonado", "pais": "Uruguay", "lat": -34.9626, "lon": -54.9431},

    # Colombia
    {"ciudad": "Bogotá", "provincia": "Cundinamarca", "pais": "Colombia", "lat": 4.7110, "lon": -74.0721},
    {"ciudad": "Medellín", "provincia": "Antioquia", "pais": "Colombia", "lat": 6.2442, "lon": -75.5812},
    {"ciudad": "Cali", "provincia": "Valle del Cauca", "pais": "Colombia", "lat": 3.4516, "lon": -76.5320},

    # México
    {"ciudad": "Ciudad de México", "provincia": "CDMX", "pais": "México", "lat": 19.4326, "lon": -99.1332},
    {"ciudad": "Guadalajara", "provincia": "Jalisco", "pais": "México", "lat": 20.6597, "lon": -103.3496},
    {"ciudad": "Monterrey", "provincia": "Nuevo León", "pais": "México", "lat": 25.6866, "lon": -100.3161},

    # Perú
    {"ciudad": "Lima", "provincia": "Lima", "pais": "Perú", "lat": -12.0464, "lon": -77.0428},
    {"ciudad": "Arequipa", "provincia": "Arequipa", "pais": "Perú", "lat": -16.4090, "lon": -71.5375}
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
        text = f"{u['ciudad']} {u['provincia']} {u['pais']}".lower()
        if q in text:
            res.append(u)
    return res if res else [{"ciudad": query.title(), "provincia": "LATAM", "pais": "", "lat": -31.4201, "lon": -64.1888}]
