#!/usr/bin/env python3
"""Script to check database tables."""

from app.db.session import engine
from sqlalchemy import text

def check_tables():
    """Check what tables exist in the database."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SHOW TABLES'))
            print('Tables in database:')
            for row in result:
                print(f'- {row[0]}')

            # Check specific settings tables
            settings_tables = ['api_keys', 'openrouter_models', 'prompts']
            print('\nSettings tables:')
            for table in settings_tables:
                try:
                    result = conn.execute(text(f'SHOW CREATE TABLE {table}'))
                    print(f'✓ Table {table} exists')
                except Exception as e:
                    print(f'✗ Table {table} does not exist: {e}')

    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == '__main__':
    check_tables()
