"""
Schemas Pydantic: contrato HTTP del API de pacientes.

Estos modelos son específicos de la capa de infraestructura (adaptador
de entrada FastAPI). NO se reutilizan en el dominio ni en la aplicación
— ahí se usan los DTOs (dataclasses) definidos en application/dtos/.
Esta separación permite que el contrato HTTP evolucione (versionado de
API, por ejemplo) sin tocar la lógica de negocio.
"""
from datetime import date, datetime

from pydantic import BaseModel, Field


class CrearPacienteRequest(BaseModel):
    curp: str = Field(..., min_length=18, max_length=18, examples=["GOMC900101HCSNZL09"])
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    fecha_nacimiento: date
    sexo: str = Field(..., pattern="^[HM]$")
    comunidad: str = Field(..., min_length=1, max_length=255)
    municipio: str = Field(..., min_length=1, max_length=255)
    lengua_materna: str | None = None
    contacto_emergencia: str | None = None
    device_generated_id: str | None = Field(
        default=None,
        description="UUID generado por el celular en modo offline-first, usado solo para trazabilidad.",
    )


class PacienteResponse(BaseModel):
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
    edad: int
    fue_creado_ahora: bool = Field(
        description="False si el CURP ya existía y se devolvió el paciente existente sin crear uno nuevo."
    )


class SincronizarPacientesRequest(BaseModel):
    dispositivo_id: str
    pacientes: list[CrearPacienteRequest]


class ResultadoSincronizacionResponse(BaseModel):
    device_generated_id: str | None
    id_servidor: str
    curp: str
    estado: str


class SincronizarPacientesResponse(BaseModel):
    resultados: list[ResultadoSincronizacionResponse]


class AgregarAntecedenteRequest(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=1000)
    tipo: str = Field(..., pattern="^(alergia|enfermedad_cronica|embarazo_previo|cirugia|otro)$")
    origen_atencion_id: str | None = Field(
        default=None,
        description="ID de la atención (MS2) que generó este antecedente, si aplica.",
    )


class ActualizarDatosPacienteRequest(BaseModel):
    """Todos los campos son opcionales: PATCH parcial, solo se actualiza lo que venga."""
    nombre_completo: str | None = Field(default=None, min_length=1, max_length=255)
    comunidad: str | None = Field(default=None, min_length=1, max_length=255)
    municipio: str | None = Field(default=None, min_length=1, max_length=255)
    lengua_materna: str | None = None
    contacto_emergencia: str | None = None
