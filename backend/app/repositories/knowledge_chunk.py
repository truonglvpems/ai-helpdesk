from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk


class KnowledgeChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        chunk: KnowledgeChunk,
    ) -> KnowledgeChunk:
        self.db.add(chunk)
        return chunk

    def get_by_id(
        self,
        chunk_id: UUID,
    ) -> KnowledgeChunk | None:
        return self.db.scalar(
            select(KnowledgeChunk).where(
                KnowledgeChunk.id == chunk_id
            )
        )

    def list_by_document(
        self,
        document_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[KnowledgeChunk]:
        return list(
            self.db.scalars(
                select(KnowledgeChunk)
                .where(
                    KnowledgeChunk.document_id == document_id
                )
                .order_by(
                    KnowledgeChunk.chunk_index.asc()
                )
                .limit(limit)
                .offset(offset)
            )
        )

    def update(
        self,
        chunk: KnowledgeChunk,
    ) -> KnowledgeChunk:
        self.db.add(chunk)
        return chunk

    def delete(
        self,
        chunk: KnowledgeChunk,
    ) -> None:
        self.db.delete(chunk)