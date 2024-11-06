from typing import Dict, List

from air_bot.bot.presentation.utils import NUMBER2MONTH_NAME, get_ticket_link
from air_bot.domain.exceptions import InternalError
from air_bot.domain.model import Ticket


class CalendarTicket:
    def __init__(
        self, full_date: str, ticket: Ticket, currency_symbol: str, domain: str
    ):
        self.day = full_date[-2:]
        link_text = f"{int(ticket.price)} {currency_symbol}"
        day_text = "{day:0>2}".format(day=self.day)
        self.visible_text = f"{day_text} - {link_text}"
        link = get_ticket_link(ticket, link_text, domain, parse_mode="Markdownv2")
        self.markup = rf"{day_text} \- {link}"


class CalendarView:
    def __init__(self, currency: str):
        if currency == "rub":
            self.currency_symbol = "₽"
            self.domain = "ru"
        elif currency == "usd":
            self.currency_symbol = "$"
            self.domain = "com"
        else:
            raise InternalError(f"Unexpected currency: {currency}")

    def print_calendar(
        self, month: int, tickets_by_date: Dict[str, Ticket]
    ) -> List[str]:
        calendar_tickets = get_calendar_tickets(
            tickets_by_date, self.currency_symbol, self.domain
        )
        calendar_lines = get_calendar_lines(calendar_tickets)
        calendar_tables = get_calendar_tables(calendar_lines)
        table_header = f"📅 {NUMBER2MONTH_NAME[month].capitalize()}"
        calendar_tables[0] = f"{table_header}\n{calendar_tables[0]}"
        return calendar_tables


def get_calendar_tables(lines: List[str]) -> List[str]:
    # Because all lines together can easily exceed message symbol limit we split table if necessary
    tables = []
    cur_table = ""
    for line in lines:
        if len(line) + len(cur_table) >= 9450:
            tables.append(cur_table)
            cur_table = line + "\n"
        else:
            cur_table += line + "\n"
    tables.append(cur_table)
    return tables


def get_calendar_lines(calendar_tickets: List[CalendarTicket]) -> List[str]:
    if not calendar_tickets:
        return [""]
    if len(calendar_tickets) == 1:
        return [calendar_tickets[0].markup]
    lines = []
    left_column, right_column = calendar_tickets[::2], calendar_tickets[1::2]
    first_column_width = max([len(x.visible_text) for x in left_column])
    for left, right in zip(left_column, right_column):
        padding = " " * (first_column_width - len(left.visible_text))
        lines.append(rf"{left.markup}`{padding}`\|{right.markup}")
    return lines


def get_calendar_tickets(
    tickets_by_date: Dict[str, Ticket], currency_symbol: str, aviasales_domain: str
) -> List[CalendarTicket]:
    """List is sorted by ticket's day."""
    result = [
        CalendarTicket(full_date, ticket, currency_symbol, aviasales_domain)
        for full_date, ticket in tickets_by_date.items()
    ]
    result.sort(key=lambda x: x.day)
    return result
