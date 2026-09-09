from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DatabaseSession, get_current_user
from app.core.security import create_access_token, decode_token
from app.models.user import User
from app.schemas.auth import (
    DoctorRegister,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserRead,
)
from app.services.auth import authenticate_user, register_doctor, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, session: DatabaseSession) -> User:
    try:
        return await register_user(session, data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error


@router.post(
    "/register-doctor", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register_as_doctor(data: DoctorRegister, session: DatabaseSession) -> User:
    try:
        return await register_doctor(session, data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DatabaseSession,
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_access_token(str(user.id), token_type="refresh"),
    )


@router.post("/refresh", response_model=Token)
async def refresh(data: RefreshTokenRequest, session: DatabaseSession) -> Token:
    subject = decode_token(data.refresh_token, expected_type="refresh")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    try:
        user_id = int(subject)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from None
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_access_token(str(user.id), token_type="refresh"),
    )


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user