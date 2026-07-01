"""
Entidad raíz de agregado: Paciente

Es la raíz del agregado Paciente, que también incluye HistorialMedico
como entidad interna. Todo acceso al historial pasa por esta clase
(encapsulamiento del agregado): nadie fuera del dominio manipula
HistorialMedico directamente.

El CURP es la clave de negocio única (business key) del paciente, según
la decisión de diseño: todos los pacientes tienen CURP, y es el criterio
de idempotencia al sincronizar altas desde el celular offline-first.

El campo `id` es la clave primaria interna del microservicio (no
depende del UUID generado por el celular). El `device_generated_id` se
conserva solo como referencia de trazabilidad de qué dispositivo originó
el registro, pero NO es la clave de negocio.
"""
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

from app.domain.entities.antecedente_medico import AntecedenteMedico
from app.domain.entities.historial_medico import HistorialMedico
from app.domain.value_objects.curp import CURP
from app.domain.value_objects.ubicacion import Ubicacion


@dataclass
class Paciente:
    curp: CURP
    nombre_completo: str
    fecha_nacimiento: date
    sexo: str  # "H" o "M", coherente con el formato CURP
    ubicacion: Ubicacion
    lengua_materna: str | None
    contacto_emergencia: str | None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    device_generated_id: str | None = None  # trazabilidad, no es business key
    historial: HistorialMedico = field(default_factory=HistorialMedico)
    creado_en: datetime = field(default_factory=datetime.utcnow)
    actualizado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre completo del paciente no puede estar vacío.")
        if self.sexo not in ("H", "M"):
            raise ValueError("El sexo debe ser 'H' o 'M'.")
        if self.fecha_nacimiento > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura.")
        if self.contacto_emergencia is not None:
            if not self.contacto_emergencia.isdigit() or len(self.contacto_emergencia) != 10:
                raise ValueError("El contacto de emergencia debe ser un número de teléfono de 10 dígitos.")

    def agregar_antecedente(self, antecedente: AntecedenteMedico) -> None:
        """
        Punto único de entrada para anexar antecedentes al historial.
        Mantiene la regla del agregado: el historial solo se modifica
        a través de la raíz (Paciente), nunca directamente.
        """
        self.historial.agregar_antecedente(antecedente)
        self.actualizado_en = datetime.utcnow()

    def actualizar_datos_basicos(
        self,
        nombre_completo: str | None = None,
        ubicacion: Ubicacion | None = None,
        lengua_materna: str | None = None,
        contacto_emergencia: str | None = None,
    ) -> None:
        """
        Actualización explícita y consciente de datos básicos, según la
        decisión de diseño: las correcciones de datos NO se infieren
        automáticamente de un alta duplicada, sino que son un flujo
        separado y deliberado (PATCH /pacientes/{id}/datos).
        """
        if nombre_completo is not None:
            self.nombre_completo = nombre_completo
        if ubicacion is not None:
            self.ubicacion = ubicacion
        if lengua_materna is not None:
            self.lengua_materna = lengua_materna
        if contacto_emergencia is not None:
            if not contacto_emergencia.isdigit() or len(contacto_emergencia) != 10:
                raise ValueError("El contacto de emergencia debe ser un número de teléfono de 10 dígitos.")
            self.contacto_emergencia = contacto_emergencia
        self.actualizado_en = datetime.utcnow()
