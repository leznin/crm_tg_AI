#!/usr/bin/env python3
"""
Test the fixed message filtering logic
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.business_account import BusinessMessage

def test_message_filtering():
    """Test the fixed message filtering logic."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== TESTING MESSAGE FILTERING ===\n")

        # Get all business accounts
        accounts = repo.get_all_business_accounts(1)  # User ID 1
        print(f"Found {len(accounts)} business accounts")

        for account in accounts:
            print(f"\n📱 Business Account: {account.first_name}")
            print(f"   Chats count: {len(account.chats) if account.chats else 0}")

            if account.chats:
                for chat in account.chats:
                    print(f"\n   💬 Chat: {chat.first_name or 'Unknown'} (ID: {chat.id}, Telegram ID: {chat.chat_id})")

                    # Test message retrieval for this chat
                    messages = repo.get_messages_for_chat(chat.id, limit=20)
                    print(f"   📨 Messages retrieved: {len(messages)}")

                    if messages:
                        print("   Message details:")
                        for msg in messages:
                            direction = "➡️ OUTGOING" if msg.is_outgoing else "⬅️ INCOMING"
                            content = msg.text[:40] + "..." if msg.text and len(msg.text) > 40 else msg.text or "[No text]"
                            print(f"      {direction} {msg.sender_first_name}: {content}")
                            print(f"         Time: {msg.telegram_date}, Message ID: {msg.message_id}")
                    else:
                        print("   ℹ️  No messages in this chat")

        print("\n=== ANALYSIS ===")

        # Check Cyprus Flowers chat in both business accounts
        cyprus_chat_ids = {}
        for account in accounts:
            if account.chats:
                for chat in account.chats:
                    if chat.first_name == "Cyprus Flowers":
                        cyprus_chat_ids[account.first_name] = chat.id

        print(f"Cyprus Flowers chat found in {len(cyprus_chat_ids)} business accounts:")

        for account_name, chat_id in cyprus_chat_ids.items():
            print(f"\n🔍 {account_name} - Chat ID: {chat_id}")
            messages = repo.get_messages_for_chat(chat_id)
            print(f"   Messages: {len(messages)}")

            if messages:
                for msg in messages:
                    direction = "FROM USER" if not msg.is_outgoing else "FROM BUSINESS"
                    content = msg.text[:30] + "..." if msg.text and len(msg.text) > 30 else msg.text or "[No content]"
                    print(f"   - {direction}: {content}")

        print("\n✅ EXPECTED BEHAVIOR:")
        print("- Each business account should show only its own messages with Cyprus Flowers")
        print("- Messages should be specific to each business account conversation")
        print("- No mixing of messages between different business accounts")

        # Verify that messages are properly separated
        if len(cyprus_chat_ids) >= 2:
            account_names = list(cyprus_chat_ids.keys())
            chat1_messages = repo.get_messages_for_chat(cyprus_chat_ids[account_names[0]])
            chat2_messages = repo.get_messages_for_chat(cyprus_chat_ids[account_names[1]])

            print("\n🔍 MESSAGE SEPARATION CHECK:")
            print(f"{account_names[0]}: {len(chat1_messages)} messages")
            print(f"{account_names[1]}: {len(chat2_messages)} messages")

            if len(chat1_messages) != len(chat2_messages):
                print("✅ GOOD: Different number of messages in each business account")
            else:
                print("⚠️  WARNING: Same number of messages - could indicate mixing")

                # Check if messages are actually different
                chat1_texts = {msg.text for msg in chat1_messages if msg.text}
                chat2_texts = {msg.text for msg in chat2_messages if msg.text}

                if chat1_texts != chat2_texts:
                    print("✅ GOOD: Messages have different content")
                else:
                    print("❌ PROBLEM: Messages appear to be duplicated")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_message_filtering()
