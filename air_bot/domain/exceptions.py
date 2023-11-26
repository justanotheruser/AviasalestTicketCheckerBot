from air_bot.domain.model import FlightDirection


class LocationsApiError(Exception):
    pass


class LocationsApiConnectionError(LocationsApiError):
    pass


class LocationsApiRespondedWithError(LocationsApiError):
    pass


class TicketsError(Exception):
    pass


class TicketsAPIConnectionError(TicketsError):
    pass


class TicketsAPIError(TicketsError):
    """Request for some reason was invalid"""

    pass


class InternalError(Exception):
    pass


class TicketsParsingError(InternalError):
    pass


class DuplicatedFlightDirection(Exception):
    def __init__(
        self, user_id: int, direction_id: int, flight_direction: FlightDirection
    ):
        self.user_id = user_id
        self.direction_id = direction_id
        self.flight_direction = flight_direction
