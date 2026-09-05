from unittest.mock import MagicMock
from uuid import uuid4

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.user import User
from app.schemas.knowledge_chunk import KnowledgeChunkCreate
from app.services.knowledge_chunk import KnowledgeChunkService


def make_current_user(organization_id):
    return User(
        id=uuid4(),
        organization_id=organization_id,
        auth_user_id=uuid4(),
        email="tenant-test@example.com",
        full_name="Tenant Test User",
        role="TECHNICIAN",
        status="active",
    )


def test_create_chunk_same_organization():
    organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(organization_id)

    db = MagicMock()

    document = KnowledgeDocument(
        id=document_id,
        organization_id=organization_id,
        uploaded_by=current_user.id,
        title="Test Document",
        file_name="test.txt",
        file_type="text/plain",
        file_size=100,
        storage_path="/tmp/test.txt",
        status="UPLOADED",
    )

    db.get.return_value = document

    service = KnowledgeChunkService(db)
    service.repository.create = MagicMock()

    chunk = KnowledgeChunk(
        id=uuid4(),
        document_id=document_id,
        content="Test chunk",
        chunk_index=0,
    )

    service.repository.create.side_effect = lambda value: None

    data = KnowledgeChunkCreate(
        document_id=document_id,
        content="Test chunk",
        chunk_index=0,
    )

    db.refresh.side_effect = lambda value: setattr(
        value,
        "id",
        chunk.id,
    )

    result = service.create_chunk(
        data,
        current_user,
    )

    assert result is not None
    assert result.document_id == document_id
    assert result.content == "Test chunk"
    assert result.chunk_index == 0

    service.repository.create.assert_called_once()

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_create_chunk_other_organization():
    user_organization_id = uuid4()
    document_organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()

    document = MagicMock()
    document.organization_id = document_organization_id

    db.get.return_value = document

    service = KnowledgeChunkService(db)
    service.repository.create = MagicMock()

    data = KnowledgeChunkCreate(
        document_id=document_id,
        content="Cross tenant chunk",
        chunk_index=0,
    )

    result = service.create_chunk(
        data,
        current_user,
    )

    assert result is None

    service.repository.create.assert_not_called()
    db.commit.assert_not_called()


def test_get_chunk_same_organization():
    organization_id = uuid4()
    document_id = uuid4()
    chunk_id = uuid4()

    current_user = make_current_user(organization_id)

    db = MagicMock()

    chunk = MagicMock()
    chunk.id = chunk_id
    chunk.document_id = document_id

    document = MagicMock()
    document.organization_id = organization_id

    db.get.return_value = document

    service = KnowledgeChunkService(db)
    service.repository.get_by_id = MagicMock(
        return_value=chunk,
    )

    result = service.get_chunk(
        chunk_id,
        current_user,
    )

    assert result is chunk


def test_get_chunk_other_organization():
    user_organization_id = uuid4()
    document_organization_id = uuid4()
    document_id = uuid4()
    chunk_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()

    chunk = MagicMock()
    chunk.document_id = document_id

    document = MagicMock()
    document.organization_id = document_organization_id

    db.get.return_value = document

    service = KnowledgeChunkService(db)
    service.repository.get_by_id = MagicMock(
        return_value=chunk,
    )

    result = service.get_chunk(
        chunk_id,
        current_user,
    )

    assert result is None


def test_list_chunks_same_organization():
    organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(organization_id)

    db = MagicMock()

    document = MagicMock()
    document.organization_id = organization_id

    db.get.return_value = document

    chunks = [
        MagicMock(chunk_index=0),
        MagicMock(chunk_index=1),
    ]

    service = KnowledgeChunkService(db)
    service.repository.list_by_document = MagicMock(
        return_value=chunks,
    )

    result = service.list_chunks(
        document_id=document_id,
        current_user=current_user,
        limit=10,
        offset=20,
    )

    assert result == chunks

    service.repository.list_by_document.assert_called_once_with(
        document_id=document_id,
        limit=10,
        offset=20,
    )


def test_list_chunks_other_organization():
    user_organization_id = uuid4()
    document_organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()

    document = MagicMock()
    document.organization_id = document_organization_id

    db.get.return_value = document

    service = KnowledgeChunkService(db)
    service.repository.list_by_document = MagicMock()

    result = service.list_chunks(
        document_id=document_id,
        current_user=current_user,
    )

    assert result == []

    service.repository.list_by_document.assert_not_called()


def test_update_chunk_same_organization():
    organization_id = uuid4()
    document_id = uuid4()
    chunk_id = uuid4()

    current_user = make_current_user(organization_id)

    db = MagicMock()

    chunk = MagicMock()
    chunk.document_id = document_id

    document = MagicMock()
    document.organization_id = organization_id

    db.get.return_value = document

    service = KnowledgeChunkService(db)

    service.repository.get_by_id = MagicMock(
        return_value=chunk,
    )
    service.repository.update = MagicMock()

    data = KnowledgeChunkCreate(
        document_id=document_id,
        content="Updated chunk",
        chunk_index=2,
    )

    result = service.update_chunk(
        chunk_id,
        data,
        current_user,
    )

    assert result is chunk
    assert chunk.content == "Updated chunk"
    assert chunk.chunk_index == 2

    service.repository.update.assert_called_once_with(
        chunk,
    )

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(chunk)


def test_delete_chunk_same_organization():
    organization_id = uuid4()
    document_id = uuid4()
    chunk_id = uuid4()

    current_user = make_current_user(organization_id)

    db = MagicMock()

    chunk = MagicMock()
    chunk.document_id = document_id

    document = MagicMock()
    document.organization_id = organization_id

    db.get.return_value = document

    service = KnowledgeChunkService(db)

    service.repository.get_by_id = MagicMock(
        return_value=chunk,
    )
    service.repository.delete = MagicMock()

    result = service.delete_chunk(
        chunk_id,
        current_user,
    )

    assert result is True

    service.repository.delete.assert_called_once_with(
        chunk,
    )

    db.commit.assert_called_once()