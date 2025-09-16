from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from app.api.v1.user_router import router as user_router
from app.api.v1.auth_router import router as auth_router
from app.api.v1.settings_router import router as settings_router
from app.api.v1.business_account_router import router as business_account_router
from app.api.v1.telegram_webhook_router import router as telegram_webhook_router, webhook_router
from app.api.v1.file_upload_router import router as file_upload_router
from app.api.v1.contact_router import router as contact_router
from app.middleware.security import SecurityMiddleware, rate_limit_handler
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.core.config import settings
from app.models.user import User
from app.models.settings import ApiKey, OpenRouterModel, Prompt
from app.utils.password import hash_password

# Create database tables
Base.metadata.create_all(bind=engine)

def create_admin_user_if_not_exists():
    """Create admin user from .env if it doesn't exist."""
    db: Session = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not existing_user:
            # Extract username from email
            username = settings.ADMIN_EMAIL.split('@')[0]
            
            # Create admin user
            hashed_password = hash_password(settings.ADMIN_PASS)
            admin_user = User(
                username=username,
                email=settings.ADMIN_EMAIL,
                full_name="Administrator",
                hashed_password=hashed_password,
                is_active=True,
                failed_login_attempts=0
            )
            
            db.add(admin_user)
            db.commit()
            print(f"✅ Admin user created: {settings.ADMIN_EMAIL}")
        else:
            print(f"ℹ️ Admin user already exists: {settings.ADMIN_EMAIL}")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize FastAPI app
app = FastAPI(
    title="Secure CRM API",
    description="A secure FastAPI application with authentication",
    version="1.0.0"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add CORS middleware first (before security middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Always allow in dev
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Add OPTIONS for preflight
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Include routers with API prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(business_account_router, prefix="/api/v1")
app.include_router(contact_router, prefix="/api/v1")
app.include_router(telegram_webhook_router, prefix="/api/v1")
app.include_router(file_upload_router, prefix="/api/v1")
app.include_router(webhook_router)  # Direct webhook without /api/v1 prefix

@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    print("🚀 Starting up Secure CRM API...")
    create_admin_user_if_not_exists()
    print("🎉 Startup complete!")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Secure CRM API!"}