from pydantic import BaseModel


class TicketStatusUpdate(BaseModel):
    status: str