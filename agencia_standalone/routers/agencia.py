# app/routers/agencia.py

from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

class DummySchemas:
    def __getattr__(self, name):
        return Any

class DummyModels:
    def __getattr__(self, name):
        return Any

def get_db():
    db = None
    try:
        from app.database import SessionLocal
        db = SessionLocal()
    except Exception:
        pass
    try:
        yield db
    finally:
        if db is not None:
            db.close()

def require_role(roles: list):
    def role_checker():
        return True
    return role_checker

class DummyDependencies:
    get_db = staticmethod(get_db)
    require_role = staticmethod(require_role)

try:
    from app import crud, models, schemas, dependencies
except Exception:
    schemas = DummySchemas()
    models = DummyModels()
    try:
        from app import crud, dependencies
    except Exception:
        crud = None
        dependencies = DummyDependencies()

try:
    from agencia_standalone.services import prospecting_service, gemini_service
except ImportError:
    from ..services import prospecting_service, gemini_service

# --- Schemas específicos ---
class ProspectingOrder(BaseModel):
    ciudad_nombre: Optional[str] = None
    ciudad_lat: Optional[float] = None
    ciudad_lng: Optional[float] = None
    tipo_busqueda: Optional[str] = None
    query: Optional[str] = None
    ciudad: Optional[str] = None

class ProspectStatusUpdate(BaseModel):
    status: str


class ProspectosB2BResponse(BaseModel):
    """
    Schema de respuesta para la lista de prospectos con paginación.
    """
    items: List[Dict[str, Any]]
    total: int    

class ProspectosStatsResponse(BaseModel):
    total_enriquecido: int
    total_sin_sitio_web: int
    total_telefono: int
    total_linkedin: int
    total_instagram: int
    total_instagram_email: int    

class FocusGroupMessage(BaseModel):
    role: str
    parts: List[Dict[str, str]]

class FocusGroupSendRequest(BaseModel):
    historial_chat: List[FocusGroupMessage]
    message: str

class FocusGroupSendResponse(BaseModel):
    reply: str
    historial_completo: List[FocusGroupMessage]

# ===================================================================
#  ROUTER PRINCIPAL PARA LA AGENCIA CMS
# ===================================================================
# ▼▼▼ CAMBIO CLAVE: Quitamos la dependencia global para permitir rutas públicas ▼▼▼
router = APIRouter(
    prefix="/api/v1/agencia",  # <-- ¡CAMBIO IMPORTANTE!
    tags=["Agencia CMS"]
)

# ===================================================================
#  ENDPOINTS PARA CLIENTES DE LA AGENCIA
# ===================================================================

