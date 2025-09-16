#!/usr/bin/env python3
"""
Test the new logic for showing all business accounts
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.user import User

def test_all_business_accounts():
    """Test the new logic for showing all business accounts."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== TESTING ALL BUSINESS ACCOUNTS LOGIC ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Telegram User ID: {user.telegram_user_id}")

        # Test the new logic
        accounts = repo.get_all_business_accounts(user.id)
        print(f"\nRepository returned {len(accounts)} business accounts:")

        for i, account in enumerate(accounts, 1):
            print(f"\n{i}. Virtual Account:")
            print(f"   ID: {account.id}")
            print(f"   Business Connection ID: {account.business_connection_id}")
            print(f"   Telegram User ID: {account.user_id}")
            print(f"   Name: {account.first_name} {account.last_name or ''}")
            print(f"   Username: @{account.username}" if account.username else "   Username: None")
            print(f"   Status: {'✅ ACTIVE' if account.is_enabled else '❌ DISABLED'}")
            print(f"   Chats count: {len(account.chats) if account.chats else 0}")

            if account.chats:
                print("   Recent chats:")
                for chat in account.chats[:3]:  # Show first 3 chats
                    chat_title = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or chat.title or f"Chat {chat.chat_id}"
                    print(f"     - {chat_title} (Unread: {chat.unread_count})")

        print("\n=== SUMMARY ===")
        print(f"Total business accounts shown: {len(accounts)}")
        print("This should now show ALL active business accounts in the system,")
        print("not just the ones belonging to the current user.")

        # Show what the old logic would have returned
        print("\n=== COMPARISON WITH OLD LOGIC ===")

        # Test what the old logic would return (only user's accounts)
        from app.models.business_account import BusinessAccount
        user_accounts = db.query(BusinessAccount).filter(
            BusinessAccount.user_id == user.telegram_user_id
        ).all()

        print(f"Old logic would return: {len(user_accounts)} accounts")
        for account in user_accounts:
            print(f"  - {account.first_name} {account.last_name or ''} (@{account.username})")

        # Show all active accounts in system
        all_active = db.query(BusinessAccount).filter(
            BusinessAccount.is_enabled == True
        ).all()

        print(f"\nAll active accounts in system: {len(all_active)}")
        for account in all_active:
            print(f"  - {account.first_name} {account.last_name or ''} (@{account.username}) - User ID: {account.user_id}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_all_business_accounts()
