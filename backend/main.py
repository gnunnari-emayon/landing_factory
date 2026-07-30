import os
import sys
import re
import uuid

# Asegurar importaciones del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn

from backend.core.config import config
from backend.core.database import get_db
from backend.services.generator import generar_landing_page, inferir_categoria_por_rubro
from backend.services.prospect_repository import (
    listar_prospectos, buscar_prospecto_por_place_id, crear_prospecto
)

app = FastAPI(
    title="Nicho Landing Factory & CRM",
    description="Fábrica de Landing Pages e Inferencia por Rubro",
    version="1.0.0"
)

# Montar archivos estáticos (CSS, JS, imágenes)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Configurar motor de plantillas Jinja2
templates_dir = os.path.join(frontend_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request, db: Session = Depends(get_db)):
    """Página principal Agencia Standalone (React + Tailwind) con precarga inmediata de Leads"""
    prospectos = [p.to_dict() for p in listar_prospectos(db, limit=20000)]
    return templates.TemplateResponse(request, "index.html", {
        "initial_prospects": prospectos,
        "initial_total": len(prospectos)
    })


@app.get("/api/v1/agencia/rubros/sugerir")
async def sugerir_rubros(q: str = ""):
    from backend.data.latam_database import autocompletar_rubro
    return {"status": "ok", "items": autocompletar_rubro(q)}


@app.get("/api/v1/agencia/ubicaciones/sugerir")
async def sugerir_ubicaciones(q: str = ""):
    from backend.data.latam_database import autocompletar_ubicacion
    return {"status": "ok", "items": autocompletar_ubicacion(q)}


@app.get("/prospector", response_class=HTMLResponse)
async def prospector_page(request: Request, db: Session = Depends(get_db)):
    """Pestaña 1: Prospector Google Maps"""
    prospectos = [p.to_dict() for p in listar_prospectos(db)]
    sin_web = len([p for p in prospectos if not p.get("sitio_web")])
    enriquecidos = len([p for p in prospectos if p.get("status") == "ENRIQUECIDO" or p.get("whatsapp") or p.get("telefono")])
    contactados = len([p for p in prospectos if p.get("status") and "CONTACTADO" in p.get("status")])
    
    return templates.TemplateResponse(request, "agencia/prospector.html", {
        "active_tab": "prospector",
        "total": len(prospectos),
        "sin_web": sin_web,
        "enriquecidos": enriquecidos,
        "contactados": contactados,
        "items": prospectos
    })


@app.post("/api/v1/agencia/b2b/prospectar-agent-reach")
async def prospectar_agent_reach(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint para prospección multicanal con Agent Reach.
    Escanea PYMEs, valida dominios institucionales (.com, .net, .org, .com.ar, etc.) vs redes sociales
    y persiste en PostgreSQL.
    """
    from backend.services.domain_checker import es_sitio_web_propio

    rubro = "Servicios generales"
    ubicacion = "Córdoba, AR"

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            payload = await request.json()
            rubro = payload.get("rubro") or payload.get("tipo_busqueda") or rubro
            ubicacion = payload.get("ubicacion") or payload.get("ciudad_nombre") or ubicacion
        except Exception:
            pass
        is_html = False
    else:
        try:
            form = await request.form()
            rubro = form.get("rubro") or form.get("tipo_busqueda") or rubro
            ubicacion = form.get("ubicacion") or form.get("ciudad_nombre") or ubicacion
        except Exception:
            pass
        is_html = True

    # Extracción multicanal Agent Reach (Facebook, Instagram, LinkedIn, Exa, Directorios)
    from backend.services.agent_reach_service import ejecutar_prospeccion_agent_reach
    
    try:
        leads_hallados = ejecutar_prospeccion_agent_reach(rubro=rubro, ciudad=ubicacion, max_results=50)
    except Exception as err:
        print(f"Error ejecutando Agent Reach: {err}")
        leads_hallados = []

    guardados = 0
    for lead in leads_hallados:
        es_propio = es_sitio_web_propio(lead.get("sitio_web"))
        p_data = {
            "place_id": f"reach_{uuid.uuid4().hex[:8]}",
            "nombre": lead["nombre"],
            "tipo_busqueda": rubro,
            "ciudad_busqueda": ubicacion,
            "sitio_web": lead.get("sitio_web") if es_propio else None,
            "telefono": lead.get("telefono") or "Sin teléfono",
            "whatsapp": lead.get("telefono") if lead.get("telefono") else None,
            "status": "ENRIQUECIDO" if lead.get("telefono") else "SIN_CONTACTAR"
        }
        crear_prospecto(db, p_data)
        guardados += 1

    if is_html:
        return RedirectResponse(url="/prospector", status_code=303)
    return {"status": "ok", "mensaje": f"Agent Reach completó el escaneo para '{rubro}' en '{ubicacion}'", "guardados": guardados}


@app.get("/focus-group", response_class=HTMLResponse)
async def focus_group_page(request: Request):
    """Pestaña 2: Focus Group AI"""
    return templates.TemplateResponse(request, "agencia/focus_group.html", {
        "active_tab": "focusgroup"
    })


@app.get("/campanias", response_class=HTMLResponse)
async def campanias_page(request: Request):
    """Pestaña 3: Gestión de Campañas & Clientes B2B"""
    return templates.TemplateResponse(request, "agencia/campañas.html", {
        "active_tab": "campaigns"
    })


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard CRM para usuario DEV"""
    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "active_user": config.CRM_USER.upper()
    })


