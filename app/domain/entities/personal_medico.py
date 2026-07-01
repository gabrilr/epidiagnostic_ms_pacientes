"""
Entidad raíz de agregado: PersonalMedico
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.domain.value_objects.ubicacion import Ubicacion


class TipoPersonal(str, Enum):
    MEDICO = "medico"
    ENFERMERA = "enfermera"


@dataclass
class PersonalMedico:
    nombre_completo: str
    tipo: TipoPersonal
    ubicacion_asignada: Ubicacion
    correo: str
    contrasena_hash: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    cedula_profesional: str | None = None
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre completo del personal médico no puede estar vacío.")
        if not self.correo or "@" not in self.correo:
            raise ValueError("El correo electrónico no es válido.")

    def desactivar(self) -> None:
        self.activo = False

    def reactivar(self) -> None:
        self.activo = True
