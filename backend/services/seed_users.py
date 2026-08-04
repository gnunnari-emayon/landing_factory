import os
from sqlalchemy.orm import Session
from backend.models.user import UserModel
from backend.core.security import obtener_password_hash, verificar_password

def inicializar_superadmins(db: Session):
    """
    Garantizar que existan únicamente los usuarios superadmin 'gabi' y 'gian'
    con las contraseñas configuradas en las variables de entorno.
    """
    from backend.core.database import Base
    Base.metadata.create_all(bind=db.get_bind())


    superadmins = [
        ("gabi", os.getenv("GABI_PASSWORD", "supergabi2026!")),
        ("gian", os.getenv("GIAN_PASSWORD", "supergian2026!"))
    ]

    for username, plain_pass in superadmins:
        usuario = db.query(UserModel).filter(UserModel.username == username).first()
        if not usuario:
            nuevo_user = UserModel(
                username=username,
                hashed_password=obtener_password_hash(plain_pass),
                role="SUPERADMIN",
                is_active=True
            )
            db.add(nuevo_user)
        else:
            # Actualizar hash si cambió la contraseña en .env
            if not verificar_password(plain_pass, usuario.hashed_password):
                usuario.hashed_password = obtener_password_hash(plain_pass)
                usuario.role = "SUPERADMIN"
    db.commit()
