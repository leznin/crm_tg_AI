#!/usr/bin/env python3
"""Test the chat summary service directly."""

import sys
import os
import asyncio
sys.path.append('backend')

from app.db.session import SessionLocal
from app.services.business_account_service import BusinessAccountService
from app.models.business_account import BusinessChat

async def test_chat_summary_service():
    """Test the chat summary service directly."""

    # Get a chat ID from database
    db = SessionLocal()
    try:
        # Get chat with messages
        chat = db.query(BusinessChat).filter(BusinessChat.id == 5).first()
        if not chat:
            print("Chat with ID 5 not found")
            return

        chat_id = chat.id
        # Get the actual user_id from business account
        from app.models.business_account import BusinessAccount
        business_account = db.query(BusinessAccount).filter(BusinessAccount.id == chat.business_account_id).first()
        user_id = business_account.user_id if business_account else 1
        print(f"Testing chat summary service with chat ID: {chat_id}, user ID: {user_id}")

        # Test the service
        service = BusinessAccountService(db)

        try:
            summary = await service.generate_chat_summary(user_id, chat_id)
            print("✅ Chat summary generated successfully!")
            print(f"Summary: {summary.summary}")
            print(f"Key points: {len(summary.key_points)}")
            print(f"Sentiment: {summary.sentiment}")
            print(f"Last updated: {summary.last_updated}")

        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_chat_summary_service())
