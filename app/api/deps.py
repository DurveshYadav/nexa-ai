from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import jwt

from app.core.config import settings
# from app.database.session import SessionLocal
from app.database.session import get_db
from app.repositories.user_repository import user_repository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


# def get_db() -> Generator[Session, None, None]:
#     db = SessionLocal()

#     try:
#         yield db
#     finally:
#         db.close()


def get_request_id(
    x_request_id: str | None = Header(default=None),
) -> str:
    return x_request_id or "generated-request-id"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Validate JWT and return current user.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (
        jwt.InvalidTokenError,
        ValueError,
    ):
        raise credentials_exception

    user = user_repository.get_by_id(
        db,
        user_id,
    )

    if user is None:
        raise credentials_exception

    return user

