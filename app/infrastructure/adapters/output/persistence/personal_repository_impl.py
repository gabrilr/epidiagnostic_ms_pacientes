"""
Adaptador de salida: PersonalRepositoryImpl
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.personal_medico import PersonalMedico, TipoPersonal
from app.domain.repositories.personal_repository import PersonalRepository
from app.domain.value_objects.ubicacion import Ubicacion
from app.infrastructure.adapters.output.persistence.models.personal_model import PersonalModel


class PersonalRepositoryImpl(PersonalRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, personal: PersonalMedico) -> PersonalMedico:
        modelo = self._a_modelo(personal)
        self._session.add(modelo)
        await self._session.commit()
        await self._session.refresh(modelo)
        return self._a_entidad(modelo)

    async def buscar_por_id(self, personal_id: UUID) -> PersonalMedico | None:
        resultado = await self._session.execute(
            select(PersonalModel).where(PersonalModel.id == personal_id)
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    async def listar_todos(self, solo_activos: bool = True) -> list[PersonalMedico]:
        query = select(PersonalModel)
        if solo_activos:
            query = query.where(PersonalModel.activo == True)  # noqa: E712
        resultado = await self._session.execute(query)
        return [self._a_entidad(m) for m in resultado.scalars().all()]

    @staticmethod
    def _a_modelo(personal: PersonalMedico) -> PersonalModel:
        return PersonalModel(
            id=personal.id,
            nombre_completo=personal.nombre_completo,
            tipo=personal.tipo.value,
            comunidad=personal.ubicacion_asignada.comunidad,
            municipio=personal.ubicacion_asignada.municipio,
            correo=personal.correo,
            contrasena_hash=personal.contrasena_hash,
            cedula_profesional=personal.cedula_profesional,
            activo=personal.activo,
            creado_en=personal.creado_en,
        )

    @staticmethod
    def _a_entidad(modelo: PersonalModel) -> PersonalMedico:
        return PersonalMedico(
            id=modelo.id,
            nombre_completo=modelo.nombre_completo,
            tipo=TipoPersonal(modelo.tipo),
            ubicacion_asignada=Ubicacion(comunidad=modelo.comunidad, municipio=modelo.municipio),
            correo=modelo.correo,
            contrasena_hash=modelo.contrasena_hash,
            cedula_profesional=modelo.cedula_profesional,
            activo=modelo.activo,
            creado_en=modelo.creado_en,
        )
