"""
Entidad raíz de agregado: PersonalMedico
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.domain.value_objects.ubicacion import Ubicacion


class TipoPersonal(str, Enum):
    USUARIO = "usuario"
    ENFERMERA = "enfermera"
    MEDICO = "medico"
    ADMIN = "admin"


# Orden de planes de menor a mayor, usado para validar que un cambio de
# plan (tras un pago) sea siempre una subida, nunca una baja ni un
# lateral. Ver PersonalMedico.actualizar_plan. ADMIN no es un plan
# pagado, pero se incluye con el rango más alto para que el método no
# reviente con KeyError si alguna vez se invoca sobre una cuenta admin.
_RANGO_PLAN = {
    TipoPersonal.USUARIO: 0,
    TipoPersonal.ENFERMERA: 1,
    TipoPersonal.MEDICO: 2,
    TipoPersonal.ADMIN: 3,
}


@dataclass
class PersonalMedico:
    nombre_completo: str
    tipo: TipoPersonal
    ubicacion_asignada: Ubicacion
    correo: str
    contrasena_hash: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    cedula_profesional: str | None = None
    activo: bool = True
    creado_en: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre completo del personal médico no puede estar vacío.")
        if not self.correo or "@" not in self.correo:
            raise ValueError("El correo electrónico no es válido.")

    def desactivar(self) -> None:
        self.activo = False

    def reactivar(self) -> None:
        self.activo = True

    def actualizar_plan(self, nuevo_tipo: "TipoPersonal", cedula_verificada: bool) -> None:
        """
        Cambia el plan (tipo) tras un pago. Solo permite subir de plan
        (usuario < enfermera < medico), nunca bajar ni quedarse igual.
        Subir a "medico" exige cedula_verificada=True (hoy la
        verificación de cédula es manual, ver SolicitudPremium).
        """
        if _RANGO_PLAN[nuevo_tipo] <= _RANGO_PLAN[self.tipo]:
            raise ValueError("No puedes bajar de plan.")
        if nuevo_tipo == TipoPersonal.MEDICO and not cedula_verificada:
            raise ValueError("Se requiere verificación de cédula para el plan Premium")
        self.tipo = nuevo_tipo
