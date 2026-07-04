"""
Adaptador de entrada: auth_router

Expone los endpoints de autenticación, cambio de plan y solicitud de
plan Premium para personal médico.
POST  /auth/login             -> devuelve JWT
PATCH /auth/upgrade-plan      -> sube de plan directo, devuelve JWT nuevo
POST  /auth/solicitar-premium -> solicita el plan Premium (requiere aprobación de un admin)
GET   /auth/mi-solicitud      -> consulta el estado de la solicitud más reciente

Nota sobre verificación de cédula: se evaluó exponer un proxy público
GET /auth/verificar-cedula contra la API de la SEP, pero la consulta
en vivo de la SEP ahora exige un token de sesión propio de su SPA más
un token de reCAPTCHA v3 generado en el navegador — no es replicable
desde un backend. Por eso la verificación de cédula es manual: el
personal manda su solicitud (POST /auth/solicitar-premium) y un admin
la aprueba o rechaza a mano tras verificarla por fuera (ver
admin_router.py).
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.solicitud_premium_dto import SolicitarPremiumInputDTO
from app.application.use_cases.login_personal import LoginPersonalUseCase
from app.application.use_cases.registrar_publico import RegistrarPublicoUseCase
from app.application.use_cases.solicitar_premium import (
    ConsultarMiSolicitudUseCase,
    SolicitarPremiumUseCase,
)
from app.application.use_cases.upgrade_plan import UpgradePlanUseCase
from app.domain.entities.personal_medico import TipoPersonal
from app.domain.exceptions.domain_exceptions import (
    CorreoDuplicadoException,
    PersonalNoEncontradoException,
    SolicitudPendienteExistenteException,
    SolicitudPremiumNoEncontradaException,
)
from app.infrastructure.adapters.input.api.auth_dependencies import (
    get_personal_id_actual,
    get_personal_id_elegible_para_premium,
)
from app.infrastructure.adapters.input.api.auth_schemas import (
    LoginRequest,
    MiSolicitudResponse,
    RegistroPublicoRequest,
    SolicitarPremiumRequest,
    SolicitarPremiumResponse,
    TokenResponse,
    UpgradePlanRequest,
)
from app.infrastructure.config.database import get_db_session
from app.infrastructure.dependency_injection import (
    get_consultar_mi_solicitud_use_case,
    get_solicitar_premium_use_case,
    get_upgrade_plan_use_case,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de personal médico. Devuelve JWT.",
)
async def login(
    request: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    try:
        use_case = LoginPersonalUseCase(session)
        resultado = await use_case.ejecutar(
            correo=request.correo,
            contrasena=request.contrasena,
        )
        return TokenResponse(**resultado.__dict__)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro público. Crea cuenta con tipo='usuario' y devuelve JWT.",
)
async def register(
    request: RegistroPublicoRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    try:
        use_case = RegistrarPublicoUseCase(session)
        resultado = await use_case.ejecutar(
            nombre_completo=request.nombre_completo,
            correo=str(request.correo),
            contrasena=request.contrasena,
        )
        return TokenResponse(**resultado.__dict__)
    except CorreoDuplicadoException as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.patch(
    "/upgrade-plan",
    response_model=TokenResponse,
    summary="Sube el plan del personal autenticado tras un pago. Devuelve un JWT nuevo.",
)
async def upgrade_plan(
    request: UpgradePlanRequest,
    personal_id: Annotated[UUID, Depends(get_personal_id_actual)],
    use_case: Annotated[UpgradePlanUseCase, Depends(get_upgrade_plan_use_case)],
) -> TokenResponse:
    try:
        resultado = await use_case.ejecutar(
            personal_id=personal_id,
            nuevo_tipo=TipoPersonal(request.nuevo_tipo),
            cedula_verificada=request.cedula_verificada,
        )
        return TokenResponse(**resultado.__dict__)
    except PersonalNoEncontradoException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post(
    "/solicitar-premium",
    response_model=SolicitarPremiumResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicita el upgrade a plan Premium. Un admin la revisa manualmente.",
)
async def solicitar_premium(
    request: SolicitarPremiumRequest,
    personal_id: Annotated[UUID, Depends(get_personal_id_elegible_para_premium)],
    use_case: Annotated[SolicitarPremiumUseCase, Depends(get_solicitar_premium_use_case)],
) -> SolicitarPremiumResponse:
    try:
        resultado = await use_case.ejecutar(
            SolicitarPremiumInputDTO(
                personal_id=str(personal_id),
                numero_cedula=request.numero_cedula,
                nombre_en_cedula=request.nombre_en_cedula,
                especialidad=request.especialidad,
            )
        )
    except SolicitudPendienteExistenteException as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))

    return SolicitarPremiumResponse(
        solicitud_id=resultado.id,
        estado=resultado.estado,
        mensaje="Tu solicitud fue enviada. Te notificaremos en menos de 48 horas.",
    )


@router.get(
    "/mi-solicitud",
    response_model=MiSolicitudResponse,
    summary="Consulta la solicitud Premium más reciente del personal autenticado.",
)
async def mi_solicitud(
    personal_id: Annotated[UUID, Depends(get_personal_id_actual)],
    use_case: Annotated[ConsultarMiSolicitudUseCase, Depends(get_consultar_mi_solicitud_use_case)],
) -> MiSolicitudResponse:
    try:
        resultado = await use_case.ejecutar(personal_id)
    except SolicitudPremiumNoEncontradaException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))

    return MiSolicitudResponse(
        solicitud_id=resultado.id,
        estado=resultado.estado,
        created_at=resultado.created_at,
        motivo_rechazo=resultado.motivo_rechazo,
    )
