"""
Caso de uso: AgregarAntecedenteHistorial

Implementa el endpoint POST /pacientes/{id}/historial. Este endpoint
siempre AÑADE, nunca reemplaza ni elimina antecedentes existentes
(regla de negocio confirmada: el historial es append-only).
"""
from uuid import UUID

from app.application.dtos.paciente_dto import AgregarAntecedenteInputDTO, PacienteOutputDTO
from app.domain.entities.antecedente_medico import AntecedenteMedico, TipoAntecedente
from app.domain.entities.paciente import Paciente
from app.domain.exceptions.domain_exceptions import PacienteNoEncontradoException
from app.domain.repositories.paciente_repository import PacienteRepository


class AgregarAntecedenteHistorialUseCase:

    def __init__(self, paciente_repository: PacienteRepository):
        self._paciente_repository = paciente_repository

    async def ejecutar(self, paciente_id: UUID, datos: AgregarAntecedenteInputDTO) -> PacienteOutputDTO:
        paciente = await self._paciente_repository.buscar_por_id(paciente_id)
        if paciente is None:
            raise PacienteNoEncontradoException(str(paciente_id))

        antecedente = AntecedenteMedico(
            descripcion=datos.descripcion,
            tipo=TipoAntecedente(datos.tipo),
            origen_atencion_id=datos.origen_atencion_id,
        )
        paciente.agregar_antecedente(antecedente)

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
