"""
Casos de uso del panel de administración: listado de usuarios y
estadísticas agregadas.
"""
from dataclasses import dataclass

from app.application.dtos.personal_dto import PersonalOutputDTO, personal_a_dto
from app.domain.entities.personal_medico import TipoPersonal
from app.domain.repositories.personal_repository import PersonalRepository
from app.domain.repositories.solicitud_premium_repository import SolicitudPremiumRepository


class ListarUsuariosUseCase:

    def __init__(self, personal_repository: PersonalRepository):
        self._personal_repository = personal_repository

    async def ejecutar(self, tipo: TipoPersonal | None = None) -> list[PersonalOutputDTO]:
        personal = await self._personal_repository.listar_todos(solo_activos=False)
        if tipo is not None:
            personal = [p for p in personal if p.tipo == tipo]
        return [personal_a_dto(p) for p in personal]


@dataclass
class EstadisticasOutputDTO:
    total_usuarios: int
    por_rol: dict[str, int]
    solicitudes_pendientes: int
    solicitudes_aprobadas_hoy: int


class EstadisticasUseCase:

    def __init__(
        self,
        personal_repository: PersonalRepository,
        solicitud_repository: SolicitudPremiumRepository,
    ):
        self._personal_repository = personal_repository
        self._solicitud_repository = solicitud_repository

    async def ejecutar(self) -> EstadisticasOutputDTO:
        personal = await self._personal_repository.listar_todos(solo_activos=False)
        por_rol = {tipo.value: 0 for tipo in TipoPersonal}
        for p in personal:
            por_rol[p.tipo.value] += 1

        return EstadisticasOutputDTO(
            total_usuarios=len(personal),
            por_rol=por_rol,
            solicitudes_pendientes=await self._solicitud_repository.contar_pendientes(),
            solicitudes_aprobadas_hoy=await self._solicitud_repository.contar_aprobadas_hoy(),
        )
