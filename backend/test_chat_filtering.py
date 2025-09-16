#!/usr/bin/env python3
"""
Test the fixed chat filtering logic
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.user import User

def test_chat_filtering():
    """Test the fixed chat filtering logic."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== TESTING FIXED CHAT FILTERING ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Telegram User ID: {user.telegram_user_id}")

        # Test repository method
        accounts = repo.get_all_business_accounts(user.id)
        print(f"\nRepository returned {len(accounts)} business accounts:")

        total_user_chats = 0
        total_business_chats_filtered = 0

        for i, account in enumerate(accounts, 1):
            print(f"\n{i}. {account.first_name} {account.last_name or ''}")
            print(f"   Chats count: {len(account.chats) if account.chats else 0}")

            if account.chats:
                user_chats = []
                business_chats = []

                # Get all active business account user IDs
                from app.models.business_account import BusinessAccount
                active_accounts = db.query(BusinessAccount).filter(
                    BusinessAccount.is_enabled == True
                ).all()
                business_user_ids = {acc.user_id for acc in active_accounts}

                for chat in account.chats:
                    if chat.chat_id in business_user_ids:
                        business_chats.append(chat)
                    else:
                        user_chats.append(chat)

                print(f"   ✅ User chats: {len(user_chats)}")
                print(f"   ❌ Business-to-business chats: {len(business_chats)}")

                total_user_chats += len(user_chats)
                total_business_chats_filtered += len(business_chats)

                # Show details of user chats
                for chat in user_chats:
                    chat_title = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or chat.title or f"Chat {chat.chat_id}"
                    print(f"     - {chat_title} (ID: {chat.chat_id}, Unread: {chat.unread_count})")

                if business_chats:
                    print("   ⚠️  WARNING: Business-to-business chats found (should be filtered):")
                    for chat in business_chats:
                        target_business = None
                        for acc in active_accounts:
                            if acc.user_id == chat.chat_id:
                                target_business = acc
                                break
                        if target_business:
                            print(f"     - Chat with {target_business.first_name}")

        print("\n=== SUMMARY ===")
        print(f"✅ Total user chats: {total_user_chats}")
        print(f"❌ Business-to-business chats (filtered): {total_business_chats_filtered}")

        if total_business_chats_filtered == 0:
            print("🎉 SUCCESS: All business-to-business chats have been filtered out!")
        else:
            print("⚠️  WARNING: Some business-to-business chats are still present")

        print("\nExpected: Only user chats should be visible")
        print("Business-to-business chats (like chat between two business accounts) should be hidden")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_chat_filtering()
