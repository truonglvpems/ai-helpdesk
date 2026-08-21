from unittest.mock import MagicMock
from uuid import uuid4

from app.api.routes.tickets import list_tickets, delete_ticket, get_ticket
from app.models.user import User


def make_current_user(organization_id):
    return User(
        id=uuid4(),
        organization_id=organization_id,
        auth_user_id=uuid4(),
        email="tenant-test@example.com",
        full_name="Tenant Test User",
        role="EMPLOYEE",
        status="active",
    )


def test_list_tickets_uses_current_user_organization():
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()

    service = MagicMock()

    expected_tickets = []

    service.list_tickets.return_value = expected_tickets

    original_service = __import__(
        "app.api.routes.tickets",
        fromlist=["TicketService"],
    ).TicketService

    try:
        __import__(
            "app.api.routes.tickets",
            fromlist=["TicketService"],
        ).TicketService = lambda db: service

        result = list_tickets(
            limit=50,
            offset=0,
            db=db,
            current_user=current_user,
        )

    finally:
        __import__(
            "app.api.routes.tickets",
            fromlist=["TicketService"],
        ).TicketService = original_service

    assert result == expected_tickets

    service.list_tickets.assert_called_once_with(
        organization_id=user_organization_id,
        limit=50,
        offset=0,
    )

def test_get_ticket_uses_current_user_organization():
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()

    service = MagicMock()

    expected_ticket = MagicMock()
    service.get_ticket.return_value = expected_ticket

    tickets_module = __import__(
        "app.api.routes.tickets",
        fromlist=["TicketService"],
    )

    original_service = tickets_module.TicketService

    try:
        tickets_module.TicketService = lambda db: service

        result = tickets_module.get_ticket(
            ticket_id=ticket_id,
            db=db,
            current_user=current_user,
        )

    finally:
        tickets_module.TicketService = original_service

    assert result is expected_ticket

    service.get_ticket.assert_called_once_with(
        ticket_id,
        current_user,
    )

def test_delete_ticket_uses_current_user():
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    service.delete_ticket.return_value = True

    tickets_module = __import__(
        "app.api.routes.tickets",
        fromlist=["TicketService"],
    )

    original_service = tickets_module.TicketService

    try:
        tickets_module.TicketService = lambda db: service

        result = tickets_module.delete_ticket(
            ticket_id=ticket_id,
            db=db,
            current_user=current_user,
        )

    finally:
        tickets_module.TicketService = original_service

    assert result is None

    service.delete_ticket.assert_called_once_with(
        ticket_id,
        current_user,
    )

def test_delete_ticket_returns_404_when_ticket_not_found():
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    service.delete_ticket.return_value = False

    tickets_module = __import__(
        "app.api.routes.tickets",
        fromlist=["TicketService"],
    )

    original_service = tickets_module.TicketService

    try:
        tickets_module.TicketService = lambda db: service

        try:
            tickets_module.delete_ticket(
                ticket_id=ticket_id,
                db=db,
                current_user=current_user,
            )
            assert False, "Expected HTTPException"
        except Exception as exc:
            assert exc.status_code == 404
            assert exc.detail == "Ticket not found"

    finally:
        tickets_module.TicketService = original_service

    service.delete_ticket.assert_called_once_with(
        ticket_id,
        current_user,
    )