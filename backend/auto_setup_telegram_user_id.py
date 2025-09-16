#!/usr/bin/env python3
"""
Auto script to set up Telegram user ID for user maksimleznin30
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.business_account import BusinessAccount
from app.models.user import User

def auto_setup_telegram_user_id():
    """Automatically set up telegram_user_id for user maksimleznin30."""
    db = SessionLocal()
    try:
        print("Auto-setting up Telegram user ID for user maksimleznin30...\n")

        # Find user maksimleznin30
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        if not user:
            print("❌ User maksimleznin30 not found")
            return

        print(f"Found user: {user.username} (ID: {user.id})")

        # Find the most recent business account
        most_recent_account = db.query(BusinessAccount).order_by(BusinessAccount.created_at.desc()).first()
        if not most_recent_account:
            print("❌ No business accounts found")
            return

        telegram_user_id = most_recent_account.user_id
        print(f"Most recent business account belongs to Telegram user ID: {telegram_user_id}")
        print(f"Business connection ID: {most_recent_account.business_connection_id}")
        print(f"Account status: {'✅ ACTIVE' if most_recent_account.is_enabled else '❌ DISABLED'}")

        # Check if this telegram_user_id is already assigned to someone else
        existing_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        if existing_user and existing_user.id != user.id:
            print(f"❌ Telegram user ID {telegram_user_id} already assigned to user {existing_user.username}")
            return

        # Assign telegram_user_id to user
        if user.telegram_user_id:
            print(f"⚠️  User already has Telegram user ID: {user.telegram_user_id}")
            if user.telegram_user_id != telegram_user_id:
                print(f"Updating to: {telegram_user_id}")
                user.telegram_user_id = telegram_user_id
                db.commit()
                print("✅ Updated Telegram user ID")
            else:
                print("✅ Telegram user ID already correct")
        else:
            user.telegram_user_id = telegram_user_id
            db.commit()
            print(f"✅ Assigned Telegram user ID {telegram_user_id} to user {user.username}")

        # Verify the assignment
        updated_user = db.query(User).filter(User.id == user.id).first()
        if updated_user.telegram_user_id:
            business_accounts_count = db.query(BusinessAccount).filter(
                BusinessAccount.user_id == updated_user.telegram_user_id
            ).count()
            print(f"\n✅ SUCCESS: User {updated_user.username} now has Telegram user ID {updated_user.telegram_user_id}")
            print(f"   Business accounts available: {business_accounts_count}")
        else:
            print("❌ FAILED: Telegram user ID was not set")

    except Exception as e:
        print(f"Error during setup: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    auto_setup_telegram_user_id()
