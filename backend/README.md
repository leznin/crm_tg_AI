
# Secure CRM Backend

A secure FastAPI application with authentication, CSRF protection, rate limiting, and comprehensive security features.

## Features

- 🔐 **Secure Authentication**: bcrypt password hashing, JWT tokens
- 🛡️ **CSRF Protection**: CSRF tokens for all state-changing operations
- 🚦 **Rate Limiting**: Prevents brute-force attacks
- 🔒 **Account Lockout**: Automatic account lockout after failed attempts
- 🍪 **Secure Cookies**: HttpOnly, Secure, SameSite cookies
- 📝 **Security Logging**: Comprehensive security event logging
- 🏗️ **SQL Injection Protection**: Parameterized queries via SQLAlchemy ORM
- 🌐 **Security Headers**: CSP, HSTS, X-Frame-Options, etc.
- ✅ **Input Validation**: Server-side validation and sanitization

## Setup Instructions

### Prerequisites

- Python 3.9+
- MySQL 8.0+
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd backend
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:696578As@localhost/tg_crm?charset=utf8mb4

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production-32-chars-min
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CSRF Configuration
CSRF_SECRET=csrf-secret-key-change-in-production-32-chars-min

# Environment
ENVIRONMENT=development

# Admin credentials (from .env)
ADMIN_EMAIL=maksimleznin30@gmail.com
ADMIN_PASS=696578As

# Telegram Bot (existing)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

**⚠️ IMPORTANT**: Change the secret keys in production!

### 4. Database Setup

Make sure MySQL is running and create the database:

```sql
CREATE DATABASE tg_crm;
```

### 5. Create Tables and Admin User

Run the setup script to create database tables and admin user from .env:

```bash
python scripts/create_test_user.py
```

This will create:
- All necessary database tables
- An admin user with credentials from .env file:
  - Email: `maksimleznin30@gmail.com`
  - Password: `696578As`

### 6. Run the Application

Make sure your virtual environment is activated:

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Run the application with MySQL
# Option 1: Using the startup script (Recommended)
./start.sh

# Option 2: Manual startup
export DATABASE_URL="mysql+pymysql://root:696578As@localhost/tg_crm?charset=utf8mb4"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

To deactivate the virtual environment when you're done:

```bash
deactivate
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `GET /auth/csrf-token` - Get CSRF token for login
- `POST /auth/login` - Login with email/password + CSRF token
- `POST /auth/logout` - Logout and clear session
- `GET /auth/me` - Get current user information

### Example Login Request

```bash
# 1. Get CSRF token
curl -X GET http://localhost:8000/auth/csrf-token \
  -H "Content-Type: application/json" \
  -c cookies.txt

# 2. Login with CSRF token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -b cookies.txt -c cookies.txt \
  -d '{
    "email": "maksimleznin30@gmail.com",
    "password": "696578As",
    "csrf_token": "YOUR_CSRF_TOKEN_HERE"
  }'
```

## Running Tests

Make sure your virtual environment is activated and run the comprehensive test suite:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
pytest tests/ -v
```

Tests include:
- ✅ Successful login
- ❌ Failed login (wrong password)
- 🛡️ SQL injection protection
- 🔒 CSRF protection
- 🚦 Rate limiting
- 📊 Security logging

## Security Features

### Password Security
- Passwords hashed with bcrypt
- Salt automatically generated
- Never stored in plaintext

### Session Security
- JWT tokens in HttpOnly cookies
- Secure flag in production
- SameSite=strict
- Automatic expiration

### Rate Limiting
- 5 login attempts per minute per IP
- Account lockout after 5 failed attempts
- 15-minute lockout duration

### CSRF Protection
- CSRF tokens required for all POST requests
- Tokens expire after 1 hour
- Automatic cleanup of expired tokens

### Security Headers
- Content-Security-Policy
- Strict-Transport-Security (HTTPS only)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Referrer-Policy

### Logging
- Failed login attempts
- Account lockouts
- Suspicious activity
- No password logging

## Production Deployment

### Environment Variables
```env
ENVIRONMENT=production
SECRET_KEY=generate-a-strong-32-character-secret-key
CSRF_SECRET=generate-another-strong-32-character-key
DATABASE_URL=mysql://user:password@host/database
```

### HTTPS Configuration
```bash
uvicorn app.main:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem
```

### Database Security
- Use dedicated database user with minimal privileges
- Enable SSL for database connections
- Regular security updates

## Troubleshooting

### Database Connection Issues
```bash
# Test MySQL connection
mysql -h localhost -u root -p tg_crm
```

### Virtual Environment Issues
```bash
# If virtual environment doesn't exist, create it
python -m venv venv

# Make sure to activate before installing dependencies
source venv/bin/activate

# If you get permission errors, check if virtual environment is activated
which python  # Should show path to venv/bin/python
```

### Missing Dependencies
```bash
# Make sure virtual environment is activated first
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables Not Loading
- Ensure `.env` file is in the backend directory
- Check file permissions
- Verify no syntax errors in `.env`

### CORS Issues (Frontend)
- Frontend must run on allowed origins (localhost:3000, localhost:5173)
- Ensure credentials are included in requests

## Development

### Adding New Endpoints
1. Create router in `app/api/v1/`
2. Add authentication with `Depends(get_current_user)`
3. Include router in `app/main.py`

### Database Changes
1. Modify models in `app/models/`
2. Create migration script
3. Update test data creation

### Security Considerations
- Always use parameterized queries
- Validate and sanitize all inputs
- Log security events
- Keep dependencies updated
- Regular security audits

## License

MIT License - see LICENSE file for details.