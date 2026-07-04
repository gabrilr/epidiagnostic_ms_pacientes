"""
Casos de uso de administración de solicitudes Premium.
"""
from uuid import UUID

from app.application.dtos.personal_dto import personal_a_dto
from app.application.dtos.solicitud_premium_dto import SolicitudConPersonalDTO, solicitud_a_dto
from app.application.use_cases.upgrade_plan import UpgradePlanUseCase
from app.domain.entities.personal_medico import TipoPersonal
from app.domain.entities.solicitud_premium import EstadoSolicitud
from app.domain.exceptions.domain_exceptions import SolicitudPremiumNoEncontradaException
from app.domain.repositories.personal_repository import PersonalRepository
from app.domain.repositories.solicitud_premium_repository import SolicitudPremiumRepository


class ListarSolicitudesUseCase:

    def __init__(
        self,
        solicitud_repository: SolicitudPremiumRepository,
        personal_repository: PersonalRepository,
    ):
        self._solicitud_repository = solicitud_repository
        self._personal_repository = personal_repository

    async def ejecutar(self, estado: EstadoSolicitud | None) -> list[SolicitudConPersonalDTO]:
        solicitudes = await self._solicitud_repository.listar(estado)
        resultado = []
        for solicitud in solicitudes:
            personal = await self._personal_repository.buscar_por_id(solicitud.personal_id)
            if personal is None:
                # Dato huérfano defensivo (no debería pasar, personal_id es FK).
                continue
            resultado.append(
                SolicitudConPersonalDTO(
                    solicitud=solicitud_a_dto(solicitud),
                    personal=personal_a_dto(personal),
                )
            )
        return resultado


class AprobarSolicitudUseCase:

    def __init__(
        self,
        solicitud_repository: SolicitudPremiumRepository,
        upgrade_plan_use_case: UpgradePlanUseCase,
    ):
        self._solicitud_repository = solicitud_repository
        self._upgrade_plan_use_case = upgrade_plan_use_case

    async def ejecutar(self, solicitud_id: UUID, admin_id: UUID) -> None:
        solicitud = await self._solicitud_repository.buscar_por_id(solicitud_id)
        if solicitud is None:
            raise SolicitudPremiumNoEncontradaException(str(solicitud_id))

        solicitud.aprobar(admin_id)
        await self._upgrade_plan_use_case.ejecutar(
            personal_id=solicitud.personal_id,
            nuevo_tipo=TipoPersonal.MEDICO,
            cedula_verificada=True,
        )
        await self._solicitud_repository.actualizar(solicitud)


class RechazarSolicitudUseCase:

    def __init__(self, solicitud_repository: SolicitudPremiumRepository):
        self._solicitud_repository = solicitud_repository

    async def ejecutar(self, solicitud_id: UUID, admin_id: UUID, motivo_rechazo: str) -> None:
        solicitud = await self._solicitud_repository.buscar_por_id(solicitud_id)
        if solicitud is None:
            raise SolicitudPremiumNoEncontradaException(str(solicitud_id))

        solicitud.rechazar(admin_id, motivo_rechazo)
        await self._solicitud_repository.actualizar(solicitud)
