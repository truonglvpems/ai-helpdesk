from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.core.database import get_db
from app.core.permissions import Permission
from app.models.user import User
from app.schemas.knowledge_document import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
)

from app.schemas.knowledge_document import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentUpdate,
)

from app.services.knowledge_document import KnowledgeDocumentService


router = APIRouter(
    prefix="/knowledge-documents",
    tags=["Knowledge Documents"],
)


@router.post(
    "",
    response_model=KnowledgeDocumentResponse,
    status_code=201,
)
def create_knowledge_document(
    data: KnowledgeDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_CREATE
        )
    ),
):
    service = KnowledgeDocumentService(db)

    try:
        return service.create_document(
            data,
            current_user,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get(
    "/{document_id}",
    response_model=KnowledgeDocumentResponse,
)
def get_knowledge_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_READ
        )
    ),
):
    service = KnowledgeDocumentService(db)

    document = service.get_document(
        document_id,
        current_user,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge document not found",
        )

    return document

@router.get(
    "",
    response_model=list[KnowledgeDocumentResponse],
)
def list_knowledge_documents(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_LIST
        )
    ),
):
    service = KnowledgeDocumentService(db)

    return service.list_documents(
        current_user=current_user,
        limit=limit,
        offset=offset,
    )

@router.patch(
    "/{document_id}",
    response_model=KnowledgeDocumentResponse,
)
def update_knowledge_document(
    document_id: UUID,
    data: KnowledgeDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_UPDATE
        )
    ),
):
    service = KnowledgeDocumentService(db)

    document = service.update_document(
        document_id,
        data,
        current_user,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge document not found",
        )

    return document

@router.delete(
    "/{document_id}",
    status_code=204,
)
def delete_knowledge_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.KNOWLEDGE_DOCUMENT_DELETE
        )
    ),
):
    service = KnowledgeDocumentService(db)

    deleted = service.delete_document(
        document_id,
        current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Knowledge document not found",
        )

    return None