import urllib.request
import urllib.parse
import json
import re

THEMES_POR_CATEGORIA = {
    "gastronomia": {
        "bg": "#0c0908",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(245, 158, 11, 0.15)",
        "border_hover": "rgba(245, 158, 11, 0.35)",
        "glow": "rgba(245, 158, 11, 0.12)",
        "glow_secondary": "rgba(234, 88, 12, 0.06)",
        "accent": "#f59e0b",
        "accent_gradient": "from-amber-300 via-orange-400 to-amber-500",
        "font_display": "'Playfair Display', serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Gastronomía & Carta Digital",
        "features": [
            {"title": "Especialidades del Día", "desc": "Preparaciones destacadas elaboradas con ingredientes frescos de estación.", "icon": "fa-utensils"},
            {"title": "Reserva & Pedidos Express", "desc": "Canal directo vía WhatsApp sin comisiones ni intermediarios.", "icon": "fa-mobile-screen-button"},
            {"title": "Ambiente & Experiencia", "desc": "Atención cálida, espacios cuidados y la mejor gastronomía local.", "icon": "fa-mug-hot"}
        ],
        "cta_text": "Reservar Mesa / Ver Carta"
    },
    "automotriz": {
        "bg": "#070a12",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(59, 130, 246, 0.15)",
        "border_hover": "rgba(59, 130, 246, 0.35)",
        "glow": "rgba(59, 130, 246, 0.14)",
        "glow_secondary": "rgba(14, 165, 233, 0.06)",
        "accent": "#3b82f6",
        "accent_gradient": "from-blue-400 via-sky-400 to-indigo-400",
        "font_display": "'Oswald', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Taller Mecánico & Servicios Automotor",
        "features": [
            {"title": "Diagnóstico Computarizado", "desc": "Escaneo multimarca de alta precisión para detectar fallas electrónicas y mecánicas.", "icon": "fa-microchip"},
            {"title": "Mantenimiento Preventivo", "desc": "Cambio de aceite, filtros, frenos y suspensión con repuestos de calidad garantizada.", "icon": "fa-wrench"},
            {"title": "Garantía Escrita", "desc": "Respaldamos cada trabajo realizado con profesionales especializados.", "icon": "fa-shield-halved"}
        ],
        "cta_text": "Solicitar Turno en Taller"
    },
    "salud_belleza": {
        "bg": "#060f14",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(14, 165, 233, 0.15)",
        "border_hover": "rgba(14, 165, 233, 0.35)",
        "glow": "rgba(14, 165, 233, 0.12)",
        "glow_secondary": "rgba(20, 184, 166, 0.06)",
        "accent": "#0ea5e9",
        "accent_gradient": "from-sky-300 via-teal-300 to-cyan-400",
        "font_display": "'Outfit', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Centro de Salud & Bienestar",
        "features": [
            {"title": "Atención Personalizada", "desc": "Tratamientos a la medida diseñados por profesionales certificados.", "icon": "fa-user-doctor"},
            {"title": "Tecnología Avanzada", "desc": "Equipamiento de última generación para procedimientos cómodos y seguros.", "icon": "fa-sparkles"},
            {"title": "Turnos Flexibles", "desc": "Agendado rápido y sin demoras adaptado a tu horario.", "icon": "fa-calendar-check"}
        ],
        "cta_text": "Agendar Consulta Directa"
    },
    "inmobiliaria": {
        "bg": "#0a0c10",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(234, 179, 8, 0.15)",
        "border_hover": "rgba(234, 179, 8, 0.35)",
        "glow": "rgba(234, 179, 8, 0.12)",
        "glow_secondary": "rgba(217, 119, 6, 0.06)",
        "accent": "#eab308",
        "accent_gradient": "from-amber-200 via-yellow-400 to-amber-500",
        "font_display": "'Cormorant Garamond', serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Bienes Raíces & Inversiones",
        "features": [
            {"title": "Propiedades Exclusivas", "desc": "Catálogo de inmuebles residenciales y comerciales seleccionados.", "icon": "fa-building"},
            {"title": "Valuación Profesional", "desc": "Tasaciones precisas basadas en análisis real del mercado local.", "icon": "fa-chart-line"},
            {"title": "Asesoramiento Legal", "desc": "Gestión transparente en alquileres, compras y desarrollos.", "icon": "fa-scale-balanced"}
        ],
        "cta_text": "Consultar Propiedades"
    },
    "tecnologia": {
        "bg": "#090a16",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(99, 102, 241, 0.15)",
        "border_hover": "rgba(99, 102, 241, 0.35)",
        "glow": "rgba(99, 102, 241, 0.14)",
        "glow_secondary": "rgba(168, 85, 247, 0.06)",
        "accent": "#6366f1",
        "accent_gradient": "from-indigo-300 via-purple-400 to-sky-400",
        "font_display": "'Space Grotesk', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Soluciones Digitales & Tecnología",
        "features": [
            {"title": "Desarrollo a Medida", "desc": "Sistemas escalables y sitios web optimizados para alta conversión.", "icon": "fa-code"},
            {"title": "Seguridad & Nube", "desc": "Infraestructura robusta con protección continua de datos.", "icon": "fa-server"},
            {"title": "Soporte 24/7", "desc": "Monitoreo constante y asistencia técnica especializada.", "icon": "fa-headset"}
        ],
        "cta_text": "Solicitar Propuesta Tech"
    },
    "retail": {
        "bg": "#0d0914",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(236, 72, 153, 0.15)",
        "border_hover": "rgba(236, 72, 153, 0.35)",
        "glow": "rgba(236, 72, 153, 0.12)",
        "glow_secondary": "rgba(244, 63, 94, 0.06)",
        "accent": "#ec4899",
        "accent_gradient": "from-pink-300 via-rose-400 to-purple-400",
        "font_display": "'Outfit', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Comercio & Indumentaria",
        "features": [
            {"title": "Catálogo Actualizado", "desc": "Variedad de colecciones y productos con stock en tiempo real.", "icon": "fa-bag-shopping"},
            {"title": "Envíos Rápido a Domicilio", "desc": "Entregas eficientes y seguimiento directo de tu compra.", "icon": "fa-truck-fast"},
            {"title": "Atención Personalizada", "desc": "Asesoramiento directo para elegir lo ideal para vos.", "icon": "fa-comments"}
        ],
        "cta_text": "Ver Catálogo / Comprar"
    },
    "logistica": {
        "bg": "#090d12",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(16, 185, 129, 0.15)",
        "border_hover": "rgba(16, 185, 129, 0.35)",
        "glow": "rgba(16, 185, 129, 0.12)",
        "glow_secondary": "rgba(6, 182, 212, 0.06)",
        "accent": "#10b981",
        "accent_gradient": "from-emerald-300 via-teal-400 to-cyan-400",
        "font_display": "'Space Grotesk', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Logística & Transporte Express",
        "features": [
            {"title": "Envíos & Fletes Seguros", "desc": "Cobertura urbana y regional con unidades equipadas y monitoreadas.", "icon": "fa-truck-ramp-box"},
            {"title": "Puntualidad Garantizada", "desc": "Tiempos de respuesta ágiles y cumplimiento estricto de entregas.", "icon": "fa-clock"},
            {"title": "Cotización Inmediata", "desc": "Presupuestos transparentes adaptados al volumen y destino.", "icon": "fa-calculator"}
        ],
        "cta_text": "Cotizar Envío / Flete"
    },
    "servicios_hogar": {
        "bg": "#0a0c0e",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(249, 115, 22, 0.15)",
        "border_hover": "rgba(249, 115, 22, 0.35)",
        "glow": "rgba(249, 115, 22, 0.12)",
        "glow_secondary": "rgba(234, 179, 8, 0.06)",
        "accent": "#f97316",
        "accent_gradient": "from-orange-300 via-amber-400 to-orange-500",
        "font_display": "'Plus Jakarta Sans', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap",
        "badge": "Servicios Especializados para el Hogar",
        "features": [
            {"title": "Atención de Urgencias", "desc": "Asistencia rápida para solucionar inconvenientes en tu hogar o comercio.", "icon": "fa-bolt"},
            {"title": "Trabajos Garantizados", "desc": "Personal idóneo con materiales y herramientas de primera calidad.", "icon": "fa-screwdriver-wrench"},
            {"title": "Presupuesto Sin Cargo", "desc": "Evaluación clara de costos antes de iniciar cualquier reparación.", "icon": "fa-clipboard-check"}
        ],
        "cta_text": "Solicitar Servicio Técnico"
    },
    "educacion": {
        "bg": "#090a14",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(139, 92, 246, 0.15)",
        "border_hover": "rgba(139, 92, 246, 0.35)",
        "glow": "rgba(139, 92, 246, 0.12)",
        "glow_secondary": "rgba(99, 102, 241, 0.06)",
        "accent": "#8b5cf6",
        "accent_gradient": "from-violet-300 via-purple-400 to-indigo-400",
        "font_display": "'Outfit', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "badge": "Formación & Educación Profesional",
        "features": [
            {"title": "Programas Actualizados", "desc": "Contenidos prácticos enfocados en habilidades de alta demanda.", "icon": "fa-graduation-cap"},
            {"title": "Modalidad Flexible", "desc": "Clases presenciales y virtuales que se adaptan a tu ritmo de estudio.", "icon": "fa-laptop-code"},
            {"title": "Certificación Oficial", "desc": "Respaldo directo de tus competencias académicas y profesionales.", "icon": "fa-certificate"}
        ],
        "cta_text": "Inscribirse / Solicitar Info"
    },
    "corporativo": {
        "bg": "#080b11",
        "card_bg": "rgba(255, 255, 255, 0.03)",
        "border": "rgba(99, 102, 241, 0.15)",
        "border_hover": "rgba(99, 102, 241, 0.35)",
        "glow": "rgba(99, 102, 241, 0.12)",
        "glow_secondary": "rgba(59, 130, 246, 0.06)",
        "accent": "#6366f1",
        "accent_gradient": "from-indigo-300 via-blue-400 to-sky-400",
        "font_display": "'Plus Jakarta Sans', sans-serif",
        "font_google": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap",
        "badge": "Servicios Profesionales & Comerciales",
        "features": [
            {"title": "Calidad Garantizada", "desc": "Procesos eficientes enfocados en superar las expectativas del cliente.", "icon": "fa-award"},
            {"title": "Atención Inmediata", "desc": "Respuesta ágil y personalizada a través de múltiples canales directos.", "icon": "fa-clock"},
            {"title": "Experiencia Comprobada", "desc": "Años de trayectoria respaldando la confianza de nuestra clientela.", "icon": "fa-thumbs-up"}
        ],
        "cta_text": "Contactar con la Empresa"
    }
}

def obtener_contexto_web_empresa(nombre: str, ciudad: str):
    """
    Extrae información real disponible en internet (DuckDuckGo / OSM)
    para alimentar la landing page con datos fidedignos del negocio.
    """
    ciudad_clean = ciudad.split(",")[0].strip()
    query = f"{nombre} {ciudad_clean}"
    
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}&kl=ar-es"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "es-AR,es;q=0.9"
    }
    
    resumen_encontrado = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            snippets = re.findall(r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            for snip in snippets:
                clean_snip = re.sub(r'<[^>]+>', '', snip).strip()
                if len(clean_snip) > 30 and not any(bad in clean_snip.lower() for bad in ["duckduckgo", "wikipedia", "busco"]):
                    resumen_encontrado = clean_snip
                    break
    except Exception:
        pass

    return {
        "resumen_web": resumen_encontrado or f"Empresa referente en {ciudad_clean}, enfocada en brindar atención de excelencia y soluciones a medida."
    }

def obtener_theme_config(categoria: str) -> dict:
    """Devuelve la configuración estética armónica del rubro."""
    cat_clean = categoria.lower().strip() if categoria else "corporativo"
    return THEMES_POR_CATEGORIA.get(cat_clean, THEMES_POR_CATEGORIA["corporativo"])
