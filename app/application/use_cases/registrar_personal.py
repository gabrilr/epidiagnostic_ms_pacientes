"""
Casos de uso: RegistrarPersonalUseCase y ConsultarPersonalUseCase.
"""
from uuid import UUID

from app.application.dtos.personal_dto import PersonalOutputDTO, RegistrarPersonalInputDTO
from app.domain.entities.personal_medico import PersonalMedico, TipoPersonal
from app.domain.exceptions.domain_exceptions import PersonalNoEncontradoException
from app.domain.repositories.personal_repository import PersonalRepository
from app.domain.value_objects.ubicacion import Ubicacion


def _a_dto(personal: PersonalMedico) -> PersonalOutputDTO:
    return PersonalOutputDTO(
        id=str(personal.id),
        nombre_completo=personal.nombre_completo,
        tipo=personal.tipo.value,
        comunidad=personal.ubicacion_asignada.comunidad,
        municipio=personal.ubicacion_asignada.municipio,
        cedula_profesional=personal.cedula_profesional,
        activo=personal.activo,
        creado_en=personal.creado_en,
    )


class RegistrarPersonalUseCase:

    def __init__(self, personal_repository: PersonalRepository):
        self._personal_repository = personal_repository

    async def ejecutar(self, datos: RegistrarPersonalInputDTO) -> PersonalOutputDTO:
        personal = PersonalMedico(
            nombre_completo=datos.nombre_completo,
            tipo=TipoPersonal(datos.tipo),
            ubicacion_asignada=Ubicacion(comunidad=datos.comunidad, municipio=datos.municipio),
            cedula_profesional=datos.cedula_profesional,
        )
        guardado = await self._personal_repository.guardar(personal)
        return _a_dto(guardado)


class ConsultarPersonalUseCase:

    def __init__(self, personal_repository: PersonalRepository):
        self._personal_repository = personal_repository

    async def ejecutar(self, personal_id: UUID) -> PersonalOutputDTO:
        personal = await self._personal_repository.buscar_por_id(personal_id)
        if personal is None:
            raise PersonalNoEncontradoException(str(personal_id))
        return _a_dto(personal)
