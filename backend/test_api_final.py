#!/usr/bin/env python3
"""
Final test for the business accounts API with virtual account logic
"""
import sys
import os
import json

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.user import User

def test_api_final():
    """Test the final API logic for business accounts."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== FINAL API TEST ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Telegram User ID: {user.telegram_user_id}")

        if not user.telegram_user_id:
            print("❌ No telegram_user_id for user")
            return

        # Test repository method (simulates API call)
        accounts = repo.get_all_business_accounts(user.id)
        print(f"\nAPI would return {len(accounts)} business accounts:")

        if accounts:
            account = accounts[0]  # Should be only one virtual account

            # Simulate API response format
            api_response = {
                "accounts": [{
                    "id": account.id,
                    "business_connection_id": account.business_connection_id,
                    "user_id": account.user_id,
                    "first_name": account.first_name,
                    "last_name": account.last_name,
                    "username": account.username,
                    "is_enabled": account.is_enabled,
                    "can_reply": account.can_reply,
                    "chats_count": len(account.chats) if account.chats else 0,
                    "chats": []
                }],
                "total": len(accounts)
            }

            if account.chats:
                for chat in account.chats:
                    chat_data = {
                        "id": chat.id,
                        "chat_id": chat.chat_id,
                        "chat_type": chat.chat_type,
                        "title": chat.title,
                        "first_name": chat.first_name,
                        "last_name": chat.last_name,
                        "username": chat.username,
                        "unread_count": chat.unread_count,
                        "message_count": chat.message_count,
                        "last_message_at": chat.last_message_at.isoformat() if chat.last_message_at else None
                    }
                    api_response["accounts"][0]["chats"].append(chat_data)

            print("API Response:")
            print(json.dumps(api_response, indent=2, ensure_ascii=False, default=str))

            print("\nSummary:")
            print(f"✅ Business Account: {account.first_name} {account.last_name or ''}")
            print(f"✅ Status: {'Active' if account.is_enabled else 'Inactive'}")
            print(f"✅ Total Chats: {len(account.chats) if account.chats else 0}")
            print(f"✅ Chats with unread messages: {sum(1 for c in account.chats if c.unread_count > 0) if account.chats else 0}")

        else:
            print("❌ No business accounts found")
            api_response = {"accounts": [], "total": 0}
            print(json.dumps(api_response, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_api_final()
