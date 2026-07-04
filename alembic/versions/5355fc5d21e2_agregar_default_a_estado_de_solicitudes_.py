"""agregar default a estado de solicitudes_premium

Revision ID: 5355fc5d21e2
Revises: 133ab7bc9611
Create Date: 2026-07-03 05:09:45.052428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5355fc5d21e2'
down_revision: Union[str, Sequence[str], None] = '133ab7bc9611'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # No detectado por --autogenerate (compare_server_default no está
    # habilitado en env.py); escrito a mano.
    op.alter_column(
        "solicitudes_premium",
        "estado",
        existing_type=sa.Enum("pendiente", "aprobada", "rechazada", name="estado_solicitud"),
        server_default="pendiente",
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "solicitudes_premium",
        "estado",
        existing_type=sa.Enum("pendiente", "aprobada", "rechazada", name="estado_solicitud"),
        server_default=None,
        existing_nullable=False,
    )
