"""
Caso de uso: CrearPaciente

Implementa la regla de negocio central definida en el diseño:

    "Cuando llega un alta con un CURP que ya existe en el servidor,
    el microservicio debe IGNORAR el alta nueva y devolver el paciente
    ya existente (silencioso, sin pedir nada a nadie)."

Este caso de uso es la pieza que da soporte tanto al alta individual
(POST /pacientes) como, reutilizado, al alta en batch
(POST /pacientes/sync) que usará el celular offline-first.

Al estar en la capa de aplicación, este caso de uso depende únicamente
del PUERTO PacienteRepository (interfaz de dominio), nunca de una
implementación concreta. La implementación real se inyecta en tiempo de
ejecución (ver infrastructure/dependency_injection.py).
"""
from app.application.dtos.paciente_dto import CrearPacienteInputDTO, PacienteOutputDTO
from app.domain.entities.paciente import Paciente
from app.domain.repositories.paciente_repository import PacienteRepository
from app.domain.value_objects.curp import CURP
from app.domain.value_objects.ubicacion import Ubicacion


class CrearPacienteUseCase:

    def __init__(self, paciente_repository: PacienteRepository):
        self._paciente_repository = paciente_repository

    async def ejecutar(self, datos: CrearPacienteInputDTO) -> PacienteOutputDTO:
        curp = CURP(datos.curp)

        # Regla de idempotencia: si el CURP ya existe, se ignora el alta
        # entrante y se devuelve el paciente existente sin modificarlo.
        paciente_existente = await self._paciente_repository.buscar_por_curp(curp)
        if paciente_existente is not None:
            return self._a_dto(paciente_existente, fue_creado_ahora=False)

        nuevo_paciente = Paciente(
            curp=curp,
            nombre_completo=datos.nombre_completo,
            fecha_nacimiento=datos.fecha_nacimiento,
            sexo=datos.sexo,
            ubicacion=Ubicacion(comunidad=datos.comunidad, municipio=datos.municipio),
            lengua_materna=datos.lengua_materna,
            contacto_emergencia=datos.contacto_emergencia,
            device_generated_id=datos.device_generated_id,
        )

        paciente_guardado = await self._paciente_repository.guardar(nuevo_paciente)
        return self._a_dto(paciente_guardado, fue_creado_ahora=True)

    @staticmethod
    def _a_dto(paciente: Paciente, fue_creado_ahora: bool) -> PacienteOutputDTO:
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
            fue_creado_ahora=fue_creado_ahora,
        )
