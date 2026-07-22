"""
Inyección de dependencias.

Este módulo es el único lugar del sistema donde se conectan los puertos
(interfaces de dominio) con sus implementaciones concretas
(adaptadores de infraestructura).
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.actualizar_datos_paciente import ActualizarDatosPacienteUseCase
from app.application.use_cases.agregar_antecedente_historial import AgregarAntecedenteHistorialUseCase
from app.application.use_cases.consultar_paciente import ConsultarPacienteUseCase
from app.application.use_cases.crear_paciente import CrearPacienteUseCase
from app.application.use_cases.listar_catalogo_offline import ListarCatalogoOfflineUseCase
from app.application.use_cases.sincronizar_pacientes_batch import SincronizarPacientesBatchUseCase
from app.domain.repositories.paciente_repository import PacienteRepository
from app.infrastructure.adapters.output.persistence.paciente_repository_impl import PacienteRepositoryImpl
from app.infrastructure.config.database import get_db_session


# ── Pacientes ──────────────────────────────────────────────────────────────

def get_paciente_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PacienteRepository:
    return PacienteRepositoryImpl(session)


def get_crear_paciente_use_case(
    repository: Annotated[PacienteRepository, Depends(get_paciente_repository)],
) -> CrearPacienteUseCase:
    return CrearPacienteUseCase(repository)


def get_consultar_paciente_use_case(
    repository: Annotated[PacienteRepository, Depends(get_paciente_repository)],
) -> ConsultarPacienteUseCase:
    return ConsultarPacienteUseCase(repository)


def get_sincronizar_pacientes_batch_use_case(
    crear_paciente_use_case: Annotated[CrearPacienteUseCase, Depends(get_crear_paciente_use_case)],
) -> SincronizarPacientesBatchUseCase:
    return SincronizarPacientesBatchUseCase(crear_paciente_use_case)


def get_listar_catalogo_offline_use_case(
    repository: Annotated[PacienteRepository, Depends(get_paciente_repository)],
) -> ListarCatalogoOfflineUseCase:
    return ListarCatalogoOfflineUseCase(repository)


def get_agregar_antecedente_historial_use_case(
    repository: Annotated[PacienteRepository, Depends(get_paciente_repository)],
) -> AgregarAntecedenteHistorialUseCase:
    return AgregarAntecedenteHistorialUseCase(repository)


def get_actualizar_datos_paciente_use_case(
    repository: Annotated[PacienteRepository, Depends(get_paciente_repository)],
) -> ActualizarDatosPacienteUseCase:
    return ActualizarDatosPacienteUseCase(repository)
