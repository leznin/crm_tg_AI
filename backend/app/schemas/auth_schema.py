"""Authentication schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str
    csrf_token: str

class LoginResponse(BaseModel):
    """Login response schema."""
    message: str
    user: dict

class LogoutResponse(BaseModel):
    """Logout response schema."""
    message: str

class CSRFTokenResponse(BaseModel):
    """CSRF token response schema."""
    csrf_token: str

class UserInfo(BaseModel):
    """User information schema."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool

class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
