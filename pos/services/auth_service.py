from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from pos.core.security import (
    hash_password,
    verify_password,
    decode_access_token,
    create_access_token,
)

from pos.repositories.user_repository import user_repository
from pos.schemas.user import UserCreate


class AuthService:

    def register(self, db: Session, data: UserCreate):

        if user_repository.get_by_username(db, data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        if data.user_email and user_repository.get_by_email(
            db, data.user_email
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        values = data.model_dump(exclude={"password"})

        values["password_hash"] = hash_password(data.password)

        return user_repository.create(db, values)

    def authenticate(
        self,
        db: Session,
        username: str,
        password: str
    ) -> dict:

        user = user_repository.get_by_username(db, username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        payload = {
            "sub": str(user.user_id),
            "username": user.username,
            "role": user.role,
        }

        access_token = create_access_token(data=payload)

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


auth_service = AuthService()