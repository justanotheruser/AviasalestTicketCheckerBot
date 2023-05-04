import logging
from datetime import datetime, timedelta
from typing import Any

from air_bot.bot_types import FlightDirection

logger = logging.getLogger("AirBot")


def print_tickets(tickets: Any, direction: FlightDirection) -> str:
    if not tickets:
        return "Рейсов нет!"
    text = f"{direction.start_name} - {direction.end_name} - вот текущие цены\n"
    with_or_without_return = (
        "Туда и обратно ➡️⬅️" if direction.return_at else "В один конец ️➡️"
    )
    direction_type = "🔄 C пересадкой" if direction.with_transfer else "🔄 Прямые"
    text += with_or_without_return + "\n" + direction_type + "\n\n"
    for ticket in tickets:
        text += print_ticket(ticket, direction) + "\n\n\n\n"
    return text


def print_ticket(ticket: Any, direction: FlightDirection) -> str:
    if direction.return_at:
        return print_two_way_ticket(ticket, direction)
    return print_one_way_ticket(ticket, direction)


def print_one_way_ticket(ticket: Any, direction: FlightDirection) -> str:
    departure_at = datetime.strptime(
        str(ticket["departure_at"])[: len(ticket["departure_at"]) - 9], "%Y-%m-%dT%H:%M"
    )
    datetime_format = "%d.%m.%Y %H:%M"
    departure_at_str = departure_at.strftime(datetime_format)
    arrival_at_str = (
        departure_at + timedelta(minutes=int(ticket["duration"]))
    ).strftime(datetime_format)
    return (
        f"{direction.start_name}({direction.start_code}) - {direction.end_name}({direction.end_code})\n"
        f"🕛 Отправление: {departure_at_str}\n"
        f"🕞 Прибытие: {arrival_at_str}\n"
        f'💳 {ticket["price"]} ₽ | <a href="https://www.aviasales.ru{get_ticket_link(ticket)}">Купить билет</a>'
    )


def print_two_way_ticket(ticket: Any, direction: FlightDirection) -> str:
    departure_at = datetime.strptime(
        str(ticket["departure_at"])[: len(ticket["departure_at"]) - 9], "%Y-%m-%dT%H:%M"
    )
    datetime_format = "%d.%m.%Y %H:%M"
    departure_at_str = departure_at.strftime(datetime_format)
    departure_arrival_at_str = (
        departure_at + timedelta(minutes=int(ticket["duration_to"]))
    ).strftime(datetime_format)

    return_at = datetime.strptime(
        str(ticket["return_at"])[: len(ticket["return_at"]) - 9], "%Y-%m-%dT%H:%M"
    )
    return_at_str = return_at.strftime(datetime_format)
    return_arrival_at_str = (
        return_at + timedelta(minutes=int(ticket["duration_back"]))
    ).strftime(datetime_format)

    return (
        f"{direction.start_name}({direction.start_code}) - {direction.end_name}({direction.end_code}) - "
        f"{direction.start_name}({direction.start_code})\n"
        f"🕛 Отправление (туда): {departure_at_str}\n"
        f"🕞 Прибытие (туда): {departure_arrival_at_str}\n"
        f"🕛 Отправление (обратно): {return_at_str}\n"
        f"🕞 Прибытие (обратно): {return_arrival_at_str}\n"
        f'💳 {ticket["price"]} ₽ | <a href="https://www.aviasales.ru{get_ticket_link(ticket)}">Купить билет</a>'
    )


def get_ticket_link(ticket: dict[str, Any]) -> str:
    return str(ticket["link"]) + "&marker=18946"
