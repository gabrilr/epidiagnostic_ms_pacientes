"""
DTOs (Data Transfer Objects) de la capa de aplicación.

Estos objetos son el contrato entre los adaptadores de entrada (API REST)
y los casos de uso. Desacoplan el dominio de los modelos de Pydantic /
FastAPI: el dominio nunca conoce a Pydantic, y la API nunca manipula
entidades de dominio directamente.
"""
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class CrearPacienteInputDTO:
    """Entrada del caso de uso CrearPaciente. Viene del endpoint de alta individual o batch."""
    curp: str
    nombre_completo: str
    fecha_nacimiento: date
    sexo: str
    comunidad: str
    municipio: str
    lengua_materna: str | None = None
    contacto_emergencia: str | None = None
    device_generated_id: str | None = None


@dataclass
class PacienteOutputDTO:
    """Salida estándar para representar un paciente hacia afuera del dominio."""
    id: str
    curp: str
    nombre_completo: str
    fecha_nacimiento: date
    sexo: str
    comunidad: str
    municipio: str
    lengua_materna: str | None
    contacto_emergencia: str | None
    creado_en: datetime
    actualizado_en: datetime
    fue_creado_ahora: bool  # True si se creó en esta llamada, False si ya existía (idempotencia)


@dataclass
class SincronizarPacientesInputDTO:
    """Entrada del caso de uso de sincronización batch desde el celular."""
    dispositivo_id: str
    pacientes: list[CrearPacienteInputDTO]


@dataclass
class ResultadoSincronizacionDTO:
    """Resultado individual de cada paciente procesado en un batch de sync."""
    device_generated_id: str | None
    id_servidor: str
    curp: str
    estado: str  # "creado" | "ya_existente"
