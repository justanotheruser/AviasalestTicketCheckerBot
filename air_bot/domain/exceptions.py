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


class InvalidFlightDirectionError(Exception):
    def __init__(self, user_id: int, flight_direction: FlightDirection):
        self.user_id = user_id
        self.flight_direction = flight_direction


class StartAndEndOfDirectionAreTheSameError(InvalidFlightDirectionError):
    pass


class DuplicatedFlightDirection(InvalidFlightDirectionError):
    def __init__(self, direction_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.direction_id = direction_id