@router.get("/clientes/", response_model=List[schemas.Usuario])
def read_clientes_de_agencia(
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    return crud.get_clientes_por_agencia(db, agencia_id=current_user.id)

@router.post("/clientes/", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def create_cliente_por_agencia(
    cliente: schemas.UsuarioCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_usuario = crud.get_usuario_by_email(db, email=cliente.email)
    if db_usuario:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    user_role = crud.get_role_by_name(db, name="user")
    if not user_role:
        raise HTTPException(status_code=500, detail="Rol 'user' no encontrado.")
    usuario_a_crear = schemas.UsuarioCreateByAdmin(**cliente.model_dump(), role_ids=[user_role.id])
    return crud.create_usuario(db=db, usuario=usuario_a_crear, agency_id=current_user.id)

# ===================================================================
#  ENDPOINTS PARA CAMPAÑAS
# ===================================================================

@router.post("/campanas/", response_model=schemas.Campana, status_code=status.HTTP_201_CREATED)
def create_campana(
    campana: schemas.CampanaCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_cliente = crud.get_usuario(db, usuario_id=campana.cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="El cliente especificado no existe.")
    return crud.create_campana(db=db, campana=campana, agencia_id=current_user.id)

@router.get("/campanas/", response_model=List[schemas.Campana])
def read_campanas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    return crud.get_campanas_por_agencia(db, agencia_id=current_user.id, skip=skip, limit=limit)

@router.get("/campanas/{campana_id}", response_model=schemas.Campana)
def read_campana(
    campana_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_campana = crud.get_campana(db, campana_id=campana_id)
    if not db_campana or (db_campana.agencia_id != current_user.id and not current_user.has_role("admin")):
        raise HTTPException(status_code=404, detail="Campaña no encontrada o sin permisos")
    return db_campana

@router.put("/campanas/{campana_id}", response_model=schemas.Campana)
def update_campana(
    campana_id: int,
    campana_update: schemas.CampanaUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_campana = read_campana(campana_id, db, current_user)
    return crud.update_campana(db, db_campana=db_campana, campana_update=campana_update)
    
@router.delete("/campanas/{campana_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campana(
    campana_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    read_campana(campana_id, db, current_user)
    crud.delete_campana(db=db, campana_id=campana_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ===================================================================
#  ENDPOINTS PARA TAREAS
# ===================================================================

@router.get("/tareas/", response_model=List[schemas.Tarea])
def read_tareas_de_la_agencia(
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    return crud.get_tareas_por_agencia(db, agencia_id=current_user.id)

@router.post("/campanas/{campana_id}/tareas/", response_model=schemas.Tarea, status_code=status.HTTP_201_CREATED)
def create_tarea_para_campana(
    campana_id: int,
    tarea: schemas.TareaCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_campana = read_campana(campana_id, db, current_user)
    return crud.create_tarea(db=db, tarea=tarea, campana_id=db_campana.id)

@router.put("/tareas/{tarea_id}", response_model=schemas.Tarea)
def update_tarea(
    tarea_id: int,
    tarea_update: schemas.TareaUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_tarea = crud.get_tarea(db, tarea_id=tarea_id)
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    read_campana(db_tarea.campana_id, db, current_user)
    return crud.update_tarea(db=db, db_tarea=db_tarea, tarea_update=tarea_update)

@router.delete("/tareas/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tarea(
    tarea_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_tarea = crud.get_tarea(db, tarea_id=tarea_id)
    if db_tarea:
        read_campana(db_tarea.campana_id, db, current_user)
        crud.delete_tarea(db=db, tarea_id=tarea_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ===================================================================
#  ENDPOINTS PARA CONTENIDOS
# ===================================================================

@router.get("/contenidos/", response_model=List[schemas.Contenido])
def read_contenidos_de_la_agencia(
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    return crud.get_contenidos_por_agencia(db, agencia_id=current_user.id)
    
@router.post("/campanas/{campana_id}/contenidos/", response_model=schemas.Contenido, status_code=status.HTTP_201_CREATED)
def create_contenido_para_campana(
    campana_id: int,
    contenido: schemas.ContenidoCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_campana = read_campana(campana_id, db, current_user)
    return crud.create_contenido(db=db, contenido=contenido, campana_id=db_campana.id)

@router.put("/contenidos/{contenido_id}", response_model=schemas.Contenido)
def update_contenido(
    contenido_id: int,
    contenido_update: schemas.ContenidoUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_contenido = crud.get_contenido(db, contenido_id=contenido_id)
    if not db_contenido:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    read_campana(db_contenido.campana_id, db, current_user)
    return crud.update_contenido(db=db, db_contenido=db_contenido, contenido_update=contenido_update)

@router.delete("/contenidos/{contenido_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contenido(
    contenido_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    db_contenido = crud.get_contenido(db, contenido_id=contenido_id)
    if db_contenido:
        read_campana(db_contenido.campana_id, db, current_user)
        crud.delete_contenido(db=db, contenido_id=contenido_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ===================================================================
#  ENDPOINTS PARA PROYECTOS B2B
# ===================================================================

@router.get("/b2b/", response_model=List[schemas.ProyectoB2B])
def read_proyectos_b2b(
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """ Obtiene todos los proyectos B2B de la agencia actual. """
    return crud.get_proyectos_b2b_por_agencia(db, agencia_id=current_user.id)

@router.post("/b2b/", response_model=schemas.ProyectoB2B, status_code=status.HTTP_201_CREATED)
def create_proyecto_b2b_endpoint(
    proyecto: schemas.ProyectoB2BCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """ Crea un nuevo proyecto B2B para un cliente. """
    db_cliente = crud.get_usuario(db, usuario_id=proyecto.cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="El cliente especificado no existe.")
    return crud.create_proyecto_b2b(db=db, proyecto=proyecto, agencia_id=current_user.id)

@router.put("/b2b/{proyecto_id}", response_model=schemas.ProyectoB2B)
def update_proyecto_b2b_endpoint(
    proyecto_id: int,
    proyecto_update: schemas.ProyectoB2BUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """ Actualiza un proyecto B2B. """
    db_proyecto = crud.get_proyecto_b2b(db, proyecto_id=proyecto_id)
    if not db_proyecto or db_proyecto.agencia_id != current_user.id:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o sin permisos.")
    return crud.update_proyecto_b2b(db, db_proyecto=db_proyecto, proyecto_update=proyecto_update)

@router.delete("/b2b/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proyecto_b2b_endpoint(
    proyecto_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """ Elimina un proyecto B2B. """
    db_proyecto = crud.get_proyecto_b2b(db, proyecto_id=proyecto_id)
    if db_proyecto and db_proyecto.agencia_id == current_user.id:
        crud.delete_proyecto_b2b(db, proyecto_id=proyecto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ===================================================================
#  ENDPOINTS PARA PROSPECCIÓN B2B AUTOMATIZADA
# ===================================================================

@router.post("/b2b/prospectar", status_code=status.HTTP_202_ACCEPTED)
def start_b2b_prospecting(
    order: ProspectingOrder,
    background_tasks: BackgroundTasks,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """
    Inicia un proceso de búsqueda de prospectos B2B en segundo plano con logs visibles en terminal.
    """
    nombre_ciudad = order.ciudad_nombre or order.ciudad or "Córdoba, AR"
    rubro_busqueda = order.tipo_busqueda or order.query or "empresa"
    
    known = prospecting_service.KNOWN_LOCATIONS.get(nombre_ciudad, {})
    lat = order.ciudad_lat or known.get("lat", -31.4201)
    lng = order.ciudad_lng or known.get("lng", -64.1888)
    
    ciudad_info = {
        "nombre": nombre_ciudad,
        "lat": lat,
        "lng": lng
    }
    
    print(f"\n🚀 [PROSPECTOR START] Petición recibida: '{rubro_busqueda}' en '{nombre_ciudad}' (lat: {lat}, lng: {lng})")
    
    background_tasks.add_task(
        prospecting_service.find_and_store_prospects,
        db,
        ciudad_info,
        rubro_busqueda
    )
    
    return {"message": f"Proceso de prospección iniciado para '{rubro_busqueda}' en {nombre_ciudad}."}

class GenerarDemoRequest(BaseModel):
    custom_prompt: Optional[str] = None
    precio_usd: float = 350.0
    dominio_elegido: Optional[str] = None

class CustomCheckoutRequest(BaseModel):
    place_id: str
    nombre_cliente: Optional[str] = "Cliente Web"
    email_cliente: Optional[str] = "sin_email@empresa.com"
    precio_usd: float = 350.0
    dominio_elegido: Optional[str] = None

@router.get("/dominio/verificar")
async def api_verificar_dominio(nombre: str = Query(...)):
    """ Verifica la disponibilidad de dominios .com, .com.ar, etc. """
    from agencia_standalone.services.domain_service import verificar_disponibilidad_dominio
    res = await verificar_disponibilidad_dominio(nombre)
    return res

@router.post("/checkout/crear-link-custom")
async def api_crear_checkout_custom(datos: CustomCheckoutRequest, db: Session = Depends(dependencies.get_db)):
    """ Crea enlace de cobro dLocal GO a nombre de CATSOF S.A.S. con monto y dominio dinámico """
    import httpx
    import uuid
    import os
    
    try:
        from app.models.prospecto import Prospecto
    except Exception:
        Prospecto = getattr(models, "Prospecto", None)
        
    prospecto = db.query(Prospecto).filter(Prospecto.place_id == datos.place_id).first() if Prospecto and db else None
    nombre_negocio = prospecto.nombre if prospecto else "Sitio Web Oficial"
    
    api_key = os.getenv("DLOCAL_API_KEY", "ZpfkstsjSNtoMbhiSPBzBhdlqtDFeXMN").strip()
    secret_key = os.getenv("DLOCAL_SECRET_KEY", "kKpXnISSreI86I0By9dQJq5OttWlIEfDhmbLeD2g").strip()
    url_exito = os.getenv("URL_EXITO", "https://emayonforge.com/gracias")
    
    dominio = datos.dominio_elegido or f"{nombre_negocio.lower().replace(' ', '')}.com"
    
    desc_corta = f"Web & Dominio {dominio} - {nombre_negocio}"[:80]
    
    payload = {
        "amount": float(datos.precio_usd),
        "currency": "USD",
        "country": "AR",
        "description": desc_corta,
        "success_url": url_exito,
        "back_url": "https://emayonforge.com/error-pago",
        "payer": {
            "name": datos.nombre_cliente,
            "email": datos.email_cliente
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}:{secret_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.dlocalgo.com/v1/payments",
                json=payload,
                headers=headers,
                timeout=15.0
            )
            if response.status_code in [200, 201]:
                data = response.json()
                return {"status": "success", "checkout_url": data.get("redirect_url"), "precio_usd": datos.precio_usd, "dominio": dominio}
            else:
                print(f"[dLocal Error] Status: {response.status_code}, Body: {response.text}")
                return {"status": "error", "checkout_url": f"https://emayonforge.com/error-pago?motivo={response.status_code}", "detail": response.text}
        except Exception as e:
            return {"status": "error", "mensaje": str(e)}

@router.post("/prospectos_b2b/generar-demo/{place_id}")
async def api_generar_demo_agencia(
    place_id: str, 
    body: Optional[GenerarDemoRequest] = None,
    db: Session = Depends(dependencies.get_db)
):
    """ Genera la landing demo y devuelve la URL y mensaje de WhatsApp """
    import urllib.parse
    
    try:
        from app.models.prospecto import Prospecto
    except Exception:
        Prospecto = getattr(models, "Prospecto", None)
        
    if not db or not Prospecto:
        raise HTTPException(status_code=500, detail="Base de datos no disponible")
        
    prospecto = db.query(Prospecto).filter(Prospecto.place_id == place_id).first()
    if not prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    custom_prompt = body.custom_prompt if body else None
    precio_usd = body.precio_usd if (body and body.precio_usd) else 350.0
    dominio_elegido = body.dominio_elegido if (body and body.dominio_elegido) else None
    
    from agencia_standalone.services.generator import mock_generar_landing
    url_demo = await mock_generar_landing(
        prospecto, 
        custom_prompt=custom_prompt, 
        precio_usd=precio_usd, 
        dominio_elegido=dominio_elegido
    )
    
    telefono = getattr(prospecto, "whatsapp", None) or getattr(prospecto, "telefono", None) or ""
    telefono_limpio = "".join(filter(str.isdigit, str(telefono)))
    
    dominio_texto = f" ({dominio_elegido})" if dominio_elegido else ""
    mensaje_wa = f"¡Hola! Vi tu negocio {prospecto.nombre} en Google y armé esta propuesta de sitio web oficial{dominio_texto} para vos: https://crm.emayonforge.com{url_demo} (Si te gusta, activamos tu plataforma y dominio hoy por ${precio_usd:.2f} USD)."
    mensaje_codificado = urllib.parse.quote(mensaje_wa)
    link_wa = f"https://wa.me/{telefono_limpio}?text={mensaje_codificado}" if telefono_limpio else ""
    
    return {
        "status": "success",
        "url_demo": url_demo,
        "link_wa": link_wa,
        "nombre": prospecto.nombre,
        "telefono": telefono,
        "precio_usd": precio_usd,
        "dominio_elegido": dominio_elegido
    }

@router.get("/prospectos_b2b/")
def read_b2b_prospects(
    skip: int = 0,
    limit: int = 100,
    ciudad: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search_query: Optional[str] = Query(None),
    db: Session = Depends(dependencies.get_db),
    current_user: Any = Depends(dependencies.require_role(["agency", "admin"]))
):
    """
    Obtiene la lista de prospectos B2B capturados en la DB con filtros y paginación.
    """
    if crud and hasattr(crud, "get_prospectos_count") and hasattr(crud, "get_prospectos"):
        try:
            filter_params = {
                "ciudad": ciudad,
                "status": status,
                "search_query": search_query
            }
            total = crud.get_prospectos_count(db, **filter_params)
            prospectos = crud.get_prospectos(db, skip=skip, limit=limit, **filter_params)
            return {"items": prospectos, "total": total}
        except Exception as e:
            print(f"⚠️ CRUD get_prospectos falló: {e}, recurriendo a consulta directa")

    # Consulta directa de respaldo usando SQLAlchemy
    try:
        from app.models.prospecto import Prospecto
    except Exception:
        Prospecto = getattr(models, "Prospecto", None)

    if not db or not Prospecto:
        return {"items": [], "total": 0}

    query = db.query(Prospecto)
    if ciudad:
        query = query.filter(Prospecto.ciudad_busqueda.ilike(f"%{ciudad}%"))
    if status:
        query = query.filter(Prospecto.status == status)
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            (Prospecto.nombre.ilike(search)) |
            (Prospecto.ciudad_busqueda.ilike(search)) |
            (Prospecto.telefono.ilike(search)) |
            (Prospecto.email.ilike(search))
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    items_dict = []
    for item in items:
        items_dict.append({
            "place_id": getattr(item, "place_id", ""),
            "nombre": getattr(item, "nombre", ""),
            "direccion": getattr(item, "direccion", ""),
            "telefono": getattr(item, "telefono", ""),
            "whatsapp": getattr(item, "whatsapp", None) or getattr(item, "telefono", None),
            "sitio_web": getattr(item, "sitio_web", ""),
            "email": getattr(item, "email", ""),
            "instagram": getattr(item, "instagram", ""),
            "tipo_busqueda": getattr(item, "tipo_busqueda", ""),
            "ciudad_busqueda": getattr(item, "ciudad_busqueda", ""),
            "status": getattr(item, "status", "NUEVO"),
            "rating": getattr(item, "rating", 0.0),
            "total_reseñas": getattr(item, "total_reseñas", 0),
            "reviews_json": getattr(item, "reviews_json", None),
            "photos_json": getattr(item, "photos_json", None),
            "fecha_agregado": str(getattr(item, "fecha_agregado", getattr(item, "created_at", "2026-07-28"))),
            "fecha_creacion": str(getattr(item, "fecha_agregado", getattr(item, "created_at", "2026-07-28")))
        })

    return {"items": items_dict, "total": total}
# === FIN DE MODIFICACIÓN ===

@router.put("/prospectos_b2b/{place_id}/status")
def update_b2b_prospect_status(
    place_id: str,
    status_update: ProspectStatusUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """
    Actualiza el estado de un prospecto B2B (ej: Nuevo, Cualificado, Contactado).
    """
    updated_prospect = crud.update_prospecto_b2b_status(
        db, place_id=place_id, status=status_update.status
    )
    if not updated_prospect:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    return updated_prospect

@router.get("/prospectos_b2b/stats/", response_model=ProspectosStatsResponse)
def get_b2b_prospects_stats(
    # --- Copia EXACTAMENTE los mismos parámetros de filtro que read_b2b_prospects ---
    ciudad: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    has_website: Optional[bool] = Query(None),
    has_whatsapp: Optional[bool] = Query(None),
    has_instagram: Optional[bool] = Query(None),
    search_query: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    has_email: Optional[bool] = Query(None),
    # --- Fin de parámetros de filtro ---
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """
    Calcula y devuelve las estadísticas globales de los prospectos B2B
    basadas en los filtros aplicados.
    """
    filter_params = {
        "ciudad": ciudad,
        "status": status,
        "has_website": has_website,
        "has_whatsapp": has_whatsapp,
        "has_instagram": has_instagram,
        "search_query": search_query,
        "email": email,
        "has_email": has_email
    }
    # Llamamos a una nueva función en el CRUD
    stats = crud.calculate_prospectos_stats(db, **filter_params)
    return ProspectosStatsResponse(**stats)    




# --- ENDPOINT AÑADIDO ---
@router.post("/prospectos_b2b/upload-csv/", status_code=status.HTTP_200_OK)
def upload_prospects_csv(
    file: UploadFile = File(...),
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """
    Sube un archivo CSV con datos de prospectos y los actualiza/inserta en la base de datos.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV.")

    try:
        content = file.file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        processed_count = 0
        for row in csv_reader:
            # Convierte las cadenas vacías a None para que la DB las ignore
            clean_row = {k: v if v else None for k, v in row.items()}
            crud.upsert_prospecto_from_csv(db, prospecto_data=clean_row)
            processed_count += 1
            
        return {"message": f"Proceso completado. Se procesaron {processed_count} filas del CSV."}
    
    except Exception as e:
        # Usamos repr(e) para obtener un error más detallado en la respuesta
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al procesar el archivo: {repr(e)}")
# --------------------

# ===================================================================
#  ENDPOINTS PARA FOCUS GROUP INTERACTIVO (REFACTORIZADOS)
# ===================================================================

# ▼▼▼ ESTE ENDPOINT AHORA ES PÚBLICO (no tiene `current_user`) ▼▼▼
@router.post("/campanas/{campana_id}/focusgroup/send", response_model=FocusGroupSendResponse)
def handle_focus_group_chat(
    campana_id: int,
    request_data: FocusGroupSendRequest,
    db: Session = Depends(dependencies.get_db)
):
    db_campana = crud.get_campana(db, campana_id=campana_id)
    if not db_campana or not db_campana.prompt_chatbot:
        raise HTTPException(status_code=404, detail="Campaña de Focus Group no encontrada o no configurada.")

    historial = [msg.model_dump() for msg in request_data.historial_chat]
    historial.append({"role": "user", "parts": [{"text": request_data.message}]})

    try:
        ai_reply = gemini_service.generate_chat_response(
            system_prompt=db_campana.prompt_chatbot,
            chat_history=historial
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contactar la IA: {str(e)}")

    historial.append({"role": "model", "parts": [{"text": ai_reply}]})

    return FocusGroupSendResponse(
        reply=ai_reply,
        historial_completo=[FocusGroupMessage(**msg) for msg in historial]
    )

# ▼▼▼ ESTE ENDPOINT AHORA ES PÚBLICO (no tiene `current_user`) ▼▼▼
@router.post("/campanas/{campana_id}/resultados/", response_model=schemas.FocusGroupResultado)
def create_focus_group_result(
    campana_id: int,
    resultado: schemas.FocusGroupResultadoCreate,
    db: Session = Depends(dependencies.get_db)
):
    """Crea/Guarda el hilo de conversación completo de un Focus Group."""
    db_campana = crud.get_campana(db, campana_id=campana_id)
    if not db_campana:
        raise HTTPException(status_code=404, detail="Campaña no encontrada")
    return crud.create_focus_group_resultado(db=db, resultado=resultado, campana_id=campana_id)

# ▼▼▼ ESTE ENDPOINT SÍ ES PROTEGIDO (tiene `current_user`) ▼▼▼
@router.get("/campanas/{campana_id}/resultados/", response_model=List[schemas.FocusGroupResultado])
def read_focus_group_results(
    campana_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.Usuario = Depends(dependencies.require_role(["agency", "admin"]))
):
    """Obtiene todos los resultados para una campaña de Focus Group."""
    db_campana = crud.get_campana(db, campana_id=campana_id)
    if not db_campana or db_campana.agencia_id != current_user.id:
         raise HTTPException(status_code=403, detail="No tienes permiso para ver los resultados de esta campaña.")
    
    resultados = crud.get_resultados_focus_group(db, campana_id=campana_id)
    return resultados or []
