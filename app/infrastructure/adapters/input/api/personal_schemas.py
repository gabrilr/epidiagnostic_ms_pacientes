"""
Schemas Pydantic: contrato HTTP del API de personal médico.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class RegistrarPersonalRequest(BaseModel):
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    tipo: str = Field(..., pattern="^(medico|enfermera)$")
    comunidad: str = Field(..., min_length=1, max_length=255)
    municipio: str = Field(..., min_length=1, max_length=255)
    cedula_profesional: str | None = Field(default=None, max_length=50)


class PersonalResponse(BaseModel):
    id: str
    nombre_completo: str
    tipo: str
    comunidad: str
    municipio: str
    cedula_profesional: str | None
    activo: bool
    creado_en: datetime
