#!/usr/bin/env python3
"""
Examine database structure and data
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.business_account import BusinessAccount, BusinessChat, BusinessMessage
from app.models.user import User

def examine_database():
    """Examine the database structure and data."""
    db = SessionLocal()
    try:
        print("=== DATABASE EXAMINATION ===\n")

        # 1. Users table
        print("1. USERS TABLE:")
        users = db.query(User).all()
        for user in users:
            print(f"   ID: {user.id}, Username: {user.username}, Telegram User ID: {user.telegram_user_id}")
        print()

        # 2. Business Accounts table
        print("2. BUSINESS ACCOUNTS TABLE:")
        business_accounts = db.query(BusinessAccount).all()
        for account in business_accounts:
            status = "✅ ACTIVE" if account.is_enabled else "❌ DISABLED"
            print(f"   ID: {account.id}")
            print(f"   Business Connection ID: {account.business_connection_id}")
            print(f"   Telegram User ID: {account.user_id}")
            print(f"   Name: {account.first_name} {account.last_name or ''}")
            print(f"   Status: {status}")
            print(f"   Created: {account.created_at}")
            print()

        # 3. Business Chats table
        print("3. BUSINESS CHATS TABLE:")
        business_chats = db.query(BusinessChat).all()
        for chat in business_chats:
            print(f"   ID: {chat.id}")
            print(f"   Chat ID (Telegram): {chat.chat_id}")
            print(f"   Business Account ID: {chat.business_account_id}")
            print(f"   Chat Type: {chat.chat_type}")
            print(f"   Title/Name: {chat.title or f'{chat.first_name or ""} {chat.last_name or ""}'.strip() or 'No name'}")
            print(f"   Unread Count: {chat.unread_count}")
            print(f"   Message Count: {chat.message_count}")
            print(f"   Last Message At: {chat.last_message_at}")
            print()

        # 4. Business Messages table
        print("4. BUSINESS MESSAGES TABLE:")
        business_messages = db.query(BusinessMessage).all()
        print(f"   Total messages: {len(business_messages)}")

        # Group messages by chat
        messages_by_chat = {}
        for message in business_messages:
            chat_id = message.chat_id
            if chat_id not in messages_by_chat:
                messages_by_chat[chat_id] = []
            messages_by_chat[chat_id].append(message)

        for chat_id, messages in messages_by_chat.items():
            print(f"   Chat ID {chat_id}: {len(messages)} messages")
            # Show last 3 messages
            for msg in sorted(messages, key=lambda m: m.telegram_date, reverse=True)[:3]:
                direction = "OUTGOING" if msg.is_outgoing else "INCOMING"
                content = msg.text[:50] + "..." if msg.text and len(msg.text) > 50 else msg.text or "[No text]"
                print(f"     [{direction}] {msg.sender_first_name or 'Unknown'}: {content}")
            print()

        # 5. Analysis
        print("5. ANALYSIS:")
        print(f"   Users: {len(users)}")
        print(f"   Business Accounts: {len(business_accounts)}")
        print(f"   Business Chats: {len(business_chats)}")
        print(f"   Business Messages: {len(business_messages)}")

        # Check connections
        print("\n   CONNECTIONS:")
        for user in users:
            if user.telegram_user_id:
                user_accounts = [acc for acc in business_accounts if acc.user_id == user.telegram_user_id]
                print(f"   User {user.username} -> {len(user_accounts)} business accounts")

                for account in user_accounts:
                    account_chats = [chat for chat in business_chats if chat.business_account_id == account.id]
                    total_messages = sum(len([msg for msg in business_messages if msg.chat_id == chat.id]) for chat in account_chats)
                    print(f"     Account {account.business_connection_id} -> {len(account_chats)} chats, {total_messages} messages")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    examine_database()
