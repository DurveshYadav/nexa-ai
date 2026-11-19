from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.repositories.user_repository import user_repository


class AuthService:
    """
    Authentication business logic.
    """

    def register(
        self,
        db: Session,
        email: str,
        password: str,
    ):

        existing_user = user_repository.get_by_email(
            db,
            email,
        )

        if existing_user:
            raise ValueError(
                "User with this email already exists."
            )

        password_hash = hash_password(password)

        return user_repository.create(
            db=db,
            email=email,
            password_hash=password_hash,
        )

    def authenticate(
        self,
        db: Session,
        email: str,
        password: str,
    ):

        user = user_repository.get_by_email(
            db,
            email,
        )

        if not user:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user


auth_service = AuthService()
