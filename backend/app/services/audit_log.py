from uuid import UUID
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log import AuditLogRepository


class AuditLogService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuditLogRepository(db)

    def create_log(
        self,
        current_user: User | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        metadata_json: dict[str, Any] | None = None,
    ) -> AuditLog:
        organization_id = (
            current_user.organization_id
            if current_user is not None
            else None
        )

        if organization_id is None:
            raise ValueError(
                "Organization is required for audit log"
            )

        audit_log = AuditLog(
            organization_id=organization_id,
            user_id=(
                current_user.id
                if current_user is not None
                else None
            ),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata_json,
        )

        self.repository.create(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log

    def get_log(
        self,
        audit_log_id: UUID,
        current_user: User,
    ) -> AuditLog | None:
        audit_log = self.repository.get_by_id(
            audit_log_id
        )

        if audit_log is None:
            return None

        if audit_log.organization_id != current_user.organization_id:
            return None

        return audit_log

    def list_logs(
        self,
        current_user: User,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        return self.repository.list_by_organization(
            organization_id=current_user.organization_id,
            limit=limit,
            offset=offset,
        )