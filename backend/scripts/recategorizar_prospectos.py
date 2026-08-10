"""
Script de procesamiento por lotes para recategorizar los prospectos B2B en PostgreSQL
aplicando el nuevo motor de inferencia jerárquica (Nombre comercial > Búsqueda genérica).
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from backend.core.database import SessionLocal
from backend.models.prospect import ProspectoB2BModel
from backend.domain.rubros import clasificar_y_refinar_rubro


def recategorizar_base_datos():
    db = SessionLocal()
    try:
        prospectos = db.query(ProspectoB2BModel).all()
        total = len(prospectos)
        print(f"[INFO] Iniciando recategorización inteligente sobre {total} prospectos...")

        modificados = 0
        for p in prospectos:
            rubro_nuevo = clasificar_y_refinar_rubro(p.nombre, p.tipo_busqueda or "")
            if rubro_nuevo and rubro_nuevo != p.tipo_busqueda:
                p.tipo_busqueda = rubro_nuevo
                modificados += 1

            if modificados > 0 and modificados % 1000 == 0:
                db.commit()
                print(f"[INFO] Procesados {modificados} prospectos corregidos...")

        db.commit()
        print(f"[OK] Recategorización finalizada con éxito. Total corregidos/actualizados: {modificados} / {total}")
    except Exception as e:
        db.rollback()
        print(f"[ERR] Error ejecutando la recategorización: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    recategorizar_base_datos()
