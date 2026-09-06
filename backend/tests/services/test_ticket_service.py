import pytest
from uuid import uuid4
from unittest.mock import MagicMock, patch

from app.models.user import User
from app.services.ticket import TicketService
from app.schemas.ticket import TicketCreate, TicketUpdate


def make_current_user(
    user_id,
    organization_id,
):
    return User(
        id=user_id,
        organization_id=organization_id,
        auth_user_id=uuid4(),
        email=f"{user_id}@example.com",
        full_name="Tenant Test User",
        role="EMPLOYEE",
        status="active",
    )


def test_create_ticket_uses_current_user_tenant_identity():
    user_id = uuid4()
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    data = TicketCreate(
        category_id=None,
        title="Tenant scope test",
        description="Testing authenticated tenant identity",
        priority="MEDIUM",
    )

    db = MagicMock()

    db.scalar.side_effect = [
        1,
        current_user,
    ]

    repository = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    ticket = service.create_ticket(
        data,
        current_user,
    )

    assert ticket.organization_id == user_organization_id
    assert ticket.created_by == user_id

    repository.create.assert_called_once_with(ticket)
    db.commit.assert_called_once()
    assert db.refresh.call_args_list[0].args == (ticket,)


def test_create_ticket_ignores_client_tenant_identity():
    user_id = uuid4()
    user_organization_id = uuid4()

    fake_organization_id = uuid4()
    fake_created_by = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    data = TicketCreate(
        category_id=None,
        title="Tenant spoofing test",
        description="Client must not control tenant identity",
        priority="MEDIUM",
    )

    db = MagicMock()

    db.scalar.side_effect = [
        1,
        current_user,
    ]

    repository = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    ticket = service.create_ticket(
        data,
        current_user,
    )

    assert ticket.organization_id == user_organization_id
    assert ticket.created_by == user_id

    assert ticket.organization_id != fake_organization_id
    assert ticket.created_by != fake_created_by

def test_create_ticket_denied_by_resource_policy():
    user_id = uuid4()
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    data = TicketCreate(
        category_id=None,
        title="Create policy test",
        description="User must not create ticket when policy denies",
        priority="MEDIUM",
    )

    db = MagicMock()
    db.scalar.side_effect = [
        1,
        current_user,
    ]

    repository = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_create",
        return_value=False,
    ) as mock_can_create:
        with pytest.raises(
            PermissionError,
            match="User is not allowed to create ticket",
        ):
            service.create_ticket(
                data=data,
                current_user=current_user,
            )

    mock_can_create.assert_called_once_with(
        current_user,
    )

    repository.create.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

def test_create_ticket_allowed_by_resource_policy():
    user_id = uuid4()
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    data = TicketCreate(
        category_id=None,
        title="Create policy allowed test",
        description="User is allowed to create ticket",
        priority="MEDIUM",
    )

    db = MagicMock()
    db.scalar.side_effect = [
        1,
        current_user,
    ]

    repository = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_create",
        return_value=True,
    ) as mock_can_create:
        ticket = service.create_ticket(
            data=data,
            current_user=current_user,
        )

    mock_can_create.assert_called_once_with(
        current_user,
    )

    assert ticket.organization_id == user_organization_id
    assert ticket.created_by == user_id

    repository.create.assert_called_once_with(ticket)
    db.commit.assert_called_once()
    assert db.refresh.call_args_list[0].args == (ticket,)

def test_get_ticket_uses_current_user_organization():
    user_id = uuid4()
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    repository = MagicMock()
    expected_ticket = MagicMock()

    repository.get_by_id.return_value = expected_ticket

    service = TicketService.__new__(TicketService)
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_read",
        return_value=True,
    ):
        result = service.get_ticket(
            ticket_id=ticket_id,
            current_user=current_user,
        )

    assert result is expected_ticket

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        user_organization_id,
    )

def test_list_tickets_filters_tickets_denied_by_resource_policy():
    user_id = uuid4()
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    ticket_allowed = MagicMock()
    ticket_denied = MagicMock()
    ticket_allowed.id = uuid4()
    ticket_denied.id = uuid4()

    repository = MagicMock()
    repository.list_by_organization.return_value = [
        ticket_allowed,
        ticket_denied,
    ]

    service = TicketService.__new__(TicketService)
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_read",
        side_effect=[True, False],
    ) as mock_can_read:
        result = service.list_tickets(
            current_user=current_user,
            limit=50,
            offset=0,
        )

    assert result == [ticket_allowed]

    repository.list_by_organization.assert_called_once_with(
        organization_id=user_organization_id,
        limit=50,
        offset=0,
    )

    assert mock_can_read.call_count == 2
    mock_can_read.assert_any_call(
        current_user,
        ticket_allowed,
    )
    mock_can_read.assert_any_call(
        current_user,
        ticket_denied,
    )

