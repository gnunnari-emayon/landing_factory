import urllib.parse
import urllib.request
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from backend.core.config import config
from backend.core.database import get_db
from backend.models.prospect import ProspectoB2BModel
from backend.services.prospect_repository import buscar_prospecto_por_place_id
from backend.services.google_places_enricher import enriquecer_prospecto_con_google_places
from backend.services.phone_enricher import enriquecer_telefono_google_maps
from backend.data.latam_database import autocompletar_rubro, autocompletar_ubicacion

router = APIRouter()


@router.get("/api/v1/agencia/rubros/sugerir")
async def sugerir_rubros(q: str = ""):
    return {"status": "ok", "items": autocompletar_rubro(q)}


@router.get("/api/v1/agencia/ubicaciones/sugerir")
async def sugerir_ubicaciones(q: str = ""):
    return {"status": "ok", "items": autocompletar_ubicacion(q)}


@router.get("/api/v1/agencia/prospectos_b2b/")
def listar_prospectos_b2b(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
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


@router.get("/api/v1/agencia/prospectos_b2b/detalle/{place_id}")
def obtener_detalle_prospecto_b2b(place_id: str, db: Session = Depends(get_db)):
    prospecto = buscar_prospecto_por_place_id(db, place_id)
    if not prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    prospecto = enriquecer_prospecto_con_google_places(db, prospecto)
    return prospecto.to_dict()


@router.api_route("/api/v1/agencia/foto_proxy", methods=["GET", "HEAD"])
async def proxy_google_photo(ref: str):
    """
    Proxy seguro para servir imágenes de Google Places API sin bloqueos de Referer en el navegador.
    """
    api_key = config.GOOGLE_PLACES_API_KEY
    if not api_key:
        raise HTTPException(status_code=400, detail="Google Places API key no configurada")

    clean_ref = urllib.parse.quote(ref.strip())
    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={clean_ref}&key={api_key}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://crm.emayonforge.com/"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            img_data = resp.read()
            return Response(content=img_data, media_type=content_type)
    except Exception as e:
        print(f"⚠️ Error en proxy_google_photo: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/v1/agencia/prospectos_b2b/sincronizar-contactos")
async def sincronizar_contactos_b2b(db: Session = Depends(get_db)):
    """
    Recorre en lote la base de datos de prospectos que figuran 'Sin teléfono' y aplica 
    el motor de enriquecimiento secundario de Google Business para completar sus contactos reales.
    """
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


@router.post("/api/v1/agencia/prospectos_b2b/limpiar-sin-telefono")
@router.delete("/api/v1/agencia/prospectos_b2b/limpiar-sin-telefono")
async def limpiar_prospectos_sin_telefono(db: Session = Depends(get_db)):
    """Elimina de la base de datos todos los prospectos que no posean número telefónico disponible."""
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


@router.get("/api/v1/agencia/dominio/verificar")
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
