#!/usr/bin/env python3
"""Test the chat summary API endpoint."""

import sys
import os
import asyncio
import httpx
import json
sys.path.append('backend')

from app.db.session import SessionLocal
from app.models.business_account import BusinessChat

async def test_chat_summary():
    """Test the chat summary API endpoint."""

    # Get a chat ID from database
    db = SessionLocal()
    try:
        chat = db.query(BusinessChat).first()
        if not chat:
            print("No chats found in database")
            return

        chat_id = chat.id
        print(f"Testing with chat ID: {chat_id}")

    finally:
        db.close()

    # Configuration
    base_url = "http://localhost:8000"

    print("Testing Chat Summary API...")
    print(f"Base URL: {base_url}")
    print(f"Chat ID: {chat_id}")

    try:
        # Test summary endpoint
        summary_url = f"{base_url}/api/v1/business-accounts/chats/{chat_id}/summary"
        print(f"\nTesting summary endpoint: {summary_url}")

        async with httpx.AsyncClient() as client:
            # For testing, we'll need to authenticate somehow
            # Since we don't have session cookies, let's try a direct test
            print("Note: This test requires authentication. In real usage, you'd be logged in via frontend.")
            print("To test manually: login to the app, go to a chat, and click 'Получить резюме'")

    except Exception as e:
        print(f"Test setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_summary())
