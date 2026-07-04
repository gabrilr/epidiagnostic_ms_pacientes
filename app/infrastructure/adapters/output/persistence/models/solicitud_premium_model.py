"""
Modelo SQLAlchemy: SolicitudPremiumModel
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.config.database import Base
from app.infrastructure.config.types import GUID


class SolicitudPremiumModel(Base):
    __tablename__ = "solicitudes_premium"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    personal_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("personal_medico.id"), nullable=False
    )
    numero_cedula: Mapped[str] = mapped_column(String(10), nullable=False)
    nombre_en_cedula: Mapped[str] = mapped_column(String(200), nullable=False)
    especialidad: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estado: Mapped[str] = mapped_column(
        SAEnum("pendiente", "aprobada", "rechazada", name="estado_solicitud"),
        default="pendiente",
        server_default="pendiente",
        nullable=False,
    )
    admin_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("personal_medico.id"), nullable=True
    )
    motivo_rechazo: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
