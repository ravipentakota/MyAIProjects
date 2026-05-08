"""Authentication service for Google OAuth using backend env credentials."""
import json
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import EmailLoginRequest, EmailRegisterRequest, OAuthStartResponse, UserResponse


class AuthService:
    """Auth service for Google OAuth startup."""

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    def create_access_token(self, user_id: str, email: str) -> str:
        """Create JWT for authenticated user."""
        expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": int(expire_at.timestamp()),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def decode_access_token(self, token: str) -> dict[str, str]:
        """Decode and validate JWT token."""
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    async def register_with_email(
        self,
        db: AsyncSession,
        payload: EmailRegisterRequest,
    ) -> UserResponse:
        """Create a local account with email/password."""
        email = payload.email.strip().lower()
        existing = await db.scalar(select(User).where(User.email == email))
        if existing:
            raise ValueError("An account with this email already exists")

        user = User(
            email=email,
            hashed_password=self._hash_password(payload.password),
            full_name=None,
            google_id=None,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserResponse(id=user.id, email=user.email)

    async def login_with_email(
        self,
        db: AsyncSession,
        payload: EmailLoginRequest,
    ) -> UserResponse:
        """Validate email/password and return user."""
        email = payload.email.strip().lower()
        user = await db.scalar(select(User).where(User.email == email))
        if not user or not user.hashed_password:
            raise ValueError("Invalid email or password")

        if not self._verify_password(payload.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        return UserResponse(id=user.id, email=user.email)

    def get_google_login_url(self, redirect_to: str | None = None) -> OAuthStartResponse:
        """Return Google OAuth URL built from backend env credentials."""
        client_id = settings.GOOGLE_CLIENT_ID.strip()
        redirect_uri = settings.GOOGLE_REDIRECT_URI.strip()
        if not client_id or not redirect_uri:
            return OAuthStartResponse(
                provider="google",
                url="",
                message="Google OAuth environment variables are not configured.",
            )

        params: dict[str, str] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        if redirect_to:
            params["state"] = redirect_to

        query = urlencode(params)
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{query}"
        return OAuthStartResponse(
            provider="google",
            url=url,
            message="Google OAuth URL generated successfully.",
        )

    async def exchange_google_code(self, code: str, db: AsyncSession) -> UserResponse:
        """Exchange auth code for tokens, then fetch user info from Google."""
        client_id = settings.GOOGLE_CLIENT_ID.strip()
        client_secret = settings.GOOGLE_CLIENT_SECRET.strip()
        redirect_uri = settings.GOOGLE_REDIRECT_URI.strip()
        if not client_id or not client_secret or not redirect_uri:
            raise ValueError("Google OAuth configuration is incomplete")

        token_payload = urlencode(
            {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
        ).encode("utf-8")

        token_request = Request(
            url="https://oauth2.googleapis.com/token",
            data=token_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )

        try:
            with urlopen(token_request, timeout=20) as response:
                token_data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ValueError(f"Google token exchange failed: {detail}") from exc

        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("Google token exchange failed: missing access_token")

        userinfo_request = Request(
            url="https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            method="GET",
        )

        try:
            with urlopen(userinfo_request, timeout=20) as response:
                user_data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ValueError(f"Google userinfo fetch failed: {detail}") from exc

        google_id = str(user_data.get("sub", "")).strip()
        email = str(user_data.get("email", "")).strip().lower()
        full_name = str(user_data.get("name", "")).strip() or None

        if not google_id or not email:
            raise ValueError("Google userinfo response is missing required fields")

        user = await self._upsert_google_user(
            db=db,
            google_id=google_id,
            email=email,
            full_name=full_name,
        )

        return UserResponse(id=user.id, email=user.email)

    async def _upsert_google_user(
        self,
        db: AsyncSession,
        google_id: str,
        email: str,
        full_name: str | None,
    ) -> User:
        """Link or create user account from Google profile data."""
        existing_by_google = await db.scalar(select(User).where(User.google_id == google_id))
        if existing_by_google:
            existing_by_google.email = email
            existing_by_google.full_name = full_name
            existing_by_google.google_id = google_id
            await db.commit()
            await db.refresh(existing_by_google)
            return existing_by_google

        existing_by_email = await db.scalar(select(User).where(User.email == email))
        if existing_by_email:
            existing_by_email.google_id = google_id
            existing_by_email.full_name = full_name
            await db.commit()
            await db.refresh(existing_by_email)
            return existing_by_email

        user = User(id=google_id, google_id=google_id, email=email, full_name=full_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


auth_service = AuthService()
