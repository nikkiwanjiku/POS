from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pos.database import get_db
from pos.schemas.auth import LoginRequest, TokenResponse
from pos.schemas.user import UserCreate, UserResponse
from pos.services.auth_service import auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_route(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    user = auth_service.register(db, data)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_route(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    result = auth_service.authenticate(db, data.username, data.password)
    return result
