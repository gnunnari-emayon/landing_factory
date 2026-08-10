import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Asegurar importaciones del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.config import config
from backend.routers import views, prospects, prospecting_agent, demos, fallback

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

# Montar módulo Neumáticos & Lubricentros (AutoCentro ERP/POS/Taller)
try:
    from neumaticos_standalone.standalone_server import app as neumaticos_app
    app.mount("/autocentro", neumaticos_app)
    print("[Backend] Módulo neumaticos_standalone montado en /autocentro")
except Exception as e:
    print(f"[Backend Error] No se pudo montar neumaticos_standalone: {e}")

# Registrar Routers Modulares
app.include_router(views.router)
app.include_router(prospects.router)
app.include_router(prospecting_agent.router)
app.include_router(demos.router)
app.include_router(fallback.router)

if __name__ == "__main__":
    print("==================================================")
    print("  Nicho Landing Factory & CRM Engine (FastAPI)    ")
    print("==================================================")
    print(f"[*] Usuario CRM Activo: {config.CRM_USER.upper()}")
    print(f"[*] Servidor Uvicorn iniciando en: http://127.0.0.1:{config.PORT}")
    print("==================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=config.PORT, reload=True)
