"""
Value Object: Ubicacion

En el contexto de comunidades rurales de Chiapas, la geografía relevante
para la atención médica es la comunidad/localidad y el municipio, no una
dirección postal tradicional (que muchas veces no existe formalmente).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Ubicacion:
    comunidad: str
    municipio: str

    def __post_init__(self) -> None:
        if not self.comunidad or not self.comunidad.strip():
            raise ValueError("La comunidad no puede estar vacía.")
        if not self.municipio or not self.municipio.strip():
            raise ValueError("El municipio no puede estar vacío.")

    def __str__(self) -> str:
        return f"{self.comunidad}, {self.municipio}"
