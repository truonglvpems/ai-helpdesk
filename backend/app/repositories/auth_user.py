from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth_user import AuthUser


class AuthUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, auth_user: AuthUser) -> AuthUser:
        self.db.add(auth_user)
        self.db.flush()
        self.db.refresh(auth_user)
        return auth_user

    def get_by_id(self, auth_user_id: UUID) -> AuthUser | None:
        stmt = select(AuthUser).where(AuthUser.id == auth_user_id)
        return self.db.scalar(stmt)

    def get_by_email(self, email: str) -> AuthUser | None:
        stmt = select(AuthUser).where(AuthUser.email == email)
        return self.db.scalar(stmt)

    def delete(self, auth_user: AuthUser) -> None:
        self.db.delete(auth_user)
        self.db.flush()