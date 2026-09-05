from uuid import uuid4
from unittest.mock import MagicMock

from app.models.knowledge_document import KnowledgeDocument
from app.repositories.knowledge_document import KnowledgeDocumentRepository


def make_document(
    organization_id,
):
    return KnowledgeDocument(
        id=uuid4(),
        organization_id=organization_id,
        uploaded_by=uuid4(),
        title="Test Document",
        file_name="test.pdf",
        file_type="application/pdf",
        file_size=1024,
        storage_path="/knowledge/test.pdf",
        status="UPLOADED",
    )


def test_create_document():
    db = MagicMock()
    repository = KnowledgeDocumentRepository(db)

    organization_id = uuid4()
    document = make_document(organization_id)

    result = repository.create(document)

    assert result is document
    db.add.assert_called_once_with(document)


def test_get_document_by_id():
    db = MagicMock()
    repository = KnowledgeDocumentRepository(db)

    document_id = uuid4()
    document = make_document(uuid4())

    db.scalar.return_value = document

    result = repository.get_by_id(document_id)

    assert result is document
    db.scalar.assert_called_once()


def test_list_documents_by_organization():
    db = MagicMock()
    repository = KnowledgeDocumentRepository(db)

    organization_id = uuid4()

    documents = [
        make_document(organization_id),
        make_document(organization_id),
    ]

    db.scalars.return_value = documents

    result = repository.list_by_organization(
        organization_id=organization_id,
        limit=50,
        offset=0,
    )

    assert result == documents
    db.scalars.assert_called_once()


def test_update_document():
    db = MagicMock()
    repository = KnowledgeDocumentRepository(db)

    document = make_document(uuid4())

    result = repository.update(document)

    assert result is document
    db.add.assert_called_once_with(document)


def test_delete_document():
    db = MagicMock()
    repository = KnowledgeDocumentRepository(db)

    document = make_document(uuid4())

    result = repository.delete(document)

    assert result is None
    db.delete.assert_called_once_with(document)