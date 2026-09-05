from unittest.mock import MagicMock
from uuid import uuid4

from app.models.knowledge_chunk import KnowledgeChunk
from app.repositories.knowledge_chunk import KnowledgeChunkRepository


def test_create_chunk():
    db = MagicMock()
    repository = KnowledgeChunkRepository(db)

    chunk = KnowledgeChunk(
        document_id=uuid4(),
        content="Test chunk content",
        chunk_index=0,
    )

    result = repository.create(chunk)

    assert result is chunk
    db.add.assert_called_once_with(chunk)


def test_get_chunk_by_id():
    db = MagicMock()
    repository = KnowledgeChunkRepository(db)

    chunk_id = uuid4()
    expected_chunk = MagicMock()

    db.scalar.return_value = expected_chunk

    result = repository.get_by_id(chunk_id)

    assert result is expected_chunk
    db.scalar.assert_called_once()


def test_list_chunks_by_document():
    db = MagicMock()
    repository = KnowledgeChunkRepository(db)

    document_id = uuid4()
    chunks = [
        MagicMock(chunk_index=0),
        MagicMock(chunk_index=1),
    ]

    db.scalars.return_value = chunks

    result = repository.list_by_document(
        document_id=document_id,
        limit=10,
        offset=20,
    )

    assert result == chunks
    db.scalars.assert_called_once()


def test_update_chunk():
    db = MagicMock()
    repository = KnowledgeChunkRepository(db)

    chunk = KnowledgeChunk(
        document_id=uuid4(),
        content="Updated content",
        chunk_index=0,
    )

    result = repository.update(chunk)

    assert result is chunk
    db.add.assert_called_once_with(chunk)


def test_delete_chunk():
    db = MagicMock()
    repository = KnowledgeChunkRepository(db)

    chunk = KnowledgeChunk(
        document_id=uuid4(),
        content="Test chunk content",
        chunk_index=0,
    )

    result = repository.delete(chunk)

    assert result is None
    db.delete.assert_called_once_with(chunk)