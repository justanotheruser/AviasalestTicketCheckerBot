import logging

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import registry

from air_bot.domain import model

mapper_registry = registry()

logger = logging.getLogger(__name__)

metadata = MetaData()

flight_direction_info_table = Table(
    "flight_direction",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("start_code", String(3), nullable=False),
    Column("start_name", Text, nullable=False),
    Column("end_code", String(3), nullable=False),
    Column("end_name", Text, nullable=False),
    Column("with_transfer", Boolean, nullable=False),
    Column("departure_at", String(10), nullable=False),
    Column("return_at", String(10), nullable=True),
    Column("price", Float, nullable=True),
    Column("last_update", DateTime, nullable=False),
    UniqueConstraint(
        "start_code",
        "end_code",
        "with_transfer",
        "departure_at",
        "return_at",
        name="flight_direction_uc",
    ),
)

users_directions_table = Table(
    "users_directions",
    metadata,
    Column("user_id", Integer, nullable=False),
    Column("direction_id", Integer, nullable=False),
    PrimaryKeyConstraint("user_id", "direction_id", name="users_directions_pk"),
    ForeignKeyConstraint(
        columns=["direction_id"],
        refcolumns=["flight_direction.id"],
        name="users_directions_fk__flight_direction",
        ondelete="CASCADE",
    ),
)

historic_flight_direction_info_table = Table(
    "historic_flight_direction",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, nullable=False),
    Column("start_code", String(3), nullable=False),
    Column("start_name", Text, nullable=False),
    Column("end_code", String(3), nullable=False),
    Column("end_name", Text, nullable=False),
    Column("with_transfer", Boolean, nullable=False),
    Column("departure_at", String(10), nullable=False),
    Column("return_at", String(10), nullable=True),
    Column("price", Float, nullable=True),
    Column("last_update", DateTime, nullable=False),
    Column("deleted_at", DateTime, nullable=False),
    Column("deleted_by_user", DateTime, nullable=False)
)

mapper_registry.map_imperatively(model.FlightDirectionInfo, flight_direction_info_table)
mapper_registry.map_imperatively(model.UserDirection, users_directions_table)
mapper_registry.map_imperatively(model.HistoricFlightDirection, historic_flight_direction_info_table)
