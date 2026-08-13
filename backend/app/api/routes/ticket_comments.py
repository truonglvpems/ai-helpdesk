from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ticket_comment import (
    TicketCommentCreate,
    TicketCommentUpdate,
    TicketCommentResponse,
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
    db: Session = Depends(get_db),
):
    service = TicketCommentService(db)

    try:
        return service.create_comment(
            ticket_id=ticket_id,
            data=data,
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
    db: Session = Depends(get_db),
):
    service = TicketCommentService(db)

    try:
        return service.list_comments(
            ticket_id=ticket_id,
            limit=limit,
            offset=offset,
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
    user_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    service = TicketCommentService(db)

    # ---------------------------------------------------------
    # Verify comment belongs to requested ticket
    # ---------------------------------------------------------
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
        comment = service.update_comment(
            comment_id=comment_id,
            user_id=user_id,
            data=data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if comment is None:
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
    user_id: UUID = Query(...),
    db: Session = Depends(get_db),
):
    service = TicketCommentService(db)

    # ---------------------------------------------------------
    # Verify comment belongs to requested ticket
    # ---------------------------------------------------------
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
            user_id=user_id,
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