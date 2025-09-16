"""Security middleware."""
import secrets
import time
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# CSRF token storage (in production, use Redis or database)
csrf_tokens: Dict[str, float] = {}

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for headers and CSRF protection."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
        # Content Security Policy - allow connections from frontend in development
        csp_connect_src = "'self'"
        if settings.ENVIRONMENT == "development":
            csp_connect_src = "'self' http://localhost:3000 http://localhost:5173"
        
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            f"connect-src {csp_connect_src}; "
            "frame-ancestors 'none';"
        )
        
        return response

def generate_csrf_token() -> str:
    """Generate CSRF token."""
    token = secrets.token_urlsafe(32)
    csrf_tokens[token] = time.time()
    return token

def verify_csrf_token(token: str) -> bool:
    """Verify CSRF token."""
    if token not in csrf_tokens:
        return False
        
    # Token expires after 1 hour
    if time.time() - csrf_tokens[token] > 3600:
        del csrf_tokens[token]
        return False
        
    return True

def cleanup_expired_tokens():
    """Clean up expired CSRF tokens."""
    current_time = time.time()
    expired_tokens = [
        token for token, timestamp in csrf_tokens.items() 
        if current_time - timestamp > 3600
    ]
    for token in expired_tokens:
        del csrf_tokens[token]

# Rate limit handler
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        {"detail": f"Rate limit exceeded: {exc.detail}"},
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response
