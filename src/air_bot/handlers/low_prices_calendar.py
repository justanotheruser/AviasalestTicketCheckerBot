import logging
from typing import Any, Tuple
from datetime import datetime
from calendar import monthrange

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery

from air_bot.aviasales_api.api_layer import AviasalesAPILayer
from air_bot.utils.tickets import get_ticket_link
from air_bot.db import DB

logger = logging.getLogger("AirBot")

router = Router()


@router.callback_query(Text(text_startswith="low_prices_calendar"))
async def show_low_prices_calendar(callback: CallbackQuery, db: DB, aviasales_api: AviasalesAPILayer) -> None:
    # TODO: use user state to pass direction, don't read each time from DB
    _, direction_id = callback.data.split("|")  # type: ignore[union-attr]
    direction_id = int(direction_id)
    direction = db.get_users_flight_direction(callback.from_user.id, direction_id)
    today = datetime.today()
    tickets_by_date, success = await aviasales_api.get_cheapest_tickets_for_month(
        direction, year=today.year, month=today.month)
    if not success:
        await callback.answer(text="Что-то пошло не так. Повторите попытку позже")
        return
    day_price_link_list = get_day_price_link_list(tickets_by_date)
    days = get_upcoming_month_days(today.year, today.month)
    await callback.message.answer(  # type: ignore[union-attr]
        f"📅 {russian_months[today.month]}\n"
        f"{day_price_link_list}",
        # reply_markup=user_home_keyboard(),
        parse_mode = "html",
        disable_web_page_preview = True
    )
    await callback.answer()

def get_day_price_link_list(tickets_by_date: dict[str, Any]) -> list[Tuple[str, str]]:
    """Returns list of pairs (day, html_link_to_ticket) where link's text is ticket price.
       List is sorted by days."""
    result = []
    for full_date, ticket in tickets_by_date.items():
        day = full_date[-2:]
        link = get_ticket_link(ticket, f"{ticket['price']} ₽")
        result.append((day, link))
    result.sort(key = lambda x: x[0])
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

def get_upcoming_month_days(year: int, month: int):
    today = datetime.now()
    if today.month > month:
        return []
    elif today.month < month:
        return get_month_days(year, month)
    month_days = get_month_days(year, month)
    return month_days[today.day-1:]


def get_month_days(year: int, month: int):
    return [*range(1, 1+monthrange(year, month)[1])]