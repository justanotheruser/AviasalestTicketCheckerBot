import logging
import time

import aiogram
from air_bot.scheduler import Scheduler
from air_bot.aviasales_api.api_layer import AviasalesAPILayer
from air_bot.bot_types import FlightDirection
from air_bot.checker.conf import Interval
from air_bot.checker.conf import read_config
from air_bot.db import DB
from air_bot.keyboards.user_home_kb import user_home_keyboard
from air_bot.utils.tickets import print_ticket

logger = logging.getLogger("AirBot")


class TicketPriceChecker:
    def __init__(
        self,
        bot: aiogram.Bot,
        aviasales_api: AviasalesAPILayer,
        db: DB,
        scheduler: Scheduler,
        config_file_path: str,
    ):
        self.bot = bot
        self.aviasales_api = aviasales_api
        self.db = db
        self.scheduler = scheduler
        self.users_jobs: dict[int, dict[FlightDirection, int]] = dict()
        self.config_file_path = config_file_path
        try:
            self.config = read_config(self.config_file_path)
        except Exception as e:
            logger.critical(
                f"[TicketPriceChecker] Can't start ticker price checker without config: {e}",
                exc_info=True,
            )
            return
        self.scheduler.schedule_every_seconds(5, self._reload_config)
        self._schedule_checks_from_db()

    def schedule_check(self, user_id: int, direction: FlightDirection) -> None:
        if user_id not in self.users_jobs:
            self.users_jobs[user_id] = dict()
        logger.info(
            f"[TicketPriceChecker] Schedule tickets check for user {user_id}: {direction}"
        )
        if self.config.check_interval_units == Interval.SECONDS:
            self.users_jobs[user_id][direction] = self.scheduler.schedule_every_seconds(
                self.config.check_interval, self._check_tickets, user_id, direction
            )
        elif self.config.check_interval_units == Interval.MINUTES:
            self.users_jobs[user_id][direction] = self.scheduler.schedule_every_minutes(
                self.config.check_interval, self._check_tickets, user_id, direction
            )

    def remove_check(self, user_id: int, direction: FlightDirection) -> None:
        logger.info(
            f"[TicketPriceChecker] Cancel tickets check for user {user_id}: {direction}"
        )
        self.scheduler.cancel(self.users_jobs[user_id][direction])
        del self.users_jobs[user_id][direction]
        if len(self.users_jobs[user_id]) == 0:
            del self.users_jobs[user_id]

    async def _check_tickets(self, user_id: int, direction: FlightDirection) -> None:
        ticket = await self.aviasales_api.get_cheapest_ticket(direction)
        if not ticket:
            return
        last_price = self.db.get_price(user_id, direction)
        if not last_price:
            await self.bot.send_message(user_id, "Появился билет!")
            await self.bot.send_message(
                user_id,
                print_ticket(ticket, direction),
                parse_mode="html",
                disable_web_page_preview=True,
                reply_markup=user_home_keyboard(),
            )
            self.db.save_flight_direction(user_id, direction, ticket["price"])
            return
        self.db.update_flight_direction_price(user_id, direction, ticket["price"])
        if ticket["price"] <= last_price * (
            1 - self.config.price_reduction_threshold_percents / 100
        ):
            await self.bot.send_message(user_id, "Появился билет!")
            await self.bot.send_message(
                user_id,
                print_ticket(ticket, direction),
                parse_mode="html",
                disable_web_page_preview=True,
                reply_markup=user_home_keyboard(),
            )

    def _schedule_checks_from_db(self) -> None:
        directions = self.db.get_all_flight_directions()
        logger.info(
            f"[TicketPriceChecker] Scheduling ticker price check for {len(directions)} existing flight directions"
        )
        for direction in directions:
            self.schedule_check(direction.user_id, direction.direction)
            time.sleep(0.5)

    async def _reload_config(self) -> None:
        config = read_config(self.config_file_path)
        if not config:
            logger.warning("[TicketPriceChecker] Ignoring invalid config")
            return
        self.config = config
