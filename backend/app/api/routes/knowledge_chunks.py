from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.core.database import get_db
from app.core.permissions import Permission
from app.models.user import User

from app.schemas.knowledge_chunk import (
    KnowledgeChunkCreate,
    KnowledgeChunkResponse,
)

from app.schemas.knowledge_chunk import (
    KnowledgeChunkCreate,
    KnowledgeChunkResponse,
)

from app.services.knowledge_chunk import KnowledgeChunkService


router = APIRouter(
    prefix="/knowledge-chunks",
    tags=["Knowledge Chunks"],
)


@router.post(
    "",
    response_model=KnowledgeChunkResponse,
    status_code=201,
)
def create_knowledge_chunk(
    data: KnowledgeChunkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_UPDATE
        )
    ),
):
    service = KnowledgeChunkService(db)

    chunk = service.create_chunk(
        data,
        current_user,
    )

    if chunk is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge document not found",
        )

    return chunk

@router.get(
    "/{chunk_id}",
    response_model=KnowledgeChunkResponse,
)
def get_knowledge_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_READ
        )
    ),
):
    service = KnowledgeChunkService(db)

    chunk = service.get_chunk(
        chunk_id,
        current_user,
    )

    if chunk is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge chunk not found",
        )

    return chunk

@router.get(
    "/document/{document_id}",
    response_model=list[KnowledgeChunkResponse],
)
def list_knowledge_chunks(
    document_id: UUID,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_READ
        )
    ),
):
    service = KnowledgeChunkService(db)

    return service.list_chunks(
        document_id=document_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )

@router.patch(
    "/{chunk_id}",
    response_model=KnowledgeChunkResponse,
)
def update_knowledge_chunk(
    chunk_id: UUID,
    data: KnowledgeChunkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_UPDATE
        )
    ),
):
    service = KnowledgeChunkService(db)

    chunk = service.update_chunk(
        chunk_id,
        data,
        current_user,
    )

    if chunk is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge chunk not found",
        )

    return chunk

@router.delete(
    "/{chunk_id}",
    status_code=204,
)
def delete_knowledge_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_UPDATE
        )
    ),
):
    service = KnowledgeChunkService(db)

    deleted = service.delete_chunk(
        chunk_id,
        current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Knowledge chunk not found",
        )

    return None