import datetime
from dataclasses import asdict, dataclass

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from air_bot.adapters.repo import orm
from air_bot.domain import model
from air_bot.domain.repository import AbstractTicketRepo


@dataclass(kw_only=True)
class TicketDB:
    id: int | None = None
    direction_id: int
    price: float
    departure_at: datetime.datetime
    duration_to: int
    return_at: datetime.datetime | None = None
    duration_back: int | None = None
    link: str

    @staticmethod
    def from_ticket(ticket: model.Ticket, direction_id: int):
        duration_to = ticket.duration_to.seconds // 60
        if ticket.duration_back:
            duration_back = ticket.duration_back // 60
        else:
            duration_back = None
        return TicketDB(
            direction_id=direction_id,
            price=ticket.price,
            departure_at=ticket.departure_at,
            duration_to=duration_to,
            return_at=ticket.return_at,
            duration_back=duration_back,
            link=ticket.link,
        )


class SqlAlchemyTicketRepo(AbstractTicketRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add(self, tickets: list[model.Ticket], direction_id: int):
        for ticket in tickets:
            ticket_db = TicketDB.from_ticket(ticket, direction_id)
            stmt = text(
                "INSERT INTO tickets (direction_id, price, departure_at, duration_to, return_at, "
                "duration_back, link) VALUES (:direction_id, :price, :departure_at, :duration_to, "
                ":return_at, :duration_back, :link)"
            )
            ticket_db_dict = asdict(ticket_db)
            del ticket_db_dict["id"]
            stmt = stmt.bindparams(**ticket_db_dict)
            await self.session.execute(stmt)

    async def get_direction_tickets(
        self, direction_id: int, limit: int | None = None
    ) -> list[model.Ticket]:
        stmt = (
            select(TicketDB)
            .filter_by(direction_id=direction_id)
            .order_by(orm.tickets_table.c.price)
        )
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        tickets = []
        for row in result:
            ticket_db: TicketDB = row[0]
            duration_to = datetime.timedelta(minutes=ticket_db.duration_to)
            duration_back = None
            if ticket_db.duration_back:
                duration_back = datetime.timedelta(minutes=ticket_db.duration_back)
            ticket = model.Ticket(
                price=ticket_db.price,
                departure_at=ticket_db.departure_at,
                duration_to=duration_to,
                return_at=ticket_db.return_at,
                duration_back=duration_back,
                link=ticket_db.link,
            )
            tickets.append(ticket)
        return tickets

    async def remove_for_direction(self, direction_id: int):
        stmt = delete(TicketDB).where(orm.tickets_table.c.direction_id == direction_id)
        await self.session.execute(stmt)
