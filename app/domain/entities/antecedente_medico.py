"""
Entidad: AntecedenteMedico

Representa un elemento individual del historial médico de un paciente
(ej. una alergia, una enfermedad crónica diagnosticada, un antecedente
de embarazo). Es una entidad interna del agregado Paciente: no tiene
sentido de negocio fuera de un paciente, y no se accede directamente
desde fuera del agregado (se accede siempre a través de Paciente).
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TipoAntecedente(str, Enum):
    ALERGIA = "alergia"
    ENFERMEDAD_CRONICA = "enfermedad_cronica"
    EMBARAZO_PREVIO = "embarazo_previo"
    CIRUGIA = "cirugia"
    OTRO = "otro"


@dataclass
class AntecedenteMedico:
    descripcion: str
    tipo: TipoAntecedente
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    fecha_registro: datetime = field(default_factory=datetime.utcnow)
    origen_atencion_id: str | None = None  # referencia opcional a la atención que lo generó (microservicio 2)

    def __post_init__(self) -> None:
        if not self.descripcion or not self.descripcion.strip():
            raise ValueError("La descripción del antecedente no puede estar vacía.")
