from abc import ABC, abstractmethod

from air_bot.adapters.repo.users_repo import AbstractUserRepo
from air_bot.service_layer.unit_of_work import AbstractUnitOfWork


async def add_user(user_id: int, uow: AbstractUnitOfWork):
    with uow:
        try:
            await uow.users.add(user_id)
        except Exception as e:
            # TODO: catch attempt to insert duplicate
            print(e)

