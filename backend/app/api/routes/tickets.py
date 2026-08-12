from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

# from app.db.session import get_db
from app.core.database import get_db
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.ticket import TicketService


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


@router.post(
    "",
    response_model=TicketResponse,
    status_code=201,
)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
):
    service = TicketService(db)
    return service.create_ticket(data)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
):
    service = TicketService(db)

    ticket = service.get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@router.get(
    "",
    response_model=list[TicketResponse],
)
def list_tickets(
    organization_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    service = TicketService(db)

    return service.list_tickets(
        organization_id=organization_id,
        limit=limit,
        offset=offset,
    )