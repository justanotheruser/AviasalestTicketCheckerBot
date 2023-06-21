"""Init

Revision ID: 81984bb2b857
Revises: 
Create Date: 2023-06-21 17:33:23.654265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81984bb2b857'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('flight_direction',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('start_code', sa.String(length=3), nullable=False),
    sa.Column('start_name', sa.Text(), nullable=False),
    sa.Column('end_code', sa.String(length=3), nullable=False),
    sa.Column('end_name', sa.Text(), nullable=False),
    sa.Column('with_transfer', sa.Boolean(), nullable=False),
    sa.Column('departure_at', sa.String(length=10), nullable=False),
    sa.Column('return_at', sa.String(length=10), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('start_code', 'end_code', 'with_transfer', 'departure_at', 'return_at', name='flight_direction_uc')
    )
    op.create_table('historic_flight_direction',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('start_code', sa.String(length=3), nullable=False),
    sa.Column('start_name', sa.Text(), nullable=False),
    sa.Column('end_code', sa.String(length=3), nullable=False),
    sa.Column('end_name', sa.Text(), nullable=False),
    sa.Column('with_transfer', sa.Boolean(), nullable=False),
    sa.Column('departure_at', sa.String(length=10), nullable=False),
    sa.Column('return_at', sa.String(length=10), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_by_user', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('users_directions',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('direction_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['direction_id'], ['flight_direction.id'], name='users_directions_fk__flight_direction', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'direction_id', name='users_directions_pk')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_directions')
    op.drop_table('user')
    op.drop_table('historic_flight_direction')
    op.drop_table('flight_direction')
    # ### end Alembic commands ###
