import re
import uuid
import datetime
from typing import Dict, List, Optional
from backend.models.schemas import ClienteLanding, LandingResponse

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

# Plantillas enriquecidas por categoría visual
PLANTILLAS_NICHO = {
    "gastronomia": {
        "tagline": "Experiencias gastronómicas de calidad superior",
        "hero_headline": "Sabores auténticos hechos con pasión y los mejores ingredientes",
        "hero_subheadline": "Disfruta de una propuesta culinaria única en un ambiente acogedor o desde la comodidad de tu hogar.",
        "cta_texto": "Reservar Mesa / Hacer Pedido",
        "beneficios": [
            {"titulo": "Ingredientes Frescos", "descripcion": "Seleccionamos materia prima de máxima calidad diariamente.", "icono": "🍳"},
            {"titulo": "Entrega Rápida", "descripcion": "Delivery optimizado para conservar el sabor y la temperatura ideal.", "icono": "🚀"},
            {"titulo": "Recetas de Autor", "descripcion": "Platos exclusivos diseñados por nuestros chefs especializados.", "icono": "⭐"}
        ],
        "servicios": [
            {"titulo": "Atención en Salón", "descripcion": "Espacios confortables y atención personalizada para familias y eventos.", "icono": "🍷"},
            {"titulo": "Servicio de Delivery & Take Away", "descripcion": "Envíos veloces empaquetados térmicamente sin perder textura.", "icono": "🛵"},
            {"titulo": "Catering para Eventos", "descripcion": "Menús a medida para reuniones corporativas y celebraciones especiales.", "icono": "🎉"}
        ],
        "testimonio": {
            "autor": "Sofía Martínez",
            "cargo": "Cliente Frecuente",
            "comentario": "La calidad de los platos es extraordinaria y el servicio siempre es cálido y rápido. Totalmente recomendado.",
            "estrellas": 5
        }
    },
    "automotriz": {
        "tagline": "Especialistas en diagnóstico y mantenimiento vehicular",
        "hero_headline": "Tu vehículo en manos de profesionales certificados",
        "hero_subheadline": "Mantenimiento preventivo, mecánica general y reparación express con repuestos originales.",
        "cta_texto": "Solicitar Cotización por WhatsApp",
        "beneficios": [
            {"titulo": "Diagnóstico Computarizado", "descripcion": "Detección precisa de fallas con escáneres de última generación.", "icono": "💻"},
            {"titulo": "Garantía Escrita", "descripcion": "Respaldamos todos nuestros trabajos de mecánica y repuestos.", "icono": "🛡️"},
            {"titulo": "Entrega Puntual", "descripcion": "Respetamos los tiempos acordados para que no frenes tu rutina.", "icono": "⏱️"}
        ],
        "servicios": [
            {"titulo": "Mecánica General & Service", "descripcion": "Cambio de aceite, filtros, frenos, suspensión y alineación.", "icono": "🛠️"},
            {"titulo": "Electricidad & Diagnóstico", "descripcion": "Reparación de sistemas eléctricos, baterías y sensores.", "icono": "⚡"},
            {"titulo": "Inyección & Motor", "descripcion": "Ajustes de precisión y optimización del rendimiento vehicular.", "icono": "🚗"}
        ],
        "testimonio": {
            "autor": "Carlos Rodríguez",
            "cargo": "Propietario de Flota",
            "comentario": "Excelente atención y honestidad total en los diagnósticos. Me solucionaron un problema complejo en tiempo récord.",
            "estrellas": 5
        }
    },
    "salud_belleza": {
        "tagline": "Cuidado integral, estética y bienestar para tu vida",
        "hero_headline": "Potencia tu bienestar con tratamientos especializados",
        "hero_subheadline": "Un espacio diseñado para brindarte calma, resultados visibles y atención personalizada de primer nivel.",
        "cta_texto": "Agendar Turno Online",
        "beneficios": [
            {"titulo": "Profesionales Titulados", "descripcion": "Equipo experto comprometido con tu salud y confort.", "icono": "👨‍⚕️"},
            {"titulo": "Tecnología Avanzada", "descripcion": "Equipamiento de vanguardia en procedimientos y tratamientos.", "icono": "✨"},
            {"titulo": "Ambiente Relax", "descripcion": "Instalaciones diseñadas para brindarte desconexión y confort absoluto.", "icono": "🌿"}
        ],
        "servicios": [
            {"titulo": "Tratamientos Faciales & Corporales", "descripcion": "Protocolos a medida para rejuvenecimiento y cuidado cutáneo.", "icono": "💆‍♀️"},
            {"titulo": "Odontología & Estética Dental", "descripcion": "Diseño de sonrisa, blanqueamiento y profilaxis avanzada.", "icono": "🦷"},
            {"titulo": "Masajes & SpaTerapia", "descripcion": "Sesiones descontracturantes, relajantes y drenaje linfático.", "icono": "🌸"}
        ],
        "testimonio": {
            "autor": "Valeria Gómez",
            "cargo": "Paciente",
            "comentario": "Increíble la calidez del equipo y los resultados de los tratamientos. Volveré sin dudas.",
            "estrellas": 5
        }
    },
    "logistica": {
        "tagline": "Soluciones eficientes de transporte y distribución",
        "hero_headline": "Conectamos tu carga con su destino seguro y a tiempo",
        "hero_subheadline": "Fletes, mudanzas y logística integral con seguimiento constante y flota adaptada a tus necesidades.",
        "cta_texto": "Cotizar Envío Inmediato",
        "beneficios": [
            {"titulo": "Rastreo en Tiempo Real", "descripcion": "Monitoreo GPS continuo de todas nuestras unidades en viaje.", "icono": "📍"},
            {"titulo": "Unidades Equipadas", "descripcion": "Camiones y vans adaptados con amarres y protección para tus bienes.", "icono": "🚛"},
            {"titulo": "Seguro de Carga", "descripcion": "Cobertura completa para garantizar la integridad de tus envíos.", "icono": "🔒"}
        ],
        "servicios": [
            {"titulo": "Fletes & Mudanzas Express", "descripcion": "Servicio de traslado residencial y comercial con personal de carga.", "icono": "📦"},
            {"titulo": "Distribución Última Milla", "descripcion": "Reparto coordinado para e-commerce y empresas locales.", "icono": "🚀"},
            {"titulo": "Cargas Especiales & Depósito", "descripcion": "Almacenamiento temporal y gestión de volúmenes pesados.", "icono": "🏭"}
        ],
        "testimonio": {
            "autor": "Mariano Ferreyra",
            "cargo": "Gerente Operativo",
            "comentario": "Puntualidad impecable en la entrega y excelente cuidado de la mercadería. Es nuestro aliado logístico indispensable.",
            "estrellas": 5
        }
    },
    "tecnologia": {
        "tagline": "Innovación digital y desarrollo a medida",
        "hero_headline": "Aceleramos la transformación tecnológica de tu negocio",
        "hero_subheadline": "Creamos software robusto, aplicaciones móviles y soluciones cloud orientadas a maximizar tu productividad.",
        "cta_texto": "Agendar Consulta Técnica",
        "beneficios": [
            {"titulo": "Arquitectura Escalable", "descripcion": "Código limpio y estructuras listas para crecer sin contratiempos.", "icono": "⚡"},
            {"titulo": "Seguridad de Datos", "descripcion": "Estándares rigurosos de encriptación y protección de datos.", "icono": "🛡️"},
            {"titulo": "Soporte Continuo", "descripcion": "Mantenimiento 24/7 y asistencia especializada constante.", "icono": "👨‍💻"}
        ],
        "servicios": [
            {"titulo": "Desarrollo Web & Apps", "descripcion": "Interfaces modernas, rápidas y optimizadas para conversión.", "icono": "🌐"},
            {"titulo": "Integraciones Cloud & API", "descripcion": "Conexión de sistemas internos y automatización de flujos.", "icono": "☁️"},
            {"titulo": "Consultoría IT & Ciberseguridad", "descripcion": "Auditorías de infraestructura y protección contra amenazas.", "icono": "🔒"}
        ],
        "testimonio": {
            "autor": "Gonzalo Rossi",
            "cargo": "CEO Fintech",
            "comentario": "Comprendieron nuestra visión desde el primer momento. Entregaron un producto impecable y en tiempo récord.",
            "estrellas": 5
        }
    },
    "retail": {
        "tagline": "Tendencia, variedad y ofertas exclusivas",
        "hero_headline": "Encuentra los productos perfectos para tu estilo de vida",
        "hero_subheadline": "Catálogo seleccionado con las mejores marcas, envíos a todo el país y atención personalizada.",
        "cta_texto": "Ver Catálogo Destacado",
        "beneficios": [
            {"titulo": "Calidad Garantizada", "descripcion": "Productos verificados de las marcas más reconocidas.", "icono": "💎"},
            {"titulo": "Envíos a Todo el País", "descripcion": "Despachos rápidos y seguros a tu puerta.", "icono": "📦"},
            {"titulo": "Facilidades de Pago", "descripcion": "Múltiples opciones de pago con cuotas y promociones.", "icono": "💳"}
        ],
        "servicios": [
            {"titulo": "Atención Comercial Directa", "descripcion": "Asesoramiento vía WhatsApp para resolver dudas antes de comprar.", "icono": "💬"},
            {"titulo": "Ventas Mayoristas & Minoristas", "descripcion": "Precios competitivos adaptados a diferentes volúmenes.", "icono": "🛍️"},
            {"titulo": "Cambios y Devoluciones Simples", "descripcion": "Proceso transparente para tu máxima tranquilidad.", "icono": "🔄"}
        ],
        "testimonio": {
            "autor": "Lucía Benítez",
            "cargo": "Compradora",
            "comentario": "El pedido llegó súper rápido y el empaque fue impecable. Muy satisfecha con la atención recibida.",
            "estrellas": 5
        }
    },
    "corporativo": {
        "tagline": "Soluciones estratégicas para el crecimiento corporativo",
        "hero_headline": "Potenciamos el valor y la eficiencia de tu organización",
        "hero_subheadline": "Asesoramiento experto, gestión de procesos y desarrollo de estrategias de negocio de alto nivel.",
        "cta_texto": "Contactar Asesor Comercial",
        "beneficios": [
            {"titulo": "Experiencia Comprobada", "descripcion": "Años liderando proyectos de transformación corporativa.", "icono": "📈"},
            {"titulo": "Metodología Ágil", "descripcion": "Resultados medibles orientados a optimizar tus procesos.", "icono": "🎯"},
            {"titulo": "Atención Personalizada", "descripcion": "Consultoría directa ajustada a la realidad de tu empresa.", "icono": "🤝"}
        ],
        "servicios": [
            {"titulo": "Consultoría Estratégica", "descripcion": "Diagnóstico y planes de acción para acelerar el crecimiento.", "icono": "👔"},
            {"titulo": "Gestión Operativa & Finanzas", "descripcion": "Optimización de costos y estructuración financiera sólida.", "icono": "📊"},
            {"titulo": "Capacitación Ejecutiva", "descripcion": "Programas de liderazgo y desarrollo para equipos de alto rendimiento.", "icono": "🎓"}
        ],
        "testimonio": {
            "autor": "Martín Silva",
            "cargo": "Director General",
            "comentario": "Su acompañamiento fue determinante para estructurar nuestro crecimiento y mejorar el margen de rentabilidad.",
            "estrellas": 5
        }
    }
}

