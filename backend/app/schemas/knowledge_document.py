from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    file_name: str = Field(min_length=1, max_length=255)
    file_type: str = Field(min_length=1, max_length=50)
    file_size: int = Field(ge=0)
    storage_path: str = Field(min_length=1)


class KnowledgeDocumentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )


class KnowledgeDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    uploaded_by: UUID
    title: str
    file_name: str
    file_type: str
    file_size: int
    storage_path: str
    status: str
    created_at: datetime
    updated_at: datetime