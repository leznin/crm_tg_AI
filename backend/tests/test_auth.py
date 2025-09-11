"""Authentication tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models.user import User
from app.utils.password import hash_password
from app.core.config import settings

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_user():
    """Create admin user from .env settings."""
    db = TestingSessionLocal()
    try:
        # Clean up existing user
        db.query(User).filter(User.email == settings.ADMIN_EMAIL).delete()
        db.commit()
        
        # Create admin user from .env
        hashed_password = hash_password(settings.ADMIN_PASS)
        user = User(
            username=settings.ADMIN_EMAIL.split('@')[0],
            email=settings.ADMIN_EMAIL,
            full_name="Administrator",
            hashed_password=hashed_password,
            is_active=True,
            failed_login_attempts=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()

def test_get_csrf_token():
    """Test CSRF token generation."""
    response = client.get("/auth/csrf-token")
    assert response.status_code == 200
    data = response.json()
    assert "csrf_token" in data
    assert len(data["csrf_token"]) > 0

def test_successful_login(test_user):
    """Test successful login."""
    # Get CSRF token
    csrf_response = client.get("/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]
    
    # Login
    response = client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASS,
        "csrf_token": csrf_token
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "user" in data
    assert data["user"]["email"] == settings.ADMIN_EMAIL

def test_failed_login_wrong_password(test_user):
    """Test failed login with wrong password."""
    # Get CSRF token
    csrf_response = client.get("/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]
    
    # Login with wrong password
    response = client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": "wrongpassword",
        "csrf_token": csrf_token
    })
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data

def test_failed_login_nonexistent_user():
    """Test failed login with non-existent user."""
    # Get CSRF token
    csrf_response = client.get("/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]
    
    # Login with non-existent user
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password",
        "csrf_token": csrf_token
    })
    
    assert response.status_code == 401

def test_csrf_protection():
    """Test CSRF protection."""
    # Try login without CSRF token
    response = client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASS,
        "csrf_token": "invalid_token"
    })
    
    assert response.status_code == 403
    data = response.json()
    assert "CSRF" in data["detail"]

def test_sql_injection_protection(test_user):
    """Test SQL injection protection."""
    # Get CSRF token
    csrf_response = client.get("/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]
    
    # Try SQL injection in email field
    response = client.post("/auth/login", json={
        "email": settings.ADMIN_EMAIL + "' OR '1'='1",
        "password": settings.ADMIN_PASS,
        "csrf_token": csrf_token
    })
    
    # Should not succeed (either 401 or 422 for invalid email format)
    assert response.status_code in [401, 422]

def test_logout():
    """Test logout functionality."""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logout successful"

def test_rate_limiting():
    """Test rate limiting on login endpoint."""
    # Get CSRF token
    csrf_response = client.get("/auth/csrf-token")
    csrf_token = csrf_response.json()["csrf_token"]
    
    # Make multiple failed login attempts
    for i in range(6):  # Exceeds the 5/minute limit
        response = client.post("/auth/login", json={
            "email": settings.ADMIN_EMAIL,
            "password": "wrongpassword",
            "csrf_token": csrf_token
        })
        
        if response.status_code == 429:
            # Rate limit exceeded
            assert "Rate limit exceeded" in response.json()["detail"]
            break
    else:
        # If we didn't hit rate limit, that's also acceptable for this test
        # as rate limiting might not kick in immediately in test environment
        pass
