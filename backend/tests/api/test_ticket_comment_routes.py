import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import HTTPException

from app.api.routes.ticket_comments import (
    create_comment,
    list_comments,
    update_comment,
    delete_comment,
)
from app.models.user import User

def make_current_user(organization_id):
    return User(
        id=uuid4(),
        organization_id=organization_id,
        auth_user_id=uuid4(),
        email="comment-test@example.com",
        full_name="Comment Test User",
        role="EMPLOYEE",
        status="active",
    )


def test_create_comment_uses_current_user():
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_comment = MagicMock()
    service.create_comment.return_value = expected_comment

    comments_module = __import__(
        "app.api.routes.ticket_comments",
        fromlist=["TicketCommentService"],
    )

    original_service = comments_module.TicketCommentService

    try:
        comments_module.TicketCommentService = lambda db: service

        data = MagicMock()

        result = create_comment(
            ticket_id=ticket_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        comments_module.TicketCommentService = original_service

    assert result is expected_comment

    service.create_comment.assert_called_once_with(
        ticket_id=ticket_id,
        data=data,
        current_user=current_user,
    )


def test_list_comments_uses_current_user():
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_comments = [
        MagicMock(),
        MagicMock(),
    ]
    service.list_comments.return_value = expected_comments

    comments_module = __import__(
        "app.api.routes.ticket_comments",
        fromlist=["TicketCommentService"],
    )

    original_service = comments_module.TicketCommentService

    try:
        comments_module.TicketCommentService = lambda db: service

        result = list_comments(
            ticket_id=ticket_id,
            current_user=current_user,
            db=db,
            limit=50,
            offset=0,
        )

    finally:
        comments_module.TicketCommentService = original_service

    assert result == expected_comments

    service.list_comments.assert_called_once_with(
        ticket_id=ticket_id,
        current_user=current_user,
        limit=50,
        offset=0,
    )


def test_list_comments_maps_permission_error_to_403():
    user_organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    service.list_comments.side_effect = PermissionError(
        "User is not allowed to read ticket comments"
    )

    comments_module = __import__(
        "app.api.routes.ticket_comments",
        fromlist=["TicketCommentService"],
    )

    original_service = comments_module.TicketCommentService

    try:
        comments_module.TicketCommentService = lambda db: service

        with pytest.raises(HTTPException) as exc_info:
            list_comments(
                ticket_id=ticket_id,
                current_user=current_user,
                db=db,
                limit=50,
                offset=0,
            )

    finally:
        comments_module.TicketCommentService = original_service

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == (
        "User is not allowed to read ticket comments"
    )

def test_update_comment_uses_current_user():
    user_organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_comment = MagicMock()
    expected_comment.ticket_id = ticket_id
    service.update_comment.return_value = expected_comment

    comments_module = __import__(
        "app.api.routes.ticket_comments",
        fromlist=["TicketCommentService"],
    )

    original_service = comments_module.TicketCommentService

    try:
        comments_module.TicketCommentService = lambda db: service

        data = MagicMock()

        result = update_comment(
            ticket_id=ticket_id,
            comment_id=comment_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        comments_module.TicketCommentService = original_service

    assert result is expected_comment

    service.update_comment.assert_called_once_with(
        comment_id=comment_id,
        current_user=current_user,
        data=data,
    )


def test_update_comment_passes_authenticated_user_to_service():
    user_organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    expected_comment = MagicMock()
    expected_comment.ticket_id = ticket_id
    service.update_comment.return_value = expected_comment

    comments_module = __import__(
        "app.api.routes.ticket_comments",
        fromlist=["TicketCommentService"],
    )

    original_service = comments_module.TicketCommentService

    try:
        comments_module.TicketCommentService = lambda db: service

        data = MagicMock()

        result = update_comment(
            ticket_id=ticket_id,
            comment_id=comment_id,
            data=data,
            db=db,
            current_user=current_user,
        )

    finally:
        comments_module.TicketCommentService = original_service

    assert result is expected_comment

    _, kwargs = service.update_comment.call_args

    assert kwargs["current_user"] is current_user
    assert kwargs["comment_id"] == comment_id
    assert kwargs["data"] is data


def test_update_comment_maps_permission_error_to_403():
    user_organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    service.update_comment.side_effect = PermissionError(
        "User is not allowed to update this comment"
    )

    comments_module = __import__(
        "app.api.routes.ticket_comments",
        fromlist=["TicketCommentService"],
    )

    original_service = comments_module.TicketCommentService

    try:
        comments_module.TicketCommentService = lambda db: service

        data = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            update_comment(
                ticket_id=ticket_id,
                comment_id=comment_id,
                data=data,
                db=db,
                current_user=current_user,
            )

    finally:
        comments_module.TicketCommentService = original_service

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == (
        "User is not allowed to update this comment"
    )

def test_delete_comment_uses_current_user():
    user_organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    comment = MagicMock()
    comment.ticket_id = ticket_id
    service.get_comment.return_value = comment

    comments_module = __import__(
        "app.api.routes.ticket_comments",
        fromlist=["TicketCommentService"],
    )

    original_service = comments_module.TicketCommentService

    try:
        comments_module.TicketCommentService = lambda db: service

        delete_comment(
            ticket_id=ticket_id,
            comment_id=comment_id,
            db=db,
            current_user=current_user,
        )

    finally:
        comments_module.TicketCommentService = original_service

    service.delete_comment.assert_called_once_with(
        comment_id=comment_id,
        current_user=current_user,
    )


def test_delete_comment_maps_permission_error_to_403():
    user_organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_organization_id,
    )

    db = MagicMock()
    service = MagicMock()

    comment = MagicMock()
    comment.ticket_id = ticket_id
    service.get_comment.return_value = comment

    service.delete_comment.side_effect = PermissionError(
        "User is not allowed to delete this comment"
    )

    comments_module = __import__(
        "app.api.routes.ticket_comments",
        fromlist=["TicketCommentService"],
    )

    original_service = comments_module.TicketCommentService

    try:
        comments_module.TicketCommentService = lambda db: service

        with pytest.raises(HTTPException) as exc_info:
            delete_comment(
                ticket_id=ticket_id,
                comment_id=comment_id,
                db=db,
                current_user=current_user,
            )

    finally:
        comments_module.TicketCommentService = original_service

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == (
        "User is not allowed to delete this comment"
    )
