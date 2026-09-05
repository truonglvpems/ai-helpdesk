from unittest.mock import MagicMock
from uuid import uuid4

from app.api.routes.knowledge_documents import (
    create_knowledge_document,
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


def test_create_knowledge_document_uses_current_user():
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_document = MagicMock()
    service.create_document.return_value = expected_document

    documents_module = __import__(
        "app.api.routes.knowledge_documents",
        fromlist=["KnowledgeDocumentService"],
    )

    original_service = documents_module.KnowledgeDocumentService

    try:
        documents_module.KnowledgeDocumentService = (
            lambda db: service
        )

        data = MagicMock()

        result = documents_module.create_knowledge_document(
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        documents_module.KnowledgeDocumentService = original_service

    assert result is expected_document

    service.create_document.assert_called_once_with(
        data,
        current_user,
    )

def test_get_knowledge_document_uses_current_user():
    user_organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_document = MagicMock()
    service.get_document.return_value = expected_document

    documents_module = __import__(
        "app.api.routes.knowledge_documents",
        fromlist=["KnowledgeDocumentService"],
    )

    original_service = documents_module.KnowledgeDocumentService

    try:
        documents_module.KnowledgeDocumentService = (
            lambda db: service
        )

        result = documents_module.get_knowledge_document(
            document_id=document_id,
            db=db,
            current_user=current_user,
        )

    finally:
        documents_module.KnowledgeDocumentService = original_service

    assert result is expected_document

    service.get_document.assert_called_once_with(
        document_id,
        current_user,
    )

def test_list_knowledge_documents_uses_current_user_and_pagination():
    user_organization_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_documents = [
        MagicMock(),
        MagicMock(),
    ]
    service.list_documents.return_value = expected_documents

    documents_module = __import__(
        "app.api.routes.knowledge_documents",
        fromlist=["KnowledgeDocumentService"],
    )

    original_service = documents_module.KnowledgeDocumentService

    try:
        documents_module.KnowledgeDocumentService = (
            lambda db: service
        )

        result = documents_module.list_knowledge_documents(
            limit=10,
            offset=20,
            db=db,
            current_user=current_user,
        )

    finally:
        documents_module.KnowledgeDocumentService = original_service

    assert result == expected_documents

    service.list_documents.assert_called_once_with(
        current_user=current_user,
        limit=10,
        offset=20,
    )

def test_update_knowledge_document_uses_current_user():
    user_organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_document = MagicMock()
    service.update_document.return_value = expected_document

    documents_module = __import__(
        "app.api.routes.knowledge_documents",
        fromlist=["KnowledgeDocumentService"],
    )

    original_service = documents_module.KnowledgeDocumentService

    try:
        documents_module.KnowledgeDocumentService = (
            lambda db: service
        )

        data = MagicMock()

        result = documents_module.update_knowledge_document(
            document_id=document_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        documents_module.KnowledgeDocumentService = original_service

    assert result is expected_document

    service.update_document.assert_called_once_with(
        document_id,
        data,
        current_user,
    )

def test_delete_knowledge_document_uses_current_user():
    user_organization_id = uuid4()
    document_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    service.delete_document.return_value = True

    documents_module = __import__(
        "app.api.routes.knowledge_documents",
        fromlist=["KnowledgeDocumentService"],
    )

    original_service = documents_module.KnowledgeDocumentService

    try:
        documents_module.KnowledgeDocumentService = (
            lambda db: service
        )

        result = documents_module.delete_knowledge_document(
            document_id=document_id,
            db=db,
            current_user=current_user,
        )

    finally:
        documents_module.KnowledgeDocumentService = original_service

    assert result is None

    service.delete_document.assert_called_once_with(
        document_id,
        current_user,
    )
