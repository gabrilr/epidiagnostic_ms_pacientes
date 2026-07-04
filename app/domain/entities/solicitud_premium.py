"""
Entidad raíz de agregado: SolicitudPremium

Representa la solicitud de un miembro del personal para subir al plan
Premium (tipo 'medico'). La verificación de la cédula profesional es
manual: un administrador la revisa por fuera (ej. consultándola en el
sitio de la SEP) y luego aprueba o rechaza la solicitud.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EstadoSolicitud(str, Enum):
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"


@dataclass
class SolicitudPremium:
    personal_id: uuid.UUID
    numero_cedula: str
    nombre_en_cedula: str
    especialidad: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    estado: EstadoSolicitud = EstadoSolicitud.PENDIENTE
    admin_id: uuid.UUID | None = None
    motivo_rechazo: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.numero_cedula or not self.numero_cedula.strip():
            raise ValueError("El número de cédula no puede estar vacío.")
        if not self.nombre_en_cedula or not self.nombre_en_cedula.strip():
            raise ValueError("El nombre en la cédula no puede estar vacío.")

    def aprobar(self, admin_id: uuid.UUID) -> None:
        if self.estado != EstadoSolicitud.PENDIENTE:
            raise ValueError("Solo se pueden aprobar solicitudes pendientes.")
        self.estado = EstadoSolicitud.APROBADA
        self.admin_id = admin_id
        self.updated_at = datetime.utcnow()

    def rechazar(self, admin_id: uuid.UUID, motivo_rechazo: str) -> None:
        if self.estado != EstadoSolicitud.PENDIENTE:
            raise ValueError("Solo se pueden rechazar solicitudes pendientes.")
        if not motivo_rechazo or not motivo_rechazo.strip():
            raise ValueError("El motivo de rechazo es obligatorio.")
        self.estado = EstadoSolicitud.RECHAZADA
        self.admin_id = admin_id
        self.motivo_rechazo = motivo_rechazo
        self.updated_at = datetime.utcnow()
