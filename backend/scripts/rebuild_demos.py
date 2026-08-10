"""
Script para regenerar todas las demos en frontend/demos/ aplicando la nueva plantilla
con la propuesta comercial High-Ticket de Emayon Forge.
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from backend.core.database import SessionLocal
from backend.models.prospect import ProspectoB2BModel
from backend.services.demo_builder import construir_demo_html
from backend.services.landing_theme_engine import obtener_theme_config, obtener_contexto_web_empresa
from backend.services.generator import inferir_categoria_por_rubro


def regenerar_demos():
    db = SessionLocal()
    try:
        prospectos = db.query(ProspectoB2BModel).all()
        print(f"[INFO] Regenerando demos para {len(prospectos)} prospectos...")

        exitosos = 0
        for p in prospectos:
            try:
                p_dict = {
                    "place_id": p.place_id,
                    "nombre": p.nombre,
                    "ciudad_busqueda": p.ciudad_busqueda or "Córdoba, AR",
                    "tipo_busqueda": p.tipo_busqueda or "Servicios generales",
                    "reviews_json": p.reviews_json,
                    "photos_json": p.photos_json,
                    "telefono": p.telefono
                }

                cat_visual = inferir_categoria_por_rubro(f"{p.nombre} {p.tipo_busqueda}")
                theme = obtener_theme_config(cat_visual, p.place_id)
                ctx_web = obtener_contexto_web_empresa(p.nombre, p.ciudad_busqueda or "Córdoba, AR")

                dominio = f"{p.nombre.lower().replace(' ', '').replace('.', '')[:20]}.com"

                construir_demo_html(
                    place_id=p.place_id,
                    nombre=p.nombre,
                    rubro=p.tipo_busqueda or "Servicios generales",
                    cat_visual=cat_visual,
                    theme=theme,
                    ctx_web=ctx_web,
                    prospecto=p_dict,
                    precio=350.0,
                    dominio=dominio,
                    telefono_wa=p.telefono
                )
                exitosos += 1
            except Exception as e_indiv:
                print(f"[WARN] Error reconstruyendo demo para {p.nombre}: {e_indiv}")

        print(f"[OK] Reconstrucción de demos finalizada. Éxito: {exitosos} / {len(prospectos)}")
    finally:
        db.close()


if __name__ == "__main__":
    regenerar_demos()