# Almacenamiento en memoria para demostración interactiva
CLIENTES_DB: Dict[str, ClienteLanding] = {}

def _inicializar_clientes_semilla():
    """Carga clientes semilla iniciales para el CRM si está vacío."""
    if not CLIENTES_DB:
        c1 = generar_landing_page(
            nombre_negocio="Taller Mecánico San José",
            rubro="Reparación Automotriz y lubricentro",
            telefono_whatsapp="+5491155550101",
            email="contacto@sanjoseauto.com",
            direccion="Av. Mitre 2340, Buenos Aires",
            horario="Lun a Vie 08:00 a 18:00"
        ).cliente
        
        c2 = generar_landing_page(
            nombre_negocio="Café de la Plaza",
            rubro="Cafetería & Panadería Artesanal",
            telefono_whatsapp="+5491155550202",
            email="hola@cafedelaplaza.com",
            direccion="Plaza Central 142, Córdoba",
            horario="Lun a Dom 07:00 a 21:00"
        ).cliente

        c3 = generar_landing_page(
            nombre_negocio="Clínica Odontológica Sonrisas",
            rubro="Salud y Estética Dental",
            telefono_whatsapp="+5491155550303",
            email="turnos@sonrisasdental.com",
            direccion="Calle 12 N° 850, La Plata",
            horario="Lun a Sab 09:00 a 20:00"
        ).cliente

        CLIENTES_DB[c1.id] = c1
        CLIENTES_DB[c2.id] = c2
        CLIENTES_DB[c3.id] = c3


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
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, texto_limpio):
                return categoria

    return "corporativo"


