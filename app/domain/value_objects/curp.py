"""
Value Object: CURP

Encapsula la validación y el formato del CURP, que en este microservicio
es la clave de negocio (business key) para identificar pacientes de forma
única, según la decisión de diseño: "partimos de que todos tienen CURP".

Al ser un Value Object es inmutable y se compara por valor, no por
identidad. Dos CURP con el mismo string son el mismo CURP.
"""
import re
from dataclasses import dataclass

CURP_REGEX = re.compile(
    r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$"
)


@dataclass(frozen=True)
class CURP:
    valor: str

    def __post_init__(self) -> None:
        valor_normalizado = self.valor.strip().upper()
        if not CURP_REGEX.match(valor_normalizado):
            raise ValueError(
                f"CURP inválido: '{self.valor}'. Debe seguir el formato "
                f"oficial de 18 caracteres (ej. GOMC900101HCSNZL09)."
            )
        # dataclass frozen no permite asignación directa, usamos object.__setattr__
        object.__setattr__(self, "valor", valor_normalizado)

    def __str__(self) -> str:
        return self.valor
