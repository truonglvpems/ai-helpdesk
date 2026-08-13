from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket_comment import TicketComment


class TicketCommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, comment: TicketComment) -> TicketComment:
        self.db.add(comment)
        self.db.flush()
        self.db.refresh(comment)
        return comment

    def get_by_id(
        self,
        comment_id: UUID,
    ) -> TicketComment | None:
        stmt = select(TicketComment).where(
            TicketComment.id == comment_id
        )
        return self.db.scalar(stmt)

    def list_by_ticket(
        self,
        ticket_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TicketComment]:
        stmt = (
            select(TicketComment)
            .where(TicketComment.ticket_id == ticket_id)
            .order_by(TicketComment.created_at.asc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.scalars(stmt).all())

    def update(
        self,
        comment: TicketComment,
    ) -> TicketComment:
        self.db.flush()
        self.db.refresh(comment)
        return comment

    def delete(
        self,
        comment: TicketComment,
    ) -> None:
        self.db.delete(comment)
        self.db.flush()