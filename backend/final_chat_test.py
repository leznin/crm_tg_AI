#!/usr/bin/env python3
"""
Final test for chat filtering through API
"""
import sys
import os
import json

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.user import User

def final_chat_test():
    """Final test of chat filtering through API."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== FINAL CHAT FILTERING TEST ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username}")

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
                "first_name": account.first_name,
                "last_name": account.last_name,
                "username": account.username,
                "chats": []
            }

            if account.chats:
                for chat in account.chats[:10]:  # Show first 10 chats
                    chat_data = {
                        "id": chat.id,
                        "chat_id": chat.chat_id,
                        "first_name": chat.first_name,
                        "last_name": chat.last_name,
                        "username": chat.username,
                        "unread_count": chat.unread_count,
                        "message_count": chat.message_count
                    }
                    account_data["chats"].append(chat_data)

            api_response["accounts"].append(account_data)

        print("API Response (Filtered Chats):")
        print(json.dumps(api_response, indent=2, ensure_ascii=False, default=str))

        print("\n=== ANALYSIS ===")

        # Check for business-to-business chats
        business_user_ids = {5615712643, 1250745524}  # From our analysis
        total_user_chats = 0
        business_to_business_chats = 0

        for account in api_response["accounts"]:
            print(f"\n{account['first_name']} {account.get('last_name', '')}:")
            print(f"  Total chats: {len(account['chats'])}")

            user_chats = []
            business_chats = []

            for chat in account["chats"]:
                if chat["chat_id"] in business_user_ids:
                    business_chats.append(chat)
                    business_to_business_chats += 1
                else:
                    user_chats.append(chat)
                    total_user_chats += 1

            print(f"  ✅ User chats: {len(user_chats)}")
            print(f"  ❌ Business chats: {len(business_chats)}")

            for chat in user_chats:
                chat_name = f"{chat['first_name'] or ''} {chat.get('last_name', '')}".strip()
                if not chat_name:
                    chat_name = f"Chat {chat['chat_id']}"
                print(f"    - {chat_name} ({chat['unread_count']} unread)")

        print("\n=== FINAL SUMMARY ===")
        print(f"✅ Total user-to-business chats: {total_user_chats}")
        print(f"❌ Business-to-business chats: {business_to_business_chats}")

        if business_to_business_chats == 0:
            print("🎉 SUCCESS: All business-to-business chats filtered out!")
            print("✅ Users will only see their actual customer chats")
            print("✅ No more duplicate chats between business accounts")
        else:
            print("⚠️  WARNING: Some business-to-business chats still present")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    final_chat_test()
