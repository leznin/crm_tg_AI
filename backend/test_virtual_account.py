#!/usr/bin/env python3
"""
Test the new virtual business account logic
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.user import User

def test_virtual_account():
    """Test the virtual business account logic."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== TESTING VIRTUAL BUSINESS ACCOUNT ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Telegram User ID: {user.telegram_user_id}")

        if not user.telegram_user_id:
            print("❌ No telegram_user_id for user")
            return

        # Test repository method directly
        accounts = repo.get_all_business_accounts(user.id)
        print(f"\nRepository returned {len(accounts)} virtual accounts:")

        for account in accounts:
            print(f"  - Virtual Account ID: {account.id}")
            print(f"    Business Connection ID: {account.business_connection_id}")
            print(f"    Name: {account.first_name} {account.last_name or ''}")
            print(f"    Username: @{account.username}" if account.username else "    Username: None")
            print(f"    Status: {'✅ ACTIVE' if account.is_enabled else '❌ DISABLED'}")
            print(f"    Chats count: {len(account.chats) if account.chats else 0}")

            if account.chats:
                print("    Chats:")
                for chat in account.chats[:5]:  # Show first 5 chats
                    chat_title = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or chat.title or f"Chat {chat.chat_id}"
                    print(f"      - {chat_title} (ID: {chat.chat_id}, Type: {chat.chat_type})")
                    print(f"        Unread: {chat.unread_count}, Messages: {chat.message_count}")
                    if chat.last_message_at:
                        print(f"        Last message: {chat.last_message_at}")

                if len(account.chats) > 5:
                    print(f"      ... and {len(account.chats) - 5} more chats")

        # Compare with direct query
        print("\nDirect query comparison:")
        direct_accounts = db.query(BusinessAccount).filter(
            BusinessAccount.user_id == user.telegram_user_id
        ).all()

        print(f"Direct query found {len(direct_accounts)} raw business accounts:")
        total_chats = 0
        for acc in direct_accounts:
            chats_count = len(acc.chats) if acc.chats else 0
            total_chats += chats_count
            status = "АКТИВЕН" if acc.is_enabled else "ОТКЛЮЧЕН"
            print(f"  - {acc.business_connection_id}: {status}, {chats_count} chats")

        print(f"Total chats in all accounts: {total_chats}")

        if accounts and accounts[0].chats:
            print(f"Virtual account chats: {len(accounts[0].chats)}")
            print("✅ SUCCESS: Virtual account shows combined chats!" if len(accounts[0].chats) >= total_chats else "⚠️  WARNING: Some chats may be missing")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_virtual_account()
