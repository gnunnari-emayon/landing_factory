import time
import traceback
from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.generator import generar_landing_page
from backend.services.prospect_repository import buscar_prospecto_por_place_id
from backend.services.google_places_enricher import enriquecer_prospecto_con_google_places
from backend.services.landing_theme_engine import obtener_theme_config, obtener_contexto_web_empresa
from backend.services.demo_builder import construir_demo_html

router = APIRouter()


@router.post("/api/generate")
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


@router.post("/api/v1/agencia/prospectos_b2b/generar-demo/{place_id}")
async def generar_demo_prospecto(place_id: str, payload: dict = Body(default={}), db: Session = Depends(get_db)):
    try:
        payload = payload or {}
        precio = payload.get("precio_usd", 350)
        dominio = payload.get("dominio_elegido", "miempresa.com")
        
        prospecto_model = buscar_prospecto_por_place_id(db, place_id)
        if prospecto_model:
            prospecto_model = enriquecer_prospecto_con_google_places(db, prospecto_model)
        prospecto = prospecto_model.to_dict() if prospecto_model else None

        nombre = prospecto["nombre"] if prospecto else f"Empresa {place_id}"
        rubro = prospecto["tipo_busqueda"] if prospecto else "Servicios"
        telefono_wa = prospecto.get("whatsapp") or prospecto.get("telefono") if prospecto else None
        
        resultado_landing = generar_landing_page(nombre_negocio=nombre, rubro=rubro)
        cat_visual = resultado_landing.categoria_visual
        
        ciudad_prospecto = prospecto.get("ciudad_busqueda") if prospecto else "Rosario, AR"
        theme = obtener_theme_config(cat_visual, prospecto_seed=place_id)
        ctx_web = obtener_contexto_web_empresa(nombre, ciudad_prospecto)

        filepath, link_wa = construir_demo_html(
            place_id=place_id,
            nombre=nombre,
            rubro=rubro,
            cat_visual=cat_visual,
            theme=theme,
            ctx_web=ctx_web,
            prospecto=prospecto,
            precio=precio,
            dominio=dominio,
            telefono_wa=telefono_wa
        )

        ts = int(time.time())
        return {
            "nombre": nombre,
            "precio_usd": precio,
            "dominio_elegido": dominio,
            "url_demo": f"/static/demos/{place_id}.html?v={ts}",
            "link_wa": link_wa or None
        }
    except Exception as e:
        traceback.print_exc()
        print(f"[ERROR GENERAR DEMO]: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.post("/api/v1/agencia/checkout/crear-link-custom")
async def crear_checkout_custom(payload: dict):
    precio = payload.get("precio_usd", 350)
    return {
        "checkout_url": f"https://checkout.dlocalgo.com/v1/pay/demo-{precio}-usd"
    }
