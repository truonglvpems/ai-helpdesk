import uuid

import pytest
from fastapi import HTTPException

from app.api.dependencies import require_permission
from app.core.permissions import Permission
from app.models.user import User


ORG_ID = uuid.uuid4()


def make_user(role: str) -> User:
    user_id = uuid.uuid4()

    return User(
        id=user_id,
        organization_id=ORG_ID,
        auth_user_id=uuid.uuid4(),
        email=f"{user_id}@example.com",
        full_name=f"Test {role}",
        role=role,
        status="active",
    )


def test_admin_has_ticket_delete_permission():
    user = make_user("ADMIN")

    dependency = require_permission(
        Permission.TICKET_DELETE,
    )

    result = dependency(current_user=user)

    assert result is user


def test_technician_does_not_have_ticket_delete_permission():
    user = make_user("TECHNICIAN")

    dependency = require_permission(
        Permission.TICKET_DELETE,
    )

    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"


def test_employee_has_ticket_create_permission():
    user = make_user("EMPLOYEE")

    dependency = require_permission(
        Permission.TICKET_CREATE,
    )

    result = dependency(current_user=user)

    assert result is user


def test_employee_does_not_have_ticket_delete_permission():
    user = make_user("EMPLOYEE")

    dependency = require_permission(
        Permission.TICKET_DELETE,
    )

    with pytest.raises(HTTPException) as exc_info:
        dependency(current_user=user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"


def test_technician_has_ticket_update_permission():
    user = make_user("TECHNICIAN")

    dependency = require_permission(
        Permission.TICKET_UPDATE,
    )

    result = dependency(current_user=user)

    assert result is user


def test_employee_has_ticket_update_own_permission():
    user = make_user("EMPLOYEE")

    dependency = require_permission(
        Permission.TICKET_UPDATE_OWN,
    )

    result = dependency(current_user=user)

    assert result is user