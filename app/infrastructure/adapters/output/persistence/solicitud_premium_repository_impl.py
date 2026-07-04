"""
Adaptador de salida: SolicitudPremiumRepositoryImpl
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.solicitud_premium import EstadoSolicitud, SolicitudPremium
from app.domain.repositories.solicitud_premium_repository import SolicitudPremiumRepository
from app.infrastructure.adapters.output.persistence.models.solicitud_premium_model import (
    SolicitudPremiumModel,
)


class SolicitudPremiumRepositoryImpl(SolicitudPremiumRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, solicitud: SolicitudPremium) -> SolicitudPremium:
        modelo = self._a_modelo(solicitud)
        self._session.add(modelo)
        await self._session.commit()
        await self._session.refresh(modelo)
        return self._a_entidad(modelo)

    async def actualizar(self, solicitud: SolicitudPremium) -> None:
        # Fetch + mutar in place (mismo patrón que PersonalRepositoryImpl.
        # actualizar_tipo) para no chocar con el identity map de
        # SQLAlchemy si la solicitud ya fue cargada antes en esta misma
        # sesión (ej. buscar_por_id dentro del mismo caso de uso).
        resultado = await self._session.execute(
            select(SolicitudPremiumModel).where(SolicitudPremiumModel.id == solicitud.id)
        )
        modelo = resultado.scalar_one_or_none()
        if modelo is None:
            return
        modelo.estado = solicitud.estado.value
        modelo.admin_id = solicitud.admin_id
        modelo.motivo_rechazo = solicitud.motivo_rechazo
        modelo.updated_at = solicitud.updated_at
        await self._session.commit()

    async def buscar_por_id(self, solicitud_id: UUID) -> SolicitudPremium | None:
        resultado = await self._session.execute(
            select(SolicitudPremiumModel).where(SolicitudPremiumModel.id == solicitud_id)
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    async def buscar_pendiente_de_personal(self, personal_id: UUID) -> SolicitudPremium | None:
        resultado = await self._session.execute(
            select(SolicitudPremiumModel).where(
                SolicitudPremiumModel.personal_id == personal_id,
                SolicitudPremiumModel.estado == EstadoSolicitud.PENDIENTE.value,
            )
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    async def buscar_mas_reciente_de_personal(self, personal_id: UUID) -> SolicitudPremium | None:
        resultado = await self._session.execute(
            select(SolicitudPremiumModel)
            .where(SolicitudPremiumModel.personal_id == personal_id)
            .order_by(SolicitudPremiumModel.created_at.desc())
            .limit(1)
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    async def listar(self, estado: EstadoSolicitud | None = None) -> list[SolicitudPremium]:
        query = select(SolicitudPremiumModel).order_by(SolicitudPremiumModel.created_at.desc())
        if estado is not None:
            query = query.where(SolicitudPremiumModel.estado == estado.value)
        resultado = await self._session.execute(query)
        return [self._a_entidad(m) for m in resultado.scalars().all()]

    async def contar_pendientes(self) -> int:
        resultado = await self._session.execute(
            select(func.count())
            .select_from(SolicitudPremiumModel)
            .where(SolicitudPremiumModel.estado == EstadoSolicitud.PENDIENTE.value)
        )
        return resultado.scalar_one()

    async def contar_aprobadas_hoy(self) -> int:
        inicio_dia = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        resultado = await self._session.execute(
            select(func.count())
            .select_from(SolicitudPremiumModel)
            .where(
                SolicitudPremiumModel.estado == EstadoSolicitud.APROBADA.value,
                SolicitudPremiumModel.updated_at >= inicio_dia,
            )
        )
        return resultado.scalar_one()

    @staticmethod
    def _a_modelo(solicitud: SolicitudPremium) -> SolicitudPremiumModel:
        return SolicitudPremiumModel(
            id=solicitud.id,
            personal_id=solicitud.personal_id,
            numero_cedula=solicitud.numero_cedula,
            nombre_en_cedula=solicitud.nombre_en_cedula,
            especialidad=solicitud.especialidad,
            estado=solicitud.estado.value,
            admin_id=solicitud.admin_id,
            motivo_rechazo=solicitud.motivo_rechazo,
            created_at=solicitud.created_at,
            updated_at=solicitud.updated_at,
        )

    @staticmethod
    def _a_entidad(modelo: SolicitudPremiumModel) -> SolicitudPremium:
        return SolicitudPremium(
            id=modelo.id,
            personal_id=modelo.personal_id,
            numero_cedula=modelo.numero_cedula,
            nombre_en_cedula=modelo.nombre_en_cedula,
            especialidad=modelo.especialidad,
            estado=EstadoSolicitud(modelo.estado),
            admin_id=modelo.admin_id,
            motivo_rechazo=modelo.motivo_rechazo,
            created_at=modelo.created_at,
            updated_at=modelo.updated_at,
        )
