"""Authentication schema placeholders."""
from pydantic import BaseModel, EmailStr, Field


class OAuthStartResponse(BaseModel):
    """Response shape for starting OAuth login."""

    provider: str
    url: str
    message: str


class UserResponse(BaseModel):
    """Authenticated user placeholder model."""

    id: str
    email: str


class EmailRegisterRequest(BaseModel):
    """Request body for email/password registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class EmailLoginRequest(BaseModel):
    """Request body for email/password login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthUserResponse(BaseModel):
    """Response for successful auth actions."""

    user: UserResponse
    message: str
