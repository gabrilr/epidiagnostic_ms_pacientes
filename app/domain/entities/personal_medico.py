"""
Entidad raíz de agregado: PersonalMedico

Representa al personal de salud (médicos y enfermeras) autorizado para
registrar atenciones. Es consultado por el microservicio 2 (Atención
Médica) para validar que quien registra una atención existe y está
activo.

Nota: la cédula profesional es opcional porque en comunidades rurales
de Chiapas puede haber personal de salud comunitario certificado pero
no titulado formalmente (ej. promotores de salud capacitados).
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
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    cedula_profesional: str | None = None
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre completo del personal médico no puede estar vacío.")

    def desactivar(self) -> None:
        self.activo = False

    def reactivar(self) -> None:
        self.activo = True
