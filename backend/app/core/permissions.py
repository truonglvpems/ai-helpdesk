class Permission:
    # Ticket
    TICKET_CREATE = "ticket:create"

    TICKET_READ = "ticket:read"
    TICKET_READ_OWN = "ticket:read:own"
    TICKET_READ_ASSIGNED = "ticket:read:assigned"

    TICKET_UPDATE = "ticket:update"
    TICKET_UPDATE_OWN = "ticket:update:own"

    TICKET_DELETE = "ticket:delete"
    TICKET_DELETE_OWN = "ticket:delete:own"

    TICKET_ASSIGN = "ticket:assign"
    TICKET_UNASSIGN = "ticket:unassign"
    TICKET_REASSIGN = "ticket:reassign"

    TICKET_COMMENT = "ticket:comment"

    TICKET_CHANGE_STATUS = "ticket:change_status"
    TICKET_CHANGE_PRIORITY = "ticket:change_priority"

    TICKET_CLOSE = "ticket:close"
    TICKET_REOPEN = "ticket:reopen"