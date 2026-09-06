from uuid import uuid4
from unittest.mock import MagicMock

from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.audit_log import AuditLogService


def make_user():
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.organization_id = uuid4()

    return user


def test_create_log():
    db = MagicMock()
    service = AuditLogService(db)

    current_user = make_user()
    entity_id = uuid4()

    result = service.create_log(
        current_user=current_user,
        action="ticket.created",
        entity_type="ticket",
        entity_id=entity_id,
        metadata_json={"title": "Test ticket"},
    )

    assert isinstance(result, AuditLog)
    assert result.organization_id == current_user.organization_id
    assert result.user_id == current_user.id
    assert result.action == "ticket.created"
    assert result.entity_type == "ticket"
    assert result.entity_id == entity_id
    assert result.metadata_json == {"title": "Test ticket"}

    db.commit.assert_not_called()
    assert db.refresh.call_count == 1


def test_create_log_requires_organization():
    db = MagicMock()
    service = AuditLogService(db)

    current_user = make_user()
    current_user.organization_id = None

    try:
        service.create_log(
            current_user=current_user,
            action="ticket.created",
            entity_type="ticket",
        )
        assert False
    except ValueError as exc:
        assert str(exc) == "Organization is required for audit log"


def test_get_log_same_organization():
    db = MagicMock()
    service = AuditLogService(db)

    current_user = make_user()

    audit_log = AuditLog(
        id=uuid4(),
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="ticket.updated",
        entity_type="ticket",
        entity_id=uuid4(),
        metadata_json={"field": "status"},
    )

    service.repository = MagicMock()
    service.repository.get_by_id.return_value = audit_log

    result = service.get_log(
        audit_log.id,
        current_user,
    )

    assert result is audit_log

    service.repository.get_by_id.assert_called_once_with(
        audit_log.id
    )


def test_get_log_other_organization_returns_none():
    db = MagicMock()
    service = AuditLogService(db)

    current_user = make_user()

    audit_log = AuditLog(
        id=uuid4(),
        organization_id=uuid4(),
        user_id=uuid4(),
        action="ticket.updated",
        entity_type="ticket",
        entity_id=uuid4(),
        metadata_json={"field": "status"},
    )

    service.repository = MagicMock()
    service.repository.get_by_id.return_value = audit_log

    result = service.get_log(
        audit_log.id,
        current_user,
    )

    assert result is None


def test_list_logs_uses_current_user_organization():
    db = MagicMock()
    service = AuditLogService(db)

    current_user = make_user()

    audit_logs = [
        MagicMock(spec=AuditLog),
        MagicMock(spec=AuditLog),
    ]

    service.repository = MagicMock()
    service.repository.list_by_organization.return_value = audit_logs

    result = service.list_logs(
        current_user=current_user,
        limit=20,
        offset=10,
    )

    assert result == audit_logs

    service.repository.list_by_organization.assert_called_once_with(
        organization_id=current_user.organization_id,
        limit=20,
        offset=10,
    )