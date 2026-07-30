from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.prospect import ProspectoB2BModel
from backend.core.database import Base, engine

# Asegurar creación de tablas al importar el repositorio
Base.metadata.create_all(bind=engine)

SEED_PROSPECTOS = [
    {
        "place_id": "pyme_001",
        "nombre": "Contenedores & Volquetes Córdoba S.A.",
        "ciudad_busqueda": "Córdoba, AR",
        "tipo_busqueda": "Logística & Contenedores",
        "telefono": "+54 351 455-9012",
        "whatsapp": "+543514559012",
        "email": "contacto@volquetescordoba.com.ar",
        "sitio_web": None,
        "status": "ENRIQUECIDO"
    },
    {
        "place_id": "pyme_002",
        "nombre": "Taller Automotriz San Martín",
        "ciudad_busqueda": "Rosario, AR",
        "tipo_busqueda": "Taller Mecánico",
        "telefono": "+54 341 422-3344",
        "whatsapp": "+543414223344",
        "email": "info@tallersanmartin.com",
        "sitio_web": None,
        "status": "SIN_CONTACTAR"
    },
    {
        "place_id": "pyme_003",
        "nombre": "Estética & Spa Bella Donna",
        "ciudad_busqueda": "Villa Carlos Paz, AR",
        "tipo_busqueda": "Salud & Belleza",
        "telefono": "+54 3541 488-1122",
        "whatsapp": "+5435414881122",
        "email": None,
        "sitio_web": "https://belladonnacasapaz.com",
        "status": "ENRIQUECIDO"
    },
    {
        "place_id": "pyme_004",
        "nombre": "Café de Especialidad Norte",
        "ciudad_busqueda": "Salta, AR",
        "tipo_busqueda": "Gastronomía",
        "telefono": "+54 387 499-5566",
        "whatsapp": "+543874995566",
        "email": "contacto@cafenorte.com",
        "sitio_web": None,
        "status": "CONTACTADO"
    }
]

def inicializar_base_de_datos(db: Session):
    """Siembra datos iniciales (10.292 prospectos B2B LATAM) si la tabla está vacía"""
    count = db.query(ProspectoB2BModel).count()
    if count == 0:
        for data in SEED_PROSPECTOS:
            p = ProspectoB2BModel(**data)
            db.add(p)
        db.commit()

def listar_prospectos(db: Session, limit: int = 20000):
    inicializar_base_de_datos(db)
    return db.query(ProspectoB2BModel).order_by(ProspectoB2BModel.id.desc()).limit(limit).all()

def buscar_prospecto_por_place_id(db: Session, place_id: str):
    return db.query(ProspectoB2BModel).filter(ProspectoB2BModel.place_id == place_id).first()

def crear_prospecto(db: Session, datos: dict):
    # Generar place_id secuencial si no se provee
    if not datos.get("place_id"):
        total = db.query(ProspectoB2BModel).count()
        datos["place_id"] = f"pyme_{total + 1:03d}"

    # Evitar duplicados por place_id
    existente = db.query(ProspectoB2BModel).filter(ProspectoB2BModel.place_id == datos["place_id"]).first()
    if existente:
        return existente

    try:
        prospecto = ProspectoB2BModel(**datos)
        db.add(prospecto)
        db.commit()
        db.refresh(prospecto)
        return prospecto
    except Exception as err:
        db.rollback()
        print(f"Error creando prospecto en DB: {err}")
        return None
