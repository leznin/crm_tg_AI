#!/usr/bin/env python3
"""
Test chat merging from multiple business accounts
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.business_account import BusinessAccount, BusinessChat
from app.models.user import User

def test_chat_merge():
    """Test that chats are properly merged from multiple business accounts."""
    db = SessionLocal()
    try:
        print("=== TESTING CHAT MERGING ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (Telegram User ID: {user.telegram_user_id})")

        if not user.telegram_user_id:
            print("❌ No telegram_user_id for user")
            return

        # Get all business accounts for this user
        accounts = db.query(BusinessAccount).filter(
            BusinessAccount.user_id == user.telegram_user_id
        ).all()

        print(f"\nFound {len(accounts)} business accounts for this user:")
        total_chats = 0
        all_chat_ids = set()

        for i, account in enumerate(accounts, 1):
            status = "АКТИВЕН" if account.is_enabled else "ОТКЛЮЧЕН"
            chats_count = len(account.chats) if account.chats else 0
            total_chats += chats_count

            print(f"\n{i}. Account: {account.business_connection_id} ({status})")
            print(f"   Chats: {chats_count}")

            if account.chats:
                for chat in account.chats:
                    all_chat_ids.add(chat.chat_id)
                    chat_title = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or chat.title or f"Chat {chat.chat_id}"
                    print(f"     - {chat_title} (ID: {chat.chat_id})")

        print("\nSUMMARY:")
        print(f"Total business accounts: {len(accounts)}")
        print(f"Total chats across all accounts: {total_chats}")
        print(f"Unique chat IDs: {len(all_chat_ids)}")

        if len(all_chat_ids) < total_chats:
            print(f"✅ GOOD: Found {total_chats - len(all_chat_ids)} duplicate chats that will be merged")
        else:
            print("ℹ️  INFO: No duplicate chats found")

        # Test the virtual account logic manually
        print("\nTESTING VIRTUAL ACCOUNT LOGIC:")

        # Get all chats from all accounts
        all_chats = []
        for account in accounts:
            if account.chats:
                all_chats.extend(account.chats)

        # Remove duplicates by chat_id
        seen_chat_ids = set()
        unique_chats = []
        for chat in sorted(all_chats, key=lambda c: c.last_message_at or c.created_at, reverse=True):
            if chat.chat_id not in seen_chat_ids:
                seen_chat_ids.add(chat.chat_id)
                unique_chats.append(chat)

        print(f"Original chats: {len(all_chats)}")
        print(f"After deduplication: {len(unique_chats)}")

        if unique_chats:
            print("Final merged chats:")
            for chat in unique_chats:
                chat_title = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or chat.title or f"Chat {chat.chat_id}"
                print(f"  - {chat_title} (ID: {chat.chat_id}, Unread: {chat.unread_count})")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_chat_merge()
