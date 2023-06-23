import abc
from typing import Self

from sqlalchemy.ext.asyncio.session import AsyncSession

from air_bot.adapters.repo.flight_direction import (
    AbstractFlightDirectionRepo,
    SqlAlchemyFlightDirectionRepo,
)
from air_bot.adapters.repo.users_directions import (
    AbstractUserDirectionRepo,
    SqlAlchemyUserDirectionRepo
)
from air_bot.adapters.repo.session_maker import AbstractSessionMaker
from air_bot.adapters.repo.users import AbstractUserRepo, SqlAlchemyUsersRepo


class AbstractUnitOfWork(abc.ABC):
    users: AbstractUserRepo
    flight_directions: AbstractFlightDirectionRepo
    users_directions: AbstractUserDirectionRepo

    def __init__(self, session_factory: AbstractSessionMaker):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.users = SqlAlchemyUsersRepo(self.session)
        self.flight_direction = SqlAlchemyFlightDirectionRepo(self.session)
        self.users_directions = SqlAlchemyUserDirectionRepo(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
