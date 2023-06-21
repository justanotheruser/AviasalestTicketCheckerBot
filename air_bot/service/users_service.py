import asyncmy.errors
from loguru import logger

from air_bot.service.unit_of_work import AbstractUnitOfWork


async def add_user(user_id: int, uow: AbstractUnitOfWork):
    with uow:
        try:
            await uow.users.add(user_id)
        except asyncmy.errors.IntegrityError:
            # User already in repo
            pass
        except Exception as e:
            logger.error(e)

