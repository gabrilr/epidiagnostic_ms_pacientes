"""
Dependencia de autenticación (solo verificación).

Este microservicio no emite JWT — el login vive en ms-personal (MS3).
Aquí solo se DECODIFICA el mismo token con la misma llave compartida
(JWT_SECRET_KEY/JWT_ALGORITHM, debe coincidir exactamente con la de
ms-personal), de forma stateless: sin llamar de vuelta a ms-personal
para validar el token en cada request.
"""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.infrastructure.config.settings import get_settings

settings = get_settings()
_bearer_scheme = HTTPBearer()


def _credenciales_invalidas() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_personal_id_actual(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UUID:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise _credenciales_invalidas()
