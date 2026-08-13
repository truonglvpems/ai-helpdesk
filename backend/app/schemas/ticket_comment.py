from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TicketCommentCreate(BaseModel):
    user_id: UUID
    content: str = Field(min_length=1)
    is_internal: bool = False


class TicketCommentUpdate(BaseModel):
    content: str = Field(
        min_length=1,
    )
    is_internal: bool | None = None


class TicketCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_id: UUID
    user_id: UUID
    content: str
    is_internal: bool
    created_at: datetime