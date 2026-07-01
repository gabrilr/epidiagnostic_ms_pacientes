"""
Modelo SQLAlchemy: AntecedenteModel

Tabla que persiste los antecedentes médicos (historial), relacionados
1-a-muchos con PacienteModel.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.config.database import Base
from app.infrastructure.config.types import GUID


class AntecedenteModel(Base):
    __tablename__ = "antecedentes_medicos"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    paciente_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("pacientes.id"), nullable=False, index=True
    )
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    origen_atencion_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    paciente: Mapped["PacienteModel"] = relationship(back_populates="antecedentes")
