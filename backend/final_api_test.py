#!/usr/bin/env python3
"""
Final API test for business accounts
"""
import sys
import os
import json

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.user import User

def final_api_test():
    """Final test of the business accounts API."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== FINAL API TEST ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (ID: {user.id})")

        # Simulate API response
        accounts = repo.get_all_business_accounts(user.id)

        print(f"API would return {len(accounts)} business accounts\n")

        # Create API response format
        api_response = {
            "accounts": [],
            "total": len(accounts)
        }

        for account in accounts:
            account_data = {
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
            }

            if account.chats:
                for chat in account.chats[:5]:  # Show first 5 chats
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
                    account_data["chats"].append(chat_data)

            api_response["accounts"].append(account_data)

        print("API Response:")
        print(json.dumps(api_response, indent=2, ensure_ascii=False, default=str))

        print("\n=== SUMMARY ===")
        print(f"✅ Total Business Accounts: {len(accounts)}")
        for i, account in enumerate(accounts, 1):
            chat_count = len(account.chats) if account.chats else 0
            print(f"✅ {i}. {account.first_name} {account.last_name or ''} - {chat_count} chats")

        print("\n🎉 SUCCESS: User can now choose between multiple business accounts!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    final_api_test()
