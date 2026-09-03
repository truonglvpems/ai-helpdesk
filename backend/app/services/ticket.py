from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.user import User
from app.models.ticket_category import TicketCategory
from app.models.organization import Organization
from app.policies.ticket import TicketPolicy
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TicketRepository(db)

    def create_ticket(
        self,
        data: TicketCreate,
        current_user: User,
    ) -> Ticket:
        # ---------------------------------------------------------
        # Tenant identity comes from authenticated user
        # ---------------------------------------------------------
        organization_id = current_user.organization_id
        created_by = current_user.id

        # ---------------------------------------------------------
        # Validate organization
        # ---------------------------------------------------------
        organization_exists = self.db.scalar(
            select(1).where(
                Organization.id == organization_id
            )
        )

        if organization_exists is None:
            raise ValueError("Organization not found")

        # ---------------------------------------------------------
        # Validate creator
        # ---------------------------------------------------------
        creator = self.db.scalar(
            select(User).where(
                User.id == created_by,
                User.organization_id == organization_id,
            )
        )

        if creator is None:
            raise ValueError(
                "Created-by user does not belong to organization"
            )

        # ---------------------------------------------------------
        # Validate category
        # ---------------------------------------------------------
        if data.category_id is not None:
            category = self.db.scalar(
                select(TicketCategory).where(
                    TicketCategory.id == data.category_id,
                    TicketCategory.organization_id == organization_id,
                    TicketCategory.is_active.is_(True),
                )
            )

            if category is None:
                raise ValueError(
                    "Category not found or inactive"
                )

        # ---------------------------------------------------------
        # Create ticket
        # ---------------------------------------------------------
        ticket = Ticket(
            organization_id=organization_id,
            created_by=created_by,
            category_id=data.category_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            status="OPEN",
        )

        self.repository.create(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_ticket(
        self,
        ticket_id: UUID,
        current_user: User,
    ) -> Ticket | None:
        ticket = self.repository.get_by_id(
            ticket_id,
            current_user.organization_id,
        )

        if ticket is None:
            return None

        # ---------------------------------------------------------
        # Resource-level read policy
        # ---------------------------------------------------------
        if not TicketPolicy.can_read(
            current_user,
            ticket,
        ):
            return None

        return ticket

    def list_tickets(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ticket]:
        return self.repository.list_by_organization(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )

    def update_ticket(
        self,
        ticket_id: UUID,
        data: TicketUpdate,
        current_user: User,
    ) -> Ticket | None:
        ticket = self.repository.get_by_id(
            ticket_id,
            current_user.organization_id,
        )

        if ticket is None:
            return None

        # ---------------------------------------------------------
        # Resource-level update policy
        # ---------------------------------------------------------
        if not TicketPolicy.can_update(
            current_user,
            ticket,
        ):
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ---------------------------------------------------------
        # Validate category when changing category
        # ---------------------------------------------------------
        if "category_id" in update_data:
            category_id = update_data["category_id"]

            if category_id is not None:
                category = self.db.scalar(
                    select(TicketCategory).where(
                        TicketCategory.id == category_id,
                        TicketCategory.organization_id
                        == ticket.organization_id,
                        TicketCategory.is_active.is_(True),
                    )
                )

                if category is None:
                    raise ValueError(
                        "Category not found or inactive"
                    )

        # ---------------------------------------------------------
        # Validate assigned user
        # ---------------------------------------------------------
        if "assigned_to" in update_data:
            assigned_to = update_data["assigned_to"]

            if assigned_to is not None:
                user = self.db.scalar(
                    select(User).where(
                        User.id == assigned_to,
                        User.organization_id
                        == ticket.organization_id,
                    )
                )

                if user is None:
                    raise ValueError(
                        "Assigned user does not belong "
                        "to ticket organization"
                    )

        # ---------------------------------------------------------
        # Update fields
        # ---------------------------------------------------------
        for field, value in update_data.items():
            setattr(ticket, field, value)

        self.repository.update(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def delete_ticket(
        self,
        ticket_id: UUID,
        current_user: User,
    ) -> bool:
        ticket = self.repository.get_by_id(
            ticket_id,
            current_user.organization_id,
        )

        if ticket is None:
            return False

        # ---------------------------------------------------------
        # Resource-level delete policy
        # ---------------------------------------------------------

        if not TicketPolicy.can_delete(current_user, ticket):
            return False

        self.repository.delete(ticket)
        self.db.commit()

        return True