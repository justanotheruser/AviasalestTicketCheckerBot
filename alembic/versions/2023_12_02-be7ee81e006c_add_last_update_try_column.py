"""Add last_update_try column

Revision ID: be7ee81e006c
Revises: 35c6bd819b9f
Create Date: 2023-12-02 22:12:22.849299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be7ee81e006c'
down_revision = '35c6bd819b9f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('flight_directions', sa.Column('last_update_try', sa.DateTime(), nullable=False))
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE flight_directions SET last_update_try=last_update"))


def downgrade() -> None:
    op.drop_column('flight_directions', 'last_update_try')
