#!/usr/bin/env python3
"""Test API key retrieval."""

import sys
sys.path.append('backend')

from app.db.session import SessionLocal
from app.services.settings_service import SettingsService
from app.schemas.settings_schema import KeyTypeEnum

db = SessionLocal()
try:
    service = SettingsService(db)

    # Test getting OpenRouter key
    key = service.get_api_key(1, KeyTypeEnum.OPENROUTER, decrypt=True)
    print(f"OpenRouter key found: {bool(key)}")
    if key:
        print(f"Key length: {len(key)}")
        print(f"Key starts with: {key[:10] if key else 'None'}...")

    # Test getting Telegram key
    telegram_key = service.get_api_key(1, KeyTypeEnum.TELEGRAM_BOT, decrypt=True)
    print(f"Telegram key found: {bool(telegram_key)}")

finally:
    db.close()
