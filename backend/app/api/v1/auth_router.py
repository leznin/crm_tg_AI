"""Authentication router."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth_schema import (
    LoginRequest, LoginResponse, LogoutResponse, 
    CSRFTokenResponse, UserInfo, ErrorResponse
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user, get_optional_current_user
from app.middleware.security import (
    generate_csrf_token, verify_csrf_token, 
    cleanup_expired_tokens, limiter
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/csrf-token", response_model=CSRFTokenResponse)
async def get_csrf_token():
    """Get CSRF token for login form."""
    cleanup_expired_tokens()
    token = generate_csrf_token()
    return CSRFTokenResponse(csrf_token=token)

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")  # Rate limit: 5 attempts per minute
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and create session."""
    # Verify CSRF token
    if not verify_csrf_token(login_data.csrf_token):
        logger.warning(f"Invalid CSRF token in login attempt from {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
    
    # Authenticate user
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create JWT token
    access_token = auth_service.create_user_token(user)
    
    # Set secure cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    logger.info(f"User {user.email} logged in successfully")
    
    return LoginResponse(
        message="Login successful",
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    )

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    current_user: UserInfo = Depends(get_optional_current_user)
):
    """Logout user and clear session."""
    # Clear the access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict"
    )
    
    if current_user:
        logger.info(f"User {current_user.email} logged out")
    
    return LogoutResponse(message="Logout successful")

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: UserInfo = Depends(get_current_user)
):
    """Get current user information."""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )
