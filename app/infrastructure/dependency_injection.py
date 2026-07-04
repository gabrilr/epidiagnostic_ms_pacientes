"""
Inyección de dependencias.

Este módulo es el único lugar del sistema donde se conectan los puertos
(interfaces de dominio) con sus implementaciones concretas
(adaptadores de infraestructura).
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.admin_dashboard import EstadisticasUseCase, ListarUsuariosUseCase
from app.application.use_cases.consultar_paciente import ConsultarPacienteUseCase
from app.application.use_cases.crear_paciente import CrearPacienteUseCase
from app.application.use_cases.gestionar_solicitudes_admin import (
    AprobarSolicitudUseCase,
    ListarSolicitudesUseCase,
    RechazarSolicitudUseCase,
)
from app.application.use_cases.sincronizar_pacientes_batch import SincronizarPacientesBatchUseCase
from app.application.use_cases.registrar_personal import (
    ConsultarPersonalUseCase,
    RegistrarPersonalUseCase,
)
from app.application.use_cases.solicitar_premium import (
    ConsultarMiSolicitudUseCase,
    SolicitarPremiumUseCase,
)
from app.application.use_cases.upgrade_plan import UpgradePlanUseCase
from app.domain.repositories.paciente_repository import PacienteRepository
from app.domain.repositories.personal_repository import PersonalRepository
from app.domain.repositories.solicitud_premium_repository import SolicitudPremiumRepository
from app.infrastructure.adapters.output.persistence.paciente_repository_impl import PacienteRepositoryImpl
from app.infrastructure.adapters.output.persistence.personal_repository_impl import PersonalRepositoryImpl
from app.infrastructure.adapters.output.persistence.solicitud_premium_repository_impl import (
    SolicitudPremiumRepositoryImpl,
)
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


# ── Personal Médico ────────────────────────────────────────────────────────

def get_personal_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PersonalRepository:
    return PersonalRepositoryImpl(session)


def get_registrar_personal_use_case(
    repository: Annotated[PersonalRepository, Depends(get_personal_repository)],
) -> RegistrarPersonalUseCase:
    return RegistrarPersonalUseCase(repository)


def get_consultar_personal_use_case(
    repository: Annotated[PersonalRepository, Depends(get_personal_repository)],
) -> ConsultarPersonalUseCase:
    return ConsultarPersonalUseCase(repository)


def get_upgrade_plan_use_case(
    repository: Annotated[PersonalRepository, Depends(get_personal_repository)],
) -> UpgradePlanUseCase:
    return UpgradePlanUseCase(repository)


# ── Solicitudes Premium ────────────────────────────────────────────────────

def get_solicitud_premium_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SolicitudPremiumRepository:
    return SolicitudPremiumRepositoryImpl(session)


def get_solicitar_premium_use_case(
    repository: Annotated[SolicitudPremiumRepository, Depends(get_solicitud_premium_repository)],
) -> SolicitarPremiumUseCase:
    return SolicitarPremiumUseCase(repository)


def get_consultar_mi_solicitud_use_case(
    repository: Annotated[SolicitudPremiumRepository, Depends(get_solicitud_premium_repository)],
) -> ConsultarMiSolicitudUseCase:
    return ConsultarMiSolicitudUseCase(repository)


def get_listar_solicitudes_use_case(
    solicitud_repository: Annotated[
        SolicitudPremiumRepository, Depends(get_solicitud_premium_repository)
    ],
    personal_repository: Annotated[PersonalRepository, Depends(get_personal_repository)],
) -> ListarSolicitudesUseCase:
    return ListarSolicitudesUseCase(solicitud_repository, personal_repository)


def get_aprobar_solicitud_use_case(
    solicitud_repository: Annotated[
        SolicitudPremiumRepository, Depends(get_solicitud_premium_repository)
    ],
    upgrade_plan_use_case: Annotated[UpgradePlanUseCase, Depends(get_upgrade_plan_use_case)],
) -> AprobarSolicitudUseCase:
    return AprobarSolicitudUseCase(solicitud_repository, upgrade_plan_use_case)


def get_rechazar_solicitud_use_case(
    repository: Annotated[SolicitudPremiumRepository, Depends(get_solicitud_premium_repository)],
) -> RechazarSolicitudUseCase:
    return RechazarSolicitudUseCase(repository)


# ── Panel de administración ────────────────────────────────────────────────

def get_listar_usuarios_use_case(
    repository: Annotated[PersonalRepository, Depends(get_personal_repository)],
) -> ListarUsuariosUseCase:
    return ListarUsuariosUseCase(repository)


def get_estadisticas_use_case(
    personal_repository: Annotated[PersonalRepository, Depends(get_personal_repository)],
    solicitud_repository: Annotated[
        SolicitudPremiumRepository, Depends(get_solicitud_premium_repository)
    ],
) -> EstadisticasUseCase:
    return EstadisticasUseCase(personal_repository, solicitud_repository)
