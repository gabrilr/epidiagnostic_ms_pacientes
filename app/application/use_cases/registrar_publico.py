"""
Caso de uso: RegistrarPublicoUseCase

Crea una cuenta nueva con tipo='usuario' a partir de nombre, correo y
contraseña. No requiere autenticación. Devuelve JWT inmediatamente para
que el cliente quede logueado al terminar el registro.

'comunidad' y 'municipio' se almacenan como 'Sin especificar' porque la
tabla los exige NOT NULL pero el registro público no recoge esa info;
un admin puede actualizarla luego desde el panel.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.domain_exceptions import CorreoDuplicadoException
from app.infrastructure.adapters.output.persistence.models.personal_model import PersonalModel
from app.infrastructure.config.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


@dataclass
class TokenOutputDTO:
    access_token: str
    token_type: str
    personal_id: str
    nombre_completo: str
    tipo: str
    correo: str


class RegistrarPublicoUseCase:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def ejecutar(
        self,
        nombre_completo: str,
        correo: str,
        contrasena: str,
    ) -> TokenOutputDTO:
        resultado = await self._session.execute(
            select(PersonalModel).where(PersonalModel.correo == correo)
        )
        if resultado.scalar_one_or_none() is not None:
            raise CorreoDuplicadoException(correo)

        nuevo = PersonalModel(
            nombre_completo=nombre_completo,
            tipo="usuario",
            comunidad="Sin especificar",
            municipio="Sin especificar",
            correo=correo,
            contrasena_hash=pwd_context.hash(contrasena),
        )
        self._session.add(nuevo)
        await self._session.commit()
        await self._session.refresh(nuevo)

        payload = {
            "sub": str(nuevo.id),
            "correo": nuevo.correo,
            "tipo": nuevo.tipo,
            "nombre_completo": nuevo.nombre_completo,
            "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        return TokenOutputDTO(
            access_token=token,
            token_type="bearer",
            personal_id=str(nuevo.id),
            nombre_completo=nuevo.nombre_completo,
            tipo=nuevo.tipo,
            correo=nuevo.correo,
        )
