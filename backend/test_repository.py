#!/usr/bin/env python3
"""
Test repository methods directly
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.user import User

def test_repository():
    """Test repository methods."""
    db = SessionLocal()
    try:
        repo = BusinessAccountRepository(db)

        print("=== TESTING REPOSITORY ===\n")

        # Get user
        user = db.query(User).filter(User.username == "maksimleznin30").first()
        print(f"User: {user.username} (ID: {user.id})")
        print(f"Telegram User ID: {user.telegram_user_id}")

        if not user.telegram_user_id:
            print("❌ No telegram_user_id for user")
            return

        # Test repository method directly
        accounts = repo.get_all_business_accounts(user.id)
        print(f"\nRepository returned {len(accounts)} accounts:")

        for account in accounts:
            print(f"  - {account.business_connection_id}: {'✅' if account.is_enabled else '❌'}")

        # Test direct query
        print("\nDirect query results:")
        direct_accounts = db.query(BusinessAccount).filter(
            BusinessAccount.user_id == user.telegram_user_id
        ).all()

        print(f"Direct query returned {len(direct_accounts)} accounts:")
        for account in direct_accounts:
            print(f"  - {account.business_connection_id}: {'✅' if account.is_enabled else '❌'}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_repository()
