from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from backend.core.database import Base

class ProspectoB2BModel(Base):
    __tablename__ = "prospectos_b2b"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String(100), unique=True, index=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    ciudad_busqueda = Column(String(150), nullable=True)
    tipo_busqueda = Column(String(150), nullable=True)
    telefono = Column(String(50), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    sitio_web = Column(String(255), nullable=True)
    status = Column(String(50), default="ENRIQUECIDO")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "place_id": self.place_id,
            "nombre": self.nombre,
            "ciudad_busqueda": self.ciudad_busqueda,
            "tipo_busqueda": self.tipo_busqueda,
            "telefono": self.telefono,
            "whatsapp": self.whatsapp,
            "email": self.email,
            "sitio_web": self.sitio_web,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
