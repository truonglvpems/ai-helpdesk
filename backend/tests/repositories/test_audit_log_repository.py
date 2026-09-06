from uuid import uuid4
from unittest.mock import MagicMock

from app.models.audit_log import AuditLog
from app.repositories.audit_log import AuditLogRepository


def make_audit_log(
    organization_id,
):
    return AuditLog(
        id=uuid4(),
        organization_id=organization_id,
        user_id=uuid4(),
        action="ticket.created",
        entity_type="ticket",
        entity_id=uuid4(),
        metadata_json={"title": "Test ticket"},
    )


def test_create_audit_log():
    db = MagicMock()
    repository = AuditLogRepository(db)

    audit_log = make_audit_log(uuid4())

    result = repository.create(audit_log)

    assert result is audit_log
    db.add.assert_called_once_with(audit_log)
    db.flush.assert_called_once()
    db.refresh.assert_called_once_with(audit_log)


def test_get_audit_log_by_id():
    db = MagicMock()
    repository = AuditLogRepository(db)

    audit_log_id = uuid4()
    audit_log = make_audit_log(uuid4())

    db.scalar.return_value = audit_log

    result = repository.get_by_id(audit_log_id)

    assert result is audit_log
    db.scalar.assert_called_once()


def test_list_audit_logs_by_organization():
    db = MagicMock()
    repository = AuditLogRepository(db)

    organization_id = uuid4()

    audit_logs = [
        make_audit_log(organization_id),
        make_audit_log(organization_id),
    ]

    db.scalars.return_value.all.return_value = audit_logs

    result = repository.list_by_organization(
        organization_id=organization_id,
        limit=50,
        offset=0,
    )

    assert result == audit_logs
    db.scalars.assert_called_once()
    db.scalars.return_value.all.assert_called_once()