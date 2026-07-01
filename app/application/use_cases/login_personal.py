"""
Caso de uso: LoginPersonalUseCase

Verifica credenciales (correo + contraseña) del personal médico y
devuelve un token JWT si son correctas. El token incluye en su payload
el id, correo y tipo del personal, para que otros microservicios puedan
identificar quién está haciendo la petición sin consultar la base de
datos en cada request.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


class LoginPersonalUseCase:

    def __init__(self, session: AsyncSession):
        # Accede directamente a la sesión en vez de ir por el repositorio
        # porque necesita buscar por correo, que no está definido en el
        # puerto PersonalRepository (que solo tiene buscar_por_id).
        # Alternativa más limpia a futuro: agregar buscar_por_correo() al
        # puerto y su implementación, pero para el login es aceptable este
        # acceso directo ya que es un caso de uso de infraestructura pura.
        self._session = session

    async def ejecutar(self, correo: str, contrasena: str) -> TokenOutputDTO:
        resultado = await self._session.execute(
            select(PersonalModel).where(PersonalModel.correo == correo)
        )
        personal = resultado.scalar_one_or_none()

        if personal is None or not pwd_context.verify(contrasena, personal.contrasena_hash):
            raise ValueError("Correo o contraseña incorrectos.")

        if not personal.activo:
            raise ValueError("El usuario está inactivo. Contacta al administrador.")

        payload = {
            "sub": str(personal.id),
            "correo": personal.correo,
            "tipo": personal.tipo,
            "nombre_completo": personal.nombre_completo,
            "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        return TokenOutputDTO(
            access_token=token,
            token_type="bearer",
            personal_id=str(personal.id),
            nombre_completo=personal.nombre_completo,
            tipo=personal.tipo,
            correo=personal.correo,
        )
