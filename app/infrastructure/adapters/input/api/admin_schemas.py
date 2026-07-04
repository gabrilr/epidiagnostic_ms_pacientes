"""
Schemas Pydantic para los endpoints de administración.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class PersonalResumenSchema(BaseModel):
    personal_id: str
    nombre_completo: str
    correo: str
    tipo: str


class SolicitudAdminResponse(BaseModel):
    solicitud_id: str
    estado: str
    created_at: datetime
    numero_cedula: str
    nombre_en_cedula: str
    especialidad: str | None
    personal: PersonalResumenSchema


class RechazarSolicitudRequest(BaseModel):
    motivo_rechazo: str = Field(..., min_length=1)


class MensajeResponse(BaseModel):
    mensaje: str


class UsuarioAdminResponse(BaseModel):
    personal_id: str
    nombre_completo: str
    correo: str
    tipo: str
    created_at: datetime


class EstadisticasResponse(BaseModel):
    total_usuarios: int
    por_rol: dict[str, int]
    solicitudes_pendientes: int
    solicitudes_aprobadas_hoy: int
