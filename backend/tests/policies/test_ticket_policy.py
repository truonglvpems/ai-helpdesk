import uuid

from app.models.ticket import Ticket
from app.models.user import User
from app.policies.ticket import TicketPolicy


ORG_A = uuid.uuid4()
ORG_B = uuid.uuid4()

ADMIN_ID = uuid.uuid4()
TECHNICIAN_ID = uuid.uuid4()
EMPLOYEE_ID = uuid.uuid4()
OTHER_EMPLOYEE_ID = uuid.uuid4()


def make_user(
    user_id: uuid.UUID,
    role: str,
    organization_id: uuid.UUID,
) -> User:
    return User(
        id=user_id,
        role=role,
        organization_id=organization_id,
        auth_user_id=uuid.uuid4(),
        email=f"{user_id}@example.com",
        full_name=f"Test {role}",
        status="active",
    )


def make_ticket(
    organization_id: uuid.UUID,
    created_by: uuid.UUID,
    assigned_to: uuid.UUID | None = None,
) -> Ticket:
    return Ticket(
        id=uuid.uuid4(),
        organization_id=organization_id,
        created_by=created_by,
        assigned_to=assigned_to,
        title="Test ticket",
        description="Test description",
        status="OPEN",
        priority="MEDIUM",
    )


def test_admin_can_read_ticket_in_same_organization():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_read(user, ticket) is True


def test_admin_cannot_read_ticket_from_other_organization():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_B,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_read(user, ticket) is False


def test_technician_can_read_ticket_in_same_organization():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_read(user, ticket) is True


def test_technician_cannot_read_ticket_from_other_organization():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_B,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_read(user, ticket) is False


def test_employee_can_read_own_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_read(user, ticket) is True


def test_employee_cannot_read_other_employee_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        OTHER_EMPLOYEE_ID,
    )

    assert TicketPolicy.can_read(user, ticket) is False


def test_employee_cannot_read_ticket_from_other_organization():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_B,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_read(user, ticket) is False


def test_admin_can_delete_ticket_in_same_organization():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_delete(user, ticket) is True


def test_admin_cannot_delete_ticket_from_other_organization():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_B,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_delete(user, ticket) is False


def test_technician_cannot_delete_ticket():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_delete(user, ticket) is False


def test_employee_cannot_delete_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_delete(user, ticket) is False


def test_employee_can_update_own_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_update(user, ticket) is True


def test_employee_cannot_update_other_employee_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        OTHER_EMPLOYEE_ID,
    )

    assert TicketPolicy.can_update(user, ticket) is False


def test_technician_can_update_ticket_in_same_organization():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_update(user, ticket) is True


def test_technician_cannot_update_ticket_from_other_organization():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_B,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_update(user, ticket) is False


def test_admin_can_create_ticket():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    assert TicketPolicy.can_create(user) is True


def test_technician_can_create_ticket():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    assert TicketPolicy.can_create(user) is True


def test_employee_can_create_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    assert TicketPolicy.can_create(user) is True


def test_admin_can_assign_ticket():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_assign(user, ticket) is True


def test_technician_can_assign_ticket():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_assign(user, ticket) is True


def test_employee_cannot_assign_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_assign(user, ticket) is False


def test_admin_can_unassign_ticket():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
        TECHNICIAN_ID,
    )

    assert TicketPolicy.can_unassign(user, ticket) is True


def test_technician_can_unassign_ticket():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
        TECHNICIAN_ID,
    )

    assert TicketPolicy.can_unassign(user, ticket) is True


def test_employee_cannot_unassign_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
        TECHNICIAN_ID,
    )

    assert TicketPolicy.can_unassign(user, ticket) is False


def test_admin_can_reassign_ticket():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
        TECHNICIAN_ID,
    )

    assert TicketPolicy.can_reassign(user, ticket) is True


def test_technician_can_reassign_ticket():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
        TECHNICIAN_ID,
    )

    assert TicketPolicy.can_reassign(user, ticket) is True


def test_employee_cannot_reassign_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_reassign(user, ticket) is False


def test_admin_can_comment_on_ticket():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_comment(user, ticket) is True


def test_technician_can_comment_on_ticket():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_comment(user, ticket) is True


def test_employee_can_comment_on_own_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_comment(user, ticket) is True


def test_employee_cannot_comment_on_other_employee_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        OTHER_EMPLOYEE_ID,
    )

    assert TicketPolicy.can_comment(user, ticket) is False

def test_user_cannot_comment_on_other_organization_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_B,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_comment(user, ticket) is False

def test_admin_can_change_status():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_change_status(user, ticket) is True


def test_technician_can_change_status():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_change_status(user, ticket) is True


def test_employee_cannot_change_status():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_change_status(user, ticket) is False


def test_admin_can_change_priority():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_change_priority(user, ticket) is True


def test_technician_can_change_priority():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_change_priority(user, ticket) is True


def test_employee_cannot_change_priority():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_change_priority(user, ticket) is False


def test_admin_can_close_ticket():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_close(user, ticket) is True


def test_technician_can_close_ticket():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_close(user, ticket) is True


def test_employee_cannot_close_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_close(user, ticket) is False


def test_admin_can_reopen_ticket():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_reopen(user, ticket) is True


def test_technician_can_reopen_ticket():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_reopen(user, ticket) is True


def test_employee_can_reopen_own_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_reopen(user, ticket) is True


def test_employee_cannot_reopen_other_employee_ticket():
    user = make_user(
        EMPLOYEE_ID,
        "EMPLOYEE",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_A,
        OTHER_EMPLOYEE_ID,
    )

    assert TicketPolicy.can_reopen(user, ticket) is False


def test_admin_cannot_assign_ticket_from_other_organization():
    user = make_user(
        ADMIN_ID,
        "ADMIN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_B,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_assign(user, ticket) is False


def test_technician_cannot_change_priority_of_other_organization():
    user = make_user(
        TECHNICIAN_ID,
        "TECHNICIAN",
        ORG_A,
    )

    ticket = make_ticket(
        ORG_B,
        EMPLOYEE_ID,
    )

    assert TicketPolicy.can_change_priority(user, ticket) is False