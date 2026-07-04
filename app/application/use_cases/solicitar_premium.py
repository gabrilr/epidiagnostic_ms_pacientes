"""
Casos de uso: SolicitarPremiumUseCase y ConsultarMiSolicitudUseCase.
"""
from uuid import UUID

from app.application.dtos.solicitud_premium_dto import (
    SolicitarPremiumInputDTO,
    SolicitudOutputDTO,
    solicitud_a_dto,
)
from app.domain.entities.solicitud_premium import SolicitudPremium
from app.domain.exceptions.domain_exceptions import (
    SolicitudPendienteExistenteException,
    SolicitudPremiumNoEncontradaException,
)
from app.domain.repositories.solicitud_premium_repository import SolicitudPremiumRepository


class SolicitarPremiumUseCase:

    def __init__(self, solicitud_repository: SolicitudPremiumRepository):
        self._solicitud_repository = solicitud_repository

    async def ejecutar(self, datos: SolicitarPremiumInputDTO) -> SolicitudOutputDTO:
        existente = await self._solicitud_repository.buscar_pendiente_de_personal(
            UUID(datos.personal_id)
        )
        if existente is not None:
            raise SolicitudPendienteExistenteException()

        solicitud = SolicitudPremium(
            personal_id=UUID(datos.personal_id),
            numero_cedula=datos.numero_cedula,
            nombre_en_cedula=datos.nombre_en_cedula,
            especialidad=datos.especialidad,
        )
        guardada = await self._solicitud_repository.guardar(solicitud)
        return solicitud_a_dto(guardada)


class ConsultarMiSolicitudUseCase:

    def __init__(self, solicitud_repository: SolicitudPremiumRepository):
        self._solicitud_repository = solicitud_repository

    async def ejecutar(self, personal_id: UUID) -> SolicitudOutputDTO:
        solicitud = await self._solicitud_repository.buscar_mas_reciente_de_personal(personal_id)
        if solicitud is None:
            raise SolicitudPremiumNoEncontradaException(str(personal_id))
        return solicitud_a_dto(solicitud)
