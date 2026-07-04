"""
DTOs de la capa de aplicación para solicitudes de plan Premium.
"""
from dataclasses import dataclass
from datetime import datetime

from app.application.dtos.personal_dto import PersonalOutputDTO
from app.domain.entities.solicitud_premium import SolicitudPremium


@dataclass
class SolicitarPremiumInputDTO:
    personal_id: str
    numero_cedula: str
    nombre_en_cedula: str
    especialidad: str | None = None


@dataclass
class SolicitudOutputDTO:
    id: str
    personal_id: str
    numero_cedula: str
    nombre_en_cedula: str
    especialidad: str | None
    estado: str
    admin_id: str | None
    motivo_rechazo: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class SolicitudConPersonalDTO:
    solicitud: SolicitudOutputDTO
    personal: PersonalOutputDTO


def solicitud_a_dto(solicitud: SolicitudPremium) -> SolicitudOutputDTO:
    return SolicitudOutputDTO(
        id=str(solicitud.id),
        personal_id=str(solicitud.personal_id),
        numero_cedula=solicitud.numero_cedula,
        nombre_en_cedula=solicitud.nombre_en_cedula,
        especialidad=solicitud.especialidad,
        estado=solicitud.estado.value,
        admin_id=str(solicitud.admin_id) if solicitud.admin_id else None,
        motivo_rechazo=solicitud.motivo_rechazo,
        created_at=solicitud.created_at,
        updated_at=solicitud.updated_at,
    )
