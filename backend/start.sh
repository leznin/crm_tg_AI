#!/bin/bash

# Set MySQL database URL
export DATABASE_URL="mysql+pymysql://root:696578As@localhost/tg_crm?charset=utf8mb4"

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI application
echo "Starting FastAPI application with MySQL database..."
echo "Database URL: $DATABASE_URL"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
