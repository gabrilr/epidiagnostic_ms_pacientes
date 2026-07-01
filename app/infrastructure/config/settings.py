"""
Settings del microservicio, cargadas desde variables de entorno (.env).

Usa pydantic-settings para validación automática de tipos y para que
falle rápido al arrancar si falta una variable de entorno crítica, en
lugar de fallar silenciosamente más adelante.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "EpiDiagnostic-Maya · Microservicio de Pacientes y Personal"
    environment: str = "development"

    database_url: str = "mysql+aiomysql://root:root@db:3306/pacientes_db"
    db_echo: bool = False

    # TODO: agregar configuración de timeouts cuando se implemente la
    # comunicación saliente hacia otros microservicios (aplica más al
    # microservicio 2, que consulta a este, pero si este microservicio
    # llega a consumir algo de otro servicio en el futuro, definir aquí
    # http_client_timeout_seconds, etc.)


@lru_cache
def get_settings() -> Settings:
    """
    Cacheado con lru_cache para no releer el .env en cada request;
    Settings se instancia una sola vez por proceso.
    """
    return Settings()
