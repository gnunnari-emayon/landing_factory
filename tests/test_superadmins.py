import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.database import Base
from backend.models.user import UserModel
from backend.services.seed_users import inicializar_superadmins
from backend.core.security import verificar_password

def test_seed_superadmins_gabi_y_gian():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    # Ejecutar sembrado de superadmins
    inicializar_superadmins(db)

    # Verificar que solo existan gabi y gian
    usuarios = db.query(UserModel).all()
    nombres = [u.username for u in usuarios]
    assert len(usuarios) == 2
    assert "gabi" in nombres
    assert "gian" in nombres

    # Verificar rol SUPERADMIN y autenticación bcrypt
    gabi = db.query(UserModel).filter(UserModel.username == "gabi").first()
    gian = db.query(UserModel).filter(UserModel.username == "gian").first()

    assert gabi.role == "SUPERADMIN"
    assert gian.role == "SUPERADMIN"
    assert verificar_password("supergabi2026!", gabi.hashed_password)
    assert verificar_password("supergian2026!", gian.hashed_password)

    db.close()
