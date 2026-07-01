"""
Adaptador de salida: PacienteRepositoryImpl

Implementación concreta del puerto PacienteRepository usando SQLAlchemy
async + MySQL. Esta es la pieza que "conecta" el dominio puro con
la tecnología real de persistencia.

Responsabilidad clave de este archivo: traducir entre Paciente (entidad
de dominio) y PacienteModel (modelo ORM), en ambas direcciones. El resto
del sistema (dominio, aplicación) nunca ve PacienteModel directamente.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.antecedente_medico import AntecedenteMedico, TipoAntecedente
from app.domain.entities.historial_medico import HistorialMedico
from app.domain.entities.paciente import Paciente
from app.domain.repositories.paciente_repository import PacienteRepository
from app.domain.value_objects.curp import CURP
from app.domain.value_objects.ubicacion import Ubicacion
from app.infrastructure.adapters.output.persistence.models.antecedente_model import AntecedenteModel
from app.infrastructure.adapters.output.persistence.models.paciente_model import PacienteModel


class PacienteRepositoryImpl(PacienteRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, paciente: Paciente) -> Paciente:
        modelo = self._a_modelo(paciente)
        self._session.add(modelo)
        await self._session.commit()
        await self._session.refresh(modelo)
        return self._a_entidad(modelo)

    async def buscar_por_id(self, paciente_id: UUID) -> Paciente | None:
        resultado = await self._session.execute(
            select(PacienteModel).where(PacienteModel.id == paciente_id)
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    async def buscar_por_curp(self, curp: CURP) -> Paciente | None:
        resultado = await self._session.execute(
            select(PacienteModel).where(PacienteModel.curp == str(curp))
        )
        modelo = resultado.scalar_one_or_none()
        return self._a_entidad(modelo) if modelo else None

    async def actualizar(self, paciente: Paciente) -> Paciente:
        resultado = await self._session.execute(
            select(PacienteModel).where(PacienteModel.id == paciente.id)
        )
        modelo = resultado.scalar_one_or_none()
        if modelo is None:
            raise ValueError(f"No se puede actualizar: paciente {paciente.id} no existe en persistencia.")

        modelo.nombre_completo = paciente.nombre_completo
        modelo.comunidad = paciente.ubicacion.comunidad
        modelo.municipio = paciente.ubicacion.municipio
        modelo.lengua_materna = paciente.lengua_materna
        modelo.contacto_emergencia = paciente.contacto_emergencia
        modelo.actualizado_en = datetime.utcnow()

        # Sincronizar antecedentes nuevos (los que están en la entidad
        # de dominio pero no en el modelo persistido aún).
        ids_existentes = {a.id for a in modelo.antecedentes}
        for antecedente in paciente.historial.antecedentes:
            if antecedente.id not in ids_existentes:
                modelo.antecedentes.append(
                    AntecedenteModel(
                        id=antecedente.id,
                        paciente_id=paciente.id,
                        descripcion=antecedente.descripcion,
                        tipo=antecedente.tipo.value,
                        fecha_registro=antecedente.fecha_registro,
                        origen_atencion_id=antecedente.origen_atencion_id,
                    )
                )

        await self._session.commit()
        await self._session.refresh(modelo)
        return self._a_entidad(modelo)

    async def listar_actualizados_desde(
        self, desde: datetime, comunidad: str | None = None
    ) -> list[Paciente]:
        # TODO: este método ya cumple el contrato del puerto, pero falta
        # exponerlo a través de un caso de uso y un endpoint (ver
        # application/use_cases/listar_catalogo_offline.py).
        query = select(PacienteModel).where(PacienteModel.actualizado_en >= desde)
        if comunidad:
            query = query.where(PacienteModel.comunidad == comunidad)

        resultado = await self._session.execute(query)
        modelos = resultado.scalars().all()
        return [self._a_entidad(m) for m in modelos]

    @staticmethod
    def _a_modelo(paciente: Paciente) -> PacienteModel:
        return PacienteModel(
            id=paciente.id,
            curp=str(paciente.curp),
            nombre_completo=paciente.nombre_completo,
            fecha_nacimiento=paciente.fecha_nacimiento,
            sexo=paciente.sexo,
            comunidad=paciente.ubicacion.comunidad,
            municipio=paciente.ubicacion.municipio,
            lengua_materna=paciente.lengua_materna,
            contacto_emergencia=paciente.contacto_emergencia,
            device_generated_id=paciente.device_generated_id,
            creado_en=paciente.creado_en,
            actualizado_en=paciente.actualizado_en,
        )

    @staticmethod
    def _a_entidad(modelo: PacienteModel) -> Paciente:
        historial = HistorialMedico(
            antecedentes=[
                AntecedenteMedico(
                    id=a.id,
                    descripcion=a.descripcion,
                    tipo=TipoAntecedente(a.tipo),
                    fecha_registro=a.fecha_registro,
                    origen_atencion_id=a.origen_atencion_id,
                )
                for a in modelo.antecedentes
            ]
        )
        return Paciente(
            id=modelo.id,
            curp=CURP(modelo.curp),
            nombre_completo=modelo.nombre_completo,
            fecha_nacimiento=modelo.fecha_nacimiento,
            sexo=modelo.sexo,
            ubicacion=Ubicacion(comunidad=modelo.comunidad, municipio=modelo.municipio),
            lengua_materna=modelo.lengua_materna,
            contacto_emergencia=modelo.contacto_emergencia,
            device_generated_id=modelo.device_generated_id,
            historial=historial,
            creado_en=modelo.creado_en,
            actualizado_en=modelo.actualizado_en,
        )
