from datetime import datetime

from air_bot.bot.i18n import i18n
from air_bot.bot.presentation.utils import get_ticket_link
from air_bot.domain.exceptions import InternalError
from air_bot.domain.model import FlightDirection, Ticket


class TicketView:
    def __init__(self, currency: str):
        if currency == "rub":
            self.currency_symbol = "₽"
            self.domain = "ru"
        elif currency == "usd":
            self.currency_symbol = "$"
            self.domain = "com"
        else:
            raise InternalError(f"Unexpected currency: {currency}")

    def print_tickets(self, tickets: list[Ticket], direction: FlightDirection) -> str:
        if not tickets:
            return i18n.translate("no_flights")
        text = f"<b>{direction.start_name} - {direction.end_name} | {i18n.translate('current_prices')}</b>\n"
        if direction.return_at:
            with_or_without_return = f"↔️ {i18n.translate('round_trip_ticket')}"
        else:
            with_or_without_return = f"➡️ {i18n.translate('one_way_ticket')}"
        if direction.with_transfer:
            direct_or_with_transfer = f"↕️ {i18n.translate('transfer_flight')}"
        else:
            direct_or_with_transfer = f"➡️ {i18n.translate('direct_flight')}"
        text += with_or_without_return + "\n" + direct_or_with_transfer + "\n\n"
        for ticket in tickets:
            text += self.print_ticket(ticket, direction)
            text += "\n------------------------------------\n"
        return text

    def print_ticket(self, ticket: Ticket, direction: FlightDirection) -> str:
        if direction.return_at:
            return self._print_two_way_ticket(ticket, direction)
        return self._print_one_way_ticket(ticket, direction)

    def _print_one_way_ticket(self, ticket: Ticket, direction: FlightDirection) -> str:
        departure_at_str = print_datetime(ticket.departure_at)
        arrival_at_str = print_datetime(ticket.departure_at + ticket.duration_to)
        ticket_link = get_ticket_link(
            ticket, i18n.translate("buy_ticket"), self.domain, parse_mode="html"
        )
        return (
            f"<b>{direction.start_name} ({direction.start_code}) - {direction.end_name} ({direction.end_code})</b>\n"
            f"🛫 {departure_at_str}\n"
            f"🛬 {arrival_at_str}\n"
            f"💳 {int(ticket.price)} {self.currency_symbol} | {ticket_link}"
        )

    def _print_two_way_ticket(self, ticket: Ticket, direction: FlightDirection) -> str:
        departure_at_str = print_datetime(ticket.departure_at)
        departure_arrival_at_str = print_datetime(
            ticket.departure_at + ticket.duration_to
        )
        return_at_str = print_datetime(ticket.return_at)
        return_arrival_at_str = print_datetime(ticket.return_at + ticket.duration_back)
        ticket_link = get_ticket_link(
            ticket, i18n.translate("buy_ticket"), self.domain, parse_mode="html"
        )
        return (
            f"<b>{direction.start_name} ({direction.start_code}) - {direction.end_name} ({direction.end_code}) - "
            f"{direction.start_name} ({direction.start_code})</b>\n"
            f"🛫 {departure_at_str}\n"
            f"🛬 {departure_arrival_at_str}\n"
            f"🛫 {return_at_str}\n"
            f"🛬 {return_arrival_at_str}\n"
            f"💳 {int(ticket.price)} {self.currency_symbol} | {ticket_link}"
        )


def print_datetime(ticket_date: datetime) -> str:
    """Returns string for using in ticket message"""
    return ticket_date.strftime("%d.%m.%Y <b>·</b> %H:%M")
