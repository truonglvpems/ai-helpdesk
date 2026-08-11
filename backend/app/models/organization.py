import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.models.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
        )

    slug: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True,
        index=True,
        )

    status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="active"
        )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False,
        )

    users: Mapped[list["User"]] = relationship(
        "User", 
        back_populates="organization"
        )

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="organization"
        )

    ticket_categories: Mapped[list["TicketCategory"]] = relationship(
        "TicketCategory",
        back_populates="organization"
        )
        