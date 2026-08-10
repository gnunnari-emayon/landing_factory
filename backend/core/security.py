import bcrypt

def obtener_password_hash(password: str) -> str:
    """Generar hash bcrypt salado para la contraseña"""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar coincidencia entre texto plano y hash bcrypt"""
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        try:
            from passlib.context import CryptContext
            ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return ctx.verify(plain_password[:72], hashed_password)
        except Exception:
            return False
