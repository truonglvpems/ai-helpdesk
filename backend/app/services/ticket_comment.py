from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.ticket_comment import TicketComment
from app.models.user import User
from app.policies.ticket import TicketPolicy
from app.repositories.ticket_comment import TicketCommentRepository
from app.schemas.ticket_comment import (
    TicketCommentCreate,
    TicketCommentUpdate,
)


class TicketCommentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TicketCommentRepository(db)

    def create_comment(
        self,
        ticket_id: UUID,
        data: TicketCommentCreate,
        current_user: User,
    ) -> TicketComment:
        # ---------------------------------------------------------
        # Validate ticket
        # ---------------------------------------------------------
        ticket = self.db.scalar(
            select(Ticket).where(
                Ticket.id == ticket_id
            )
        )

        if ticket is None:
            raise ValueError("Ticket not found")

                # ---------------------------------------------------------
        # Resource-level comment policy
        # ---------------------------------------------------------
        if not TicketPolicy.can_comment(
            current_user,
            ticket,
        ):
            raise PermissionError(
                "User is not allowed to comment on ticket"
            )

        # ---------------------------------------------------------
        # Validate authenticated user
        # ---------------------------------------------------------
        user = self.db.scalar(
            select(User).where(
                User.id == current_user.id,
                User.organization_id == ticket.organization_id,
            )
        )

        if user is None:
            raise ValueError(
                "User does not belong to ticket organization"
            )

        # ---------------------------------------------------------
        # Create comment
        # ---------------------------------------------------------
        comment = TicketComment(
            ticket_id=ticket_id,
            user_id=current_user.id,
            content=data.content,
            is_internal=data.is_internal,
        )

        self.repository.create(comment)
        self.db.commit()
        self.db.refresh(comment)

        return comment

    def get_comment(
        self,
        comment_id: UUID,
    ) -> TicketComment | None:
        return self.repository.get_by_id(comment_id)

    def list_comments(
        self,
        ticket_id: UUID,
        current_user: User,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TicketComment]:
        # ---------------------------------------------------------
        # Validate ticket
        # ---------------------------------------------------------
        ticket = self.db.scalar(
            select(Ticket).where(
                Ticket.id == ticket_id
            )
        )

        if ticket is None:
            raise ValueError("Ticket not found")

        # ---------------------------------------------------------
        # Resource-level ticket read policy
        # ---------------------------------------------------------
        if not TicketPolicy.can_read(
            current_user,
            ticket,
        ):
            raise PermissionError(
                "User is not allowed to read ticket comments"
            )

        return self.repository.list_by_ticket(
            ticket_id=ticket_id,
            limit=limit,
            offset=offset,
        )

    def update_comment(
        self,
        comment_id: UUID,
        current_user: User,
        data: TicketCommentUpdate,
    ) -> TicketComment | None:
        # ---------------------------------------------------------
        # Validate comment
        # ---------------------------------------------------------
        comment = self.repository.get_by_id(comment_id)

        if comment is None:
            return None

        # ---------------------------------------------------------
        # Validate ticket
        # ---------------------------------------------------------
        ticket = self.db.scalar(
            select(Ticket).where(
                Ticket.id == comment.ticket_id
            )
        )

        if ticket is None:
            return None

        # ---------------------------------------------------------
        # Resource-level comment update policy
        # ---------------------------------------------------------
        if not TicketPolicy.can_update(
            current_user,
            ticket,
        ):
            raise PermissionError(
                "User is not allowed to update ticket comment"
            )

        # ---------------------------------------------------------
        # Validate authenticated user / organization
        # ---------------------------------------------------------
        user = self.db.scalar(
            select(User).where(
                User.id == current_user.id,
                User.organization_id == ticket.organization_id,
            )
        )

        if user is None:
            raise ValueError(
                "User does not belong to ticket organization"
            )

        # ---------------------------------------------------------
        # Update fields
        # ---------------------------------------------------------
        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(comment, field, value)

        self.repository.update(comment)
        self.db.commit()
        self.db.refresh(comment)

        return comment

    def delete_comment(
        self,
        comment_id: UUID,
        current_user: User,
    ) -> bool:
        # ---------------------------------------------------------
        # Validate comment
        # ---------------------------------------------------------
        comment = self.repository.get_by_id(comment_id)

        if comment is None:
            return False

        # ---------------------------------------------------------
        # Validate ticket
        # ---------------------------------------------------------
        ticket = self.db.scalar(
            select(Ticket).where(
                Ticket.id == comment.ticket_id
            )
        )

        if ticket is None:
            return False

        # ---------------------------------------------------------
        # Resource-level comment delete policy
        # ---------------------------------------------------------
        if not TicketPolicy.can_comment(
            current_user,
            ticket,
        ):
            raise PermissionError(
                "User is not allowed to delete ticket comment"
            )

        # ---------------------------------------------------------
        # Validate authenticated user / organization
        # ---------------------------------------------------------
        user = self.db.scalar(
            select(User).where(
                User.id == current_user.id,
                User.organization_id == ticket.organization_id,
            )
        )

        if user is None:
            raise ValueError(
                "User does not belong to ticket organization"
            )

        # ---------------------------------------------------------
        # Delete
        # ---------------------------------------------------------
        self.repository.delete(comment)
        self.db.commit()

        return True