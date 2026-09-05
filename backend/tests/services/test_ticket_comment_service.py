import pytest
from uuid import uuid4
from unittest.mock import MagicMock, patch

from app.models.ticket import Ticket
from app.models.user import User
from app.services.ticket_comment import TicketCommentService
from app.schemas.ticket_comment import (
    TicketCommentCreate,
    TicketCommentUpdate,
)


def make_current_user(
    user_id,
    organization_id,
):
    return User(
        id=user_id,
        organization_id=organization_id,
        auth_user_id=uuid4(),
        email=f"{user_id}@example.com",
        full_name="Comment Test User",
        role="EMPLOYEE",
        status="active",
    )


def test_create_comment_denied_by_resource_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    data = TicketCommentCreate(
        # user_id=user_id,
        content="Policy denied comment",
        is_internal=False,
    )

    ticket = MagicMock(spec=Ticket)
    ticket.id = ticket_id
    ticket.organization_id = organization_id

    db = MagicMock()
    db.scalar.side_effect = [
        ticket,
    ]

    repository = MagicMock()

    service = TicketCommentService.__new__(
        TicketCommentService
    )
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket_comment.TicketPolicy.can_comment",
        return_value=False,
    ) as mock_can_comment:
        with pytest.raises(
            PermissionError,
            match="User is not allowed to comment on ticket",
        ):
            service.create_comment(
                ticket_id=ticket_id,
                data=data,
                current_user=current_user,
            )

    mock_can_comment.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.create.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_create_comment_allowed_by_resource_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    data = TicketCommentCreate(
        user_id=user_id,
        content="Policy allowed comment",
        is_internal=False,
    )

    ticket = MagicMock(spec=Ticket)
    ticket.id = ticket_id
    ticket.organization_id = organization_id

    db = MagicMock()
    db.scalar.side_effect = [
        ticket,
        current_user,
    ]

    repository = MagicMock()

    service = TicketCommentService.__new__(
        TicketCommentService
    )
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket_comment.TicketPolicy.can_comment",
        return_value=True,
    ) as mock_can_comment:
        comment = service.create_comment(
            ticket_id=ticket_id,
            data=data,
            current_user=current_user,
        )

    mock_can_comment.assert_called_once_with(
        current_user,
        ticket,
    )

    assert comment.ticket_id == ticket_id
    assert comment.user_id == user_id
    assert comment.content == data.content
    assert comment.is_internal is False

    repository.create.assert_called_once_with(comment)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(comment)

def test_list_comments_allowed_by_ticket_read_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock(spec=Ticket)
    ticket.id = ticket_id
    ticket.organization_id = organization_id

    comments = [
        MagicMock(),
        MagicMock(),
    ]

    db = MagicMock()
    db.scalar.return_value = ticket

    repository = MagicMock()
    repository.list_by_ticket.return_value = comments

    service = TicketCommentService.__new__(
        TicketCommentService
    )
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket_comment.TicketPolicy.can_read",
        return_value=True,
    ) as mock_can_read:
        result = service.list_comments(
            ticket_id=ticket_id,
            current_user=current_user,
            limit=50,
            offset=0,
        )

    assert result == comments

    mock_can_read.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.list_by_ticket.assert_called_once_with(
        ticket_id=ticket_id,
        limit=50,
        offset=0,
    )


def test_list_comments_denied_by_ticket_read_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    ticket = MagicMock(spec=Ticket)
    ticket.id = ticket_id
    ticket.organization_id = organization_id

    db = MagicMock()
    db.scalar.return_value = ticket

    repository = MagicMock()

    service = TicketCommentService.__new__(
        TicketCommentService
    )
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket_comment.TicketPolicy.can_read",
        return_value=False,
    ) as mock_can_read:
        with pytest.raises(
            PermissionError,
            match="User is not allowed to read ticket comments",
        ):
            service.list_comments(
                ticket_id=ticket_id,
                current_user=current_user,
                limit=50,
                offset=0,
            )

    mock_can_read.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.list_by_ticket.assert_not_called()