def generar_slug(nombre: str) -> str:
    """Genera un slug único para la URL de la landing."""
    slug = re.sub(r'[^a-zA-Z0-9]', '-', nombre.lower()).strip('-')
    slug = re.sub(r'-+', '-', slug)
    return f"{slug}-{uuid.uuid4().hex[:6]}"


def generar_landing_page(
    nombre_negocio: str,
    rubro: str,
    telefono_whatsapp: str = "",
    email: str = "",
    direccion: str = "",
    horario: str = "",
    ia_client=None
) -> LandingResponse:
    """
    Genera un objeto ClienteLanding completo con copia y elementos visuales por nicho.
    """
    categoria_visual = None

    if ia_client:
        try:
            respuesta = ia_client.clasificar_rubro(nombre_negocio=nombre_negocio, rubro=rubro)
            categoria_visual = respuesta.get("categoria")
        except Exception as e:
            print(f"[WARN] Llamada a IA falló o no devolvió respuesta ({e}). Activando Fallback Inteligente.")
            categoria_visual = None

    if not categoria_visual:
        texto_busqueda = f"{nombre_negocio} {rubro}"
        categoria_visual = inferir_categoria_por_rubro(texto_busqueda)

    plantilla = PLANTILLAS_NICHO.get(categoria_visual, PLANTILLAS_NICHO["corporativo"])

    client_id = generar_slug(nombre_negocio)
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Valores por defecto para contacto si están vacíos
    tel = telefono_whatsapp or "+5491100000000"
    em = email or f"contacto@{client_id[:12]}.com"
    dir_str = direccion or "Centro Comercial Principal"
    hor_str = horario or "Lun a Vie 09:00 a 18:00"

    cliente = ClienteLanding(
        id=client_id,
        nombre_negocio=nombre_negocio,
        rubro=rubro,
        categoria_visual=categoria_visual,
        telefono_whatsapp=tel,
        email=em,
        direccion=dir_str,
        horario=hor_str,
        tagline=plantilla["tagline"],
        hero_headline=f"{nombre_negocio} - {plantilla['hero_headline']}",
        hero_subheadline=plantilla["hero_subheadline"],
        cta_texto=plantilla["cta_texto"],
        beneficios=plantilla["beneficios"],
        servicios=plantilla["servicios"],
        testimonio=plantilla["testimonio"],
        estado_lead="Landing Generada",
        fecha_creacion=fecha_actual,
        fallback_aplicado=categoria_visual != "corporativo" and not ia_client
    )

    # Persistir en memoria
    CLIENTES_DB[cliente.id] = cliente

    return LandingResponse(
        status="success",
        cliente=cliente
    )

# Inicializar clientes semilla al cargar el módulo
_inicializar_clientes_semilla()
