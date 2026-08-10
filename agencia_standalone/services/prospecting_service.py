# app/services/prospecting_service.py

import random
import time
import re
import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import Session
from urllib.parse import quote_plus

try:
    from app import models, schemas, crud
except Exception:
    try:
        from app.models import prospecto as models
    except Exception:
        models = None
    schemas = None
    crud = None

try:
    from app.database import SessionLocal
except Exception:
    SessionLocal = None

try:
    from app.core.config import settings
except Exception:
    import os
    settings = type("Settings", (), {
        "GOOGLE_SERVER_API_KEY": os.getenv("GOOGLE_SERVER_API_KEY", os.getenv("GOOGLE_MAPS_API_KEY", ""))
    })()

# --- IMPORTACIONES DE SERVICIOS (CORREGIDO) ---
try:
    from agencia_standalone.services.gemini_service import generate_chat_response
except ImportError:
    from app.services.gemini_service import generate_chat_response

try:
    from app.services.email_service import send_google_workspace_email
    from app.services.meta_service import send_template 
except ImportError:
    send_google_workspace_email = None
    send_template = None 

# --- CONFIGURACIÓN ---
TZ_ARGENTINA = pytz.timezone('America/Argentina/Buenos_Aires')
GOOGLE_API_KEY = settings.GOOGLE_SERVER_API_KEY
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_API_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# --- MEMORIA GEOGRÁFICA ---
KNOWN_LOCATIONS = {
    # ARGENTINA
    "Buenos Aires, AR": {"lat": -34.6037, "lng": -58.3816},
    "Córdoba, AR": {"lat": -31.4201, "lng": -64.1888},
    "Rosario, AR": {"lat": -32.9442, "lng": -60.6500},
    "Mendoza, AR": {"lat": -32.8895, "lng": -68.8458},
    "La Plata, AR": {"lat": -34.9215, "lng": -57.9545},
    "Mar del Plata, AR": {"lat": -38.0055, "lng": -57.5426},
    "San Miguel de Tucumán, AR": {"lat": -26.8083, "lng": -65.2176},
    "Salta, AR": {"lat": -24.7829, "lng": -65.4106},
    "Santa Fe, AR": {"lat": -31.6107, "lng": -60.7073},
    "Neuquén, AR": {"lat": -38.9516, "lng": -68.0591},
    
    # LATAM (Principales)
    "Ciudad de México, MX": {"lat": 19.4326, "lng": -99.1332},
    "Bogotá, CO": {"lat": 4.7110, "lng": -74.0721},
    "Santiago, CL": {"lat": -33.4489, "lng": -70.6693},
    "Lima, PE": {"lat": -12.0464, "lng": -77.0428},
    "Montevideo, UY": {"lat": -34.9011, "lng": -56.1645},
    "Asunción, PY": {"lat": -25.2637, "lng": -57.5759},
    "Madrid, ES": {"lat": 40.4168, "lng": -3.7038},
}

# --- DICCIONARIO DE PREFIJOS ---
PREFIX_MAP = {
    "AR": "549", "ES": "34", "MX": "52", "CO": "57", "CL": "56",
    "PE": "51", "EC": "593", "BO": "591", "UY": "598", "PY": "595", "VE": "58"
}

# ==============================================================================
# 1. HERRAMIENTAS COMUNES
# ==============================================================================

def is_business_hours() -> bool:
    """Devuelve True solo Lunes a Viernes, 9-18hs."""
    now = datetime.now(TZ_ARGENTINA)
    if now.weekday() >= 5:
        return False
    if 9 <= now.hour < 18:
        return True
    return False

def clean_digits(phone_str):
    if not phone_str:
        return None
    return re.sub(r"\D", "", str(phone_str))

def sanitize_phone_number(phone_raw: str, ciudad: str) -> str:
    if not phone_raw:
        return None
    limpio = clean_digits(phone_raw)
    if not limpio:
        return None

    pais_code = None
    target_prefix = ""
    if ciudad:
        for codigo_iso, prefijo in PREFIX_MAP.items():
            if ciudad.strip().endswith(codigo_iso):
                pais_code = codigo_iso
                target_prefix = prefijo
                break
    
    if pais_code == "ES" and len(limpio) == 9 and (limpio.startswith("9") or limpio.startswith("6")):
        return f"34{limpio}"
    if pais_code == "AR" and len(limpio) == 10:
        return f"549{limpio}"
    if pais_code == "MX" and len(limpio) == 10:
        return f"52{limpio}"

    if len(limpio) < 10 and target_prefix and not limpio.startswith(target_prefix):
        return f"{target_prefix}{limpio}"

    return limpio

