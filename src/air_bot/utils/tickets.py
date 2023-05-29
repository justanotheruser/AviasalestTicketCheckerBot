import logging
from datetime import datetime, timedelta
from typing import Any

from air_bot.bot_types import FlightDirection

logger = logging.getLogger(__name__)


def print_tickets(tickets: Any, direction: FlightDirection) -> str:
    if not tickets:
        return "Рейсов нет!"
    text = f"<b>{direction.start_name} - {direction.end_name} | текущие цены</b>\n"
    with_or_without_return = (
        "↔️ туда-обратно" if direction.return_at else "➡️ в одну сторону"
    )
    direction_type = "↕️ с пересадками" if direction.with_transfer else "➡️ прямой рейс"
    text += with_or_without_return + "\n" + direction_type + "\n\n"
    for ticket in tickets:
        text += print_ticket(ticket, direction)
        text += "\n------------------------------------\n"
    return text


def print_ticket(ticket: Any, direction: FlightDirection) -> str:
    if direction.return_at:
        return print_two_way_ticket(ticket, direction)
    return print_one_way_ticket(ticket, direction)


def print_one_way_ticket(ticket: Any, direction: FlightDirection) -> str:
    departure_at = datetime_from_ticket(ticket["departure_at"])
    departure_at_str = print_datetime(departure_at)
    arrival_at_str = print_datetime(
        departure_at + timedelta(minutes=int(ticket["duration_to"]))
    )
    return (
        f"<b>{direction.start_name} ({direction.start_code}) - {direction.end_name} ({direction.end_code})</b>\n"
        f"🛫 {departure_at_str}\n"
        f"🛬 {arrival_at_str}\n"
        f'💳 {ticket["price"]} ₽ | {get_ticket_link(ticket, "купить билет", parse_mode="html")}'
    )


def print_two_way_ticket(ticket: Any, direction: FlightDirection) -> str:
    departure_at = datetime_from_ticket(ticket["departure_at"])
    departure_at_str = print_datetime(departure_at)
    departure_arrival_at_str = print_datetime(
        departure_at + timedelta(minutes=int(ticket["duration_to"]))
    )

    return_at = datetime_from_ticket(ticket["return_at"])
    return_at_str = print_datetime(return_at)
    return_arrival_at_str = print_datetime(
        return_at + timedelta(minutes=int(ticket["duration_back"]))
    )

    return (
        f"<b>{direction.start_name} ({direction.start_code}) - {direction.end_name} ({direction.end_code}) - "
        f"{direction.start_name} ({direction.start_code})</b>\n"
        f"🛫 {departure_at_str}\n"
        f"🛬 {departure_arrival_at_str}\n"
        f"🛫 {return_at_str}\n"
        f"🛬 {return_arrival_at_str}\n"
        f'💳 {ticket["price"]} ₽ | {get_ticket_link(ticket, "купить билет", parse_mode="html")}'
    )


def get_ticket_link(ticket: dict[str, Any], link_text: str, parse_mode: str) -> str:
    url = f'https://www.aviasales.ru{ticket["link"]}&marker=18946'
    if parse_mode == "html":
        return f'<a href="{url}">{link_text}</a>'
    elif parse_mode == "Markdownv2":
        return f"[{link_text}]({url})"
    raise RuntimeError(f"Invalid parse_mode option: {parse_mode}")


def datetime_from_ticket(datetime_str: str) -> datetime:
    """Converts datetime from string in Aviasales API response to Python's datetime"""
    return datetime.strptime(
        str(datetime_str)[: len(datetime_str) - 9], "%Y-%m-%dT%H:%M"
    )


def print_datetime(ticket_date: datetime) -> str:
    """Returns string for using in ticket message"""
    return ticket_date.strftime("%d.%m.%Y <b>·</b> %H:%M")
