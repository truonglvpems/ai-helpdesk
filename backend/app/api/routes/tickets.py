from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.schemas.ticket_assignment import TicketAssignmentUpdate
from app.schemas.ticket_status import TicketStatusUpdate
from app.services.ticket import TicketService
from app.api.dependencies import (
    get_current_user,
    require_permission,
)
from app.core.permissions import Permission
from app.models.user import User

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
    current_user: User = Depends(
        require_permission(Permission.TICKET_CREATE)
        ),
):
    service = TicketService(db)

    try:
        return service.create_ticket(
            data,
            current_user,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.TICKET_READ)
        ),
):
    service = TicketService(db)

    ticket = service.get_ticket(
        ticket_id,
        current_user,
        )
    
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
    # organization_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.TICKET_READ)
    ),
):
    service = TicketService(db)

    return service.list_tickets(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )

@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def update_ticket(
    ticket_id: UUID,
    data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.TICKET_UPDATE)
    ),
):
    service = TicketService(db)

    try:
        ticket = service.update_ticket(
            ticket_id,
            data,
            current_user,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket

@router.patch(
    "/{ticket_id}/assignment",
    response_model=TicketResponse,
)
def update_ticket_assignment(
    ticket_id: UUID,
    data: TicketAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    service = TicketService(db)

    try:
        ticket = service.update_assignment(
            ticket_id=ticket_id,
            assigned_to=data.assigned_to,
            current_user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket

@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
)
def update_ticket_status(
    ticket_id: UUID,
    data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    service = TicketService(db)

    try:
        ticket = service.update_status(
            ticket_id=ticket_id,
            status=data.status,
            current_user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket

@router.delete(
    "/{ticket_id}",
    status_code=204,
)
def delete_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.TICKET_DELETE)
    ),
):
    service = TicketService(db)

    try:
        deleted = service.delete_ticket(
            ticket_id,
            current_user,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return None