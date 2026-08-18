from uuid import UUID

from app.core.permissions import Permission
from app.core.role_permissions import has_permission
from app.models.ticket import Ticket
from app.models.user import User


class TicketPolicy:
    """Authorization policy for Ticket resources.

    This class contains authorization rules only.
    It does not perform database operations or raise HTTP exceptions.
    """

    @staticmethod
    def _same_organization(
        user: User,
        ticket: Ticket,
    ) -> bool:
        return user.organization_id == ticket.organization_id

    @staticmethod
    def _is_owner(
        user: User,
        ticket: Ticket,
    ) -> bool:
        return user.id == ticket.created_by

    @staticmethod
    def _is_assigned(
        user: User,
        ticket: Ticket,
    ) -> bool:
        return ticket.assigned_to == user.id

    @staticmethod
    def can_create(user: User) -> bool:
        return has_permission(
            user.role,
            Permission.TICKET_CREATE,
        )

    @staticmethod
    def can_read(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        if has_permission(
            user.role,
            Permission.TICKET_READ,
        ):
            return True

        if has_permission(
            user.role,
            Permission.TICKET_READ_OWN,
        ):
            return TicketPolicy._is_owner(user, ticket)

        if has_permission(
            user.role,
            Permission.TICKET_READ_ASSIGNED,
        ):
            return TicketPolicy._is_assigned(user, ticket)

        return False

    @staticmethod
    def can_update(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        if has_permission(
            user.role,
            Permission.TICKET_UPDATE,
        ):
            return True

        if has_permission(
            user.role,
            Permission.TICKET_UPDATE_OWN,
        ):
            return TicketPolicy._is_owner(user, ticket)

        return False

    @staticmethod
    def can_delete(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        return has_permission(
            user.role,
            Permission.TICKET_DELETE,
        )

    @staticmethod
    def can_assign(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        return has_permission(
            user.role,
            Permission.TICKET_ASSIGN,
        )

    @staticmethod
    def can_unassign(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        return has_permission(
            user.role,
            Permission.TICKET_UNASSIGN,
        )

    @staticmethod
    def can_reassign(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        return has_permission(
            user.role,
            Permission.TICKET_REASSIGN,
        )

    @staticmethod
    def can_comment(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        if not has_permission(
            user.role,
            Permission.TICKET_COMMENT,
        ):
            return False

        if user.role == "EMPLOYEE":
            return TicketPolicy._is_owner(user, ticket)

        return True

    @staticmethod
    def can_change_status(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        return has_permission(
            user.role,
            Permission.TICKET_CHANGE_STATUS,
        )

    @staticmethod
    def can_change_priority(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        return has_permission(
            user.role,
            Permission.TICKET_CHANGE_PRIORITY,
        )

    @staticmethod
    def can_close(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        return has_permission(
            user.role,
            Permission.TICKET_CLOSE,
        )

    @staticmethod
    def can_reopen(
        user: User,
        ticket: Ticket,
    ) -> bool:
        if not TicketPolicy._same_organization(user, ticket):
            return False

        if not has_permission(
            user.role,
            Permission.TICKET_REOPEN,
        ):
            return False

        if user.role == "EMPLOYEE":
            return TicketPolicy._is_owner(user, ticket)

        return True