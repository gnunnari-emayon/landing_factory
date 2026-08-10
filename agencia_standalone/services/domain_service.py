import socket
import httpx

async def verificar_disponibilidad_dominio(nombre_empresa: str) -> dict:
    base = "".join(c.lower() for c in nombre_empresa if c.isalnum())
    if not base:
        base = "miempresa"
        
    dominios_a_probar = [
        f"{base}.com",
        f"{base}.com.ar",
        f"{base}.net",
        f"{base}oficial.com"
    ]
    
    resultados = []
    for dom in dominios_a_probar:
        disponible = False
        try:
            socket.gethostbyname(dom)
            disponible = False
        except socket.gaierror:
            disponible = True
        except Exception:
            disponible = True
            
        resultados.append({
            "dominio": dom,
            "disponible": disponible,
            "sugerido": dom == dominios_a_probar[0]
        })
        
    return {
        "base_busqueda": base,
        "sugerencia_principal": resultados[0]["dominio"],
        "dominios": resultados
    }