def test_update_ticket_uses_current_user_organization():
    user_id = uuid4()
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    ticket_id = uuid4()

    data = TicketUpdate(
        title="Updated title",
    )

    db = MagicMock()
    repository = MagicMock()

    ticket = MagicMock()
    ticket.organization_id = user_organization_id

    repository.get_by_id.return_value = ticket

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_update",
        return_value=True,
    ):
        result = service.update_ticket(
            ticket_id,
            data,
            current_user,
        )

    assert result == ticket

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        user_organization_id,
    )

def test_delete_ticket_uses_current_user_organization():
    user_id = uuid4()
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    repository = MagicMock()
    ticket = MagicMock()

    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_delete",
        return_value=True,
    ):
        result = service.delete_ticket(
            ticket_id,
            current_user,
        )

    assert result is True

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        user_organization_id,
    )

    repository.delete.assert_called_once_with(ticket)
    db.commit.assert_called_once()

def test_delete_ticket_denied_by_resource_policy():
    user_id = uuid4()
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    repository = MagicMock()
    ticket = MagicMock()

    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_delete",
        return_value=False,
    ):
        result = service.delete_ticket(
            ticket_id,
            current_user,
        )

    assert result is False

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        user_organization_id,
    )

    repository.delete.assert_not_called()
    db.commit.assert_not_called()


def test_delete_ticket_cannot_delete_other_organization_ticket():
    user_id = uuid4()
    user_organization_id = uuid4()
    other_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    repository = MagicMock()

    # Repository tenant scope prevents access to
    # a ticket belonging to another organization.
    repository.get_by_id.return_value = None

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    result = service.delete_ticket(
        ticket_id,
        current_user,
    )

    assert result is False

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        user_organization_id,
    )

    repository.delete.assert_not_called()
    db.commit.assert_not_called()


def test_delete_ticket_returns_false_when_ticket_not_found():
    user_id = uuid4()
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    repository = MagicMock()
    repository.get_by_id.return_value = None

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    result = service.delete_ticket(
        ticket_id,
        current_user,
    )

    assert result is False

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        user_organization_id,
    )

    repository.delete.assert_not_called()
    db.commit.assert_not_called()

def test_update_ticket_cannot_update_other_organization_ticket():
    user_id = uuid4()
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=user_organization_id,
    )

    data = TicketUpdate(
        title="Unauthorized tenant update",
    )

    repository = MagicMock()
    repository.get_by_id.return_value = None

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    result = service.update_ticket(
        ticket_id,
        data,
        current_user,
    )

    assert result is None

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        user_organization_id,
    )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_update_assignment_assign():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    assignee_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.assigned_to = None

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()
    db.scalar.return_value = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_assign",
        return_value=True,
    ) as mock_policy:
        result = service.update_assignment(
            ticket_id=ticket_id,
            assigned_to=assignee_id,
            current_user=current_user,
        )

    assert result == ticket
    assert ticket.assigned_to == assignee_id
    mock_policy.assert_called_once_with(
        current_user,
        ticket,
    )
    repository.update.assert_called_once_with(ticket)
    db.commit.assert_called_once()
    assert db.refresh.call_args_list[0].args == (ticket,)


def test_update_assignment_unassign():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    assignee_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.assigned_to = assignee_id

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_unassign",
        return_value=True,
    ) as mock_policy:
        result = service.update_assignment(
            ticket_id=ticket_id,
            assigned_to=None,
            current_user=current_user,
        )

    assert result == ticket
    assert ticket.assigned_to is None
    mock_policy.assert_called_once_with(
        current_user,
        ticket,
    )
    repository.update.assert_called_once_with(ticket)
    db.commit.assert_called_once()
    assert db.refresh.call_args_list[0].args == (ticket,)


def test_update_assignment_reassign():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    old_assignee_id = uuid4()
    new_assignee_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.assigned_to = old_assignee_id

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()
    db.scalar.return_value = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_reassign",
        return_value=True,
    ) as mock_policy:
        result = service.update_assignment(
            ticket_id=ticket_id,
            assigned_to=new_assignee_id,
            current_user=current_user,
        )

    assert result == ticket
    assert ticket.assigned_to == new_assignee_id
    mock_policy.assert_called_once_with(
        current_user,
        ticket,
    )
    repository.update.assert_called_once_with(ticket)
    db.commit.assert_called_once()
    assert db.refresh.call_args_list[0].args == (ticket,)


