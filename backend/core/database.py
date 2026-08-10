import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import config

# Exigir URL de PostgreSQL
db_url = config.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if not db_url.startswith("postgresql://"):
    raise ValueError(
        f"DATABASE_URL inválida: '{db_url}'. "
        "El sistema está configurado para operar exclusivamente con PostgreSQL (postgresql://user:pass@host:port/dbname)."
    )

engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency para obtener sesión de DB por request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
