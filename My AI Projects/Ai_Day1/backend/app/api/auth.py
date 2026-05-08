"""Authentication routes scaffold (Google OAuth via Supabase)."""
from typing import Optional
from urllib.parse import urlencode

import jwt
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthUserResponse,
    EmailLoginRequest,
    EmailRegisterRequest,
    UserResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/email/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
async def email_register(
    payload: EmailRegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthUserResponse:
    """Register a user with email and password, then issue JWT cookie."""
    try:
        user = await auth_service.register_with_email(db=db, payload=payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "email_exists", "message": str(exc)},
        ) from exc

    token = auth_service.create_access_token(user_id=user.id, email=user.email)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
    )
    return AuthUserResponse(user=user, message="Registration successful")


@router.post("/email/login", response_model=AuthUserResponse)
async def email_login(
    payload: EmailLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthUserResponse:
    """Authenticate user with email/password and issue JWT cookie."""
    try:
        user = await auth_service.login_with_email(db=db, payload=payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials", "message": str(exc)},
        ) from exc

    token = auth_service.create_access_token(user_id=user.id, email=user.email)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
    )
    return AuthUserResponse(user=user, message="Login successful")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """Clear auth cookie."""
    response.delete_cookie("access_token")


@router.get("/google/login")
async def start_google_login(
    redirect_to: Optional[str] = Query(default=None),
) -> RedirectResponse:
    """Redirect browser to Google OAuth initiation URL."""
    oauth_start = auth_service.get_google_login_url(redirect_to=redirect_to)
    if not oauth_start.url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "google_oauth_not_configured", "message": oauth_start.message},
        )
    return RedirectResponse(url=oauth_start.url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
async def google_callback(
    code: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Google OAuth callback using backend env credentials and frontend redirect."""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "missing_code", "message": "Authorization code is required"},
        )

    try:
        user = await auth_service.exchange_google_code(code=code, db=db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "google_oauth_failed", "message": str(exc)},
        ) from exc

    frontend_base = (state or settings.FRONTEND_URL).strip() or "http://localhost:5173"

    separator = "&" if "?" in frontend_base else "?"
    query = urlencode({"oauth_user_id": user.id, "oauth_email": user.email})
    target = f"{frontend_base}{separator}{query}"
    return RedirectResponse(url=target, status_code=status.HTTP_302_FOUND)


@router.get("/me", response_model=UserResponse)
async def me(
    access_token: str | None = Cookie(default=None),
    x_user_email: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Resolve current user by JWT cookie, falling back to headers."""
    user = None

    if access_token:
        try:
            payload = auth_service.decode_access_token(access_token)
            token_user_id = str(payload.get("sub", "")).strip()
            if token_user_id:
                user = await db.scalar(select(User).where(User.id == token_user_id))
        except jwt.PyJWTError:
            user = None

    if x_user_id:
        user = await db.scalar(select(User).where(User.id == x_user_id))
    if not user and x_user_email:
        user = await db.scalar(select(User).where(User.email == x_user_email.lower()))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "user_not_found", "message": "User not found"},
        )

    return UserResponse(id=user.id, email=user.email)
