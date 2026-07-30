from dataclasses import dataclass, field
from typing import Optional

@dataclass
class LandingRequest:
    nombre_negocio: str
    rubro: str

@dataclass
class LandingResponse:
    nombre_negocio: str
    rubro: str
    categoria_visual: str
    status: str = "success"
    fallback_aplicado: bool = False
