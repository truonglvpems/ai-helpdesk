from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.auth_user import AuthUser
from app.repositories.auth_user import AuthUserRepository


class AuthUserService:
    def __init__(self, db: Session):
        self.repository = AuthUserRepository(db)

    def create_auth_user(
        self,
        email: str,
        password: str,
        is_active: bool = True,
    ) -> AuthUser:
        password_hash = hash_password(password)

        auth_user = AuthUser(
            email=email,
            password_hash=password_hash,
            is_active=is_active,
        )

        return self.repository.create(auth_user)

    def get_by_email(self, email: str) -> AuthUser | None:
        return self.repository.get_by_email(email)

    def verify_credentials(
        self,
        email: str,
        password: str,
    ) -> AuthUser | None:
        auth_user = self.repository.get_by_email(email)

        if auth_user is None:
            return None

        if not auth_user.is_active:
            return None

        if not verify_password(password, auth_user.password_hash):
            return None

        return auth_user