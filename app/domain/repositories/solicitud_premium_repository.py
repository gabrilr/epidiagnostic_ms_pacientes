"""
Puerto de salida: SolicitudPremiumRepository

Contrato de persistencia para el agregado SolicitudPremium.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.solicitud_premium import EstadoSolicitud, SolicitudPremium


class SolicitudPremiumRepository(ABC):

    @abstractmethod
    async def guardar(self, solicitud: SolicitudPremium) -> SolicitudPremium:
        raise NotImplementedError

    @abstractmethod
    async def actualizar(self, solicitud: SolicitudPremium) -> None:
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_id(self, solicitud_id: UUID) -> SolicitudPremium | None:
        raise NotImplementedError

    @abstractmethod
    async def buscar_pendiente_de_personal(self, personal_id: UUID) -> SolicitudPremium | None:
        raise NotImplementedError

    @abstractmethod
    async def buscar_mas_reciente_de_personal(self, personal_id: UUID) -> SolicitudPremium | None:
        raise NotImplementedError

    @abstractmethod
    async def listar(self, estado: EstadoSolicitud | None = None) -> list[SolicitudPremium]:
        raise NotImplementedError

    @abstractmethod
    async def contar_pendientes(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def contar_aprobadas_hoy(self) -> int:
        raise NotImplementedError
