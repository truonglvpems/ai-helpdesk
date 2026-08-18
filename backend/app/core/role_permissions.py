from app.core.permissions import Permission


ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "ADMIN": frozenset(
        {
            Permission.TICKET_CREATE,
            Permission.TICKET_READ,
            Permission.TICKET_UPDATE,
            Permission.TICKET_DELETE,
            Permission.TICKET_ASSIGN,
            Permission.TICKET_UNASSIGN,
            Permission.TICKET_REASSIGN,
            Permission.TICKET_COMMENT,
            Permission.TICKET_CHANGE_STATUS,
            Permission.TICKET_CHANGE_PRIORITY,
            Permission.TICKET_CLOSE,
            Permission.TICKET_REOPEN,
        }
    ),

    "TECHNICIAN": frozenset(
        {
            Permission.TICKET_CREATE,
            Permission.TICKET_READ,
            Permission.TICKET_UPDATE,
            Permission.TICKET_COMMENT,
            Permission.TICKET_ASSIGN,
            Permission.TICKET_UNASSIGN,
            Permission.TICKET_REASSIGN,
            Permission.TICKET_CHANGE_STATUS,
            Permission.TICKET_CHANGE_PRIORITY,
            Permission.TICKET_CLOSE,
            Permission.TICKET_REOPEN,
        }
    ),

    "EMPLOYEE": frozenset(
        {
            Permission.TICKET_CREATE,
            Permission.TICKET_READ_OWN,
            Permission.TICKET_UPDATE_OWN,
            Permission.TICKET_COMMENT,
            Permission.TICKET_REOPEN,
        }
    ),
}


def has_permission(role: str, permission: str) -> bool:
    permissions = ROLE_PERMISSIONS.get(role, frozenset())

    return permission in permissions