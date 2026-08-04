import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_password_hash(password: str) -> str:
    """Generar hash bcrypt salado para la contraseña"""
    return pwd_context.hash(password)

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar coincidencia entre texto plano y hash bcrypt"""
    return pwd_context.verify(plain_password, hashed_password)
