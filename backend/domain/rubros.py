"""
Catálogo Unificado de Rubros Comerciales y Categorías Visuales
Single Source of Truth para Autocompletado, Búsquedas y Motor de Inferencia de Landings.
"""

from enum import Enum
from typing import Dict, List, Any


class RubroCategoria(str, Enum):
    TALLER_MECANICO = "taller_mecanico"
    GASTRONOMIA = "gastronomia"
    SALUD_BELLEZA = "salud_belleza"
    RETAIL = "retail"
    LOGISTICA = "logistica"
    TECNOLOGIA = "tecnologia"
    SERVICIOS_HOGAR = "servicios_hogar"
    EDUCACION = "educacion"
    INMOBILIARIA = "inmobiliaria"
    METALURGICA = "metalurgica"
    JURIDICO = "juridico"
    CONTABILIDAD = "contabilidad"
    CONSTRUCCION = "construccion"
    CORPORATIVO = "corporativo"


RUBROS_MASTER: List[Dict[str, Any]] = [
    {
        "id": RubroCategoria.TALLER_MECANICO.value,
        "nombre": "Taller Mecánico & Automotor",
        "categoria_visual": RubroCategoria.TALLER_MECANICO.value,
        "synonyms": [
            "taller mecanico", "taller mecánico", "mecanica", "mecánica", "repuestos", "lubricentro", "auto", "autos", 
            "automotor", "lavadero", "gomeria", "gomería", "concesionaria", "chapa", "pintura",
            "moto", "motos", "motocicleta", "motocicletas", "motomecanica", "motomecánica", "scooter",
            "suspension", "suspensiones", "amortiguador", "amortiguadores", "frenos", "alineacion", "alineación",
            "balanceo", "mecanico", "mecánico", "electromecanica", "electromecánica", "neumaticos", "neumáticos",
            "llantas", "baterias", "baterías", "inyeccion", "inyección", "escape", "escapes", "embrague", "embragues",
            "motor", "motores", "taller automotor"
        ]
    },
    {
        "id": RubroCategoria.GASTRONOMIA.value,
        "nombre": "Cafetería & Gastronomía",
        "categoria_visual": RubroCategoria.GASTRONOMIA.value,
        "synonyms": [
            "cafeteria", "café", "cafe", "bar", "resto", "restaurante", "restaurant", 
            "rotiseria", "rotisería", "comida", "pizza", "pizzeria", "pizzería", "sushi", 
            "panaderia", "panadería", "heladeria", "heladería", "parrilla", "bistro", "catering", "gastronomia"
        ]
    },
    {
        "id": RubroCategoria.LOGISTICA.value,
        "nombre": "Fletes & Logística",
        "categoria_visual": RubroCategoria.LOGISTICA.value,
        "synonyms": [
            "flete", "fletes", "mudanza", "mudanzas", "logistica", "logística", 
            "transporte", "envio", "envíos", "envios", "correo", "distribuidora", "cargas"
        ]
    },
    {
        "id": RubroCategoria.SALUD_BELLEZA.value,
        "nombre": "Odontología & Salud Dental",
        "categoria_visual": RubroCategoria.SALUD_BELLEZA.value,
        "synonyms": [
            "odontologo", "odontología", "dentista", "clinica dental", "ortodoncia", "clinica", "clínica",
            "medico", "médico", "medicina", "estetica", "estética", "spa", "peluqueria", "peluquería",
            "barberia", "barbería", "cosmetica", "cosmética", "psicologia", "psicología", "belleza", "salud"
        ]
    },
    {
        "id": RubroCategoria.JURIDICO.value,
        "nombre": "Estudio Jurídico & Abogados",
        "categoria_visual": RubroCategoria.JURIDICO.value,
        "synonyms": ["abogado", "estudio juridico", "legales", "derecho", "abogados"]
    },
    {
        "id": RubroCategoria.CONTABILIDAD.value,
        "nombre": "Estudio Contable & Asesoría",
        "categoria_visual": RubroCategoria.CONTABILIDAD.value,
        "synonyms": ["contador", "estudio contable", "impuestos", "finanzas", "asesoria"]
    },
    {
        "id": RubroCategoria.INMOBILIARIA.value,
        "nombre": "Inmobiliaria & Bienes Raíces",
        "categoria_visual": RubroCategoria.INMOBILIARIA.value,
        "synonyms": ["inmobiliaria", "propiedades", "alquileres", "bienes raices", "bienes raíces", "realtor"]
    },
    {
        "id": RubroCategoria.CONSTRUCCION.value,
        "nombre": "Construcción & Corralón",
        "categoria_visual": RubroCategoria.CONSTRUCCION.value,
        "synonyms": ["construccion", "construcción", "corralon", "corralón", "arquitectura", "reformas"]
    },
    {
        "id": RubroCategoria.METALURGICA.value,
        "nombre": "Metalúrgica & Herrería",
        "categoria_visual": RubroCategoria.METALURGICA.value,
        "synonyms": ["metalurgica", "metalúrgica", "herreria", "herrería", "talleres metalurgicos", "aluminio"]
    },
    {
        "id": RubroCategoria.RETAIL.value,
        "nombre": "Retail & Comercio",
        "categoria_visual": RubroCategoria.RETAIL.value,
        "synonyms": [
            "tienda", "boutique", "ropa", "calzado", "indumentaria", "mercado", "bazar", 
            "super", "supermercado", "joyeria", "joyería", "electronica", "electrónica", "comercial"
        ]
    },
    {
        "id": RubroCategoria.TECNOLOGIA.value,
        "nombre": "Tecnología & Software",
        "categoria_visual": RubroCategoria.TECNOLOGIA.value,
        "synonyms": [
            "software", "sistemas", "tech", "technology", "digital", "web", "desarrollo", 
            "app", "apps", "informatica", "informática", "it", "ciberseguridad", "nube", "cloud"
        ]
    },
    {
        "id": RubroCategoria.SERVICIOS_HOGAR.value,
        "nombre": "Servicios para el Hogar",
        "categoria_visual": RubroCategoria.SERVICIOS_HOGAR.value,
        "synonyms": [
            "plomeria", "plomería", "electricidad", "electricista", "pintura", "refrigeracion", 
            "refrigeración", "aire acondicionado", "cerrajeria", "cerrajería", "limpieza", "fumigacion", "fumigación"
        ]
    },
    {
        "id": RubroCategoria.EDUCACION.value,
        "nombre": "Educación & Academias",
        "categoria_visual": RubroCategoria.EDUCACION.value,
        "synonyms": [
            "instituto", "academia", "colegio", "escuela", "cursos", "capacitacion", 
            "capacitación", "clases", "universidad", "tutoria", "tutoría", "enseñanza"
        ]
    }
]

