import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CRM_USER: str = os.getenv("CRM_USER", "dev")
    CRM_PASSWORD: str = os.getenv("CRM_PASSWORD", "ventas2026")
    PORT: int = int(os.getenv("PORT", 8000))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "emayonforge_secret_key_2026")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///crm_factory.db"
    )
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_PLACES_API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "")

config = Config()
