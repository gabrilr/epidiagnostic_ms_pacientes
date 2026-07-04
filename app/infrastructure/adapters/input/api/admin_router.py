"""
Adaptador de entrada: admin_router

Endpoints de administración: gestión de solicitudes de plan Premium,
listado de usuarios y estadísticas. Todos requieren JWT con tipo='admin'.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.use_cases.admin_dashboard import EstadisticasUseCase, ListarUsuariosUseCase
from app.application.use_cases.gestionar_solicitudes_admin import (
    AprobarSolicitudUseCase,
    ListarSolicitudesUseCase,
    RechazarSolicitudUseCase,
)
from app.domain.entities.personal_medico import TipoPersonal
from app.domain.entities.solicitud_premium import EstadoSolicitud
from app.domain.exceptions.domain_exceptions import (
    PersonalNoEncontradoException,
    SolicitudPremiumNoEncontradaException,
)
from app.infrastructure.adapters.input.api.admin_schemas import (
    EstadisticasResponse,
    MensajeResponse,
    PersonalResumenSchema,
    RechazarSolicitudRequest,
    SolicitudAdminResponse,
    UsuarioAdminResponse,
)
from app.infrastructure.adapters.input.api.auth_dependencies import get_admin_id_actual
from app.infrastructure.dependency_injection import (
    get_aprobar_solicitud_use_case,
    get_estadisticas_use_case,
    get_listar_solicitudes_use_case,
    get_listar_usuarios_use_case,
    get_rechazar_solicitud_use_case,
)

router = APIRouter(prefix="/admin", tags=["Administración"])


@router.get(
    "/solicitudes",
    response_model=list[SolicitudAdminResponse],
    summary="Lista solicitudes de plan Premium, ordenadas por fecha descendente.",
)
async def listar_solicitudes(
    _admin_id: Annotated[UUID, Depends(get_admin_id_actual)],
    use_case: Annotated[ListarSolicitudesUseCase, Depends(get_listar_solicitudes_use_case)],
    estado: Annotated[str, Query(pattern="^(pendiente|aprobada|rechazada|all)$")] = "pendiente",
) -> list[SolicitudAdminResponse]:
    estado_filtro = None if estado == "all" else EstadoSolicitud(estado)
    resultados = await use_case.ejecutar(estado_filtro)
    return [
        SolicitudAdminResponse(
            solicitud_id=r.solicitud.id,
            estado=r.solicitud.estado,
            created_at=r.solicitud.created_at,
            numero_cedula=r.solicitud.numero_cedula,
            nombre_en_cedula=r.solicitud.nombre_en_cedula,
            especialidad=r.solicitud.especialidad,
            personal=PersonalResumenSchema(
                personal_id=r.personal.id,
                nombre_completo=r.personal.nombre_completo,
                correo=r.personal.correo,
                tipo=r.personal.tipo,
            ),
        )
        for r in resultados
    ]


@router.patch(
    "/solicitudes/{solicitud_id}/aprobar",
    response_model=MensajeResponse,
    summary="Aprueba una solicitud Premium y sube al solicitante a 'medico'.",
)
async def aprobar_solicitud(
    solicitud_id: UUID,
    admin_id: Annotated[UUID, Depends(get_admin_id_actual)],
    use_case: Annotated[AprobarSolicitudUseCase, Depends(get_aprobar_solicitud_use_case)],
) -> MensajeResponse:
    try:
        await use_case.ejecutar(solicitud_id, admin_id)
    except (SolicitudPremiumNoEncontradaException, PersonalNoEncontradoException) as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return MensajeResponse(mensaje="Solicitud aprobada. El usuario ahora tiene acceso Premium.")


@router.patch(
    "/solicitudes/{solicitud_id}/rechazar",
    response_model=MensajeResponse,
    summary="Rechaza una solicitud Premium.",
)
async def rechazar_solicitud(
    solicitud_id: UUID,
    request: RechazarSolicitudRequest,
    admin_id: Annotated[UUID, Depends(get_admin_id_actual)],
    use_case: Annotated[RechazarSolicitudUseCase, Depends(get_rechazar_solicitud_use_case)],
) -> MensajeResponse:
    try:
        await use_case.ejecutar(solicitud_id, admin_id, request.motivo_rechazo)
    except SolicitudPremiumNoEncontradaException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return MensajeResponse(mensaje="Solicitud rechazada.")


@router.get(
    "/usuarios",
    response_model=list[UsuarioAdminResponse],
    summary="Lista todos los usuarios, filtrables por tipo.",
)
async def listar_usuarios(
    _admin_id: Annotated[UUID, Depends(get_admin_id_actual)],
    use_case: Annotated[ListarUsuariosUseCase, Depends(get_listar_usuarios_use_case)],
    tipo: Annotated[str | None, Query(pattern="^(usuario|enfermera|medico|admin)$")] = None,
) -> list[UsuarioAdminResponse]:
    tipo_filtro = TipoPersonal(tipo) if tipo else None
    resultados = await use_case.ejecutar(tipo_filtro)
    return [
        UsuarioAdminResponse(
            personal_id=p.id,
            nombre_completo=p.nombre_completo,
            correo=p.correo,
            tipo=p.tipo,
            created_at=p.creado_en,
        )
        for p in resultados
    ]


@router.get(
    "/estadisticas",
    response_model=EstadisticasResponse,
    summary="Estadísticas agregadas del sistema.",
)
async def estadisticas(
    _admin_id: Annotated[UUID, Depends(get_admin_id_actual)],
    use_case: Annotated[EstadisticasUseCase, Depends(get_estadisticas_use_case)],
) -> EstadisticasResponse:
    resultado = await use_case.ejecutar()
    return EstadisticasResponse(
        total_usuarios=resultado.total_usuarios,
        por_rol=resultado.por_rol,
        solicitudes_pendientes=resultado.solicitudes_pendientes,
        solicitudes_aprobadas_hoy=resultado.solicitudes_aprobadas_hoy,
    )
