import os
from dotenv import load_dotenv
from generator import generar_landing_page, inferir_categoria_por_rubro

# Cargar variables de entorno
load_dotenv()

CRM_USER = os.getenv("CRM_USER", "dev")
CRM_PASSWORD = os.getenv("CRM_PASSWORD", "ventas2026")
PORT = int(os.getenv("PORT", 8000))

def autenticar_usuario(usuario, password):
    """
    Verifica las credenciales del usuario CRM.
    """
    if usuario == CRM_USER and password == CRM_PASSWORD:
        return True, {"user": CRM_USER.upper(), "role": "developer", "authenticated": True}
    return False, {"error": "Credenciales inválidas"}

def main():
    print("==================================================")
    print("      Nicho Landing Factory & CRM Engine          ")
    print("==================================================")
    print(f"[*] Usuario CRM Activo: {CRM_USER.upper()}")
    print(f"[*] Puerto de Operación: {PORT}")
    print(f"[*] Dominio de Producción: https://crm.emayonforge.com/")
    print("==================================================")
    
    # Simulación de autenticación y Dashboard
    es_valido, info = autenticar_usuario("dev", "ventas2026")
    if es_valido:
        print(f"\n[OK] Sesión iniciada correctamente como usuario: {info['user']}")
    else:
        print(f"\n[FAIL] Error de autenticación: {info['error']}")

if __name__ == "__main__":
    main()
