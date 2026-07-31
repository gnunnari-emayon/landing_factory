import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import config

# Normalizar URL para PostgreSQL si se especifica en .env (postgres:// a postgresql://)
db_url = config.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if db_url.startswith("sqlite:///"):
    db_path = db_url.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        abs_db_path = os.path.join(base_dir, db_path)
        db_url = f"sqlite:///{abs_db_path}"
    connect_args = {"check_same_thread": False, "timeout": 15.0}
elif db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 15.0}

engine = create_engine(db_url, connect_args=connect_args, echo=False)

if db_url.startswith("sqlite"):
    from sqlalchemy import event
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency para obtener sesión de DB por request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
