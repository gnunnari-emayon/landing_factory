import os
import re

# Diccionario de palabras clave por categoría visual
CATEGORIA_KEYWORDS = {
    "gastronomia": [
        "café", "cafe", "cafetería", "cafeteria", "bar", "restaurante", "restaurant", 
        "rotisería", "rotiseria", "comida", "pizza", "pizzería", "pizzeria", "sushi", 
        "panadería", "panaderia", "heladería", "heladeria", "parrilla", "bistro", "catering", "gastronomia"
    ],
    "automotriz": [
        "taller", "mecánico", "mecanico", "auto", "autos", "automotor", "repuestos", 
        "lavadero", "gomería", "gomeria", "lubricentro", "concesionaria", "chapa", "pintura"
    ],
    "salud_belleza": [
        "clínica", "clinica", "odontología", "odontologia", "dental", "médico", "medico", 
        "medicina", "estética", "estetica", "spa", "peluquería", "peluqueria", "barbería", 
        "barberia", "cosmética", "cosmetica", "psicología", "psicologia", "belleza", "salud"
    ],
    "retail": [
        "tienda", "boutique", "ropa", "calzado", "indumentaria", "mercado", "bazar", 
        "super", "supermercado", "joyería", "joyeria", "electrónica", "electronica", "comercial"
    ],
    "logistica": [
        "flete", "fletes", "transporte", "mudanza", "mudanzas", "envío", "envio", 
        "envíos", "envios", "logística", "logistica", "correo", "distribuidora", "cargas"
    ],
    "tecnologia": [
        "software", "sistemas", "tech", "technology", "digital", "web", "desarrollo", 
        "app", "apps", "informática", "informatica", "it", "ciberseguridad", "nube", "cloud"
    ],
    "servicios_hogar": [
        "plomería", "plomeria", "electricidad", "electricista", "pintura", "refrigeración", 
        "refrigeracion", "aire acondicionado", "cerrajería", "cerrajeria", "limpieza", "fumigación", "reformas"
    ],
    "educacion": [
        "instituto", "academia", "colegio", "escuela", "cursos", "capacitación", 
        "capacitacion", "clases", "universidad", "tutoría", "tutoria", "enseñanza"
    ],
    "inmobiliaria": [
        "inmobiliaria", "propiedades", "bienes raíces", "bienes raices", "alquileres", "realtor"
    ]
}

def inferir_categoria_por_rubro(rubro_o_nombre: str) -> str:
    """
    Fallback Inteligente: Analiza el texto del rubro o nombre comercial 
    y devuelve la categoría visual correspondiente.
    Si no encuentra ninguna coincidencia, retorna 'corporativo'.
    """
    if not rubro_o_nombre:
        return "corporativo"

    texto_limpio = rubro_o_nombre.lower()

    for categoria, keywords in CATEGORIA_KEYWORDS.items():
        for kw in keywords:
            # Usar coincidencia exacta de límite de palabra (\b) para evitar falsos positivos (ej: 'bar' en 'barbería')
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, texto_limpio):
                return categoria

    return "corporativo"


def generar_landing_page(nombre_negocio: str, rubro: str, ia_client=None) -> dict:
    """
    Genera la configuración y contenido de una landing page.
    Utiliza el cliente de IA si está disponible; de lo contrario o ante falla,
    aplica inferir_categoria_por_rubro para garantizar variedad visual por rubro.
    """
    categoria_visual = None

    # Intentar obtener la categoría visual mediante llamada a la IA si existe cliente
    if ia_client:
        try:
            # Simulación o llamada a API de IA
            respuesta = ia_client.clasificar_rubro(nombre_negocio=nombre_negocio, rubro=rubro)
            categoria_visual = respuesta.get("categoria")
        except Exception as e:
            # Fallo en la llamada a la IA -> log y activación de fallback
            print(f"[WARN] Llamada a IA falló o no devolvió respuesta ({e}). Activando Fallback Inteligente.")
            categoria_visual = None

    # Si la IA no devolvió categoría válida, aplicamos el Fallback Inteligente
    if not categoria_visual:
        texto_busqueda = f"{nombre_negocio} {rubro}"
        categoria_visual = inferir_categoria_por_rubro(texto_busqueda)

    return {
        "nombre_negocio": nombre_negocio,
        "rubro": rubro,
        "categoria_visual": categoria_visual,
        "status": "success",
        "fallback_aplicado": categoria_visual != "corporativo" and not ia_client
    }


if __name__ == "__main__":
    # Prueba rápida en consola
    ejemplos = [
        ("Café de la Plaza", "Gastronomía / Cafetería"),
        ("Taller San José", "Reparación de Automóviles"),
        ("Clínica Odontológica Sonrisas", "Salud y Medicina"),
        ("Fletes Express SRL", "Transporte y Envíos"),
        ("ByteLogic", "Desarrollo de Software y Cloud"),
        ("Moda & Estilo", "Boutique de Ropa"),
        ("Empresa Consultora Global", "Servicios Varios")
    ]
    
    print("--- Verificación de Fallback Inteligente por Rubro ---")
    for nombre, rubro in ejemplos:
        res = generar_landing_page(nombre, rubro)
        print(f"Negocio: {nombre} | Rubro: {rubro} -> Categoría Visual: [{res['categoria_visual']}]")
