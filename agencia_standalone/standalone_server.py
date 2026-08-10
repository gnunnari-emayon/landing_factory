# agencia_standalone/standalone_server.py
"""
Servidor independiente para la Agencia CMS en localhost.
Permite ejecutar y auditar el frontend (agenciacms.html y agencia_services.html)
y los endpoints (agencia.py) de forma desacoplada y controlada.

Para ejecutar:
    uvicorn agencia_standalone.standalone_server:app --reload --port 8005
"""

import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Intentar cargar la configuración y la base de datos existente si está disponible
try:
    from app.core.config import settings
    from app import models, dependencies
except ImportError:
    settings = type("Settings", (), {"GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", "")})()
    dependencies = None
    models = None

from agencia_standalone.routers import agencia

app = FastAPI(
    title="Agencia CMS - Standalone Localhost",
    description="Entorno de desarrollo local e independiente para Agencia CMS",
    version="1.0.0"
)

# Montar carpeta de demos generadas
media_demos_dir = os.path.join(os.path.dirname(__file__), "media", "demos_generadas")
os.makedirs(media_demos_dir, exist_ok=True)
app.mount("/demos", StaticFiles(directory=media_demos_dir), name="demos")

# Configuración CORS para pruebas locales
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Overrides de Autenticación para Entorno Standalone ---
class MockRole:
    def __init__(self, name):
        self.id = 1 if name == "agency" else 2
        self.name = name

class MockUser:
    def __init__(self):
        self.id = 1
        self.email = "agencia_dev@localhost"
        self.nombre = "Agencia Localhost"
        self.agency_id = 1
        self.is_active = True
        self.roles = [MockRole("agency"), MockRole("admin")]
    
    def has_role(self, role_name: str) -> bool:
        return any(r.name == role_name for r in self.roles)

def mock_get_current_user():
    return MockUser()

if dependencies:
    if hasattr(dependencies, "get_current_user"):
        app.dependency_overrides[dependencies.get_current_user] = mock_get_current_user
    if hasattr(dependencies, "get_current_user_from_cookie"):
        app.dependency_overrides[dependencies.get_current_user_from_cookie] = mock_get_current_user
    if hasattr(dependencies, "get_current_user_from_cookie_optional"):
        app.dependency_overrides[dependencies.get_current_user_from_cookie_optional] = mock_get_current_user

# Plantillas
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Incluir Router de Agencia
app.include_router(agencia.router)

# Endpoint Mock para perfil de usuario
@app.get("/api/v1/auth/me")
def mock_auth_me():
    return {
        "id": 1,
        "email": "agencia_dev@localhost",
        "nombre": "Agencia Localhost",
        "roles": [{"name": "agency"}, {"name": "admin"}]
    }

# Endpoint Mock de Cursos para evitar caídas si la app principal no está activa
@app.get("/api/v1/school/cursos/")
def mock_school_cursos():
    return [
        {
            "id": 1,
            "titulo": "Curso de Prospección B2B (Mock Local)",
            "descripcion": "Curso de prueba para entorno independiente",
            "modulos": []
        }
    ]

# Endpoint Mock para cerrar sesión en entorno independiente
@app.post("/api/v1/auth/logout")
def mock_logout():
    return {"message": "Sesión cerrada en entorno local"}

# Manejador de Login para redirección suave en desarrollo local
@app.get("/login.html", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
async def login_page_mock(request: Request):
    return RedirectResponse(url="/", status_code=302)

@app.get("/", response_class=HTMLResponse)
@app.get("/agencia_services.html", response_class=HTMLResponse)
async def agencia_services_page(request: Request):
    """
    Renderizador del nuevo frontend modular (agencia_services.html) para localhost.
    """
    mock_user = {
        "id": 1,
        "email": "agencia_dev@localhost",
        "nombre": "Agencia Localhost",
        "roles": [{"name": "agency"}, {"name": "admin"}]
    }
    google_key = getattr(settings, "GOOGLE_API_KEY", getattr(settings, "GOOGLE_SERVER_API_KEY", ""))
    return templates.TemplateResponse(
        "agencia_services.html", 
        {
            "request": request, 
            "user": mock_user, 
            "settings": {"GOOGLE_API_KEY": google_key}
        }
    )

@app.get("/agenciacms.html", response_class=HTMLResponse)
async def agencia_cms_page(request: Request):
    """
    Renderizador del frontend monolítico agenciacms.html para localhost.
    """
    mock_user = {
        "id": 1,
        "email": "agencia_dev@localhost",
        "nombre": "Agencia Localhost",
        "roles": [{"name": "agency"}, {"name": "admin"}]
    }
    google_key = getattr(settings, "GOOGLE_API_KEY", getattr(settings, "GOOGLE_SERVER_API_KEY", ""))
    return templates.TemplateResponse(
        "agenciacms.html", 
        {
            "request": request, 
            "user": mock_user, 
            "settings": {"GOOGLE_API_KEY": google_key}
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agencia_standalone.standalone_server:app", host="127.0.0.1", port=8005, reload=True)
