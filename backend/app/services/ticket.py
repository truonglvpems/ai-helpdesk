from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TicketRepository(db)

    def create_ticket(self, data: TicketCreate) -> Ticket:
        ticket = Ticket(
            organization_id=data.organization_id,
            created_by=data.created_by,
            category_id=data.category_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            status="OPEN",
        )

        self.repository.create(ticket)
        self.db.commit()

        return ticket

    def get_ticket(self, ticket_id: UUID) -> Ticket | None:
        return self.repository.get_by_id(ticket_id)

    def list_tickets(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ticket]:
        return self.repository.list_by_organization(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )