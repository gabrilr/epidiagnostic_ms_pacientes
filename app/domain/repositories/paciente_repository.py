"""
Puerto de salida: PacienteRepository

Define el contrato que el dominio espera para persistir y consultar
pacientes, sin saber NADA sobre la tecnología de persistencia real
(MySQL, SQLAlchemy, etc.). La implementación concreta vive en
infrastructure/adapters/output/persistence/.

Esta es la esencia de la arquitectura hexagonal: el dominio define el
puerto, la infraestructura lo implementa, y la dependencia apunta hacia
adentro (infraestructura depende del dominio, nunca al revés).
"""
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.paciente import Paciente
from app.domain.value_objects.curp import CURP


class PacienteRepository(ABC):

    @abstractmethod
    async def guardar(self, paciente: Paciente) -> Paciente:
        """Persiste un paciente nuevo. Devuelve la entidad persistida."""
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_id(self, paciente_id: UUID) -> Paciente | None:
        """Busca un paciente por su ID interno (clave primaria del microservicio)."""
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_curp(self, curp: CURP) -> Paciente | None:
        """
        Busca un paciente por CURP. Es el método clave para la lógica de
        idempotencia en altas: si existe, el alta entrante se ignora
        silenciosamente y se devuelve este paciente (regla de negocio
        confirmada en el diseño).
        """
        raise NotImplementedError

    @abstractmethod
    async def actualizar(self, paciente: Paciente) -> Paciente:
        """Persiste cambios sobre un paciente existente (ej. nuevo antecedente, datos corregidos)."""
        raise NotImplementedError

    @abstractmethod
    async def listar_actualizados_desde(
        self, desde: datetime, comunidad: str | None = None
    ) -> list[Paciente]:
        """
        Soporta el flujo de descarga incremental del catálogo offline
        (GET /pacientes/catalogo?desde=...). Filtra opcionalmente por
        comunidad para no sobrecargar el celular con datos irrelevantes.
        """
        raise NotImplementedError
