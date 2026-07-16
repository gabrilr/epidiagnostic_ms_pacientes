"""
Caso de uso: ActualizarDatosPaciente

Implementa el endpoint PATCH /pacientes/{id}/datos. Esta es la ÚNICA vía
para corregir datos de un paciente existente: la corrección NUNCA se
infiere automáticamente de un alta duplicada (CrearPacienteUseCase
ignora silenciosamente los duplicados sin fusionar datos) — debe ser una
acción explícita y consciente del personal médico que detecta el dato
desactualizado.
"""
from uuid import UUID

from app.application.dtos.paciente_dto import ActualizarDatosPacienteInputDTO, PacienteOutputDTO
from app.domain.entities.paciente import Paciente
from app.domain.exceptions.domain_exceptions import PacienteNoEncontradoException
from app.domain.repositories.paciente_repository import PacienteRepository
from app.domain.value_objects.ubicacion import Ubicacion


class ActualizarDatosPacienteUseCase:

    def __init__(self, paciente_repository: PacienteRepository):
        self._paciente_repository = paciente_repository

    async def ejecutar(self, paciente_id: UUID, datos: ActualizarDatosPacienteInputDTO) -> PacienteOutputDTO:
        paciente = await self._paciente_repository.buscar_por_id(paciente_id)
        if paciente is None:
            raise PacienteNoEncontradoException(str(paciente_id))

        ubicacion = None
        if datos.comunidad is not None or datos.municipio is not None:
            # Ubicacion es un Value Object inmutable con ambos campos
            # obligatorios: si solo viene uno de los dos, se completa con
            # el valor que el paciente ya tenía para el otro.
            ubicacion = Ubicacion(
                comunidad=datos.comunidad if datos.comunidad is not None else paciente.ubicacion.comunidad,
                municipio=datos.municipio if datos.municipio is not None else paciente.ubicacion.municipio,
            )

        paciente.actualizar_datos_basicos(
            nombre_completo=datos.nombre_completo,
            ubicacion=ubicacion,
            lengua_materna=datos.lengua_materna,
            contacto_emergencia=datos.contacto_emergencia,
        )

        paciente_actualizado = await self._paciente_repository.actualizar(paciente)
        return self._a_dto(paciente_actualizado)

    @staticmethod
    def _a_dto(paciente: Paciente) -> PacienteOutputDTO:
        return PacienteOutputDTO(
            id=str(paciente.id),
            curp=str(paciente.curp),
            nombre_completo=paciente.nombre_completo,
            fecha_nacimiento=paciente.fecha_nacimiento,
            sexo=paciente.sexo,
            comunidad=paciente.ubicacion.comunidad,
            municipio=paciente.ubicacion.municipio,
            lengua_materna=paciente.lengua_materna,
            contacto_emergencia=paciente.contacto_emergencia,
            creado_en=paciente.creado_en,
            actualizado_en=paciente.actualizado_en,
            edad=paciente.edad,
            fue_creado_ahora=False,
        )
