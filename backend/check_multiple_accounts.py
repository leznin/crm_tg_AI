#!/usr/bin/env python3
"""
Check if user has multiple business accounts that should be shown separately
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.business_account import BusinessAccount
from app.models.user import User

def check_multiple_accounts():
    """Check user's business accounts."""
    db = SessionLocal()
    try:
        print("=== CHECKING MULTIPLE BUSINESS ACCOUNTS ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Telegram User ID: {user.telegram_user_id}")
        print()

        # Get ALL business accounts
        all_accounts = db.query(BusinessAccount).all()
        print(f"Total business accounts in DB: {len(all_accounts)}")

        for account in all_accounts:
            status = "✅ ACTIVE" if account.is_enabled else "❌ DISABLED"
            print(f"  ID: {account.id}")
            print(f"  Business Connection ID: {account.business_connection_id}")
            print(f"  Telegram User ID: {account.user_id}")
            print(f"  Name: {account.first_name} {account.last_name or ''}")
            print(f"  Username: @{account.username}" if account.username else "  Username: None")
            print(f"  Status: {status}")
            print()

        # Check if user should have multiple separate accounts
        print("=== ANALYSIS ===")

        # Group accounts by telegram user_id
        from collections import defaultdict
        accounts_by_user_id = defaultdict(list)

        for account in all_accounts:
            if account.is_enabled:  # Only consider active accounts
                accounts_by_user_id[account.user_id].append(account)

        print(f"Active accounts grouped by Telegram User ID:")
        for telegram_user_id, accounts in accounts_by_user_id.items():
            print(f"  Telegram User ID {telegram_user_id}: {len(accounts)} active accounts")
            for account in accounts:
                print(f"    - {account.first_name} {account.last_name or ''} (@{account.username})")

        print("\nUser's Telegram User ID:", user.telegram_user_id)
        if user.telegram_user_id in accounts_by_user_id:
            user_accounts = accounts_by_user_id[user.telegram_user_id]
            print(f"User has {len(user_accounts)} active business accounts")

            if len(user_accounts) > 1:
                print("❌ ISSUE: User has multiple active business accounts that should be shown separately!")
                print("Current logic combines them into one virtual account.")
                print("Need to show each business account separately.")
            elif len(user_accounts) == 1:
                print("✅ OK: User has 1 active business account")
            else:
                print("❌ ISSUE: User has no active business accounts")
        else:
            print("❌ ISSUE: User's telegram_user_id not found in any business accounts")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_multiple_accounts()