@app.get("/static/demos/{file_name}", response_class=HTMLResponse)
async def ver_demo_html(file_name: str):
    """Servir demo HTML de prospectos"""
    demos_dir = os.path.join(frontend_dir, "demos")
    filepath = os.path.join(demos_dir, file_name)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Demo no encontrada</h1>", status_code=404)


@app.post("/api/generate")
async def generate_landing_api(payload: dict):
    """Endpoint API para generar landing page con fallback inteligente"""
    nombre = payload.get("nombre_negocio", "")
    rubro = payload.get("rubro", "")
    res = generar_landing_page(nombre_negocio=nombre, rubro=rubro)
    return {
        "nombre_negocio": res.nombre_negocio,
        "rubro": res.rubro,
        "categoria_visual": res.categoria_visual,
        "status": res.status,
        "fallback_aplicado": res.fallback_aplicado
    }


# Endpoints API v1 Agencia B2B (Conectados a Base de Datos PostgreSQL/SQLite)
@app.get("/api/v1/agencia/prospectos_b2b/")
async def listar_prospectos_b2b(limit: int = 20000, db: Session = Depends(get_db)):
    from backend.models.prospect import ProspectoB2BModel
    total_db = db.query(ProspectoB2BModel).count()
    prospectos = listar_prospectos(db, limit=limit)
    items = [p.to_dict() for p in prospectos]
    return {
        "total": total_db,
        "items": items
    }


