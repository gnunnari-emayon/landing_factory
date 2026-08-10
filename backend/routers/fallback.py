from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/login")
async def redirect_login():
    return RedirectResponse(url="/autocentro/login", status_code=307)

@router.get("/turnos")
async def redirect_turnos():
    return RedirectResponse(url="/autocentro/turnos", status_code=307)

@router.get("/cotizador")
@router.get("/tienda")
@router.get("/operaciones/tienda")
async def redirect_cotizador():
    return RedirectResponse(url="/autocentro/cotizador", status_code=307)

@router.get("/admin/pos-mostrador")
async def redirect_pos():
    return RedirectResponse(url="/autocentro/admin/pos-mostrador", status_code=307)

@router.get("/admin/taller-control")
async def redirect_taller_control():
    return RedirectResponse(url="/autocentro/admin/taller-control", status_code=307)

@router.get("/admin/recepcion-taller")
async def redirect_recepcion():
    return RedirectResponse(url="/autocentro/admin/recepcion-taller", status_code=307)

@router.get("/admin/importador-neumaticos")
async def redirect_importador():
    return RedirectResponse(url="/autocentro/admin/importador-neumaticos", status_code=307)


# Fallback comodín para todas las rutas /admin/...
@router.get("/admin/{subpath:path}")
async def redirect_admin_subpath(subpath: str):
    return RedirectResponse(url=f"/autocentro/admin/{subpath}", status_code=307)


# Forwarder de APIs para AutoCentro (/api/v1/operaciones, /api/v1/cuenta-corriente, /api/v1/finanzas, /api/v1/taller, /api/v1/tienda)
@router.api_route("/api/v1/operaciones/{subpath:path}", methods=["GET", "POST", "PUT", "DELETE"])
@router.api_route("/api/v1/cuenta-corriente/{subpath:path}", methods=["GET", "POST", "PUT", "DELETE"])
@router.api_route("/api/v1/finanzas/{subpath:path}", methods=["GET", "POST", "PUT", "DELETE"])
@router.api_route("/api/v1/taller/{subpath:path}", methods=["GET", "POST", "PUT", "DELETE"])
@router.api_route("/api/v1/tienda/{subpath:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def forward_autocentro_apis(request: Request):
    new_url = f"/autocentro{request.url.path}"
    if request.url.query:
        new_url += f"?{request.url.query}"
    return RedirectResponse(url=new_url, status_code=307)