# Mapa derivado de keywords por categoría para el generador de Landings
CATEGORIA_KEYWORDS: Dict[str, List[str]] = {
    rubro["categoria_visual"]: rubro["synonyms"]
    for rubro in RUBROS_MASTER
}


def clasificar_y_refinar_rubro(nombre_negocio: str, rubro_busqueda: str = "") -> str:
    """
    Analiza el nombre comercial y el término de búsqueda para retornar el nombre del rubro más preciso.
    Prioriza la detección de palabras clave en el NOMBRE del negocio sobre la búsqueda genérica.
    """
    from backend.services.generator import inferir_categoria_por_rubro

    # 1. Prioridad: Evaluar coincidencia específica en el NOMBRE del negocio
    if nombre_negocio:
        cat_nombre = inferir_categoria_por_rubro(nombre_negocio)
        if cat_nombre != "corporativo":
            for r in RUBROS_MASTER:
                if r["categoria_visual"] == cat_nombre or r["id"] == cat_nombre:
                    return r["nombre"]

    # 2. Fallback: Evaluar el término de búsqueda si el nombre no dio resultado directo
    if rubro_busqueda:
        cat_busqueda = inferir_categoria_por_rubro(rubro_busqueda)
        for r in RUBROS_MASTER:
            if r["categoria_visual"] == cat_busqueda or r["id"] == cat_busqueda:
                return r["nombre"]
        return rubro_busqueda.title()

    return "Servicios Generales"

