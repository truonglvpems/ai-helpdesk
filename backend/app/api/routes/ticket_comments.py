from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.core.database import get_db
from app.core.permissions import Permission
from app.models.user import User
from app.schemas.ticket_comment import (
    TicketCommentCreate,
    TicketCommentResponse,
    TicketCommentUpdate,
)
from app.services.ticket_comment import TicketCommentService


router = APIRouter(
    prefix="/tickets/{ticket_id}/comments",
    tags=["Ticket Comments"],
)


@router.post(
    "",
    response_model=TicketCommentResponse,
    status_code=201,
)
def create_comment(
    ticket_id: UUID,
    data: TicketCommentCreate,
    current_user: User = Depends(
        require_permission(Permission.TICKET_COMMENT)
    ),
    db: Session = Depends(get_db),
):
    service = TicketCommentService(db)

    try:
        return service.create_comment(
            ticket_id=ticket_id,
            data=data,
            current_user=current_user,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[TicketCommentResponse],
)
def list_comments(
    ticket_id: UUID,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(
        require_permission(Permission.TICKET_READ)
    ),
    db: Session = Depends(get_db),
):
    service = TicketCommentService(db)

    try:
        return service.list_comments(
            ticket_id=ticket_id,
            current_user=current_user,
            limit=limit,
            offset=offset,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.patch(
    "/{comment_id}",
    response_model=TicketCommentResponse,
)
def update_comment(
    ticket_id: UUID,
    comment_id: UUID,
    data: TicketCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.TICKET_COMMENT)
    ),
):
    service = TicketCommentService(db)

    try:
        comment = service.update_comment(
            comment_id=comment_id,
            current_user=current_user,
            data=data,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if comment.ticket_id != ticket_id:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    return comment


@router.delete(
    "/{comment_id}",
    status_code=204,
)
def delete_comment(
    ticket_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(
        require_permission(Permission.TICKET_COMMENT)
    ),
    db: Session = Depends(get_db),
):
    service = TicketCommentService(db)

    comment = service.get_comment(comment_id)

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if comment.ticket_id != ticket_id:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    try:
        deleted = service.delete_comment(
            comment_id=comment_id,
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

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    return None