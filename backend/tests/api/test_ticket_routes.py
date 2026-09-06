from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.schemas.ticket_status import TicketStatusUpdate
from app.schemas.ticket_assignment import TicketAssignmentUpdate
from app.api.routes.tickets import (
    create_ticket,
    delete_ticket,
    get_ticket,
    list_tickets,
    update_ticket,
    update_ticket_status,
    update_ticket_assignment
)
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
        current_user=current_user,
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

def test_update_ticket_uses_current_user():
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_ticket = MagicMock()
    service.update_ticket.return_value = expected_ticket

    tickets_module = __import__(
        "app.api.routes.tickets",
        fromlist=["TicketService"],
    )

    original_service = tickets_module.TicketService

    try:
        tickets_module.TicketService = lambda db: service

        data = MagicMock()

        result = tickets_module.update_ticket(
            ticket_id=ticket_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        tickets_module.TicketService = original_service

    assert result is expected_ticket

    service.update_ticket.assert_called_once_with(
        ticket_id,
        data,
        current_user,
    )

def test_update_ticket_returns_404_when_ticket_not_found():
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    service.update_ticket.return_value = None

    tickets_module = __import__(
        "app.api.routes.tickets",
        fromlist=["TicketService"],
    )

    original_service = tickets_module.TicketService

    try:
        tickets_module.TicketService = lambda db: service

        data = MagicMock()

        try:
            tickets_module.update_ticket(
                ticket_id=ticket_id,
                data=data,
                db=db,
                current_user=current_user,
            )
            assert False, "Expected HTTPException"
        except Exception as exc:
            assert exc.status_code == 404
            assert exc.detail == "Ticket not found"

    finally:
        tickets_module.TicketService = original_service

    service.update_ticket.assert_called_once_with(
        ticket_id,
        data,
        current_user,
    )

def test_create_ticket_uses_current_user():
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_ticket = MagicMock()
    service.create_ticket.return_value = expected_ticket

    tickets_module = __import__(
        "app.api.routes.tickets",
        fromlist=["TicketService"],
    )

    original_service = tickets_module.TicketService

    try:
        tickets_module.TicketService = lambda db: service

        data = MagicMock()

        result = tickets_module.create_ticket(
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        tickets_module.TicketService = original_service

    assert result is expected_ticket

    service.create_ticket.assert_called_once_with(
        data,
        current_user,
    )

def test_update_ticket_assignment_uses_current_user():
    ticket_id = uuid4()
    assignee_id = uuid4()
    current_user = MagicMock()

    data = TicketAssignmentUpdate(
        assigned_to=assignee_id,
    )

    expected_ticket = MagicMock()

    service = MagicMock()
    service.update_assignment.return_value = expected_ticket

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        from app.api.routes.tickets import update_ticket_assignment

        db = MagicMock()

        result = update_ticket_assignment(
            ticket_id=ticket_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    assert result is expected_ticket

    service.update_assignment.assert_called_once_with(
        ticket_id=ticket_id,
        assigned_to=assignee_id,
        current_user=current_user,
    )

def test_update_ticket_assignment_returns_404_when_ticket_not_found():
    ticket_id = uuid4()
    assignee_id = uuid4()
    current_user = MagicMock()

    data = TicketAssignmentUpdate(
        assigned_to=assignee_id,
    )

    service = MagicMock()
    service.update_assignment.return_value = None

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        from app.api.routes.tickets import update_ticket_assignment

        db = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            update_ticket_assignment(
                ticket_id=ticket_id,
                data=data,
                db=db,
                current_user=current_user,
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Ticket not found"

def test_update_ticket_assignment_returns_400_for_invalid_assignee():
    ticket_id = uuid4()
    assignee_id = uuid4()
    current_user = MagicMock()

    data = TicketAssignmentUpdate(
        assigned_to=assignee_id,
    )

    service = MagicMock()
    service.update_assignment.side_effect = ValueError(
        "Assigned user does not belong to ticket organization"
    )

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        from app.api.routes.tickets import update_ticket_assignment

        db = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            update_ticket_assignment(
                ticket_id=ticket_id,
                data=data,
                db=db,
                current_user=current_user,
            )

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "Assigned user does not belong to ticket organization"
    )

def test_update_ticket_status_uses_current_user():
    ticket_id = uuid4()
    current_user = MagicMock()

    data = TicketStatusUpdate(
        status="IN_PROGRESS",
    )

    expected_ticket = MagicMock()

    service = MagicMock()
    service.update_status.return_value = expected_ticket

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        from app.api.routes.tickets import update_ticket_status

        db = MagicMock()

        result = update_ticket_status(
            ticket_id=ticket_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    assert result is expected_ticket

    service.update_status.assert_called_once_with(
        ticket_id=ticket_id,
        status="IN_PROGRESS",
        current_user=current_user,
    )


def test_update_ticket_status_returns_404_when_ticket_not_found():
    ticket_id = uuid4()
    current_user = MagicMock()

    data = TicketStatusUpdate(
        status="IN_PROGRESS",
    )

    service = MagicMock()
    service.update_status.return_value = None

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        from app.api.routes.tickets import update_ticket_status

        db = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            update_ticket_status(
                ticket_id=ticket_id,
                data=data,
                db=db,
                current_user=current_user,
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Ticket not found"


def test_update_ticket_status_passes_status_to_service():
    ticket_id = uuid4()
    current_user = MagicMock()

    data = TicketStatusUpdate(
        status="RESOLVED",
    )

    expected_ticket = MagicMock()

    service = MagicMock()
    service.update_status.return_value = expected_ticket

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        from app.api.routes.tickets import update_ticket_status

        db = MagicMock()

        result = update_ticket_status(
            ticket_id=ticket_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    assert result is expected_ticket

    service.update_status.assert_called_once_with(
        ticket_id=ticket_id,
        status="RESOLVED",
        current_user=current_user,
    )

def test_update_ticket_status_returns_400_for_invalid_transition():
    ticket_id = uuid4()
    current_user = MagicMock()

    data = TicketStatusUpdate(
        status="RESOLVED",
    )

    service = MagicMock()
    service.update_status.side_effect = ValueError(
        "Invalid ticket status transition: OPEN -> RESOLVED"
    )

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        db = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            update_ticket_status(
                ticket_id=ticket_id,
                data=data,
                db=db,
                current_user=current_user,
            )

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == "Invalid ticket status transition: OPEN -> RESOLVED"
    )

    service.update_status.assert_called_once_with(
        ticket_id=ticket_id,
        status="RESOLVED",
        current_user=current_user,
    )

def test_update_ticket_status_returns_403_when_close_not_allowed():
    ticket_id = uuid4()
    current_user = MagicMock()

    data = TicketStatusUpdate(
        status="CLOSED",
    )

    service = MagicMock()
    service.update_status.side_effect = PermissionError(
        "User is not allowed to close ticket"
    )

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        db = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            from app.api.routes.tickets import update_ticket_status

            update_ticket_status(
                ticket_id=ticket_id,
                data=data,
                db=db,
                current_user=current_user,
            )

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == "User is not allowed to close ticket"
    )


def test_update_ticket_status_returns_403_when_reopen_not_allowed():
    ticket_id = uuid4()
    current_user = MagicMock()

    data = TicketStatusUpdate(
        status="IN_PROGRESS",
    )

    service = MagicMock()
    service.update_status.side_effect = PermissionError(
        "User is not allowed to reopen ticket"
    )

    with patch(
        "app.api.routes.tickets.TicketService",
        return_value=service,
    ):
        db = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            from app.api.routes.tickets import update_ticket_status

            update_ticket_status(
                ticket_id=ticket_id,
                data=data,
                db=db,
                current_user=current_user,
            )

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == "User is not allowed to reopen ticket"
    )