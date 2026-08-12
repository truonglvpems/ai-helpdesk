from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.flush()
        self.db.refresh(ticket)
        return ticket

    def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        return self.db.scalar(stmt)

    def list_by_organization(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ticket]:
        stmt = (
            select(Ticket)
            .where(Ticket.organization_id == organization_id)
            .order_by(Ticket.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.scalars(stmt).all())

    def update(self, ticket: Ticket) -> Ticket:
        self.db.flush()
        self.db.refresh(ticket)
        return ticket

    def delete(self, ticket: Ticket) -> None:
        self.db.delete(ticket)
        self.db.flush()