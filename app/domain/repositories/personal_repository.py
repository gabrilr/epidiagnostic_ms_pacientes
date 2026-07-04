"""
Puerto de salida: PersonalRepository

Contrato de persistencia para el agregado PersonalMedico. Igual que
PacienteRepository, es una interfaz abstracta que el dominio define y
la infraestructura implementa.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.personal_medico import PersonalMedico, TipoPersonal


class PersonalRepository(ABC):

    @abstractmethod
    async def guardar(self, personal: PersonalMedico) -> PersonalMedico:
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_id(self, personal_id: UUID) -> PersonalMedico | None:
        raise NotImplementedError

    @abstractmethod
    async def listar_todos(self, solo_activos: bool = True) -> list[PersonalMedico]:
        raise NotImplementedError

    @abstractmethod
    async def actualizar_tipo(self, personal_id: UUID, nuevo_tipo: TipoPersonal) -> None:
        raise NotImplementedError
