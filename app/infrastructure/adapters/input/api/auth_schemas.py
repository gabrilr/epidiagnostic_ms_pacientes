"""
Schemas Pydantic para autenticación.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class RegistroPublicoRequest(BaseModel):
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    correo: EmailStr
    contrasena: str = Field(..., min_length=8, description="Mínimo 8 caracteres.")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    personal_id: str
    nombre_completo: str
    tipo: str
    correo: str


class UpgradePlanRequest(BaseModel):
    nuevo_tipo: str = Field(..., pattern="^(usuario|enfermera|medico)$")
    cedula_verificada: bool = False


class SolicitarPremiumRequest(BaseModel):
    numero_cedula: str = Field(..., min_length=1, max_length=10)
    nombre_en_cedula: str = Field(..., min_length=1, max_length=200)
    especialidad: str | None = Field(default=None, max_length=100)


class SolicitarPremiumResponse(BaseModel):
    solicitud_id: str
    estado: str
    mensaje: str


class MiSolicitudResponse(BaseModel):
    solicitud_id: str
    estado: str
    created_at: datetime
    motivo_rechazo: str | None
