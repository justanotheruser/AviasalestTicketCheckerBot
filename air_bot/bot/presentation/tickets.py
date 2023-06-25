from datetime import datetime

from air_bot.bot.i18n import i18n
from air_bot.domain.exceptions import InternalError
from air_bot.domain.model import FlightDirection, Ticket


class TicketView:
    def __init__(self, currency: str):
        if currency == "rub":
            self.currency_symbol = "₽"
        elif currency == "usd":
            self.currency_symbol = "$"
        else:
            raise InternalError(f"Unexpected currency: {currency}")

    def print_tickets(self, tickets: list[Ticket], direction: FlightDirection) -> str:
        if not tickets:
            return i18n.translate("no_flights")
        text = f"<b>{direction.start_name} - {direction.end_name} | {i18n.translate('current_prices')}</b>\n"
        with_or_without_return = (
            "↔️ туда-обратно" if direction.return_at else "➡️ в одну сторону"
        )
        direction_type = (
            "↕️ с пересадками" if direction.with_transfer else "➡️ прямой рейс"
        )
        text += with_or_without_return + "\n" + direction_type + "\n\n"
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
            ticket, i18n.translate("buy_ticket"), parse_mode="html"
        )
        return (
            f"<b>{direction.start_name} ({direction.start_code}) - {direction.end_name} ({direction.end_code})</b>\n"
            f"🛫 {departure_at_str}\n"
            f"🛬 {arrival_at_str}\n"
            f"💳 {ticket.price} {self.currency_symbol} | {ticket_link}"
        )

    def _print_two_way_ticket(self, ticket: Ticket, direction: FlightDirection) -> str:
        departure_at_str = print_datetime(ticket.departure_at)
        departure_arrival_at_str = print_datetime(
            ticket.departure_at + ticket.duration_to
        )
        return_at_str = print_datetime(ticket.return_at)
        return_arrival_at_str = print_datetime(ticket.return_at + ticket.duration_back)
        ticket_link = get_ticket_link(
            ticket, i18n.translate("buy_ticket"), parse_mode="html"
        )
        return (
            f"<b>{direction.start_name} ({direction.start_code}) - {direction.end_name} ({direction.end_code}) - "
            f"{direction.start_name} ({direction.start_code})</b>\n"
            f"🛫 {departure_at_str}\n"
            f"🛬 {departure_arrival_at_str}\n"
            f"🛫 {return_at_str}\n"
            f"🛬 {return_arrival_at_str}\n"
            f"💳 {ticket.price} {self.currency_symbol} | {ticket_link}"
        )


def get_ticket_link(ticket: Ticket, link_text: str, parse_mode: str) -> str:
    url = f"https://www.aviasales.ru{ticket.link}&marker=18946"
    if parse_mode == "html":
        return f'<a href="{url}">{link_text}</a>'
    elif parse_mode == "Markdownv2":
        return f"[{link_text}]({url})"
    raise RuntimeError(f"Invalid parse_mode option: {parse_mode}")


def print_datetime(ticket_date: datetime) -> str:
    """Returns string for using in ticket message"""
    return ticket_date.strftime("%d.%m.%Y <b>·</b> %H:%M")
