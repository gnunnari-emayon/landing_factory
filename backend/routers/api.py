from backend.core.config import config
from backend.services.generator import generar_landing_page, inferir_categoria_por_rubro

def autenticar_usuario(usuario: str, password: str):
    if usuario == config.CRM_USER and password == config.CRM_PASSWORD:
        return True, {"user": config.CRM_USER.upper(), "role": "developer", "authenticated": True}
    return False, {"error": "Credenciales inválidas"}

def solicitar_generacion(nombre_negocio: str, rubro: str):
    return generar_landing_page(nombre_negocio, rubro)