@app.post("/api/v1/agencia/b2b/prospectar")
async def iniciar_prospeccion_b2b(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Motor de prospección real por geolocalización usando Google Places API / Web Scraping.
    """
    import urllib.request
    import json
    from backend.services.domain_checker import es_sitio_web_propio

    # Extraer parámetros ya sea por JSON o Formulario HTML
    if request.headers.get("content-type") == "application/json":
        payload = await request.json()
        tipo = payload.get("tipo_busqueda", "Servicios generales")
        ciudad = payload.get("ciudad_nombre", "Córdoba, AR")
        is_html = False
    else:
        form = await request.form()
        tipo = form.get("tipo_busqueda", "Servicios generales")
        ciudad = form.get("ciudad_nombre", "Córdoba, AR")
        is_html = True

    api_key = config.GOOGLE_PLACES_API_KEY
    nuevos_prospectos = []

    if api_key and len(api_key) > 5:
        try:
            query = f"{tipo} en {ciudad}"
            url_api = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query)}&key={api_key}"
            req = urllib.request.Request(url_api, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                results = data.get("results", [])

                for item in results:
                    place_id = item.get("place_id", f"real_{uuid.uuid4().hex[:8]}")
                    nombre = item.get("name", f"{tipo.title()} {ciudad.split(',')[0].title()}")
                    sitio_web = item.get("website")

                    es_propio = es_sitio_web_propio(sitio_web)
                    p_data = {
                        "place_id": place_id,
                        "nombre": nombre,
                        "ciudad_busqueda": ciudad,
                        "tipo_busqueda": tipo,
                        "telefono": item.get("formatted_phone_number", "+54 351 555-0000"),
                        "whatsapp": "+543515550000",
                        "sitio_web": sitio_web if es_propio else None,
                        "status": "ENRIQUECIDO"
                    }
                    crear_prospecto(db, p_data)
                    nuevos_prospectos.append(p_data)
        except Exception as err:
            print(f"Error consultando Google Places API: {err}")

    # Si no hay API key o se requieren mas leads reales, ejecutar el Scraper Multicanal en vivo
    if len(nuevos_prospectos) < 50:
        from backend.services.web_scraper import extraer_leads_reales_duckduckgo
        leads_scraped = extraer_leads_reales_duckduckgo(tipo=tipo, ciudad=ciudad, max_results=50)

        for lead in leads_scraped:
            pid = f"real_web_{uuid.uuid4().hex[:8]}"
            es_propio = es_sitio_web_propio(lead.get("sitio_web"))
            tel_real = lead.get("telefono")

            p_data = {
                "place_id": pid,
                "nombre": lead["nombre"],
                "ciudad_busqueda": ciudad,
                "tipo_busqueda": tipo,
                "telefono": tel_real or "Sin teléfono",
                "whatsapp": tel_real if tel_real else None,
                "email": None,
                "sitio_web": lead.get("sitio_web") if es_propio else None,
                "status": "ENRIQUECIDO" if tel_real else "SIN_CONTACTAR"
            }
            crear_prospecto(db, p_data)
            nuevos_prospectos.append(p_data)

    if is_html:
        return RedirectResponse(url="/prospector", status_code=303)
    return {"status": "ok", "mensaje": f"Prospección finalizada para '{tipo}' en '{ciudad}'"}


@app.post("/api/v1/agencia/b2b/prospectar-agent-reach")
async def prospectar_agent_reach(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint dedicado de Agent Reach: búsqueda real de negocios con extracción
    de teléfonos auténticos desde resultados de búsqueda web en vivo.
    """
    from backend.services.agent_reach_service import buscar_negocios_reales_google
    from backend.services.domain_checker import es_sitio_web_propio

    payload = await request.json()
    rubro = payload.get("rubro", "Servicios generales")
    ubicacion = payload.get("ubicacion", "Córdoba, AR")

    # Ejecutar búsqueda real en vivo
    leads = buscar_negocios_reales_google(rubro=rubro, ciudad=ubicacion, max_results=20)

    nuevos = 0
    for lead in leads:
        pid = f"reach_{uuid.uuid4().hex[:8]}"
        es_propio = es_sitio_web_propio(lead.get("sitio_web"))
        tel = lead.get("telefono")

        p_data = {
            "place_id": pid,
            "nombre": lead["nombre"],
            "ciudad_busqueda": ubicacion,
            "tipo_busqueda": rubro,
            "telefono": tel or "Sin teléfono",
            "whatsapp": tel if tel else None,
            "email": None,
            "sitio_web": lead.get("sitio_web") if es_propio else None,
            "status": "ENRIQUECIDO" if tel else "SIN_CONTACTAR"
        }
        crear_prospecto(db, p_data)
        nuevos += 1

    return {
        "status": "ok",
        "nuevos": nuevos,
        "mensaje": f"Agent Reach: {nuevos} negocios reales encontrados para '{rubro}' en '{ubicacion}'"
    }


@app.post("/api/v1/agencia/prospectos_b2b/sincronizar-contactos")
async def sincronizar_contactos_b2b(db: Session = Depends(get_db)):
    """
    Recorre en lote la base de datos de prospectos que figuran 'Sin teléfono' y aplica 
    el motor de enriquecimiento secundario de Google Business para completar sus contactos reales.
    """
    from backend.models.prospect import ProspectoB2BModel
    from backend.services.phone_enricher import enriquecer_telefono_google_maps

    prospectos_sin_tel = db.query(ProspectoB2BModel).filter(
        (ProspectoB2BModel.telefono == "Sin teléfono") | (ProspectoB2BModel.telefono == None)
    ).limit(30).all()

    actualizados = 0
    for p in prospectos_sin_tel:
        tel_real = enriquecer_telefono_google_maps(p.nombre, p.ciudad_busqueda or "Argentina")
        if tel_real:
            p.telefono = tel_real
            p.whatsapp = tel_real
            p.status = "ENRIQUECIDO"
            actualizados += 1

    if actualizados > 0:
        db.commit()

    return {
        "status": "ok",
        "procesados": len(prospectos_sin_tel),
        "actualizados": actualizados,
        "mensaje": f"Sincronizados {actualizados} teléfonos reales en la base de datos."
    }


@app.get("/api/v1/agencia/dominio/verificar")
async def verificar_dominio(nombre: str = ""):
    clean_nombre = "".join(e for e in nombre if e.isalnum()).lower() or "miempresa"
    sugerencia = f"{clean_nombre}.com"
    return {
        "sugerencia_principal": sugerencia,
        "dominios": [
            {"dominio": f"{clean_nombre}.com", "disponible": True},
            {"dominio": f"{clean_nombre}.com.ar", "disponible": True},
            {"dominio": f"{clean_nombre}.net", "disponible": False}
        ]
    }


@app.post("/api/v1/agencia/prospectos_b2b/generar-demo/{place_id}")
async def generar_demo_prospecto(place_id: str, payload: dict, db: Session = Depends(get_db)):
    try:
        precio = payload.get("precio_usd", 350)
        dominio = payload.get("dominio_elegido", "miempresa.com")
        
        # Buscar datos del prospecto en la base de datos real
        prospecto_model = buscar_prospecto_por_place_id(db, place_id)
        prospecto = prospecto_model.to_dict() if prospecto_model else None

        nombre = prospecto["nombre"] if prospecto else f"Empresa {place_id}"
        rubro = prospecto["tipo_busqueda"] if prospecto else "Servicios"
        telefono_wa = prospecto.get("whatsapp") or prospecto.get("telefono") if prospecto else None
        
        # Invocación del servicio de inferencia de categoría visual por rubro
        resultado_landing = generar_landing_page(nombre_negocio=nombre, rubro=rubro)
        cat_visual = resultado_landing.categoria_visual
        
        # Crear directorio de demos en frontend si no existe
        demos_dir = os.path.join(frontend_dir, "demos")
        os.makedirs(demos_dir, exist_ok=True)
        
        # Armar link de WhatsApp si cuenta con teléfono
        link_wa = ""
        if telefono_wa:
            num_clean = re.sub(r"[^\d]", "", telefono_wa)
            msg_wa = f"Hola {nombre}, preparé una demo comercial exclusiva de su nuevo sitio web ({dominio}): http://localhost:8000/static/demos/{place_id}.html"
            link_wa = f"https://wa.me/{num_clean}?text={msg_wa.replace(' ', '%20')}"

        button_wa_html = f'<a href="{link_wa}" target="_blank" class="bg-gray-800 hover:bg-gray-700 text-white font-bold py-3.5 px-6 rounded-xl border border-gray-700 transition-all text-sm flex items-center justify-center gap-2"><i class="fa-brands fa-whatsapp text-emerald-400"></i> Consultar por WhatsApp</a>' if link_wa else ''
        nav_wa_link = link_wa if link_wa else '#'

        # Generar contenido HTML glassmorphic de alta gama para la demo estática
        filepath = os.path.join(demos_dir, f"{place_id}.html")
        html_demo_content = f"""<!DOCTYPE html>
<html lang="es" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nombre} — Sitio Oficial & Solución Digital</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ background-color: #090d16; color: #f3f4f6; font-family: 'Plus Jakarta Sans', sans-serif; }}
        .glass-card {{ background: rgba(17, 24, 39, 0.6); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); }}
        .hero-gradient {{ background: radial-gradient(circle at top center, rgba(99, 102, 241, 0.15) 0%, transparent 70%); }}
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between hero-gradient">

    <!-- NAV BAR -->
    <header class="max-w-6xl mx-auto w-full px-6 py-6 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
                <i class="fa-solid fa-briefcase"></i>
            </div>
            <span class="text-lg font-bold text-white tracking-tight">{nombre}</span>
        </div>
        <div class="flex items-center gap-4">
            <span class="text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-3 py-1 rounded-full font-mono uppercase font-bold">{cat_visual}</span>
            <a href="{nav_wa_link}" target="_blank" class="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-600/20">
                <i class="fa-brands fa-whatsapp"></i> Contactar
            </a>
        </div>
    </header>

    <!-- HERO SECTION -->
    <main class="max-w-6xl mx-auto w-full px-6 py-12 space-y-16">
        <section class="text-center space-y-6 max-w-3xl mx-auto pt-6">
            <div class="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs px-4 py-1.5 rounded-full font-medium">
                <i class="fa-solid fa-sparkles text-amber-400"></i> Calidad & Servicio de Excelencia en {rubro}
            </div>
            <h1 class="text-4xl md:text-6xl font-extrabold text-white leading-tight tracking-tight">
                Impulsamos la excelencia de <span class="bg-gradient-to-r from-indigo-400 via-sky-400 to-emerald-400 bg-clip-text text-transparent">{nombre}</span>
            </h1>
            <p class="text-gray-400 text-base md:text-lg leading-relaxed">
                Brindamos atención personalizada, rapidez y la máxima confiabilidad comercial en el rubro de <strong class="text-gray-200">{rubro}</strong>. Soluciones diseñadas a la medida de tus necesidades.
            </p>
            <div class="flex flex-col sm:flex-row justify-center gap-4 pt-4">
                <a href="https://checkout.dlocalgo.com/v1/pay/demo-{precio}-usd" target="_blank" class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 px-8 rounded-xl shadow-xl shadow-indigo-600/25 transition-all text-sm flex items-center justify-center gap-2">
                    <i class="fa-solid fa-lock"></i> Adquirir Dominio {dominio} (${precio} USD)
                </a>
                {button_wa_html}
            </div>
        </section>

        <!-- FEATURES / SERVICIOS GRID -->
        <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass-card p-6 rounded-2xl space-y-3">
                <div class="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center text-xl">
                    <i class="fa-solid fa-shield-halved"></i>
                </div>
                <h3 class="text-lg font-bold text-white">Garantía & Confianza</h3>
                <p class="text-sm text-gray-400 leading-relaxed">Procesos respaldados por estándares internacionales de calidad y cumplimiento asegurado.</p>
            </div>
            <div class="glass-card p-6 rounded-2xl space-y-3">
                <div class="w-12 h-12 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center text-xl">
                    <i class="fa-solid fa-bolt"></i>
                </div>
                <h3 class="text-lg font-bold text-white">Respuesta Inmediata</h3>
                <p class="text-sm text-gray-400 leading-relaxed">Atención ágil y canales directos para asesorarte sin esperas en todo momento.</p>
            </div>
            <div class="glass-card p-6 rounded-2xl space-y-3">
                <div class="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xl">
                    <i class="fa-solid fa-star"></i>
                </div>
                <h3 class="text-lg font-bold text-white">Atención Personalizada</h3>
                <p class="text-sm text-gray-400 leading-relaxed">Soluciones a la medida de tu presupuesto con foco en la satisfacción completa.</p>
            </div>
        </section>

        <!-- BANNER DE CONVERSIÓN COMERCIAL -->
        <section class="glass-card p-8 rounded-3xl border border-indigo-500/20 text-center space-y-4 relative overflow-hidden">
            <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-indigo-600/10 rounded-full blur-2xl"></div>
            <h2 class="text-2xl font-bold text-white">¿Listo para potenciar la presencia de {nombre}?</h2>
            <p class="text-sm text-gray-400 max-w-xl mx-auto">Reserva la propiedad intelectual del dominio oficial <strong class="text-indigo-300 font-mono">{dominio}</strong> y activa la plataforma comercial hoy mismo.</p>
            <div class="pt-2">
                <a href="https://checkout.dlocalgo.com/v1/pay/demo-{precio}-usd" target="_blank" class="inline-flex bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 px-8 rounded-xl shadow-lg shadow-emerald-600/20 transition-all text-sm items-center gap-2">
                    <i class="fa-solid fa-cart-shopping"></i> Confirmar Propuesta (${precio} USD)
                </a>
            </div>
        </section>
    </main>

    <!-- FOOTER -->
    <footer class="max-w-6xl mx-auto w-full px-6 py-8 border-t border-gray-800/80 flex flex-col md:flex-row justify-between items-center text-xs text-gray-500 gap-4">
        <p>© 2026 {nombre}. Todos los derechos reservados.</p>
        <p class="font-mono text-gray-600">Demo Comercial Generada por Emayon Forge — Nicho Landing Factory</p>
    </footer>

</body>
</html>"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_demo_content)

        return {
            "nombre": nombre,
            "precio_usd": precio,
            "dominio_elegido": dominio,
            "url_demo": f"/static/demos/{place_id}.html",
            "link_wa": link_wa or None
        }
    except Exception as e:
        print(f"[ERROR GENERAR DEMO]: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.post("/api/v1/agencia/checkout/crear-link-custom")
async def crear_checkout_custom(payload: dict):
    precio = payload.get("precio_usd", 350)
    return {
        "checkout_url": f"https://checkout.dlocalgo.com/v1/pay/demo-{precio}-usd"
    }


if __name__ == "__main__":
    print("==================================================")
    print("  Nicho Landing Factory & CRM Engine (FastAPI)    ")
    print("==================================================")
    print(f"[*] Usuario CRM Activo: {config.CRM_USER.upper()}")
    print(f"[*] Servidor Uvicorn iniciando en: http://127.0.0.1:{config.PORT}")
    print("==================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=config.PORT, reload=True)
