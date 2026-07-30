from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid

@dataclass
class ServicioItem:
    titulo: str
    descripcion: str
    icono: str

@dataclass
class BeneficioItem:
    titulo: str
    descripcion: str
    icono: str

@dataclass
class TestimonioItem:
    autor: str
    cargo: str
    comentario: str
    estrellas: int = 5

@dataclass
class LandingRequest:
    nombre_negocio: str
    rubro: str
    telefono_whatsapp: Optional[str] = ""
    email: Optional[str] = ""
    direccion: Optional[str] = ""
    horario: Optional[str] = ""

@dataclass
class ClienteLanding:
    id: str
    nombre_negocio: str
    rubro: str
    categoria_visual: str
    telefono_whatsapp: str
    email: str
    direccion: str
    horario: str
    tagline: str
    hero_headline: str
    hero_subheadline: str
    cta_texto: str
    beneficios: List[Dict[str, str]]
    servicios: List[Dict[str, str]]
    testimonio: Dict[str, str]
    estado_lead: str = "Landing Generada"
    fecha_creacion: str = ""
    fallback_aplicado: bool = False

@dataclass
class LandingResponse:
    status: str
    cliente: ClienteLanding

