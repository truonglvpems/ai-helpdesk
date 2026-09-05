from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument
from app.models.organization import Organization
from app.models.user import User
from app.repositories.knowledge_document import KnowledgeDocumentRepository
from app.schemas.knowledge_document import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
)


class KnowledgeDocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = KnowledgeDocumentRepository(db)

    def create_document(
        self,
        data: KnowledgeDocumentCreate,
        current_user: User,
    ) -> KnowledgeDocument:
        # ---------------------------------------------------------
        # Tenant identity comes from authenticated user
        # ---------------------------------------------------------
        organization_id = current_user.organization_id
        uploaded_by = current_user.id

        # ---------------------------------------------------------
        # Validate organization
        # ---------------------------------------------------------
        organization_exists = self.db.scalar(
            select(1).where(
                Organization.id == organization_id
            )
        )

        if organization_exists is None:
            raise ValueError("Organization not found")

        # ---------------------------------------------------------
        # Validate uploader
        # ---------------------------------------------------------
        uploader = self.db.scalar(
            select(User).where(
                User.id == uploaded_by,
                User.organization_id == organization_id,
            )
        )

        if uploader is None:
            raise ValueError(
                "Uploaded-by user does not belong to organization"
            )

        # ---------------------------------------------------------
        # Create document
        # ---------------------------------------------------------
        document = KnowledgeDocument(
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            title=data.title,
            file_name=data.file_name,
            file_type=data.file_type,
            file_size=data.file_size,
            storage_path=data.storage_path,
            status="UPLOADED",
        )

        self.repository.create(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def get_document(
        self,
        document_id: UUID,
        current_user: User,
    ) -> KnowledgeDocument | None:
        document = self.repository.get_by_id(document_id)

        if document is None:
            return None

        # ---------------------------------------------------------
        # Tenant scope
        # ---------------------------------------------------------
        if document.organization_id != current_user.organization_id:
            return None

        return document

    def list_documents(
        self,
        current_user: User,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeDocument]:
        return self.repository.list_by_organization(
            organization_id=current_user.organization_id,
            limit=limit,
            offset=offset,
        )

    def update_document(
        self,
        document_id: UUID,
        data: KnowledgeDocumentUpdate,
        current_user: User,
    ) -> KnowledgeDocument | None:
        document = self.repository.get_by_id(document_id)

        if document is None:
            return None

        # ---------------------------------------------------------
        # Tenant scope
        # ---------------------------------------------------------
        if document.organization_id != current_user.organization_id:
            return None

        # ---------------------------------------------------------
        # Update fields
        # ---------------------------------------------------------
        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(document, field, value)

        self.repository.update(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def delete_document(
        self,
        document_id: UUID,
        current_user: User,
    ) -> bool:
        document = self.repository.get_by_id(document_id)

        if document is None:
            return False

        # ---------------------------------------------------------
        # Tenant scope
        # ---------------------------------------------------------
        if document.organization_id != current_user.organization_id:
            return False

        self.repository.delete(document)
        self.db.commit()

        return True