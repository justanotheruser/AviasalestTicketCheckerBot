import abc

from sqlalchemy.ext.asyncio.session import AsyncSession

from air_bot.adapters.repo.flight_directions import (
    FlightDirectionRepo,
    SqlAlchemyFlightDirectionRepo,
)
from air_bot.adapters.repo.session_maker import AbstractSessionMaker
from air_bot.adapters.repo.tickets import SqlAlchemyTicketRepo, TicketRepo
from air_bot.adapters.repo.users import SqlAlchemyUsersRepo, UserRepo
from air_bot.adapters.repo.users_directions import (
    SqlAlchemyUserDirectionRepo,
    UserDirectionRepo,
)


class AbstractUnitOfWork(abc.ABC):
    users: UserRepo
    flight_directions: FlightDirectionRepo
    users_directions: UserDirectionRepo
    tickets: TicketRepo

    def __init__(self, session_factory: AbstractSessionMaker):
        self.session_factory = session_factory
        self._is_commited = False

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()
        self._is_commited = True

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    async def rollback(self):
        if not self._is_commited:
            await self._rollback()

    @abc.abstractmethod
    async def _rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.users = SqlAlchemyUsersRepo(self.session)
        self.flight_directions = SqlAlchemyFlightDirectionRepo(self.session)
        self.users_directions = SqlAlchemyUserDirectionRepo(self.session)
        self.tickets = SqlAlchemyTicketRepo(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def _rollback(self):
        await self.session.rollback()
