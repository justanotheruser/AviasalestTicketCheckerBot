from air_bot.domain.model import FlightDirection

FLIGHT_DIRECTION_NO_RETURN = FlightDirection(
    start_code="STA",
    start_name="Start",
    end_code="END",
    end_name="End",
    with_transfer=False,
    departure_at="2023-05-16",
    return_at=None,
)

FLIGHT_DIRECTION_WITH_RETURN = FlightDirection(
    start_code="STA",
    start_name="Start",
    end_code="END",
    end_name="End",
    with_transfer=False,
    departure_at="2023-05-16",
    return_at="2023-06",
)
