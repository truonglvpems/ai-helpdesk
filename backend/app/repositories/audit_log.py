from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        audit_log: AuditLog,
    ) -> AuditLog:
        self.db.add(audit_log)
        self.db.flush()
        self.db.refresh(audit_log)

        return audit_log

    def get_by_id(
        self,
        audit_log_id: UUID,
    ) -> AuditLog | None:
        stmt = select(AuditLog).where(
            AuditLog.id == audit_log_id
        )

        return self.db.scalar(stmt)

    def list_by_organization(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.organization_id == organization_id
            )
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(
            self.db.scalars(stmt).all()
        )