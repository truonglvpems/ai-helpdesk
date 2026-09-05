from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument


class KnowledgeDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        document: KnowledgeDocument,
    ) -> KnowledgeDocument:
        self.db.add(document)
        return document

    def get_by_id(
        self,
        document_id: UUID,
    ) -> KnowledgeDocument | None:
        return self.db.scalar(
            select(KnowledgeDocument).where(
                KnowledgeDocument.id == document_id
            )
        )

    def list_by_organization(
        self,
        organization_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeDocument]:
        return list(
            self.db.scalars(
                select(KnowledgeDocument)
                .where(
                    KnowledgeDocument.organization_id
                    == organization_id
                )
                .order_by(
                    KnowledgeDocument.created_at.desc()
                )
                .limit(limit)
                .offset(offset)
            )
        )

    def update(
        self,
        document: KnowledgeDocument,
    ) -> KnowledgeDocument:
        self.db.add(document)
        return document

    def delete(
        self,
        document: KnowledgeDocument,
    ) -> None:
        self.db.delete(document)