def test_update_comment_allowed_by_resource_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    data = TicketCommentUpdate(
        content="Updated comment",
        is_internal=False,
    )

    comment = MagicMock()
    comment.id = comment_id
    comment.ticket_id = ticket_id

    ticket = MagicMock(spec=Ticket)
    ticket.id = ticket_id
    ticket.organization_id = organization_id

    db = MagicMock()
    db.scalar.side_effect = [
        ticket,
        current_user,
    ]

    repository = MagicMock()
    repository.get_by_id.return_value = comment
    repository.update.return_value = comment

    service = TicketCommentService.__new__(
        TicketCommentService
    )
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket_comment.TicketPolicy.can_update",
        return_value=True,
    ) as mock_can_update:
        result = service.update_comment(
            comment_id=comment_id,
            current_user=current_user,
            data=data,
        )

    assert result is comment

    mock_can_update.assert_called_once_with(
        current_user,
        ticket,
    )

    assert comment.content == data.content
    assert comment.is_internal is False

    repository.update.assert_called_once_with(comment)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(comment)


def test_update_comment_denied_by_resource_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    data = TicketCommentUpdate(
        content="Denied update",
    )

    comment = MagicMock()
    comment.id = comment_id
    comment.ticket_id = ticket_id

    ticket = MagicMock(spec=Ticket)
    ticket.id = ticket_id
    ticket.organization_id = organization_id

    db = MagicMock()
    db.scalar.return_value = ticket

    repository = MagicMock()
    repository.get_by_id.return_value = comment

    service = TicketCommentService.__new__(
        TicketCommentService
    )
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket_comment.TicketPolicy.can_update",
        return_value=False,
    ) as mock_can_update:
        with pytest.raises(
            PermissionError,
            match="User is not allowed to update ticket comment",
        ):
            service.update_comment(
                comment_id=comment_id,
                current_user=current_user,
                data=data,
            )

    mock_can_update.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.update.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

def test_delete_comment_allowed_by_resource_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    comment = MagicMock()
    comment.id = comment_id
    comment.ticket_id = ticket_id

    ticket = MagicMock(spec=Ticket)
    ticket.id = ticket_id
    ticket.organization_id = organization_id

    db = MagicMock()
    db.scalar.side_effect = [
        ticket,
        current_user,
    ]

    repository = MagicMock()
    repository.get_by_id.return_value = comment

    service = TicketCommentService.__new__(
        TicketCommentService
    )
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket_comment.TicketPolicy.can_comment",
        return_value=True,
    ) as mock_can_comment:
        result = service.delete_comment(
            comment_id=comment_id,
            current_user=current_user,
        )

    assert result is True

    mock_can_comment.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.delete.assert_called_once_with(comment)
    db.commit.assert_called_once()


def test_delete_comment_denied_by_resource_policy():
    user_id = uuid4()
    organization_id = uuid4()
    ticket_id = uuid4()
    comment_id = uuid4()

    current_user = make_current_user(
        user_id=user_id,
        organization_id=organization_id,
    )

    comment = MagicMock()
    comment.id = comment_id
    comment.ticket_id = ticket_id

    ticket = MagicMock(spec=Ticket)
    ticket.id = ticket_id
    ticket.organization_id = organization_id

    db = MagicMock()
    db.scalar.return_value = ticket

    repository = MagicMock()
    repository.get_by_id.return_value = comment

    service = TicketCommentService.__new__(
        TicketCommentService
    )
    service.db = db
    service.repository = repository

    with patch(
        "app.services.ticket_comment.TicketPolicy.can_comment",
        return_value=False,
    ) as mock_can_comment:
        with pytest.raises(
            PermissionError,
            match="User is not allowed to delete ticket comment",
        ):
            service.delete_comment(
                comment_id=comment_id,
                current_user=current_user,
            )

    mock_can_comment.assert_called_once_with(
        current_user,
        ticket,
    )

    repository.delete.assert_not_called()
    db.commit.assert_not_called()