#!/usr/bin/env python3
"""
Debug script to check business accounts in database
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.business_account import BusinessAccount
from app.models.user import User

def debug_business_accounts():
    """Debug business accounts in database."""
    db = SessionLocal()
    try:
        print("=== DEBUG BUSINESS ACCOUNTS ===\n")

        # Check all users
        users = db.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - User ID: {user.id}, Username: {user.username}")

        print("\n" + "="*50 + "\n")

        # Check all business accounts
        all_accounts = db.query(BusinessAccount).all()
        print(f"Total business accounts in DB: {len(all_accounts)}")

        if all_accounts:
            for account in all_accounts:
                status = "✅ АКТИВЕН" if account.is_enabled else "❌ ОТКЛЮЧЕН"
                print(f"\n📱 Account ID: {account.id}")
                print(f"   Business Connection ID: {account.business_connection_id}")
                print(f"   User ID: {account.user_id}")
                print(f"   Name: {account.first_name} {account.last_name or ''}")
                print(f"   Username: @{account.username}" if account.username else "   Username: None")
                print(f"   Status: {status}")
                print(f"   Can Reply: {'✅' if account.can_reply else '❌'}")
                print(f"   Created: {account.created_at}")
                print(f"   Updated: {account.updated_at}")

        print("\n" + "="*50 + "\n")

        # Check for duplicates by business_connection_id
        from collections import defaultdict
        connection_counts = defaultdict(int)

        for account in all_accounts:
            connection_counts[account.business_connection_id] += 1

        duplicates = {k: v for k, v in connection_counts.items() if v > 1}
        if duplicates:
            print("🚨 FOUND DUPLICATES:")
            for conn_id, count in duplicates.items():
                print(f"  - {conn_id}: {count} times")
                # Show details of duplicates
                dup_accounts = db.query(BusinessAccount).filter(
                    BusinessAccount.business_connection_id == conn_id
                ).order_by(BusinessAccount.created_at.desc()).all()

                for i, acc in enumerate(dup_accounts):
                    status = "АКТИВЕН" if acc.is_enabled else "ОТКЛЮЧЕН"
                    print(f"    {i+1}. User {acc.user_id} - {status} - Created: {acc.created_at}")
        else:
            print("✅ No duplicates found by business_connection_id")

        print("\n" + "="*50 + "\n")

        # Test our filtering logic for each user
        for user in users:
            print(f"Testing filtering for user {user.username or user.id} (ID: {user.id}):")
            print(f"  Telegram User ID: {user.telegram_user_id}")

            if user.telegram_user_id:
                # Get accounts for user's telegram_user_id
                user_accounts = db.query(BusinessAccount).filter(
                    BusinessAccount.user_id == user.telegram_user_id
                ).order_by(BusinessAccount.created_at.desc()).all()

                print(f"  Raw accounts for Telegram user: {len(user_accounts)}")

                # Apply deduplication logic
                seen_connections = set()
                unique_accounts = []

                for account in user_accounts:
                    if account.business_connection_id not in seen_connections:
                        seen_connections.add(account.business_connection_id)
                        unique_accounts.append(account)

                print(f"  After deduplication: {len(unique_accounts)}")

                if unique_accounts:
                    print("  Active accounts:")
                    for acc in unique_accounts:
                        if acc.is_enabled:
                            print(f"    ✅ {acc.first_name} {acc.last_name or ''} (@{acc.username}) - {acc.business_connection_id}")
                        else:
                            print(f"    ❌ {acc.first_name} {acc.last_name or ''} (@{acc.username}) - {acc.business_connection_id} [DISABLED]")
                else:
                    print("  No active accounts after deduplication")
            else:
                print("  No Telegram User ID assigned")

            print()

    except Exception as e:
        print(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_business_accounts()
