import sys
import os

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.config import config
from backend.routers.api import autenticar_usuario, solicitar_generacion

def main():
    print("==================================================")
    print("  Nicho Landing Factory & CRM Engine (Enterprise) ")
    print("==================================================")
    print(f"[*] Usuario CRM Activo: {config.CRM_USER.upper()}")
    print(f"[*] Puerto de Operación: {config.PORT}")
    print(f"[*] Dominio de Producción: https://crm.emayonforge.com/")
    print("==================================================")
    
    es_valido, info = autenticar_usuario(config.CRM_USER, config.CRM_PASSWORD)
    if es_valido:
        print(f"\n[OK] Sesión iniciada correctamente como usuario: {info['user']}")
        
        # Generación de prueba demostrativa
        res = solicitar_generacion("Taller Mecánico San José", "Reparación Automotriz")
        print(f"[OK] Landing Generada -> Negocio: {res.nombre_negocio} | Categoría: [{res.categoria_visual}]")
    else:
        print(f"\n[FAIL] Error de autenticación: {info['error']}")

if __name__ == "__main__":
    main()