def extract_social_url(text: str, domain: str) -> str:
    if not text:
        return None
    pattern = r"(https?://(?:www\.)?" + re.escape(domain) + r"\.com/[\w\.-]+)"
    match = re.search(pattern, text)
    return match.group(1) if match else None

def get_coordinates(city_name: str):
    if city_name in KNOWN_LOCATIONS:
        loc = KNOWN_LOCATIONS[city_name]
        return {"nombre": city_name, "lat": loc["lat"], "lng": loc["lng"]}
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={quote_plus(city_name)}&key={GOOGLE_API_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("results"):
            loc = res["results"][0]["geometry"]["location"]
            return {"nombre": city_name, "lat": loc["lat"], "lng": loc["lng"]}
        else:
            print(f"⚠️ [Geocoding] No se encontraron coordenadas para: {city_name}")
    except Exception as e:
        print(f"🚨 Error Geocoding: {e}")
    return None

# ==============================================================================
# 2. SCRAPING Y BÚSQUEDA
# ==============================================================================

def scrape_contact_info(url: str) -> dict:
    contact_info = {"email": None, "whatsapp": None, "instagram": None}
    if not url:
        return contact_info
    if not url.startswith("http"):
        url = "https://" + url
    headers = {"User-Agent": "Mozilla/5.0 (Compatible; BeCubicalBot/1.0)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].lower()
                if "mailto:" in href and not contact_info["email"]:
                    contact_info["email"] = href.replace("mailto:", "").split("?")[0]
                if "instagram.com" in href:
                    contact_info["instagram"] = a["href"]
                if "wa.me" in href or "whatsapp" in href:
                    match = re.search(r"(?:phone=|wa\.me\/|whatsapp\.com\/send\/\?phone=)(\d+)", a["href"])
                    if match:
                        contact_info["whatsapp"] = match.group(1)

            if not contact_info["email"]:
                text = soup.get_text()
                match_email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
                if match_email:
                    contact_info["email"] = match_email.group(0)
    except:
        pass
    return contact_info

def find_and_store_prospects(db: Session, ciudad_info: dict, tipo_busqueda: str):
    print(f"🚀 [AutoHunter] Cazando '{tipo_busqueda}' en '{ciudad_info['nombre']}'...")
    existing = {r[0] for r in db.query(models.Prospecto.place_id).all()}
    url = f"{PLACES_API_URL}?location={ciudad_info['lat']},{ciudad_info['lng']}&radius=5000&keyword={quote_plus(tipo_busqueda)}&key={GOOGLE_API_KEY}&language=es"
    count_new = 0

    while url:
        try:
            res = requests.get(url, timeout=10)
            data = res.json()
            
            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                print(f"⚠️ [Google API] Error: {data.get('status')} - {data.get('error_message')}")
                break
            
            for place in data.get("results", []):
                pid = place.get("place_id")
                if not pid or pid in existing:
                    continue
                
                d_res = requests.get(
                    DETAILS_API_URL,
                    params={
                        "place_id": pid,
                        "fields": "name,website,formatted_phone_number,rating,user_ratings_total,reviews,photos,formatted_address",
                        "language": "es",
                        "key": GOOGLE_API_KEY,
                    },
                ).json().get("result", {})
                web = d_res.get("website")
                nombre = d_res.get("name", "N/A")
                phone_raw = d_res.get("formatted_phone_number")
                rating_val = d_res.get("rating") or place.get("rating")
                total_reseñas_val = d_res.get("user_ratings_total") or place.get("user_ratings_total")
                
                # Extracción de fotos y reseñas reales de Google Maps
                photos_raw = d_res.get("photos", [])
                photo_urls = []
                for p in photos_raw[:5]:
                    pref = p.get("photo_reference")
                    if pref:
                        photo_urls.append(f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={pref}&key={GOOGLE_API_KEY}")
                        
                reviews_raw = d_res.get("reviews", [])
                top_reviews = []
                for r in reviews_raw[:5]:
                    top_reviews.append({
                        "autor": r.get("author_name"),
                        "rating": r.get("rating"),
                        "texto": r.get("text"),
                        "tiempo": r.get("relative_time_description")
                    })
                
                import json
                reviews_json_str = json.dumps(top_reviews, ensure_ascii=False) if top_reviews else None
                photos_json_str = json.dumps(photo_urls, ensure_ascii=False) if photo_urls else None
                
                scraped = {}
                status = "NUEVO"

                if web:
                    print(f"🌐 [Scraping] Analizando web de {nombre}...")
                    scraped = scrape_contact_info(web)

                telefono_final = None
                if scraped.get("whatsapp"):
                    telefono_final = sanitize_phone_number(scraped["whatsapp"], ciudad_info["nombre"])
                if not telefono_final and phone_raw:
                    telefono_final = sanitize_phone_number(phone_raw, ciudad_info["nombre"])

                if telefono_final:
                    scraped["whatsapp"] = telefono_final

                if scraped.get("email") or scraped.get("instagram") or scraped.get("whatsapp"):
                    status = "ENRIQUECIDO"
                else:
                    status = "SIN_SITIO_WEB"
                    print(f"⚡ [IA] Marcado para Rescate/Enriquecimiento Nocturno: {nombre}")

                crud.create_prospecto(
                    db,
                    schemas.ProspectoB2BCreate(
                        place_id=pid,
                        nombre=nombre,
                        direccion=d_res.get("formatted_address") or place.get("vicinity"),
                        rating=rating_val,
                        total_reseñas=total_reseñas_val,
                        telefono=telefono_final,
                        sitio_web=web,
                        tipo_busqueda=tipo_busqueda,
                        ciudad_busqueda=ciudad_info["nombre"],
                        status=status,
                        email=scraped.get("email"),
                        instagram=scraped.get("instagram"),
                        whatsapp=telefono_final,
                        reviews_json=reviews_json_str,
                        photos_json=photos_json_str,
                    ),
                )
                existing.add(pid)
                count_new += 1
            
            db.commit()
            token = data.get("next_page_token")
            if token:
                time.sleep(2)
                url = f"{PLACES_API_URL}?pagetoken={token}&key={GOOGLE_API_KEY}"
            else:
                url = None
            
        except Exception as e:
            print(f"🚨 Error Crítico en Loop de Búsqueda: {e}")
            break
            
    print(f"✅ [AutoHunter] Fin. {count_new} prospectos nuevos guardados en BD.")

# ==============================================================================
# 4. WORKERS 
# ==============================================================================

def run_auto_hunter_worker():
    """Worker 24/7: Busca nuevos prospectos en Google Maps."""
    print("🕵️ WORKER [AutoHunter]: Iniciando...")
    db = SessionLocal()
    try:
        config = db.query(models.AgenteProspeccionConfig).first()
        if not config:
            print("⚠️ [AutoHunter] No hay configuración de prospección en la BD.")
            return
        
        if not config.is_active:
            print("⏸️ [AutoHunter] El agente está pausado.")
            return
        
        ciudades = config.target_cities or []
        rubros = config.target_keywords or []
        
        if not ciudades or not rubros:
            print("⚠️ [AutoHunter] Faltan ciudades o rubros en la configuración.")
            return
        
        ciudad = random.choice(ciudades)
        rubro = random.choice(rubros)
        
        coords = get_coordinates(ciudad)
        if coords:
            find_and_store_prospects(db, coords, rubro)
        else:
            print(f"❌ [AutoHunter] No se pudieron obtener coordenadas para {ciudad}")
            
    except Exception as e:
        print(f"🚨 Hunter Error: {e}")
    finally:
        db.close()

def run_sms_prospector_worker():
    """
    Worker WhatsApp Outbound: Envía la PLANTILLA OFICIAL.
    """
    print("📱 WORKER [WhatsApp Outbound]: Iniciando ronda de prospección...")
    
    if not is_business_hours():
        print("zzz Fuera de horario comercial.")
        return

    db = SessionLocal()
    try:
        config = db.query(models.AgenteProspeccionConfig).first()
        if not config or not config.is_active:
            print("⏸️ Prospector WhatsApp pausado.")
            return

        prospectos = (
            db.query(models.Prospecto)
            .filter(
                models.Prospecto.status.in_(["NUEVO", "ENRIQUECIDO"]),
                models.Prospecto.telefono.isnot(None),
                models.Prospecto.telefono != "",
            )
            .limit(config.mensajes_por_hora)
            .all()
        )

        if not prospectos:
            print("✅ No hay prospectos pendientes.")
            return

        for p in prospectos:
            print(f"👉 Intentando contactar a {p.nombre} ({p.telefono})...")
            
            # NOTA: Asegúrate de tener esta plantilla aprobada en Meta
            NOMBRE_PLANTILLA = "prospeccion_fria_v1"
            IDIOMA = "es_AR"

            try:
                res = asyncio.run(
                    send_template(
                        phone_number_id=settings.WHATSAPP_PHONE_ID,
                        to=p.telefono,
                        template_name=NOMBRE_PLANTILLA,
                        language_code=IDIOMA,
                        components=[
                            {
                                "type": "body",
                                "parameters": [
                                    {
                                        "type": "text",
                                        "parameter_name": "nombre",
                                        "text": p.nombre,
                                    },
                                    {
                                        "type": "text",
                                        "parameter_name": "ciudad",
                                        "text": p.ciudad_busqueda or "tu ciudad",
                                    },
                                ],
                            }
                        ],
                        access_token=settings.WHATSAPP_ACCESS_TOKEN,
                    )
                )

                exito_meta = False
                if res:
                    if "messages" in res:
                        exito_meta = True
                    elif res.get("data") and "messages" in res.get("data"):
                        exito_meta = True
                    elif "status" in res and res["status"] == "success":
                        exito_meta = True

                if exito_meta:
                    p.status = "CONTACTADO_WSP"
                    crud.log_action(db, "WHATSAPP_TEMPLATE", f"Plantilla enviada a {p.telefono}", p.place_id)
                    print(f"✅ Plantilla enviada a {p.nombre}")
                else:
                    print(f"❌ Falló envío a {p.nombre}. META DIJO: {res}")
                    p.status = "ERROR_CONTACTO"

            except Exception as e:
                print(f"❌ Error enviando template a {p.nombre}: {e}")
                p.status = "ERROR_CONTACTO"
            
            db.commit()
            time.sleep(15)

    except Exception as e:
        print(f"🚨 Error en Worker WhatsApp: {e}")
    finally:
        db.close()

def run_email_prospector_worker():
    """Worker Email: Versión ULTRA-CORTA para máxima conversión."""
    print("📧 WORKER [Email]: Iniciando...")
    if not is_business_hours():
        return
    db = SessionLocal()
    try:
        config = db.query(models.EmailProspectorConfig).first()
        if not config or not config.is_active:
            return

        prospectos = (
            db.query(models.Prospecto)
            .filter(
                models.Prospecto.status.in_(["NUEVO", "ENRIQUECIDO"]),
                models.Prospecto.email.isnot(None),
                models.Prospecto.email != "",
            )
            .limit(config.emails_por_hora)
            .all()
        )

        for p in prospectos:
            # --- ESTRATEGIA ULTRA-DIRECTA ---
            subject = f"{p.nombre}, 2 preguntas rápidas"

            body = f"""
<p>Hola {p.nombre},</p>
<p>Noté que manejan WhatsApp en {p.ciudad_busqueda or 'su ciudad'}. ¿Responden todo manualmente o ya tienen algún sistema?</p>
<p>Pregunto porque tengo algo que podría ayudarles. Si te interesa, respondé "SI" y te paso el link.</p>
<p>Saludos,<br>Guillermo</p>
"""
            # ----------------------------------------------------

            if send_google_workspace_email(p.email, subject, html_body=body):
                p.status = "CONTACTADO_EMAIL"
                crud.log_action(db, "EMAIL_ENVIADO", f"Enviado a {p.email}", p.place_id)
            else:
                p.status = "ERROR_CONTACTO"
            db.commit()
            time.sleep(2)
    finally:
        db.close()




def run_rescue_mission_worker():
    """
    Misión de Rescate: ULTRA-OPTIMIZADA con DeepSeek (10x más barato que Perplexity).
    DeepSeek cuesta $0.28/1M tokens vs Perplexity $3/1M = 90% de ahorro.
    """
    print("🚑 WORKER [Rescue]: Iniciando rescate nocturno con DeepSeek...")
    db = SessionLocal()
    try:
        # FILTROS ESTRICTOS: Solo prospectos de alta calidad
        candidatos = (
            db.query(models.Prospecto)
            .filter(
                models.Prospecto.status == "SIN_SITIO_WEB",
                models.Prospecto.rating >= 4.0,  # Solo 4+ estrellas
                models.Prospecto.total_reseñas >= 10  # Al menos 10 reseñas
            )
            .order_by(models.Prospecto.total_reseñas.desc())  # Priorizar más populares
            .limit(20)  # Límite conservador para no quemar créditos
            .all()
        )
        
        if not candidatos:
            print("✅ [Rescue] No hay candidatos para rescatar.")
            return
        
        print(f"🎯 [Rescue] Encontrados {len(candidatos)} candidatos de alta calidad.")
        
        for p in candidatos:
            try:
                # Query ultra-específico para DeepSeek
                q = f"Negocio: {p.nombre} - Ciudad: {p.ciudad_busqueda}. Dame SOLO Instagram y teléfono. Formato: IG: [url] - Tel: [numero]"
                
                # Usar asyncio.run() para ejecutar la función async
                ia_txt = asyncio.run(
                    generate_chat_response(
                        system_prompt="Sos un asistente de búsqueda de contactos. Respondé SOLO con datos concretos: Instagram y teléfono. Sin explicaciones adicionales.",
                        chat_history=[{"role": "user", "content": q}]
                    )
                )
                
                print(f"🤖 [DeepSeek] Respuesta para {p.nombre}: {ia_txt[:100]}...")
                
                # Extraer Instagram
                ig_url = extract_social_url(ia_txt, "instagram")
                
                # Extraer teléfono
                phone_match = re.search(r"\+?\d[\d\s-]{8,}\d", ia_txt)
                if phone_match:
                    clean_phone = sanitize_phone_number(
                        phone_match.group(0), p.ciudad_busqueda
                    )
                    if clean_phone:
                        p.telefono = clean_phone
                        p.whatsapp = clean_phone
                        print(f"    📞 Tel encontrado: {clean_phone}")

                if ig_url:
                    p.instagram = ig_url
                    p.status = "ENRIQUECIDO"
                    print(f"    ✅ ¡RESCATADO! {p.nombre} -> IG: {ig_url}")
                elif p.telefono:
                    p.status = "ENRIQUECIDO"
                    print(f"    ✅ ¡RESCATADO! {p.nombre} -> Tel: {p.telefono}")
                
                db.commit()
                time.sleep(3)  # Esperar 3s entre requests para no saturar
                
            except Exception as e:
                print(f"❌ [Rescue] Error procesando {p.nombre}: {e}")
                continue
        
        print(f"✅ [Rescue] Misión completada. Procesados {len(candidatos)} prospectos.")
        
    except Exception as e:
        print(f"🚨 ERROR CRÍTICO en Rescue Worker: {e}")
    finally:
        db.close()

def run_remarketing_worker():
    """Remarketing: Seguimiento a leads contactados hace > 3 días sin respuesta."""
    print("🔄 WORKER [Remarketing]: Buscando oportunidades de seguimiento...")
    if not is_business_hours():
        return

    db = SessionLocal()
    try:
        tres_dias_atras = datetime.now(TZ_ARGENTINA) - timedelta(days=3)

        candidatos = (
            db.query(models.Prospecto)
            .filter(
                models.Prospecto.status == "CONTACTADO_EMAIL",
                models.Prospecto.fecha_actualizado < tres_dias_atras,
            )
            .limit(20)
            .all()
        )

        for p in candidatos:
            if db.query(models.LogAccionAgente).filter(
                models.LogAccionAgente.prospecto_id == p.place_id,
                models.LogAccionAgente.tipo_accion == "REMARKETING_EMAIL",
            ).first():
                continue

            # --- NUEVO REMARKETING: Coherente con el primer mail ---
            subject = f"¿Pudiste ver el video, {p.nombre}?"
            body = f"""
<p>Hola {p.nombre},</p>
<p>Hace unos días te comenté sobre el video de 40 segundos del caso Giorda Neumáticos.</p>
<p>Si te interesa ver cómo funciona, avísame y te paso el link por acá o por WhatsApp.</p>
<p>Saludos,</p>
<p>Guillermo</p>
"""
            # --------------------------------------------------------

            if send_google_workspace_email(p.email, subject, html_body=body):
                crud.log_action(db, "REMARKETING_EMAIL", "Seguimiento enviado", p.place_id)
                p.fecha_actualizado = datetime.now(TZ_ARGENTINA)
                db.commit()
                print(f"    🔄 Remarketing enviado a {p.nombre}")
                time.sleep(2)
    except Exception as e:
        print(f"🚨 ERROR en Remarketing: {e}")
    finally:
        db.close()

# --- NUEVA SECCIÓN: PROSPECCIÓN MUSICAL (JULY CARDOZO) ---

def ejecutar_barrido_musical(db: Session, ciudad_objetivo: str = "Villa María, AR"):
    """
    Busca Venues, Bares y Estudios para la gira de July.
    INCLUYE: Extracción inmediata de Teléfono y Web + DEBUG DE ERROR.
    """
    print(f"🎸 --- INICIANDO BARRIDO MUSICAL EN: {ciudad_objetivo} ---")
    
    keywords_musicales = [
        "Bar con música en vivo", "Centro Cultural", "Discoteca",
        "Sala de conciertos", "Estudio de grabación", "Productora de eventos", "Radio FM"
    ]

    coords = KNOWN_LOCATIONS.get(ciudad_objetivo, KNOWN_LOCATIONS["Córdoba, AR"])
    location_str = f"{coords['lat']},{coords['lng']}"
    total_nuevos = 0

    for kw in keywords_musicales:
        print(f"   🔎 Buscando: '{kw}'...")
        
        # 1. Búsqueda General (Nearby Search)
        params = {
            "location": location_str, "radius": "5000", 
            "keyword": kw, "key": GOOGLE_API_KEY, "language": "es"
        }
        
        try:
            response = requests.get(PLACES_API_URL, params=params)
            
            # --- AQUÍ ESTABA EL ERROR: Definimos 'data' ---
            data = response.json() 
            
            # Debug: Si Google da error, lo imprimimos
            if "error_message" in data:
                print(f"      ⚠️ GOOGLE ERROR: {data['error_message']}")
            
            results = data.get("results", [])
            
            if not results:
                 print(f"      ⚠️ Sin resultados para '{kw}' (Status: {data.get('status')})")

            for place in results:
                place_id = place.get("place_id")
                
                # Check Duplicados
                if db.query(models.Prospecto).filter(models.Prospecto.place_id == place_id).first():
                    continue

                # 2. Búsqueda de Detalles (PARA OBTENER EL TELÉFONO)
                try:
                    detalles_resp = requests.get(
                        DETAILS_API_URL,
                        params={
                            "place_id": place_id,
                            "fields": "formatted_phone_number,website",
                            "key": GOOGLE_API_KEY
                        }
                    )
                    detalles = detalles_resp.json().get("result", {})
                except Exception as e:
                    print(f"      ⚠️ Error obteniendo detalles: {e}")
                    detalles = {}

                phone_raw = detalles.get("formatted_phone_number")
                website = detalles.get("website")
                
                telefono_final = sanitize_phone_number(phone_raw, ciudad_objetivo)

                status = "ENRIQUECIDO" if (telefono_final or website) else "SIN_SITIO_WEB"

                nuevo_prospecto = models.Prospecto(
                    place_id=place_id,
                    nombre=place.get("name"),
                    direccion=place.get("vicinity"),
                    ciudad_busqueda=ciudad_objetivo,
                    tipo_busqueda="INDUSTRIA_MUSICAL",
                    status=status,
                    telefono=telefono_final,
                    whatsapp=telefono_final, 
                    sitio_web=website,
                    rating=place.get("rating"),
                    fecha_agregado=datetime.now(TZ_ARGENTINA)
                )
                
                if place.get("rating", 0) > 3.0 or place.get("user_ratings_total", 0) == 0:
                    db.add(nuevo_prospecto)
                    total_nuevos += 1
                    print(f"      ✅ Capturado: {nuevo_prospecto.nombre}")
            
            db.commit()
            
        except Exception as e:
            # Imprimimos el error real si pasa algo
            print(f"❌ Error CRÍTICO buscando '{kw}': {e}")
            db.rollback()

    print(f"🚀 BARRIDO FINALIZADO. Se agregaron {total_nuevos} prospectos musicales con datos.")