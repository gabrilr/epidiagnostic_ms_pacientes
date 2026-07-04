"""
Caso de uso: UpgradePlanUseCase

Cambia el plan (tipo) del personal autenticado tras un pago. Por ahora
no hay integración real con Stripe: el cambio se aplica directamente
cuando se invoca este caso de uso. Cuando se agregue el webhook de
Stripe, será ese webhook el que dispare este mismo caso de uso en vez
de que el cliente lo llame directo.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from jose import jwt

from app.application.use_cases.login_personal import TokenOutputDTO
from app.domain.entities.personal_medico import TipoPersonal
from app.domain.exceptions.domain_exceptions import PersonalNoEncontradoException
from app.domain.repositories.personal_repository import PersonalRepository
from app.infrastructure.config.settings import get_settings

settings = get_settings()


class UpgradePlanUseCase:

    def __init__(self, personal_repository: PersonalRepository):
        self._personal_repository = personal_repository

    async def ejecutar(
        self, personal_id: UUID, nuevo_tipo: TipoPersonal, cedula_verificada: bool
    ) -> TokenOutputDTO:
        personal = await self._personal_repository.buscar_por_id(personal_id)
        if personal is None:
            raise PersonalNoEncontradoException(str(personal_id))

        personal.actualizar_plan(nuevo_tipo, cedula_verificada)
        await self._personal_repository.actualizar_tipo(personal.id, personal.tipo)

        payload = {
            "sub": str(personal.id),
            "correo": personal.correo,
            "tipo": personal.tipo.value,
            "nombre_completo": personal.nombre_completo,
            "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes),
        }
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        return TokenOutputDTO(
            access_token=token,
            token_type="bearer",
            personal_id=str(personal.id),
            nombre_completo=personal.nombre_completo,
            tipo=personal.tipo.value,
            correo=personal.correo,
        )