def test_update_assignment_denied_by_assign_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    assignee_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.assigned_to = None

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_assign",
        return_value=False,
    ) as mock_policy:
        result = service.update_assignment(
            ticket_id=ticket_id,
            assigned_to=assignee_id,
            current_user=current_user,
        )

    assert result is None

    mock_policy.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_update_assignment_denied_by_unassign_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    assignee_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.assigned_to = assignee_id

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_unassign",
        return_value=False,
    ) as mock_policy:
        result = service.update_assignment(
            ticket_id=ticket_id,
            assigned_to=None,
            current_user=current_user,
        )

    assert result is None

    mock_policy.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_update_assignment_denied_by_reassign_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    old_assignee_id = uuid4()
    new_assignee_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.assigned_to = old_assignee_id

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_reassign",
        return_value=False,
    ) as mock_policy:
        result = service.update_assignment(
            ticket_id=ticket_id,
            assigned_to=new_assignee_id,
            current_user=current_user,
        )

    assert result is None

    mock_policy.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()



def test_update_status_allowed_by_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.status = "OPEN"

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_change_status",
        return_value=True,
    ) as mock_can_change_status:
        result = service.update_status(
            ticket_id=ticket_id,
            status="IN_PROGRESS",
            current_user=current_user,
        )

    assert result == ticket
    assert ticket.status == "IN_PROGRESS"

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        organization_id,
    )

    mock_can_change_status.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.update.assert_called_once_with(ticket)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ticket)

@pytest.mark.parametrize(
    ("from_status", "to_status"),
    [
        ("OPEN", "IN_PROGRESS"),
        ("IN_PROGRESS", "WAITING_FOR_USER"),
        ("IN_PROGRESS", "WAITING_FOR_VENDOR"),
        ("IN_PROGRESS", "RESOLVED"),
        ("WAITING_FOR_USER", "IN_PROGRESS"),
        ("WAITING_FOR_VENDOR", "IN_PROGRESS"),
        ("RESOLVED", "IN_PROGRESS"),
        ("RESOLVED", "CLOSED"),
    ],
)
def test_update_status_accepts_valid_transitions(
    from_status,
    to_status,
):
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.status = from_status

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_change_status",
        return_value=True,
    ), patch(
        "app.services.ticket.TicketPolicy.can_close",
        return_value=True,
    ), patch(
        "app.services.ticket.TicketPolicy.can_reopen",
        return_value=True,
    ):
        result = service.update_status(
            ticket_id=ticket_id,
            status=to_status,
            current_user=current_user,
        )

    assert result == ticket
    assert ticket.status == to_status
    repository.update.assert_called_once_with(ticket)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(ticket)

def test_update_status_rejects_invalid_transition():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.status = "OPEN"

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_change_status",
        return_value=True,
    ) as mock_can_change_status:
        with pytest.raises(
            ValueError,
            match="Invalid ticket status transition: OPEN -> RESOLVED",
        ):
            service.update_status(
                ticket_id=ticket_id,
                status="RESOLVED",
                current_user=current_user,
            )

    assert ticket.status == "OPEN"

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        organization_id,
    )

    mock_can_change_status.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

def test_update_status_denied_by_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.status = "OPEN"

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_change_status",
        return_value=False,
    ) as mock_can_change_status:
        result = service.update_status(
            ticket_id=ticket_id,
            status="IN_PROGRESS",
            current_user=current_user,
        )

    assert result is None
    assert ticket.status == "OPEN"

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        organization_id,
    )

    mock_can_change_status.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_update_status_returns_none_when_ticket_not_found():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    repository = MagicMock()
    repository.get_by_id.return_value = None

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    result = service.update_status(
        ticket_id=ticket_id,
        status="IN_PROGRESS",
        current_user=current_user,
    )

    assert result is None

    repository.get_by_id.assert_called_once_with(
        ticket_id,
        organization_id,
    )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

def test_update_status_close_requires_close_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.status = "RESOLVED"

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_change_status",
        return_value=True,
    ), patch(
        "app.services.ticket.TicketPolicy.can_close",
        return_value=False,
    ):
        with pytest.raises(PermissionError):
            service.update_status(
                ticket_id=ticket_id,
                status="CLOSED",
                current_user=current_user,
            )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_update_status_reopen_requires_reopen_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock()
    ticket.organization_id = organization_id
    ticket.status = "RESOLVED"

    repository = MagicMock()
    repository.get_by_id.return_value = ticket

    db = MagicMock()

    service = TicketService.__new__(TicketService)
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket.TicketPolicy.can_change_status",
        return_value=True,
    ), patch(
        "app.services.ticket.TicketPolicy.can_reopen",
        return_value=False,
    ):
        with pytest.raises(PermissionError):
            service.update_status(
                ticket_id=ticket_id,
                status="IN_PROGRESS",
                current_user=current_user,
            )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()
