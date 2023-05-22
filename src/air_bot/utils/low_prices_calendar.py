from typing import Any
from air_bot.utils.tickets import get_ticket_link


class CalendarTicket:
    def __init__(self, full_date: str, ticket: dict[str, Any]):
        self.day = full_date[-2:]
        self.visible_text = f"{self.day:02} - {ticket['price']} ₽"
        link = get_ticket_link(ticket, f"{ticket['price']} ₽", parse_mode="Markdownv2")
        self.markup = rf"{self.day:02} \- {link}"


def print_calendar(month: int, tickets_by_date: dict[str, Any]) -> str:
    calendar_tickets = get_calendar_tickets(tickets_by_date)
    day_prices_table = get_calendar_table(calendar_tickets)
    return f"📅 {russian_months[month]}\n" f"{day_prices_table}"


def get_calendar_table(calendar_tickets: list[CalendarTicket]) -> str:
    if not calendar_tickets:
        return ""
    if len(calendar_tickets) == 1:
        return calendar_tickets[0].markup
    lines = []
    left_column, right_column = calendar_tickets[::2], calendar_tickets[1::2]
    first_column_width = max([len(x.visible_text) for x in left_column])
    for left, right in zip(left_column, right_column):
        padding = " " * (first_column_width - len(left.visible_text))
        lines.append(rf"{left.markup}`{padding}`\|{right.markup}")
    return "\n".join(lines)


def get_calendar_tickets(tickets_by_date: dict[str, Any]) -> list[CalendarTicket]:
    """List is sorted by ticket's day."""
    result = [
        CalendarTicket(full_date, ticket)
        for full_date, ticket in tickets_by_date.items()
    ]
    result.sort(key=lambda x: x.day)
    return result


russian_months = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}
