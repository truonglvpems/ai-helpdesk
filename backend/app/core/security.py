from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from fastapi.security import HTTPBearer


_password_hasher = PasswordHasher()

bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    try:
        return _password_hasher.verify(
            password_hash,
            password,
        )
    except (VerifyMismatchError, InvalidHashError):
        return False