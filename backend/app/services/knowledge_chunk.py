from uuid import UUID

from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.user import User
from app.repositories.knowledge_chunk import KnowledgeChunkRepository
from app.schemas.knowledge_chunk import KnowledgeChunkCreate


class KnowledgeChunkService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = KnowledgeChunkRepository(db)

    def _document_belongs_to_user_organization(
        self,
        document_id: UUID,
        current_user: User,
    ) -> bool:
        document = self.db.get(
            KnowledgeDocument,
            document_id,
        )

        if document is None:
            return False

        return (
            document.organization_id
            == current_user.organization_id
        )

    def create_chunk(
        self,
        data: KnowledgeChunkCreate,
        current_user: User,
    ) -> KnowledgeChunk | None:
        if not self._document_belongs_to_user_organization(
            data.document_id,
            current_user,
        ):
            return None

        chunk = KnowledgeChunk(
            document_id=data.document_id,
            content=data.content,
            chunk_index=data.chunk_index,
        )

        self.repository.create(chunk)
        self.db.commit()
        self.db.refresh(chunk)

        return chunk

    def get_chunk(
        self,
        chunk_id: UUID,
        current_user: User,
    ) -> KnowledgeChunk | None:
        chunk = self.repository.get_by_id(chunk_id)

        if chunk is None:
            return None

        if not self._document_belongs_to_user_organization(
            chunk.document_id,
            current_user,
        ):
            return None

        return chunk

    def list_chunks(
        self,
        document_id: UUID,
        current_user: User,
        limit: int = 100,
        offset: int = 0,
    ) -> list[KnowledgeChunk]:
        if not self._document_belongs_to_user_organization(
            document_id,
            current_user,
        ):
            return []

        return self.repository.list_by_document(
            document_id=document_id,
            limit=limit,
            offset=offset,
        )

    def update_chunk(
        self,
        chunk_id: UUID,
        data: KnowledgeChunkCreate,
        current_user: User,
    ) -> KnowledgeChunk | None:
        chunk = self.repository.get_by_id(chunk_id)

        if chunk is None:
            return None

        if not self._document_belongs_to_user_organization(
            chunk.document_id,
            current_user,
        ):
            return None

        chunk.content = data.content
        chunk.chunk_index = data.chunk_index

        self.repository.update(chunk)
        self.db.commit()
        self.db.refresh(chunk)

        return chunk

    def delete_chunk(
        self,
        chunk_id: UUID,
        current_user: User,
    ) -> bool:
        chunk = self.repository.get_by_id(chunk_id)

        if chunk is None:
            return False

        if not self._document_belongs_to_user_organization(
            chunk.document_id,
            current_user,
        ):
            return False

        self.repository.delete(chunk)
        self.db.commit()

        return True