import os
from jinja2 import Template
from agencia_standalone.services.ai_copywriter import generar_textos_persuasivos

MAPA_ESTILOS = {
    "musica": {
        "img": "https://images.unsplash.com/photo-1516280440502-6298923a1a36?q=80&w=2070&auto=format&fit=crop",
        "primario": "#E11D48",
        "gradient": "from-rose-600 to-pink-500",
        "badge": "bg-rose-500/20 text-rose-300 border-rose-500/30"
    },
    "gastronomia": {
        "img": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?q=80&w=2070&auto=format&fit=crop",
        "primario": "#F59E0B",
        "gradient": "from-amber-600 to-orange-500",
        "badge": "bg-amber-500/20 text-amber-300 border-amber-500/30"
    },
    "automotriz": {
        "img": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?q=80&w=2070&auto=format&fit=crop",
        "primario": "#DC2626",
        "gradient": "from-red-600 to-rose-500",
        "badge": "bg-red-500/20 text-red-300 border-red-500/30"
    },
    "tecnologia": {
        "img": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop",
        "primario": "#3B82F6",
        "gradient": "from-blue-600 to-indigo-500",
        "badge": "bg-blue-500/20 text-blue-300 border-blue-500/30"
    },
    "logistica": {
        "img": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop",
        "primario": "#EAB308",
        "gradient": "from-yellow-600 to-amber-500",
        "badge": "bg-yellow-500/20 text-yellow-300 border-yellow-500/30"
    },
    "salud_belleza": {
        "img": "https://images.unsplash.com/photo-1560066984-138dadb4c035?q=80&w=2070&auto=format&fit=crop",
        "primario": "#10B981",
        "gradient": "from-emerald-600 to-teal-500",
        "badge": "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
    },
    "retail": {
        "img": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=2070&auto=format&fit=crop",
        "primario": "#8B5CF6",
        "gradient": "from-purple-600 to-violet-500",
        "badge": "bg-purple-500/20 text-purple-300 border-purple-500/30"
    },
    "corporativo": {
        "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop",
        "primario": "#475569",
        "gradient": "from-slate-700 to-gray-600",
        "badge": "bg-slate-500/20 text-slate-300 border-slate-500/30"
    }
}

def inferir_categoria_por_rubro(tipo_busqueda: str, nombre: str) -> str:
    texto = f"{tipo_busqueda or ''} {nombre or ''}".lower()
    if any(k in texto for k in ["cafe", "cafeteria", "bar", "resto", "restaurante", "pizza", "comida", "gourmet", "bistro", "panaderia", "gastronomia"]):
        return "gastronomia"
    elif any(k in texto for k in ["auto", "mecanic", "taller", "lubri", "car", "repuesto", "motor", "vehiculo", "flete", "traslado", "neumatico"]):
        return "automotriz"
    elif any(k in texto for k in ["musi", "sonido", "banda", "show", "dj", "audio", "evento"]):
        return "musica"
    elif any(k in texto for k in ["salud", "estetic", "spa", "peluquer", "dentist", "medico", "clinic", "nutri", "belleza", "odontolog"]):
        return "salud_belleza"
    elif any(k in texto for k in ["tech", "soft", "informatic", "comput", "celular", "electr", "digital"]):
        return "tecnologia"
    elif any(k in texto for k in ["logist", "transpor", "mudanza", "deposito", "cruz"]):
        return "logistica"
    elif any(k in texto for k in ["tienda", "local", "ropa", "indumentaria", "modas", "bazar", "regal"]):
        return "retail"
    else:
        return "corporativo"

