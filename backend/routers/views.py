import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.core.config import config
from backend.core.database import get_db
from backend.models.prospect import ProspectoB2BModel
from backend.services.prospect_repository import listar_prospectos
from backend.data.latam_database import RUBROS_LATAM, UBICACIONES_LATAM

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_dir = os.path.join(BASE_DIR, "frontend")
templates_dir = os.path.join(frontend_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
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


@router.get("/prospector", response_class=HTMLResponse)
def prospector_page(request: Request, db: Session = Depends(get_db)):
    """Pestaña 1: Prospector Google Maps"""
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


@router.get("/focus-group", response_class=HTMLResponse)
async def focus_group_page(request: Request):
    """Pestaña 2: Focus Group AI"""
    return templates.TemplateResponse(request, "agencia/focus_group.html", {
        "active_tab": "focusgroup"
    })


@router.get("/campanias", response_class=HTMLResponse)
async def campanias_page(request: Request):
    """Pestaña 3: Gestión de Campañas & Clientes B2B"""
    return templates.TemplateResponse(request, "agencia/campañas.html", {
        "active_tab": "campaigns"
    })


@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard CRM para usuario DEV"""
    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "active_user": config.CRM_USER.upper()
    })


@router.get("/static/demos/{file_name}", response_class=HTMLResponse)
async def ver_demo_html(file_name: str):
    """Servir demo HTML de prospectos con protección contra Path Traversal"""
    demos_dir = os.path.abspath(os.path.join(frontend_dir, "demos"))
    safe_filename = os.path.basename(file_name)
    filepath = os.path.abspath(os.path.join(demos_dir, safe_filename))

    if filepath.startswith(demos_dir) and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return HTMLResponse(
                content=f.read(),
                headers={"Cache-Control": "no-cache, no-store, must-revalidate, max-age=0", "Pragma": "no-cache"}
            )
    return HTMLResponse(content="<h1>Demo no encontrada</h1>", status_code=404)
