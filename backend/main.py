import os
import sys

# Asegurar importaciones del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from backend.core.config import config
from backend.services.generator import generar_landing_page, inferir_categoria_por_rubro

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
async def home_page(request: Request):
    """Página de inicio comercial"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard CRM para usuario DEV"""
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "active_user": config.CRM_USER.upper()
    })


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


if __name__ == "__main__":
    print("==================================================")
    print("  Nicho Landing Factory & CRM Engine (FastAPI)    ")
    print("==================================================")
    print(f"[*] Usuario CRM Activo: {config.CRM_USER.upper()}")
    print(f"[*] Servidor Uvicorn iniciando en: http://127.0.0.1:{config.PORT}")
    print("==================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=config.PORT, reload=True)
