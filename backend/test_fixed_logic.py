#!/usr/bin/env python3
"""
Test the fixed business account logic
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.user import User

def test_fixed_logic():
    """Test the fixed business account logic."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== TESTING FIXED BUSINESS ACCOUNT LOGIC ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Telegram User ID: {user.telegram_user_id}")

        if not user.telegram_user_id:
            print("❌ No telegram_user_id for user")
            return

        # Test repository method
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
                for chat in account.chats:
                    chat_title = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or chat.title or f"Chat {chat.chat_id}"
                    print(f"      - {chat_title} (Telegram ID: {chat.chat_id}, Business Chat ID: {chat.id})")
                    print(f"        Unread: {chat.unread_count}, Messages: {chat.message_count}")
                    if chat.last_message_at:
                        print(f"        Last message: {chat.last_message_at}")

                    # Test message retrieval for this chat
                    messages = repo.get_messages_for_chat(chat.id, limit=10)
                    print(f"        Messages retrieved: {len(messages)}")
                    for msg in messages[:3]:  # Show first 3 messages
                        direction = "OUTGOING" if msg.is_outgoing else "INCOMING"
                        content = msg.text[:30] + "..." if msg.text and len(msg.text) > 30 else msg.text or "[No text]"
                        print(f"          [{direction}] {msg.sender_first_name or 'Unknown'}: {content}")
                print()

        print("=== SUMMARY ===")
        if accounts:
            account = accounts[0]
            total_chats = len(account.chats) if account.chats else 0
            total_messages = sum(len(repo.get_messages_for_chat(chat.id)) for chat in account.chats) if account.chats else 0

            print(f"✅ Virtual Account: {account.first_name} {account.last_name or ''}")
            print(f"✅ Total Chats: {total_chats}")
            print(f"✅ Total Messages: {total_messages}")
            print(f"✅ Chats with messages: {sum(1 for chat in account.chats if repo.get_messages_for_chat(chat.id)) if account.chats else 0}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_fixed_logic()