async def mock_generar_landing(prospecto, custom_prompt: str = None, precio_usd: float = 350.0, dominio_elegido: str = None):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    directorio = os.path.join(base_dir, "media", "demos_generadas")
    os.makedirs(directorio, exist_ok=True)
    
    nombre_archivo = f"demo_{prospecto.place_id}.html"
    ruta_completa = os.path.join(directorio, nombre_archivo)
    
    textos = await generar_textos_persuasivos(prospecto.nombre, prospecto.tipo_busqueda, prospecto.ciudad_busqueda, custom_prompt=custom_prompt)
    
    cat_fallback = inferir_categoria_por_rubro(prospecto.tipo_busqueda, prospecto.nombre)
    estilo = MAPA_ESTILOS.get(cat_fallback, MAPA_ESTILOS["corporativo"]).copy()
    
    import json
    # Usar foto real del local si fue capturada de Google Maps
    if getattr(prospecto, "photos_json", None):
        try:
            p_list = json.loads(prospecto.photos_json)
            if p_list and len(p_list) > 0:
                estilo["img"] = p_list[0]
        except Exception as e:
            print(f"⚠️ Error cargando foto real: {e}")
            
    if not textos:
        textos = {
            "titulo_principal": f"Innovación Digital para {prospecto.nombre}",
            "subtitulo": f"Servicios de máxima calidad y atención profesional en {prospecto.ciudad_busqueda or 'tu ciudad'}.",
            "beneficio_1_titulo": "Atención Personalizada 24/7",
            "beneficio_1_desc": "Respuesta inmediata y asesoramiento adaptado a tus necesidades.",
            "beneficio_2_titulo": "Garantía de Excelencia",
            "beneficio_2_desc": "Procesos estandarizados y resultados de primer nivel probados por la comunidad.",
            "beneficio_3_titulo": "Tecnología e Innovación",
            "beneficio_3_desc": "Herramientas de vanguardia diseñadas para ahorrarte tiempo y dinero.",
            "testimonio_1_nombre": "Valeria R. (Cliente Frecuente)",
            "testimonio_1_texto": f"Impresionante la rapidez y la amabilidad de {prospecto.nombre}. Totalmente recomendados.",
            "testimonio_2_nombre": "Martín G.",
            "testimonio_2_texto": "Buscaba una solución seria y transparente en la zona. Superaron todas mis expectativas.",
            "faq_1_preg": "¿Cómo puedo contratar o solicitar presupuesto?",
            "faq_1_resp": "Hacé clic en el botón de activación para iniciar el onboarding directo.",
            "faq_2_preg": "¿Qué incluye la infraestructura?",
            "faq_2_resp": "Dominio SSL profesional, Hosting ultrarrápido y CRM comercial integrado.",
            "cta": "Activar Sitio Oficial",
            "categoria_imagen": cat_fallback
        }

    # Inyectar reseñas reales capturadas de Google Maps en los testimonios
    if getattr(prospecto, "reviews_json", None):
        try:
            r_list = json.loads(prospecto.reviews_json)
            if r_list and len(r_list) > 0:
                textos["testimonio_1_nombre"] = f"{r_list[0].get('autor')} ({'★' * int(r_list[0].get('rating', 5))})"
                textos["testimonio_1_texto"] = r_list[0].get("texto")
            if r_list and len(r_list) > 1:
                textos["testimonio_2_nombre"] = f"{r_list[1].get('autor')} ({'★' * int(r_list[1].get('rating', 5))})"
                textos["testimonio_2_texto"] = r_list[1].get("texto")
        except Exception as e:
            print(f"⚠️ Error inyectando reseñas reales: {e}")

    categoria = textos.get("categoria_imagen", cat_fallback).lower()

    link_checkout_interno = f"/checkout/{prospecto.place_id}"
    dominio_display = dominio_elegido or f"{prospecto.nombre.lower().replace(' ', '')}.com"

    html_final = f"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prospecto.nombre} | Plataforma Web Oficial</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ background-color: #0b0f19; color: #f3f4f6; font-family: 'Plus Jakarta Sans', sans-serif; }}
        .glass-panel {{ background: rgba(17, 24, 39, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); }}
        .hero-gradient {{ background: linear-gradient(180deg, rgba(11, 15, 25, 0.65) 0%, rgba(11, 15, 25, 0.95) 100%), url('{estilo["img"]}'); background-size: cover; background-position: center; }}
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between">

    <!-- Header Glass Nav -->
    <header class="glass-panel sticky top-0 z-50 px-6 py-4 flex items-center justify-between max-w-7xl mx-auto w-full mt-4 rounded-2xl">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr {estilo["gradient"]} flex items-center justify-center font-bold text-white shadow-lg">
                <i class="fa-solid fa-star"></i>
            </div>
            <div>
                <h1 class="text-lg font-bold text-white tracking-tight">{prospecto.nombre}</h1>
                <p class="text-xs text-gray-400 font-mono">{prospecto.ciudad_busqueda or 'Sitio Oficial'}</p>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <span class="text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-xl hidden sm:inline-block">
                🌐 {dominio_display}
            </span>
            <a href="{link_checkout_interno}" class="bg-gradient-to-r {estilo["gradient"]} text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-lg transition-all flex items-center gap-2">
                <i class="fa-solid fa-bolt"></i> {textos.get("cta", "Activar Sitio Oficial")}
            </a>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero-gradient px-6 py-20 md:py-28 flex flex-col items-center justify-center text-center my-6">
        <div class="max-w-4xl space-y-6">
            <span class="inline-block text-xs font-bold px-3.5 py-1.5 rounded-full border {estilo["badge"]} uppercase tracking-widest font-mono">
                {prospecto.tipo_busqueda or 'Soluciones Premium'}
            </span>
            <h2 class="text-4xl md:text-6xl font-extrabold text-white leading-tight tracking-tight">
                {textos.get("titulo_principal")}
            </h2>
            <p class="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
                {textos.get("subtitulo")}
            </p>
            <div class="pt-4 flex flex-wrap items-center justify-center gap-4">
                <a href="{link_checkout_interno}" class="bg-gradient-to-r {estilo["gradient"]} hover:opacity-90 text-white font-extrabold text-base px-8 py-4 rounded-2xl shadow-xl shadow-indigo-500/20 transition-all flex items-center gap-2">
                    <i class="fa-solid fa-credit-card"></i> Activar Dominio & Plataforma (${precio_usd:.2f} USD)
                </a>
            </div>
        </div>
    </section>

    <!-- Section: 3 Beneficios Clave -->
    <section class="max-w-7xl mx-auto px-6 py-12 w-full">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass-panel p-6 rounded-2xl space-y-3 hover:border-gray-700 transition-all">
                <div class="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center text-xl">
                    <i class="fa-solid fa-shield-halved"></i>
                </div>
                <h3 class="text-lg font-bold text-white">{textos.get("beneficio_1_titulo", "Garantía de Calidad")}</h3>
                <p class="text-sm text-gray-400">{textos.get("beneficio_1_desc", "Servicios verificados con altos estándares de cumplimiento.")}</p>
            </div>
            <div class="glass-panel p-6 rounded-2xl space-y-3 hover:border-gray-700 transition-all">
                <div class="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xl">
                    <i class="fa-solid fa-clock"></i>
                </div>
                <h3 class="text-lg font-bold text-white">{textos.get("beneficio_2_titulo", "Respuesta Inmediata")}</h3>
                <p class="text-sm text-gray-400">{textos.get("beneficio_2_desc", "Atención prioritaria para resolver tus consultas sin demoras.")}</p>
            </div>
            <div class="glass-panel p-6 rounded-2xl space-y-3 hover:border-gray-700 transition-all">
                <div class="w-12 h-12 rounded-xl bg-pink-500/10 text-pink-400 flex items-center justify-center text-xl">
                    <i class="fa-solid fa-gem"></i>
                </div>
                <h3 class="text-lg font-bold text-white">{textos.get("beneficio_3_titulo", "Experiencia Premium")}</h3>
                <p class="text-sm text-gray-400">{textos.get("beneficio_3_desc", "Diseño y estructura pensados para dar la mejor imagen a tus clientes.")}</p>
            </div>
        </div>
    </section>

    <!-- Section: Testimonios -->
    <section class="max-w-7xl mx-auto px-6 py-12 w-full space-y-6">
        <h3 class="text-2xl font-bold text-white text-center">Lo que opinan nuestros clientes</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="glass-panel p-6 rounded-2xl space-y-3">
                <div class="flex text-amber-400 text-sm gap-1">
                    <i class="fa-solid fa-star"></i><i className="fa-solid fa-star"></i><i className="fa-solid fa-star"></i><i className="fa-solid fa-star"></i><i className="fa-solid fa-star"></i>
                </div>
                <p class="text-sm text-gray-300 italic">"{textos.get("testimonio_1_texto")}"</p>
                <p class="text-xs font-bold text-white">— {textos.get("testimonio_1_nombre")}</p>
            </div>
            <div class="glass-panel p-6 rounded-2xl space-y-3">
                <div class="flex text-amber-400 text-sm gap-1">
                    <i class="fa-solid fa-star"></i><i className="fa-solid fa-star"></i><i className="fa-solid fa-star"></i><i className="fa-solid fa-star"></i><i className="fa-solid fa-star"></i>
                </div>
                <p class="text-sm text-gray-300 italic">"{textos.get("testimonio_2_texto")}"</p>
                <p class="text-xs font-bold text-white">— {textos.get("testimonio_2_nombre")}</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="glass-panel border-t border-gray-800 text-center py-6 text-xs text-gray-500 mt-12">
        Plataforma Oficial para {prospecto.nombre} — Desarrollado con BeCubical & CATSOF S.A.S.
    </footer>

</body>
</html>
"""
    with open(ruta_completa, "w", encoding="utf-8") as f:
        f.write(html_final)
        
    return f"/demos/{nombre_archivo}"
