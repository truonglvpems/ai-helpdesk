from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    organization_id: UUID
    created_by: UUID
    category_id: UUID | None = None

    title: str = Field(min_length=1, max_length=200)
    description: str

    priority: str = "MEDIUM"


class TicketUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assigned_to: UUID | None = None
    category_id: UUID | None = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_by: UUID
    assigned_to: UUID | None
    category_id: UUID | None

    title: str
    description: str
    status: str
    priority: str

    ai_summary: str | None
    ai_suggested_solution: str | None
    ai_confidence: float | None

    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None