from unittest.mock import MagicMock
from uuid import uuid4

from app.models.knowledge_document import KnowledgeDocument
from app.models.user import User
from app.schemas.knowledge_document import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
)
from app.services.knowledge_document import KnowledgeDocumentService


def make_user(organization_id):
    return User(
        id=uuid4(),
        organization_id=organization_id,
    )


def make_document(organization_id, uploaded_by):
    return KnowledgeDocument(
        id=uuid4(),
        organization_id=organization_id,
        uploaded_by=uploaded_by,
        title="Test Document",
        file_name="test.pdf",
        file_type="application/pdf",
        file_size=1024,
        storage_path="/documents/test.pdf",
        status="UPLOADED",
    )


def test_create_document():
    db = MagicMock()
    service = KnowledgeDocumentService(db)

    organization_id = uuid4()
    current_user = make_user(organization_id)

    db.scalar.side_effect = [
        1,
        current_user,
    ]

    data = KnowledgeDocumentCreate(
        title="Test Document",
        file_name="test.pdf",
        file_type="application/pdf",
        file_size=1024,
        storage_path="/documents/test.pdf",
    )

    result = service.create_document(
        data=data,
        current_user=current_user,
    )

    assert result.organization_id == organization_id
    assert result.uploaded_by == current_user.id
    assert result.title == "Test Document"
    assert result.status == "UPLOADED"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_get_document_same_organization():
    db = MagicMock()
    service = KnowledgeDocumentService(db)

    organization_id = uuid4()
    current_user = make_user(organization_id)
    document = make_document(
        organization_id,
        current_user.id,
    )

    service.repository.get_by_id = MagicMock(
        return_value=document
    )

    result = service.get_document(
        document_id=document.id,
        current_user=current_user,
    )

    assert result == document


def test_get_document_other_organization():
    db = MagicMock()
    service = KnowledgeDocumentService(db)

    organization_id = uuid4()
    other_organization_id = uuid4()

    current_user = make_user(organization_id)
    document = make_document(
        other_organization_id,
        uuid4(),
    )

    service.repository.get_by_id = MagicMock(
        return_value=document
    )

    result = service.get_document(
        document_id=document.id,
        current_user=current_user,
    )

    assert result is None


def test_list_documents():
    db = MagicMock()
    service = KnowledgeDocumentService(db)

    organization_id = uuid4()
    current_user = make_user(organization_id)

    documents = [
        make_document(organization_id, current_user.id),
        make_document(organization_id, current_user.id),
    ]

    service.repository.list_by_organization = MagicMock(
        return_value=documents
    )

    result = service.list_documents(
        current_user=current_user,
        limit=50,
        offset=0,
    )

    assert result == documents

    service.repository.list_by_organization.assert_called_once_with(
        organization_id=organization_id,
        limit=50,
        offset=0,
    )


def test_update_document():
    db = MagicMock()
    service = KnowledgeDocumentService(db)

    organization_id = uuid4()
    current_user = make_user(organization_id)
    document = make_document(
        organization_id,
        current_user.id,
    )

    service.repository.get_by_id = MagicMock(
        return_value=document
    )

    data = KnowledgeDocumentUpdate(
        title="Updated Document",
        status="PROCESSED",
    )

    result = service.update_document(
        document_id=document.id,
        data=data,
        current_user=current_user,
    )

    assert result == document
    assert document.title == "Updated Document"
    assert document.status == "PROCESSED"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(document)


def test_delete_document():
    db = MagicMock()
    service = KnowledgeDocumentService(db)

    organization_id = uuid4()
    current_user = make_user(organization_id)
    document = make_document(
        organization_id,
        current_user.id,
    )

    service.repository.get_by_id = MagicMock(
        return_value=document
    )

    service.repository.delete = MagicMock()

    result = service.delete_document(
        document_id=document.id,
        current_user=current_user,
    )

    assert result is True

    service.repository.delete.assert_called_once_with(
        document
    )
    db.commit.assert_called_once()