"""
Schemas Pydantic para autenticación.
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    personal_id: str
    nombre_completo: str
    tipo: str
    correo: str
