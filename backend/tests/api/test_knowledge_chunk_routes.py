from unittest.mock import MagicMock
from uuid import uuid4

from app.api.routes.knowledge_chunks import (
    create_knowledge_chunk,
)
from app.models.user import User


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


def test_create_knowledge_chunk_uses_current_user():
    user_organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_chunk = MagicMock()
    service.create_chunk.return_value = expected_chunk

    chunks_module = __import__(
        "app.api.routes.knowledge_chunks",
        fromlist=["KnowledgeChunkService"],
    )

    original_service = chunks_module.KnowledgeChunkService

    try:
        chunks_module.KnowledgeChunkService = (
            lambda db: service
        )

        data = MagicMock()
        data.document_id = document_id

        result = chunks_module.create_knowledge_chunk(
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        chunks_module.KnowledgeChunkService = original_service

    assert result is expected_chunk

    service.create_chunk.assert_called_once_with(
        data,
        current_user,
    )

def test_get_knowledge_chunk_uses_current_user():
    user_organization_id = uuid4()
    chunk_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_chunk = MagicMock()
    service.get_chunk.return_value = expected_chunk

    chunks_module = __import__(
        "app.api.routes.knowledge_chunks",
        fromlist=["KnowledgeChunkService"],
    )

    original_service = chunks_module.KnowledgeChunkService

    try:
        chunks_module.KnowledgeChunkService = (
            lambda db: service
        )

        result = chunks_module.get_knowledge_chunk(
            chunk_id=chunk_id,
            db=db,
            current_user=current_user,
        )

    finally:
        chunks_module.KnowledgeChunkService = original_service

    assert result is expected_chunk

    service.get_chunk.assert_called_once_with(
        chunk_id,
        current_user,
    )

def test_list_knowledge_chunks_uses_current_user_and_pagination():
    user_organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_chunks = [
        MagicMock(),
        MagicMock(),
    ]
    service.list_chunks.return_value = expected_chunks

    chunks_module = __import__(
        "app.api.routes.knowledge_chunks",
        fromlist=["KnowledgeChunkService"],
    )

    original_service = chunks_module.KnowledgeChunkService

    try:
        chunks_module.KnowledgeChunkService = (
            lambda db: service
        )

        result = chunks_module.list_knowledge_chunks(
            document_id=document_id,
            limit=10,
            offset=20,
            db=db,
            current_user=current_user,
        )

    finally:
        chunks_module.KnowledgeChunkService = original_service

    assert result == expected_chunks

    service.list_chunks.assert_called_once_with(
        document_id=document_id,
        current_user=current_user,
        limit=10,
        offset=20,
    )

def test_update_knowledge_chunk_uses_current_user():
    user_organization_id = uuid4()
    chunk_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_chunk = MagicMock()
    service.update_chunk.return_value = expected_chunk

    chunks_module = __import__(
        "app.api.routes.knowledge_chunks",
        fromlist=["KnowledgeChunkService"],
    )

    original_service = chunks_module.KnowledgeChunkService

    try:
        chunks_module.KnowledgeChunkService = (
            lambda db: service
        )

        data = MagicMock()

        result = chunks_module.update_knowledge_chunk(
            chunk_id=chunk_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        chunks_module.KnowledgeChunkService = original_service

    assert result is expected_chunk

    service.update_chunk.assert_called_once_with(
        chunk_id,
        data,
        current_user,
    )

def test_delete_knowledge_chunk_uses_current_user():
    user_organization_id = uuid4()
    chunk_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    service.delete_chunk.return_value = True

    chunks_module = __import__(
        "app.api.routes.knowledge_chunks",
        fromlist=["KnowledgeChunkService"],
    )

    original_service = chunks_module.KnowledgeChunkService

    try:
        chunks_module.KnowledgeChunkService = (
            lambda db: service
        )

        result = chunks_module.delete_knowledge_chunk(
            chunk_id=chunk_id,
            db=db,
            current_user=current_user,
        )

    finally:
        chunks_module.KnowledgeChunkService = original_service

    assert result is None

    service.delete_chunk.assert_called_once_with(
        chunk_id,
        current_user,
    )
