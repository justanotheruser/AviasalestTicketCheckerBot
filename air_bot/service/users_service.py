import asyncmy.errors
from adapters.repo.uow import AbstractUnitOfWork
from loguru import logger


async def add_user(user_id: int, uow: AbstractUnitOfWork):
    async with uow:
        try:
            await uow.users.add(user_id)
            await uow.commit()
        except asyncmy.errors.IntegrityError:
            # User already in repo
            pass
        except Exception as e:
            logger.error(e)
