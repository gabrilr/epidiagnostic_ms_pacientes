"""
Modelo SQLAlchemy: PacienteModel

Este es el modelo de PERSISTENCIA (tabla real en MySQL), distinto de
la entidad de dominio Paciente. Mantenerlos separados es clave en
arquitectura hexagonal: el dominio no debe saber que existe SQLAlchemy,
y el modelo ORM no debe tener lógica de negocio.

La traducción entre ambos ocurre en el repositorio
(paciente_repository_impl.py), nunca aquí ni en el dominio.
"""
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.config.database import Base
from app.infrastructure.config.types import GUID


class PacienteModel(Base):
    __tablename__ = "pacientes"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    curp: Mapped[str] = mapped_column(String(18), unique=True, nullable=False, index=True)
    nombre_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[str] = mapped_column(String(1), nullable=False)
    comunidad: Mapped[str] = mapped_column(String(255), nullable=False)
    municipio: Mapped[str] = mapped_column(String(255), nullable=False)
    lengua_materna: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contacto_emergencia: Mapped[str | None] = mapped_column(String(255), nullable=True)
    device_generated_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    antecedentes: Mapped[list["AntecedenteModel"]] = relationship(
        back_populates="paciente", cascade="all, delete-orphan", lazy="selectin"
    )


# Import al final para evitar import circular entre modelos relacionados.
from app.infrastructure.adapters.output.persistence.models.antecedente_model import AntecedenteModel  # noqa: E402
