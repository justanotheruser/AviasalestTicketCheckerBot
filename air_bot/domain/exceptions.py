class LocationsApiError(Exception):
    pass


class LocationsApiConnectionError(LocationsApiError):
    pass


class LocationsApiRespondedWithError(LocationsApiError):
    pass


class TicketsError(Exception):
    pass


class TicketsTimeoutError(TicketsError):
    pass


class TicketsConnectionError(TicketsError):
    pass


class TicketsAPIError(TicketsError):
    """Request for some reason was invalid"""

    pass


class TicketsParsingError(TicketsError):
    pass


class InternalError(Exception):
    pass
