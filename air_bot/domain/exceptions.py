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
