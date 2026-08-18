from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth import AuthService
from app.api.dependencies import get_current_user, require_role
from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    result = service.login(data)

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return result

@router.get(
    "/me",
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "organization_id": str(current_user.organization_id),
        "status": current_user.status,
    }

@router.get(
    "/admin-test",
)
def admin_test(
    current_user: User = Depends(
        require_role("ADMIN")
    ),
):
    return {
        "message": "Admin access granted",
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
    }