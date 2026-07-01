"""
DTOs de la capa de aplicación para personal médico.
"""
from dataclasses import dataclass
from datetime import datetime


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
