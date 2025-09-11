"""Authentication service."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.utils.password import verify_password
from app.utils.jwt import create_access_token

# Configure logging for security events
logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger("security")

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            security_logger.warning(f"Login attempt with non-existent email: {email}")
            return None
            
        if not user.is_active:
            security_logger.warning(f"Login attempt with inactive user: {email}")
            return None
            
        # Check if account is locked
        if user.locked_until and datetime.utcnow() < user.locked_until:
            security_logger.warning(f"Login attempt with locked account: {email}")
            return None
            
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                security_logger.warning(f"Account locked due to failed attempts: {email}")
            else:
                security_logger.warning(f"Failed login attempt {user.failed_login_attempts}/5 for: {email}")
                
            self.db.commit()
            return None
            
        # Reset failed attempts on successful login
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            user.locked_until = None
            self.db.commit()
            
        security_logger.info(f"Successful login for user: {email}")
        return user

    def create_user_token(self, user: User) -> str:
        """Create JWT token for authenticated user."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username
        }
        return create_access_token(data=token_data)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
