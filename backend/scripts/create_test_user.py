#!/usr/bin/env python3
"""Script to create admin user from .env file in the database."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.utils.password import hash_password
from app.core.config import settings

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def create_admin_user():
    """Create admin user from .env configuration."""
    db: Session = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing_user:
            print(f"⚠️  Admin user {settings.ADMIN_EMAIL} already exists!")
            # Update password if needed
            existing_user.hashed_password = hash_password(settings.ADMIN_PASS)
            existing_user.is_active = True
            existing_user.failed_login_attempts = 0
            existing_user.locked_until = None
            db.commit()
            print("✅ Admin user password updated!")
            return
        
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
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   Email: {settings.ADMIN_EMAIL}")
        print(f"   Password: {settings.ADMIN_PASS}")
        print(f"   Username: {username}")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Setting up database and admin user from .env...")
    print(f"📧 Admin email from .env: {settings.ADMIN_EMAIL}")
    create_tables()
    create_admin_user()
    print("🎉 Setup complete!")
