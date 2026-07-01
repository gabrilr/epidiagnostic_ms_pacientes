"""
Modelo SQLAlchemy: PersonalModel

Tabla que persiste el personal médico (médicos y enfermeras).
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.config.database import Base
from app.infrastructure.config.types import GUID


class PersonalModel(Base):
    __tablename__ = "personal_medico"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    nombre_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)          # "medico" | "enfermera"
    comunidad: Mapped[str] = mapped_column(String(255), nullable=False)
    municipio: Mapped[str] = mapped_column(String(255), nullable=False)
    cedula_profesional: Mapped[str | None] = mapped_column(String(50), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
