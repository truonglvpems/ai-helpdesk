from sqlalchemy.orm import Session

from app.core.jwt import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_user import AuthUserService


class AuthService:
    def __init__(self, db: Session):
        self.auth_user_service = AuthUserService(db)

    def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse | None:
        auth_user = self.auth_user_service.verify_credentials(
            email=data.email,
            password=data.password,
        )

        if auth_user is None:
            return None

        access_token = create_access_token(auth_user.id)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )