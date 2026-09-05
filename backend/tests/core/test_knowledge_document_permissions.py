from app.core.permissions import Permission
from app.core.role_permissions import has_permission


def test_admin_has_all_knowledge_document_permissions():
    assert has_permission(
        "ADMIN",
        Permission.KNOWLEDGE_DOCUMENT_CREATE,
    )
    assert has_permission(
        "ADMIN",
        Permission.KNOWLEDGE_DOCUMENT_READ,
    )
    assert has_permission(
        "ADMIN",
        Permission.KNOWLEDGE_DOCUMENT_LIST,
    )
    assert has_permission(
        "ADMIN",
        Permission.KNOWLEDGE_DOCUMENT_UPDATE,
    )
    assert has_permission(
        "ADMIN",
        Permission.KNOWLEDGE_DOCUMENT_DELETE,
    )


def test_technician_has_knowledge_document_crud_except_delete():
    assert has_permission(
        "TECHNICIAN",
        Permission.KNOWLEDGE_DOCUMENT_CREATE,
    )
    assert has_permission(
        "TECHNICIAN",
        Permission.KNOWLEDGE_DOCUMENT_READ,
    )
    assert has_permission(
        "TECHNICIAN",
        Permission.KNOWLEDGE_DOCUMENT_LIST,
    )
    assert has_permission(
        "TECHNICIAN",
        Permission.KNOWLEDGE_DOCUMENT_UPDATE,
    )
    assert not has_permission(
        "TECHNICIAN",
        Permission.KNOWLEDGE_DOCUMENT_DELETE,
    )


def test_employee_has_only_knowledge_document_read_and_list():
    assert not has_permission(
        "EMPLOYEE",
        Permission.KNOWLEDGE_DOCUMENT_CREATE,
    )
    assert has_permission(
        "EMPLOYEE",
        Permission.KNOWLEDGE_DOCUMENT_READ,
    )
    assert has_permission(
        "EMPLOYEE",
        Permission.KNOWLEDGE_DOCUMENT_LIST,
    )
    assert not has_permission(
        "EMPLOYEE",
        Permission.KNOWLEDGE_DOCUMENT_UPDATE,
    )
    assert not has_permission(
        "EMPLOYEE",
        Permission.KNOWLEDGE_DOCUMENT_DELETE,
    )