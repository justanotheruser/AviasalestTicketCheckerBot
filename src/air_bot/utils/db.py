from air_bot.bot_types import FlightDirection
from air_bot.db.mapping import UserFlightDirection


def flight_direction_from_db_type(ufd: UserFlightDirection) -> FlightDirection:
    return FlightDirection(
        start_code=ufd.start_code,
        start_name=ufd.start_name,
        end_code=ufd.end_code,
        end_name=ufd.end_name,
        with_transfer=ufd.with_transfer,
        departure_at=ufd.departure_at,
        return_at=ufd.return_at,
    )
