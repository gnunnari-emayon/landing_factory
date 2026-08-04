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

@app.on_event("startup")
def startup_event():
    """Inicializar esquema de base de datos y sembrar Superadmins gabi y gian"""
    from backend.core.database import SessionLocal
    from backend.services.seed_users import inicializar_superadmins
    db = SessionLocal()
    try:
        inicializar_superadmins(db)
    finally:
        db.close()


# Montar archivos estáticos (CSS, JS, imágenes)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Configurar motor de plantillas Jinja2
templates_dir = os.path.join(frontend_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)


from backend.data.latam_database import RUBROS_LATAM, UBICACIONES_LATAM
from backend.models.prospect import ProspectoB2BModel

@app.get("/", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    """Página principal Agencia Standalone (React + Tailwind) con precarga ultrarrápida de Leads"""
    total_db = db.query(ProspectoB2BModel).count()
    prospectos_iniciales = [p.to_dict() for p in listar_prospectos(db, limit=100)]
    return templates.TemplateResponse(request, "index.html", {
        "initial_prospects": prospectos_iniciales,
        "initial_total": total_db,
        "rubros_latam": RUBROS_LATAM,
        "ubicaciones_latam": UBICACIONES_LATAM
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
    from backend.models.prospect import ProspectoB2BModel
    
    total = db.query(ProspectoB2BModel).count()
    sin_web = db.query(ProspectoB2BModel).filter(
        (ProspectoB2BModel.sitio_web == None) | (ProspectoB2BModel.sitio_web == "")
    ).count()
    enriquecidos = db.query(ProspectoB2BModel).filter(
        (ProspectoB2BModel.status == "ENRIQUECIDO") | (ProspectoB2BModel.telefono != None) | (ProspectoB2BModel.whatsapp != None)
    ).count()
    contactados = db.query(ProspectoB2BModel).filter(
        ProspectoB2BModel.status.like("%CONTACTADO%")
    ).count()

    prospectos_models = db.query(ProspectoB2BModel).order_by(ProspectoB2BModel.id.desc()).limit(200).all()
    prospectos = [p.to_dict() for p in prospectos_models]

    return templates.TemplateResponse(request, "agencia/prospector.html", {
        "active_tab": "prospector",
        "total": total,
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
        leads_hallados = ejecutar_prospeccion_agent_reach(rubro=rubro, ciudad=ubicacion, max_results=50, solo_con_telefono=True)
    except Exception as err:
        print(f"Error ejecutando Agent Reach: {err}")
        leads_hallados = []

    # Fallback si Agent Reach no halló resultados suficientes
    if len(leads_hallados) == 0:
        try:
            from backend.services.web_scraper import extraer_leads_reales_duckduckgo
            leads_hallados = extraer_leads_reales_duckduckgo(tipo=rubro, ciudad=ubicacion, max_results=50)
        except Exception as err2:
            print(f"Error en fallback DuckDuckGo para Agent Reach: {err2}")

    guardados = 0
    for lead in leads_hallados:
        telefono = lead.get("telefono")
        if not telefono or telefono == "Por verificar":
            continue

        es_propio = es_sitio_web_propio(lead.get("sitio_web"))
        p_data = {
            "place_id": f"reach_{uuid.uuid4().hex[:8]}",
            "nombre": lead["nombre"],
            "tipo_busqueda": rubro,
            "ciudad_busqueda": ubicacion,
            "sitio_web": lead.get("sitio_web") if es_propio else None,
            "telefono": telefono,
            "whatsapp": telefono,
            "status": "ENRIQUECIDO"
        }
        crear_prospecto(db, p_data)
        guardados += 1
        if guardados >= 50:
            break

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
    """Servir demo HTML de prospectos con protección contra Path Traversal"""
    demos_dir = os.path.abspath(os.path.join(frontend_dir, "demos"))
    safe_filename = os.path.basename(file_name)
    filepath = os.path.abspath(os.path.join(demos_dir, safe_filename))

    if filepath.startswith(demos_dir) and os.path.exists(filepath):
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
def listar_prospectos_b2b(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    from backend.models.prospect import ProspectoB2BModel
    total_db = db.query(ProspectoB2BModel).count()
    
    query = db.query(ProspectoB2BModel).order_by(ProspectoB2BModel.id.desc())
    if limit > 0:
        query = query.offset(offset).limit(limit)
    prospectos_models = query.all()
    items = [p.to_dict() for p in prospectos_models]
    return {
        "total": total_db,
        "items": items,
        "limit": limit,
        "offset": offset
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

    api_key = getattr(config, "GOOGLE_PLACES_API_KEY", "")
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

    # Fallback si no hay API key de Google: Scraper Web Multicanal geolocalizado
    if len(nuevos_prospectos) < 50:
        from backend.services.web_scraper import extraer_leads_reales_duckduckgo
        leads_scraped = extraer_leads_reales_duckduckgo(tipo=tipo, ciudad=ciudad, max_results=50)

        for lead in leads_scraped:
            tel_real = lead.get("telefono")
            if not tel_real or tel_real == "Por verificar":
                continue

            pid = f"real_web_{uuid.uuid4().hex[:8]}"
            es_propio = es_sitio_web_propio(lead.get("sitio_web"))

            p_data = {
                "place_id": pid,
                "nombre": lead["nombre"],
                "ciudad_busqueda": ciudad,
                "tipo_busqueda": tipo,
                "telefono": tel_real,
                "whatsapp": tel_real,
                "email": None,
                "sitio_web": lead.get("sitio_web") if es_propio else None,
                "status": "ENRIQUECIDO"
            }
            crear_prospecto(db, p_data)
            nuevos_prospectos.append(p_data)
            if len(nuevos_prospectos) >= 50:
                break

    if is_html:
        return RedirectResponse(url="/prospector", status_code=303)
    return {"status": "ok", "mensaje": f"Prospección finalizada para '{tipo}' en '{ciudad}'"}





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


@app.post("/api/v1/agencia/prospectos_b2b/limpiar-sin-telefono")
@app.delete("/api/v1/agencia/prospectos_b2b/limpiar-sin-telefono")
async def limpiar_prospectos_sin_telefono(db: Session = Depends(get_db)):
    """Elimina de la base de datos todos los prospectos que no posean número telefónico disponible."""
    from backend.models.prospect import ProspectoB2BModel
    eliminados = db.query(ProspectoB2BModel).filter(
        (ProspectoB2BModel.telefono == None) | 
        (ProspectoB2BModel.telefono == "") | 
        (ProspectoB2BModel.telefono == "Por verificar") | 
        (ProspectoB2BModel.telefono == "Sin teléfono")
    ).delete(synchronize_session=False)
    db.commit()
    restantes = db.query(ProspectoB2BModel).count()
    return {
        "status": "ok",
        "eliminados": eliminados,
        "restantes": restantes,
        "mensaje": f"Se eliminaron {eliminados} prospectos sin teléfono. Restan {restantes} prospectos en la base de datos."
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


from fastapi import Body

@app.post("/api/v1/agencia/prospectos_b2b/generar-demo/{place_id}")
async def generar_demo_prospecto(place_id: str, payload: dict = Body(default={}), db: Session = Depends(get_db)):
    try:
        payload = payload or {}
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
        
        # Enriquecimiento web e integración con el motor de temas visuales
        from backend.services.landing_theme_engine import obtener_theme_config, obtener_contexto_web_empresa
        ciudad_prospecto = prospecto.get("ciudad_busqueda") if prospecto else "Rosario, AR"
        theme = obtener_theme_config(cat_visual, prospecto_seed=place_id)
        ctx_web = obtener_contexto_web_empresa(nombre, ciudad_prospecto)
        
        # Crear directorio de demos en frontend si no existe
        demos_dir = os.path.join(frontend_dir, "demos")
        os.makedirs(demos_dir, exist_ok=True)
        
        # Armar link de WhatsApp si cuenta con teléfono
        link_wa = ""
        if telefono_wa and telefono_wa != "Por verificar":
            num_clean = re.sub(r"[^\d]", "", telefono_wa)
            msg_wa = f"Hola {nombre}, preparé una demo comercial exclusiva de su nuevo sitio web ({dominio}): http://localhost:8000/static/demos/{place_id}.html"
            link_wa = f"https://wa.me/{num_clean}?text={msg_wa.replace(' ', '%20')}"

        button_wa_html = f'<a href="{link_wa}" target="_blank" class="bg-emerald-500/10 hover:bg-emerald-500 text-emerald-400 hover:text-white font-bold py-3.5 px-6 rounded-xl border border-emerald-500/30 hover:border-emerald-500 transition-all duration-200 text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-900/10 hover:shadow-emerald-500/20"><i class="fa-brands fa-whatsapp text-lg"></i> Consultar por WhatsApp</a>' if link_wa else ''
        nav_wa_link = link_wa if link_wa else '#'

        # 1. Formatear características en Grilla Enterprise 3x2 con asignación semántica 1:1
        features_html = ""
        items_features = theme["features"][:6]
        seed_hash = sum(ord(c) for c in place_id)
        services_offset = seed_hash % 6
        news_offset = (seed_hash + 3) % 6

        for idx, feat in enumerate(items_features):
            if "image_key" in feat:
                img_path = f"/static/img/services/{feat['image_key']}.jpg"
            else:
                img_num = ((idx + services_offset) % 6) + 1
                img_path = f"/static/img/services/{cat_visual}_{img_num}.jpg"
            
            features_html += f"""
            <div class="glass-card rounded-3xl overflow-hidden group flex flex-col justify-between transition-all duration-300 hover:-translate-y-1">
                <div>
                    <!-- CABECERA FOTOGRÁFICA 16:9 DEL SERVICIO SIN OVERLAY -->
                    <div class="relative h-44 w-full overflow-hidden">
                        <img src="{img_path}" alt="{feat['title']}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy">
                        
                        <!-- ICONO Y BADGE SUPERPUESTOS EN LA FOTO -->
                        <div class="absolute top-4 left-4 right-4 flex justify-between items-center z-10">
                            <div class="w-10 h-10 rounded-xl backdrop-blur-md flex items-center justify-center text-lg shadow-lg" style="background: rgba(15, 23, 42, 0.85); color: {theme['accent']}; border: 1px solid {theme['border']};">
                                <i class="fa-solid {feat['icon']}"></i>
                            </div>
                            <span class="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full backdrop-blur-md shadow-md" style="background: rgba(15, 23, 42, 0.85); color: {theme['accent']}; border: 1px solid {theme['border']};">{feat.get('tag', 'Servicio')}</span>
                        </div>
                    </div>

                    <!-- CONTENIDO DE LA TARJETA -->
                    <div class="p-6 space-y-3">
                        <h3 class="text-lg font-bold text-white tracking-tight leading-snug display-font group-hover:text-amber-400 transition-colors">{feat['title']}</h3>
                        <p class="text-xs text-slate-300 leading-relaxed">{feat['desc']}</p>
                    </div>
                </div>
            </div>
            """

        # 2. Formatear novedades / noticias del sector con asignación semántica 1:1
        news_html = ""
        for idx, item in enumerate(theme.get("news", [])):
            if "image_key" in item:
                news_img_path = f"/static/img/news/{item['image_key']}.jpg"
            else:
                news_img_num = ((idx + news_offset) % 6) + 1
                news_img_path = f"/static/img/news/{cat_visual}_news_{news_img_num}.jpg"
            
            news_html += f"""
            <div class="flex-none w-[88%] md:w-[31%] glass-card rounded-3xl overflow-hidden group flex flex-col justify-between transition-all duration-300 hover:-translate-y-1 snap-start">
                <div>
                    <!-- CABECERA FOTOGRÁFICA 16:9 DE LA NOTICIA SIN OVERLAY -->
                    <div class="relative h-44 w-full overflow-hidden">
                        <img src="{news_img_path}" alt="{item['title']}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy">
                        
                        <div class="absolute top-4 left-4 right-4 flex justify-between items-center z-10">
                            <span class="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full backdrop-blur-md shadow-md text-emerald-400" style="background: rgba(15, 23, 42, 0.85); border: 1px solid {theme['border']};">
                                <i class="fa-solid fa-circle-check text-[9px]"></i> {item['date']}
                            </span>
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-950/80 text-slate-300 border border-white/10 backdrop-blur-md">{item['read_time']}</span>
                        </div>
                    </div>

                    <!-- CONTENIDO DE LA NOTICIA -->
                    <div class="p-6 space-y-3">
                        <h3 class="text-lg font-bold text-white group-hover:text-amber-400 transition-colors leading-snug display-font">{item['title']}</h3>
                        <p class="text-xs text-slate-300 leading-relaxed">{item['snippet']}</p>
                    </div>
                </div>

                <div class="px-6 pb-6 pt-2">
                    <a href="{nav_wa_link}" target="_blank" class="text-xs font-semibold inline-flex items-center gap-1.5 transition-all group-hover:translate-x-1" style="color: {theme['accent']};">
                        Leer artículo completo <i class="fa-solid fa-arrow-right text-[10px]"></i>
                    </a>
                </div>
            </div>
            """

        # 3. Verificación de Reseñas Auténticas de Google Maps (Si NO existen, NO mostrar la sección)
        from backend.services.google_reviews_service import obtener_resenas_reales_google
        resenas_autenticas = obtener_resenas_reales_google(nombre, ciudad_prospecto)

        reviews_section_html = ""
        nav_reviews_link_html = ""

        if resenas_autenticas:
            reviews_cards_html = ""
            for rev in resenas_autenticas:
                reviews_cards_html += f"""
                <div class="glass-card p-6 rounded-2xl space-y-4">
                    <div class="flex items-center justify-between">
                        <div class="flex text-amber-400 text-xs gap-1">
                            <i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i><i class="fa-solid fa-star"></i>
                        </div>
                        <span class="text-[11px] text-slate-400 font-mono flex items-center gap-1"><i class="fa-brands fa-google text-slate-400"></i> {rev['city']}</span>
                    </div>
                    <p class="text-sm text-slate-300 italic leading-relaxed">"{rev['comment']}"</p>
                    <div class="flex items-center gap-3 pt-2 border-t border-white/5">
                        <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs text-white" style="background-color: {theme['accent']}; font-family: {theme['font_display']};">
                            {rev['name'][0]}
                        </div>
                        <div>
                            <div class="text-xs font-bold text-white">{rev['name']}</div>
                            <div class="text-[10px] text-emerald-400 flex items-center gap-1"><i class="fa-solid fa-circle-check text-[8px]"></i> Opinión Verificada en Google</div>
                        </div>
                    </div>
                </div>
                """
            reviews_section_html = f"""
            <!-- SECCIÓN 3: PRUEBA SOCIAL & RESEÑAS -->
            <section id="reseñas" class="space-y-8">
                <div class="text-center space-y-2">
                    <span class="text-xs font-bold uppercase font-mono tracking-widest text-slate-400">Confianza Comprobada</span>
                    <h2 class="text-3xl font-extrabold text-white tracking-tight display-font">Opiniones Reales de Nuestros Clientes</h2>
                    <p class="text-sm text-slate-400 max-w-xl mx-auto">Reseñas autenticadas de quienes confían en {nombre} en Google Maps.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {reviews_cards_html}
                </div>
            </section>
            """
            nav_reviews_link_html = '<a href="#reseñas" class="hover:text-white transition-colors">Opiniones</a>'

        # 4. Formatear los 6 Módulos Enterprise en tarjetas Apple-Style (Canvas Blanco)
        enterprise_html = ""
        for mod in theme.get("enterprise_modules", []):
            enterprise_html += f"""
            <div class="bg-slate-50 p-7 rounded-3xl space-y-4 border border-slate-200 hover:border-slate-400 hover:shadow-xl transition-all duration-300 relative group flex flex-col justify-between">
                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <div class="w-12 h-12 rounded-2xl bg-white flex items-center justify-center text-xl text-slate-900 shadow-sm border border-slate-200">
                            <i class="fa-solid {mod['icon']}"></i>
                        </div>
                        <span class="text-[10px] font-bold tracking-wider uppercase px-3 py-1 rounded-full bg-amber-100 text-amber-900 border border-amber-200 flex items-center gap-1">
                            <i class="fa-solid fa-lock text-[9px]"></i> Módulo A Desbloquear
                        </span>
                    </div>
                    <div>
                        <span class="text-[10px] text-slate-500 uppercase font-mono font-bold tracking-wider">{mod['tag']}</span>
                        <h3 class="text-xl font-bold text-slate-950 tracking-tight mt-0.5">{mod['title']}</h3>
                    </div>
                    <p class="text-xs text-slate-600 leading-relaxed">{mod['desc']}</p>
                </div>
                <div class="pt-4 border-t border-slate-200">
                    <a href="{nav_wa_link}" target="_blank" class="w-full text-xs font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all bg-slate-950 hover:bg-slate-800 text-white shadow-md">
                        <i class="fa-solid fa-key text-[10px]"></i> Solicitar Activación de Módulo
                    </a>
                </div>
            </div>
            """

        # Generar contenido HTML con Taste DNA y estética personalizada
        filepath = os.path.join(demos_dir, f"{place_id}.html")
        html_demo_content = f"""<!DOCTYPE html>
<html lang="es" class="dark scroll-smooth" style="background-color: {theme['bg']};">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nombre} — Sitio Oficial Público & Vista Previa</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="{theme['font_google']}" rel="stylesheet">
    <style>
        html, body {{ background-color: {theme['bg']}; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; padding: 0; scroll-behavior: smooth; }}
        .display-font {{ font-family: {theme['font_display']}; }}
        .glass-card {{ background: {theme['card_bg']}; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid {theme['border']}; box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), inset 0 1px 0 0 rgba(255, 255, 255, 0.08); transition: all 0.25s ease; }}
        .glass-card:hover {{ border-color: {theme['border_hover']}; transform: translateY(-2px); }}
        .hero-banner-full {{
            position: relative;
            width: 100%;
            min-height: 540px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-image: linear-gradient(to bottom, rgba(7, 10, 18, 0.65) 0%, rgba(7, 10, 18, 0.75) 50%, {theme['bg']} 100%), url('{theme.get("hero_image", "")}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between antialiased hero-bg text-slate-100" style="background-color: {theme['bg']};">

    <!-- EMAYOON FORGE COMMERCIAL B2B DOCK (SUPERIOR) -->
    <div class="bg-slate-950 border-b border-amber-500/20 px-6 py-2 flex flex-wrap justify-between items-center text-xs backdrop-blur-xl z-50">
        <div class="flex items-center gap-2.5 font-medium py-1">
            <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
            <span class="text-slate-300">Propuesta Comercial B2B por <a href="https://emayonforge.com/" target="_blank" class="text-amber-400 font-bold hover:underline">Emayon Forge</a> para <strong class="text-white">{nombre}</strong></span>
        </div>
        <div class="flex items-center gap-3 py-1">
            <a href="#enterprise" class="bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold px-3.5 py-1.5 rounded-full transition-all flex items-center gap-1.5 shadow-md">
                <i class="fa-solid fa-arrow-down text-xs"></i> Ver Módulos Enterprise
            </a>
            <a href="https://emayonforge.com/" target="_blank" class="text-slate-400 hover:text-white transition-colors flex items-center gap-1 text-[11px]">
                emayonforge.com <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
            </a>
        </div>
    </div>

    <!-- STICKY NAVBAR PÚBLICO DEL CLIENTE -->
    <header class="sticky top-0 z-40 backdrop-blur-xl border-b border-white/5 bg-slate-950/90 shadow-lg">
        <div class="max-w-7xl mx-auto px-6 py-3.5 flex justify-between items-center">
            <a href="#hero" class="flex items-center gap-3 group">
                <div class="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-white shadow-lg transition-transform group-hover:scale-105" style="background-color: {theme['accent']};">
                    <i class="fa-solid fa-briefcase text-sm"></i>
                </div>
                <span class="text-base md:text-lg font-bold text-white tracking-tight display-font">{nombre}</span>
            </a>

            <!-- NAV LINKS PÚBLICOS -->
            <nav class="hidden md:flex items-center gap-6 text-xs font-medium text-slate-300">
                <a href="#hero" class="hover:text-white transition-colors">Inicio</a>
                <a href="#servicios" class="hover:text-white transition-colors">Servicios</a>
                <a href="#noticias" class="hover:text-white transition-colors">Novedades</a>
                {nav_reviews_link_html}
                <a href="#contacto" class="hover:text-white transition-colors">Ubicación</a>
            </nav>

            <div class="flex items-center gap-3">
                <a href="{nav_wa_link}" target="_blank" class="text-xs bg-emerald-500/10 hover:bg-emerald-500 text-emerald-400 hover:text-white font-bold px-3.5 py-2 rounded-xl transition-all duration-200 border border-emerald-500/30 hover:border-emerald-500 flex items-center gap-1.5 shadow-sm whitespace-nowrap">
                    <i class="fa-brands fa-whatsapp text-sm"></i> Contactar
                </a>
            </div>
        </div>
    </header>

    <!-- 1. PARTE PÚBLICA: LANDING PAGE DEL CLIENTE (HERO SPLIT 2-COLUMNS BANNER) -->
    <section class="hero-banner-full py-20 md:py-28 px-6 w-full" id="hero">
        <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10 items-center relative z-10">
            
            <!-- COLUMNA IZQUIERDA: MENSAJE PRINCIPAL & IDENTIDAD DEL CLIENTE -->
            <div class="lg:col-span-7 space-y-6 text-left">
                
                <!-- EYEBROW / PILL ENTERPRISE REDISEÑADO CON ALTO CONTRASTE -->
                <div class="inline-flex flex-wrap items-center gap-2.5 text-xs px-4 py-2 rounded-full font-medium shadow-xl bg-slate-900/90 border border-white/10 text-slate-200 backdrop-blur-md">
                    <span class="flex items-center gap-1.5 text-emerald-400 font-semibold"><i class="fa-solid fa-location-dot text-xs"></i> {ciudad_prospecto.split(',')[0]}</span>
                    <span class="text-slate-600">•</span>
                    <span class="flex items-center gap-1 text-amber-400 font-semibold"><i class="fa-solid fa-star text-xs"></i> 4.9 (Google Reviews)</span>
                    <span class="text-slate-600">•</span>
                    <span class="text-slate-300 font-medium">{theme['badge']}</span>
                </div>
                
                <h1 class="text-4xl md:text-6xl font-extrabold text-white leading-tight tracking-tight display-font drop-shadow-2xl">
                    <span class="bg-gradient-to-r {theme['accent_gradient']} bg-clip-text text-transparent">{nombre}</span>
                </h1>
                
                <p class="text-slate-200 text-base md:text-lg font-normal leading-relaxed max-w-2xl text-shadow">
                    {ctx_web['resumen_web']}
                </p>
                
                <div class="flex flex-col sm:flex-row gap-4 pt-2">
                    <a href="#contacto" class="text-white font-bold py-4 px-8 rounded-xl transition-all duration-200 text-sm flex items-center justify-center gap-2 glow-btn shadow-xl" style="background-color: {theme['accent']};">
                        <i class="fa-solid fa-calendar-check"></i> {theme.get('cta_text', 'Consultar Ahora')}
                    </a>
                    {button_wa_html}
                </div>
            </div>

            <!-- COLUMNA DERECHA: CARD FLOTANTE GLASSMORPHIC DE ACCIÓN RÁPIDA -->
            <div class="lg:col-span-5">
                <div class="glass-card p-7 rounded-3xl space-y-6 shadow-2xl backdrop-blur-2xl border border-white/15" style="background: rgba(15, 23, 42, 0.85);">
                    <div class="flex items-center justify-between border-b border-white/10 pb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 text-lg">
                                <i class="fa-solid fa-clock font-bold"></i>
                            </div>
                            <div>
                                <div class="text-xs font-bold text-white uppercase tracking-wider">Atención Directa</div>
                                <div class="text-[11px] text-emerald-400 flex items-center gap-1 font-medium"><i class="fa-solid fa-circle text-[6px]"></i> Respuesta Inmediata</div>
                            </div>
                        </div>
                        <span class="text-[11px] font-semibold px-3 py-1 rounded-full bg-white/5 text-slate-200 border border-white/10">{ciudad_prospecto.split(',')[0]}</span>
                    </div>

                    <div class="space-y-3 text-xs text-slate-300">
                        <div class="flex items-start gap-3">
                            <i class="fa-solid fa-calendar-days text-amber-400 w-5 text-center text-sm pt-0.5"></i>
                            <div>
                                <strong class="text-white block font-semibold">Horarios de Atención:</strong>
                                <span>{theme.get('hours', 'Lunes a Viernes 08:30 - 19:30 hs')}</span>
                            </div>
                        </div>
                        <div class="flex items-start gap-3">
                            <i class="fa-solid fa-shield-halved text-sky-400 w-5 text-center text-sm pt-0.5"></i>
                            <div>
                                <strong class="text-white block font-semibold">Calidad Garantizada:</strong>
                                <span>Diagnóstico, profesionalismo y atención personalizada.</span>
                            </div>
                        </div>
                    </div>

                    <div class="pt-2">
                        <a href="{nav_wa_link}" target="_blank" class="w-full text-white font-bold py-3.5 px-6 rounded-xl transition-all duration-200 text-xs flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 shadow-lg shadow-emerald-900/30">
                            <i class="fa-brands fa-whatsapp text-base"></i> Consultar por WhatsApp
                        </a>
                    </div>
                </div>
            </div>

        </div>
    </section>

    <main class="max-w-7xl mx-auto w-full px-6 py-16 space-y-24 relative z-10">

        <!-- SECCIÓN 1: SERVICIOS & ESPECIALIDADES DEL CLIENTE -->
        <section id="servicios" class="space-y-8">
            <div class="text-center space-y-2">
                <span class="text-xs font-bold uppercase font-mono tracking-widest text-slate-400">Oferta Comercial</span>
                <h2 class="text-3xl font-extrabold text-white tracking-tight display-font">Servicios & Especialidades Destacadas</h2>
                <p class="text-sm text-slate-400 max-w-xl mx-auto">Soluciones profesionales diseñadas a la medida para garantizar el máximo valor a nuestros clientes.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {features_html}
            </div>
        </section>

        <!-- SECCIÓN 2: NOVEDADES & NOTICIAS DEL SECTOR (CARROUSEL INTERACTIVO) -->
        <section id="noticias" class="space-y-8">
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div class="space-y-2 text-left">
                    <span class="text-xs font-bold uppercase font-mono tracking-widest text-slate-400">Actualidad & Contenido</span>
                    <h2 class="text-3xl font-extrabold text-white tracking-tight display-font">Novedades & Noticias del Sector</h2>
                    <p class="text-sm text-slate-400 max-w-xl">Información de interés, tendencias y recomendaciones preparadas por nuestro equipo.</p>
                </div>
                
                <!-- BOTONES DE NAVEGACIÓN DEL CARROUSEL -->
                <div class="flex items-center gap-3">
                    <button onclick="document.getElementById('news-carousel').scrollBy({{left: -350, behavior: 'smooth'}})" class="w-10 h-10 rounded-full bg-slate-900/90 hover:bg-slate-800 border border-white/10 text-white flex items-center justify-center transition-all shadow-md active:scale-95">
                        <i class="fa-solid fa-chevron-left text-xs"></i>
                    </button>
                    <button onclick="document.getElementById('news-carousel').scrollBy({{left: 350, behavior: 'smooth'}})" class="w-10 h-10 rounded-full bg-slate-900/90 hover:bg-slate-800 border border-white/10 text-white flex items-center justify-center transition-all shadow-md active:scale-95">
                        <i class="fa-solid fa-chevron-right text-xs"></i>
                    </button>
                </div>
            </div>

            <!-- CONTENEDOR SLIDER CON SNAP SCROLL & HIDE SCROLLBAR -->
            <div id="news-carousel" class="flex gap-6 overflow-x-auto snap-x snap-mandatory scroll-smooth pb-4 pt-1 no-scrollbar" style="scrollbar-width: none; -ms-overflow-style: none;">
                {news_html}
            </div>
        </section>

        {reviews_section_html}

        <!-- SECCIÓN 5: UBICACIÓN & HORARIOS -->
        <section id="contacto" class="glass-card p-8 md:p-10 rounded-3xl relative overflow-hidden">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
                <!-- Columna Izquierda: Información de Atención & Canales -->
                <div class="lg:col-span-6 space-y-6 flex flex-col justify-between">
                    <div class="space-y-4">
                        <span class="text-xs font-bold uppercase font-mono tracking-widest text-emerald-400 flex items-center gap-2">
                            <i class="fa-solid fa-location-dot"></i> Ubicación & Atención Directa
                        </span>
                        <h2 class="text-3xl font-extrabold text-white tracking-tight display-font">Atención Presencial & Canales Oficiales en {ciudad_prospecto}</h2>
                        <p class="text-sm text-slate-300 leading-relaxed">
                            Estamos comprometidos a brindar respuestas rápidas y asesoría transparente. Contáctanos por nuestro canal directo o solicita una reunión comercial.
                        </p>
                    </div>

                    <div class="space-y-3 text-xs text-slate-300 bg-slate-900/40 p-4 rounded-xl border border-white/5">
                        <div class="flex items-center gap-3"><i class="fa-solid fa-clock text-amber-400 w-5 text-center"></i> <span><strong>Horarios:</strong> {theme.get('hours', 'Lunes a Sábados 09:00 - 20:00 hs')}</span></div>
                        <div class="flex items-center gap-3"><i class="fa-solid fa-map-location-dot text-sky-400 w-5 text-center"></i> <span><strong>Ciudad:</strong> {ciudad_prospecto}</span></div>
                        <div class="flex items-center gap-3"><i class="fa-solid fa-globe text-indigo-400 w-5 text-center"></i> <span><strong>Dominio Exclusivo:</strong> {dominio}</span></div>
                    </div>

                    <!-- Tarjeta WhatsApp Integrada -->
                    <div class="glass-card p-5 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4 border border-white/10" style="background: rgba(0,0,0,0.25);">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-full flex items-center justify-center text-lg text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 shrink-0">
                                <i class="fa-solid fa-headset"></i>
                            </div>
                            <div class="text-left">
                                <h3 class="text-sm font-bold text-white display-font">¿Dudas sobre el servicio?</h3>
                                <p class="text-[11px] text-slate-400">Atención directa con nuestro equipo.</p>
                            </div>
                        </div>
                        <a href="{nav_wa_link}" target="_blank" class="w-full sm:w-auto text-white font-bold py-2.5 px-5 rounded-xl transition-all duration-200 text-xs flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 shadow-lg shadow-emerald-900/30 whitespace-nowrap">
                            <i class="fa-brands fa-whatsapp text-sm"></i> Iniciar Chat
                        </a>
                    </div>
                </div>

                <!-- Columna Derecha: Mapa Interactivo Dark -->
                <div class="lg:col-span-6 flex flex-col">
                    <div class="map-frame-wrapper relative w-full h-full min-h-[320px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-slate-950 group">
                        <!-- Google Maps Iframe con filtro dark -->
                        <iframe 
                            class="w-full h-full min-h-[320px] border-0 filter invert-[90%] hue-rotate-180 contrast-[120%] grayscale-[20%] transition-all duration-500 group-hover:filter-none"
                            src="https://maps.google.com/maps?q={ciudad_prospecto}&t=&z=13&ie=UTF8&iwloc=&output=embed"
                            allowfullscreen="" 
                            loading="lazy" 
                            referrerpolicy="no-referrer-when-downgrade">
                        </iframe>

                        <!-- Pin de Ubicación con animación de pulso -->
                        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none z-10 flex flex-col items-center">
                            <div class="w-4 h-4 bg-emerald-400 rounded-full shadow-[0_0_12px_#00c885] animate-ping opacity-75"></div>
                            <div class="w-3 h-3 bg-emerald-500 rounded-full shadow-[0_0_8px_#00c885] -mt-3"></div>
                        </div>

                        <!-- Overlay Glassmorphism con botón 'Abrir Mapa' -->
                        <div class="absolute bottom-4 left-4 right-4 p-3 rounded-xl bg-slate-900/80 backdrop-blur-md border border-white/10 flex items-center justify-between z-20 shadow-lg">
                            <div class="flex items-center gap-2 text-xs text-white font-medium">
                                <i class="fa-solid fa-compass text-emerald-400"></i>
                                <span>{ciudad_prospecto}</span>
                            </div>
                            <a href="https://maps.google.com/?q={ciudad_prospecto}" target="_blank" class="text-[11px] font-bold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition-colors">
                                Abrir en Google Maps <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- PIE DE PÁGINA PÚBLICO DEL CLIENTE -->
    <footer class="max-w-7xl mx-auto w-full px-6 py-6 border-t border-white/5 flex justify-between items-center text-xs text-slate-500 relative z-10">
        <p>© 2026 {nombre}. Todos los derechos reservados.</p>
        <p class="text-slate-500 font-mono">Sitio Web Oficial — {ciudad_prospecto}</p>
    </footer>

    <!-- WIDGET FLOTANTE DE WHATSAPP PÚBLICO -->
    <a href="{nav_wa_link}" target="_blank" class="fixed bottom-6 right-6 z-40 w-14 h-14 bg-emerald-500 hover:bg-emerald-600 text-white rounded-full flex items-center justify-center text-2xl shadow-2xl shadow-emerald-900/50 transition-transform duration-300 hover:scale-110 border-2 border-white/20">
        <i class="fa-brands fa-whatsapp"></i>
    </a>


    <!-- ========================================================================= -->
    <!-- 2. DIVISOR COMERCIAL MARKETINERO: "IMPULSÁ TU NEGOCIO"                    -->
    <!-- ========================================================================= -->
    <section class="w-full bg-slate-900 border-t-2 border-b-2 border-amber-400/40 py-10 px-6 text-slate-100 shadow-2xl relative z-30">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
            <div class="flex items-center gap-4 text-left">
                <div class="w-12 h-12 rounded-2xl bg-amber-400/10 border border-amber-400/30 flex items-center justify-center text-amber-400 text-2xl font-bold">
                    <i class="fa-solid fa-rocket"></i>
                </div>
                <div>
                    <span class="text-xs font-mono font-bold tracking-widest text-amber-400 uppercase flex items-center gap-1.5">
                        <i class="fa-solid fa-bolt text-[10px]"></i> Crecimiento & Automatización B2B
                    </span>
                    <h3 class="text-xl md:text-2xl font-extrabold text-white tracking-tight">Impulsá la Presencia Digital de {nombre} al Siguiente Nivel</h3>
                    <p class="text-xs text-slate-300">Descubrí las capacidades enterprise y módulos avanzados desarrollados por Emayon Forge.</p>
                </div>
            </div>
            <a href="#enterprise" class="px-6 py-3.5 rounded-full bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-amber-400/20 transition-all">
                Ver Módulos Enterprise <i class="fa-solid fa-arrow-down text-[10px]"></i>
            </a>
        </div>
    </section>


    <!-- ========================================================================= -->
    <!-- 3. CANVAS ENTERPRISE APPLE STYLE (FONDO BLANCO LÍMPIDO CON LOGO EMAYOON)   -->
    <!-- ========================================================================= -->
    <section id="enterprise" class="w-full bg-white text-slate-950 py-20 px-6 relative z-20 border-b border-slate-200">
        <div class="max-w-7xl mx-auto space-y-12">
            
            <!-- HEADER DE SECCIÓN CON LOGO EMAYOON FORGE -->
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-200 pb-8">
                <div class="space-y-2 max-w-2xl">
                    <div class="inline-flex items-center gap-2 text-xs font-bold uppercase font-mono tracking-widest px-3.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-300">
                        <i class="fa-solid fa-crown text-amber-600"></i> Potencial Enterprise de {nombre}
                    </div>
                    <h2 class="text-3xl md:text-5xl font-black text-slate-950 tracking-tight leading-tight display-font">
                        Módulos & Capacidades a Desbloquear
                    </h2>
                    <p class="text-slate-600 text-sm md:text-base leading-relaxed">
                        Esta demo representa la base visual de tu plataforma. Al contratar tu plan oficial, podrás desbloquear estas 6 funciones avanzadas para automatizar tu negocio al 100%.
                    </p>
                </div>

                <!-- BADGE CON LOGO OFICIAL EMAYOON FORGE Y ENLACE -->
                <a href="https://emayonforge.com/" target="_blank" class="flex items-center gap-3.5 p-3.5 rounded-2xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-all group shadow-sm">
                    <div class="w-11 h-11 rounded-xl bg-slate-950 flex items-center justify-center text-amber-400 font-bold text-2xl shadow-md group-hover:scale-105 transition-transform">
                        ⚡
                    </div>
                    <div>
                        <span class="text-xs font-black tracking-tight text-slate-950 uppercase block">EMAYON FORGE</span>
                        <span class="text-[10px] font-mono text-slate-500 flex items-center gap-1">emayonforge.com <i class="fa-solid fa-arrow-up-right-from-square text-[8px]"></i></span>
                    </div>
                </a>
            </div>

            <!-- GRID DE LOS 6 MÓDULOS ENTERPRISE (ESTILO APPLE) -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {enterprise_html}
            </div>

            <!-- ADQUISICIÓN RÁPIDA & GARANTÍA -->
            <div class="p-8 rounded-3xl bg-slate-900 text-white flex flex-col md:flex-row justify-between items-center gap-6 shadow-xl">
                <div class="space-y-1 text-center md:text-left">
                    <h3 class="text-xl font-bold tracking-tight">¿Listo para activar el dominio exclusivo {dominio}?</h3>
                    <p class="text-xs text-slate-300">Incluye alta en &lt; 24hs, infraestructura Cloud y la base para integrar estos módulos enterprise.</p>
                </div>
                <a href="https://checkout.dlocalgo.com/v1/pay/demo-{precio}-usd" target="_blank" class="px-8 py-4 rounded-full bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-amber-400/20 transition-all">
                    Adquirir Dominio (${precio} USD) <i class="fa-solid fa-cart-shopping text-xs"></i>
                </a>
            </div>

            <!-- INFRAESTRUCTURA & SEGURIDAD -->
            <div class="pt-8 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center gap-6 text-xs text-slate-500">
                <span class="font-mono font-bold tracking-widest uppercase text-slate-400">INFRAESTRUCTURA CERTIFICADA:</span>
                <div class="flex flex-wrap items-center gap-8 font-semibold text-slate-700">
                    <div class="flex items-center gap-2">
                        <i class="fa-solid fa-shield-halved text-emerald-600 text-base"></i>
                        <span>Infraestructura Cloud SSL 99.9% Uptime</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <i class="fa-solid fa-bolt text-amber-500 text-base"></i>
                        <span>Despliegue e Integración por Emayon Forge</span>
                    </div>
                </div>
            </div>

        </div>
    </section>

    <!-- FOOTER B2B OFICIAL EMAYOON FORGE -->
    <footer class="w-full bg-slate-950 text-slate-400 py-8 px-6 text-xs border-t border-slate-800">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <p>© 2026 Emayon Forge. Plataforma comercial desarrollada para <strong class="text-white">{nombre}</strong>.</p>
            <a href="https://emayonforge.com/" target="_blank" class="text-amber-400 font-bold hover:underline flex items-center gap-1.5">
                www.emayonforge.com <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
            </a>
        </div>
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
        import traceback
        traceback.print_exc()
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
