"""
Schemas Pydantic para el API de personal médico.

La validación de contraseña == confirmar_contraseña vive aquí,
en la capa de entrada, porque es una regla de presentación/API
(confirmar que el usuario no cometió un error al escribir), no
una regla de negocio del dominio. El hash se genera en el caso
de uso, nunca en el schema ni en la base de datos.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator


class RegistrarPersonalRequest(BaseModel):
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    tipo: str = Field(..., pattern="^(medico|enfermera)$")
    comunidad: str = Field(..., min_length=1, max_length=255)
    municipio: str = Field(..., min_length=1, max_length=255)
    correo: EmailStr
    contrasena: str = Field(..., min_length=8, description="Mínimo 8 caracteres.")
    confirmar_contrasena: str = Field(..., min_length=8)
    cedula_profesional: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validar_contrasenas_coinciden(self) -> "RegistrarPersonalRequest":
        if self.contrasena != self.confirmar_contrasena:
            raise ValueError("Las contraseñas no coinciden.")
        return self


class PersonalResponse(BaseModel):
    id: str
    nombre_completo: str
    tipo: str
    comunidad: str
    municipio: str
    correo: str
    cedula_profesional: str | None
    activo: bool
    creado_en: datetime
    # confirmar_contrasena y contrasena nunca aparecen en la respuesta
