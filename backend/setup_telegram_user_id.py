#!/usr/bin/env python3
"""
Script to set up Telegram user ID for existing users based on business accounts
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.business_account import BusinessAccount
from app.models.user import User

def setup_telegram_user_ids():
    """Set up telegram_user_id for users based on existing business accounts."""
    db = SessionLocal()
    try:
        print("Setting up Telegram user IDs for users...\n")

        # Get all users
        users = db.query(User).all()
        print(f"Found {len(users)} users")

        # Get all business accounts
        business_accounts = db.query(BusinessAccount).all()
        print(f"Found {len(business_accounts)} business accounts")

        # Group business accounts by telegram user ID
        telegram_user_map = {}
        for account in business_accounts:
            telegram_user_id = account.user_id
            if telegram_user_id not in telegram_user_map:
                telegram_user_map[telegram_user_id] = []
            telegram_user_map[telegram_user_id].append(account)

        print(f"Found business accounts for {len(telegram_user_map)} different Telegram users")

        # For each Telegram user ID, find the most recent business account
        for telegram_user_id, accounts in telegram_user_map.items():
            print(f"\nTelegram User ID: {telegram_user_id}")
            print(f"  Business accounts: {len(accounts)}")

            # Find the most recent active account
            active_accounts = [acc for acc in accounts if acc.is_enabled]
            if active_accounts:
                most_recent = max(active_accounts, key=lambda x: x.created_at)
                print(f"  Most recent active account: {most_recent.business_connection_id}")
                print(f"  Created: {most_recent.created_at}")

                # Check if any user already has this telegram_user_id
                existing_user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
                if existing_user:
                    print(f"  ⚠️  Telegram user ID already assigned to user: {existing_user.username}")
                else:
                    # Ask user to assign this Telegram user ID to a user
                    print("  Available users to assign to:")
                    for i, user in enumerate(users):
                        print(f"    {i+1}. {user.username} (ID: {user.id})")

                    while True:
                        try:
                            choice = input(f"  Assign Telegram user {telegram_user_id} to user number (1-{len(users)}), or 0 to skip: ")
                            choice = int(choice)

                            if choice == 0:
                                print("  Skipped")
                                break
                            elif 1 <= choice <= len(users):
                                selected_user = users[choice - 1]

                                # Check if user already has telegram_user_id
                                if selected_user.telegram_user_id:
                                    print(f"  ❌ User {selected_user.username} already has Telegram user ID: {selected_user.telegram_user_id}")
                                    continue

                                # Assign telegram_user_id to user
                                selected_user.telegram_user_id = telegram_user_id
                                db.commit()
                                print(f"  ✅ Assigned Telegram user ID {telegram_user_id} to user {selected_user.username}")
                                break
                            else:
                                print(f"  Invalid choice. Please enter 1-{len(users)} or 0")
                        except ValueError:
                            print("  Invalid input. Please enter a number")

            else:
                print("  ❌ No active accounts found for this Telegram user")

        print("\n" + "="*50)
        print("Final user assignments:")

        for user in db.query(User).all():
            if user.telegram_user_id:
                business_accounts_count = db.query(BusinessAccount).filter(
                    BusinessAccount.user_id == user.telegram_user_id
                ).count()
                print(f"  {user.username}: Telegram ID {user.telegram_user_id} ({business_accounts_count} business accounts)")
            else:
                print(f"  {user.username}: No Telegram ID assigned")

        print("\nSetup completed!")

    except Exception as e:
        print(f"Error during setup: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_telegram_user_ids()
