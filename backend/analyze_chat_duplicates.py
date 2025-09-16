#!/usr/bin/env python3
"""
Analyze chat duplicates between business accounts
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.business_account import BusinessAccount, BusinessChat, BusinessMessage
from app.models.user import User

def analyze_chat_duplicates():
    """Analyze chat duplicates between business accounts."""
    db = SessionLocal()
    try:
        print("=== ANALYZING CHAT DUPLICATES ===\n")

        # Get all active business accounts
        active_accounts = db.query(BusinessAccount).filter(
            BusinessAccount.is_enabled == True
        ).all()

        print(f"Active business accounts: {len(active_accounts)}")
        business_user_ids = {acc.user_id for acc in active_accounts}
        print(f"Business account Telegram User IDs: {business_user_ids}")

        print("\n" + "="*50 + "\n")

        # Get all business chats
        all_chats = db.query(BusinessChat).all()
        print(f"Total business chats: {len(all_chats)}")

        # Analyze each chat
        for chat in all_chats:
            chat_id = chat.chat_id
            business_account_id = chat.business_account_id

            # Get business account info
            business_account = db.query(BusinessAccount).filter(
                BusinessAccount.id == business_account_id
            ).first()

            if business_account:
                is_business_chat = chat_id in business_user_ids
                chat_type = "BUSINESS-TO-BUSINESS" if is_business_chat else "USER-TO-BUSINESS"

                print(f"\nChat ID: {chat_id}")
                print(f"Business Account: {business_account.first_name} {business_account.last_name or ''}")
                print(f"Business Account Telegram ID: {business_account.user_id}")
                print(f"Chat Type: {chat_type}")
                print(f"Unread: {chat.unread_count}, Messages: {chat.message_count}")

                if is_business_chat:
                    # Find which business account this chat belongs to
                    target_business = None
                    for acc in active_accounts:
                        if acc.user_id == chat_id:
                            target_business = acc
                            break

                    if target_business:
                        print(f"Target Business Account: {target_business.first_name} {target_business.last_name or ''}")
                        print("❌ PROBLEM: This is a chat between two business accounts!")

                        # Show messages in this chat
                        messages = db.query(BusinessMessage).filter(
                            BusinessMessage.chat_id == chat.id
                        ).order_by(BusinessMessage.telegram_date.desc()).limit(3).all()

                        print(f"Recent messages ({len(messages)}):")
                        for msg in messages:
                            print(f"  - {msg.sender_first_name}: {msg.text[:50] if msg.text else '[No text]'}")
                    else:
                        print("ℹ️  INFO: Chat ID matches a business user ID but account not found")
                else:
                    print("✅ OK: This is a regular user chat")

        print("\n" + "="*50 + "\n")

        # Summary
        business_chats = []
        user_chats = []

        for chat in all_chats:
            if chat.chat_id in business_user_ids:
                business_chats.append(chat)
            else:
                user_chats.append(chat)

        print("SUMMARY:")
        print(f"✅ User-to-Business chats: {len(user_chats)}")
        print(f"❌ Business-to-Business chats: {len(business_chats)}")

        if business_chats:
            print("\nBusiness-to-Business chats that should be filtered out:")
            for chat in business_chats:
                business_account = db.query(BusinessAccount).filter(
                    BusinessAccount.id == chat.business_account_id
                ).first()
                if business_account:
                    target_business = None
                    for acc in active_accounts:
                        if acc.user_id == chat.chat_id:
                            target_business = acc
                            break
                    if target_business:
                        print(f"  - {business_account.first_name} ↔ {target_business.first_name}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    analyze_chat_duplicates()
