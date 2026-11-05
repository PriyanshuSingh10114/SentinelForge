import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, description="User email address")
    password: str = Field(..., min_length=8, description="User password")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean_email = v.strip().lower()
        if not EMAIL_REGEX.match(clean_email):
            raise ValueError("Invalid email format")
        return clean_email


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in_seconds: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PermissionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class UserCreateRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, description="User email address")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    role_name: str = Field(default="Viewer", description="Admin, Analyst, Developer, Viewer")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean_email = v.strip().lower()
        if not EMAIL_REGEX.match(clean_email):
            raise ValueError("Invalid email format")
        return clean_email


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    permissions: List[str] = []
    failed_login_attempts: int = 0
    last_login_at: Optional[datetime] = None
