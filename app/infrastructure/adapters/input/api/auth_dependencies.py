"""
Dependencias compartidas de autenticación y autorización.

Validan el JWT Bearer emitido por /auth/login (o /auth/upgrade-plan) y
exponen distintas variantes según qué rol necesita cada endpoint:
- get_personal_id_actual: cualquier tipo autenticado.
- get_admin_id_actual: solo tipo='admin'.
- get_personal_id_elegible_para_premium: cualquier tipo excepto
  'medico' (ya tiene el plan) y 'admin' (no aplica).
"""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.domain.entities.personal_medico import TipoPersonal
from app.infrastructure.config.settings import get_settings

settings = get_settings()
_bearer_scheme = HTTPBearer()


def _credenciales_invalidas() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decodificar_token(credentials: HTTPAuthorizationCredentials) -> tuple[UUID, str]:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return UUID(payload["sub"]), payload["tipo"]
    except (JWTError, KeyError, ValueError):
        raise _credenciales_invalidas()


async def get_personal_id_actual(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UUID:
    personal_id, _tipo = _decodificar_token(credentials)
    return personal_id


async def get_admin_id_actual(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UUID:
    admin_id, tipo = _decodificar_token(credentials)
    if tipo != TipoPersonal.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador.",
        )
    return admin_id


async def get_personal_id_elegible_para_premium(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UUID:
    personal_id, tipo = _decodificar_token(credentials)
    if tipo in (TipoPersonal.MEDICO.value, TipoPersonal.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta no puede solicitar el plan Premium.",
        )
    return personal_id
