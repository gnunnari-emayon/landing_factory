import os
import sys

# Asegurar importaciones del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from dataclasses import asdict

from backend.core.config import config
from backend.services.generator import (
    generar_landing_page, 
    inferir_categoria_por_rubro, 
    CLIENTES_DB
)

app = FastAPI(
    title="Nicho Landing Factory & CRM",
    description="Fábrica Inteligente de Landing Pages por Nicho y CRM Comercial",
    version="2.0.0"
)

# Montar archivos estáticos (CSS, JS, imágenes)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Configurar motor de plantillas Jinja2
templates_dir = os.path.join(frontend_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Página de inicio comercial"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_landings": len(CLIENTES_DB)
    })


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard CRM para usuario DEV con lista de clientes activos"""
    lista_clientes = list(CLIENTES_DB.values())
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "active_user": config.CRM_USER.upper(),
        "clientes": lista_clientes
    })


@app.get("/preview/{client_id}", response_class=HTMLResponse)
async def preview_landing(request: Request, client_id: str):
    """Vista previa responsiva e interactiva de la Landing Page generada para un cliente"""
    cliente = CLIENTES_DB.get(client_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Landing page de cliente no encontrada")
    
    return templates.TemplateResponse("preview_landing.html", {
        "request": request,
        "cliente": cliente
    })


@app.get("/api/clients")
async def get_clients_api():
    """Endpoint API para obtener la lista de clientes registrados en el CRM"""
    return [asdict(c) for c in CLIENTES_DB.values()]


@app.post("/api/generate")
async def generate_landing_api(payload: dict):
    """Endpoint API para generar landing page completa con fallback inteligente"""
    nombre = payload.get("nombre_negocio", "").strip()
    rubro = payload.get("rubro", "").strip()
    telefono = payload.get("telefono_whatsapp", "").strip()
    email = payload.get("email", "").strip()
    direccion = payload.get("direccion", "").strip()
    horario = payload.get("horario", "").strip()

    if not nombre or not rubro:
        raise HTTPException(status_code=400, detail="El nombre del negocio y el rubro son requeridos")

    res = generar_landing_page(
        nombre_negocio=nombre,
        rubro=rubro,
        telefono_whatsapp=telefono,
        email=email,
        direccion=direccion,
        horario=horario
    )
    
    return {
        "status": res.status,
        "cliente": asdict(res.cliente)
    }


if __name__ == "__main__":
    print("==================================================")
    print("  Nicho Landing Factory & CRM Engine v2.0 (FastAPI)")
    print("==================================================")
    print(f"[*] Usuario CRM Activo: {config.CRM_USER.upper()}")
    print(f"[*] Servidor Uvicorn iniciando en: http://127.0.0.1:{config.PORT}")
    print("==================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=config.PORT, reload=True)
