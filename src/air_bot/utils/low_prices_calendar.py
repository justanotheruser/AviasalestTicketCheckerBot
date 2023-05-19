from typing import Any

from air_bot.utils.tickets import get_ticket_link


def print_calendar(month: int, tickets_by_date):
    day_price_link_list = get_day_price_link_list(tickets_by_date)
    day_prices_table = get_day_prices_table(day_price_link_list)
    return f"📅 {russian_months[month]}\n" \
           f"{day_prices_table}"


def get_day_prices_table(day_price_link_list: list[str]) -> str:
    if not day_price_link_list:
        return ""
    if len(day_price_link_list) == 1:
        return day_price_link_list[0]
    lines = []
    first_column, second_column = day_price_link_list[::2], day_price_link_list[1::2]
    first_column_width = max([len(x) for x in first_column])
    first_column = [x + ' ' * (first_column_width - len(x)) for x in first_column]
    for left, right in zip(first_column, second_column):
        lines.append(f'{left}|{right}')
    return '\n'.join(lines)


def get_day_price_link_list(tickets_by_date: dict[str, Any]) -> list[str]:
    """Returns list of pairs (day, html_link_to_ticket) where link's text is ticket price.
       List is sorted by days."""
    result = []
    for full_date, ticket in tickets_by_date.items():
        day = full_date[-2:]
        link = get_ticket_link(ticket, f"{ticket['price']} ₽")
        result.append(f'{day:02} - {link}')
    result.sort(key=lambda x: x[0])
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
    12: "Декабрь"
}
