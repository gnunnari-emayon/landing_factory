"""
Script de migración para copiar registros desde la base de datos SQLite legacy (crm_factory.db)
hacia la base de datos PostgreSQL objetivo configurada en el archivo .env.
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar path del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from backend.core.config import config
from backend.core.database import Base
from backend.models.prospect import ProspectoB2BModel


def migrar_sqlite_a_postgres():
    sqlite_db_path = os.path.join(BASE_DIR, "crm_factory.db")
    if not os.path.exists(sqlite_db_path):
        print(f"[ERR] No se encontró el archivo SQLite de origen en: {sqlite_db_path}")
        return

    pg_url = config.DATABASE_URL
    if not pg_url.startswith("postgresql"):
        print("[ERR] DATABASE_URL en .env debe apuntar a una base PostgreSQL (postgresql://user:pass@host:port/dbname)")
        return

    print("[INFO] Conectando a SQLite origen...")
    sqlite_engine = create_engine(f"sqlite:///{sqlite_db_path.replace('\\', '/')}")
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_db = SqliteSession()

    print(f"[INFO] Conectando a PostgreSQL destino: {pg_url}...")
    try:
        pg_engine = create_engine(pg_url)
        # Crear tablas en PG si no existen
        Base.metadata.create_all(bind=pg_engine)
        PgSession = sessionmaker(bind=pg_engine)
        pg_db = PgSession()
    except Exception as e:
        print(f"[ERR] Error al conectar con PostgreSQL: {e}")
        return

    # Extraer registros de SQLite
    prospectos_sqlite = sqlite_db.query(ProspectoB2BModel).all()
    print(f"[INFO] Se encontraron {len(prospectos_sqlite)} prospectos en SQLite.")

    migrados = 0
    omitidos = 0

    for p in prospectos_sqlite:
        # Evitar duplicados en PG si ya existe un prospecto con la misma place_id o (nombre, ciudad)
        existente = None
        if p.place_id:
            existente = pg_db.query(ProspectoB2BModel).filter(ProspectoB2BModel.place_id == p.place_id).first()
        else:
            existente = pg_db.query(ProspectoB2BModel).filter(
                ProspectoB2BModel.nombre == p.nombre,
                ProspectoB2BModel.ciudad_busqueda == p.ciudad_busqueda
            ).first()

        if existente:
            omitidos += 1
            continue

        nuevo_prospecto = ProspectoB2BModel(
            place_id=getattr(p, 'place_id', None),
            nombre=getattr(p, 'nombre', 'Sin Nombre'),
            ciudad_busqueda=getattr(p, 'ciudad_busqueda', None),
            tipo_busqueda=getattr(p, 'tipo_busqueda', None),
            telefono=getattr(p, 'telefono', None),
            whatsapp=getattr(p, 'whatsapp', None),
            email=getattr(p, 'email', None),
            sitio_web=getattr(p, 'sitio_web', None),
            status=getattr(p, 'status', 'ENRIQUECIDO'),
            rating=str(getattr(p, 'rating', '4.8')) if getattr(p, 'rating', None) else None,
            total_reseñas=getattr(p, 'total_reseñas', 0),
            reviews_json=getattr(p, 'reviews_json', None),
            photos_json=getattr(p, 'photos_json', None)
        )
        pg_db.add(nuevo_prospecto)
        migrados += 1
        if migrados % 1000 == 0:
            pg_db.commit()
            print(f"[INFO] Migrados {migrados} / {len(prospectos_sqlite)}...")

    pg_db.commit()
    sqlite_db.close()
    pg_db.close()

    print(f"[OK] Migración finalizada con éxito. Migrados: {migrados} | Omitidos (duplicados): {omitidos}")



if __name__ == "__main__":
    migrar_sqlite_a_postgres()
