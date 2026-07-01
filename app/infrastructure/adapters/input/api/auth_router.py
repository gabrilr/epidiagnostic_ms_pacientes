"""
Adaptador de entrada: auth_router

Expone el endpoint de login para personal médico.
POST /auth/login -> devuelve JWT
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.login_personal import LoginPersonalUseCase
from app.infrastructure.adapters.input.api.auth_schemas import LoginRequest, TokenResponse
from app.infrastructure.config.database import get_db_session

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
