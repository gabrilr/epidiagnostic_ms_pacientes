"""
Caso de uso: ConsultarPaciente

Soporta GET /pacientes/{id}, el endpoint que el microservicio 2
(Atención Médica) consulta para validar que un paciente existe antes
de registrar una atención.
"""
from uuid import UUID

from app.application.dtos.paciente_dto import PacienteOutputDTO
from app.domain.exceptions.domain_exceptions import PacienteNoEncontradoException
from app.domain.repositories.paciente_repository import PacienteRepository


class ConsultarPacienteUseCase:

    def __init__(self, paciente_repository: PacienteRepository):
        self._paciente_repository = paciente_repository

    async def ejecutar(self, paciente_id: UUID) -> PacienteOutputDTO:
        paciente = await self._paciente_repository.buscar_por_id(paciente_id)
        if paciente is None:
            raise PacienteNoEncontradoException(str(paciente_id))

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
