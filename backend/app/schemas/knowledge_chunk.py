from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeChunkCreate(BaseModel):
    document_id: UUID
    content: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)


class KnowledgeChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    created_at: datetime