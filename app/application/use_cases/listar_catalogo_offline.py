"""
Caso de uso: ListarCatalogoOffline

Implementa el endpoint GET /pacientes/catalogo?desde=...&comunidad=...,
que la app móvil offline-first llama cada vez que tiene señal para
mantener actualizado su catálogo local de pacientes (sync incremental,
no el catálogo completo en cada llamada).
"""
from datetime import datetime

from app.application.dtos.paciente_dto import PacienteOutputDTO
from app.domain.entities.paciente import Paciente
from app.domain.repositories.paciente_repository import PacienteRepository

# Si el celular nunca ha sincronizado (primera vez), no manda `desde`;
# se interpreta como "todo el catálogo" usando esta fecha piso en vez de
# datetime.min, que MySQL no acepta como DATETIME válido.
_DESDE_POR_DEFECTO = datetime(2000, 1, 1)


class ListarCatalogoOfflineUseCase:

    def __init__(self, paciente_repository: PacienteRepository):
        self._paciente_repository = paciente_repository

    async def ejecutar(
        self, desde: datetime | None = None, comunidad: str | None = None
    ) -> list[PacienteOutputDTO]:
        pacientes = await self._paciente_repository.listar_actualizados_desde(
            desde or _DESDE_POR_DEFECTO, comunidad
        )
        return [self._a_dto(p) for p in pacientes]

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
