from uuid import UUID

from pydantic import BaseModel


class TicketAssignmentUpdate(BaseModel):
    assigned_to: UUID | None = None