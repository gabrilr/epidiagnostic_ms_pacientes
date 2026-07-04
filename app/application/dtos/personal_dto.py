"""
DTOs de la capa de aplicación para personal médico.
"""
from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.personal_medico import PersonalMedico


@dataclass
class RegistrarPersonalInputDTO:
    nombre_completo: str
    tipo: str
    comunidad: str
    municipio: str
    correo: str
    contrasena: str                     # texto plano; el caso de uso la hashea antes de persistir
    cedula_profesional: str | None = None


@dataclass
class PersonalOutputDTO:
    id: str
    nombre_completo: str
    tipo: str
    comunidad: str
    municipio: str
    correo: str
    cedula_profesional: str | None
    activo: bool
    creado_en: datetime
    # contrasena_hash nunca se expone hacia afuera


def personal_a_dto(personal: PersonalMedico) -> PersonalOutputDTO:
    return PersonalOutputDTO(
        id=str(personal.id),
        nombre_completo=personal.nombre_completo,
        tipo=personal.tipo.value,
        comunidad=personal.ubicacion_asignada.comunidad,
        municipio=personal.ubicacion_asignada.municipio,
        correo=personal.correo,
        cedula_profesional=personal.cedula_profesional,
        activo=personal.activo,
        creado_en=personal.creado_en,
    )
