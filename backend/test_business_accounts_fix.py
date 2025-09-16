#!/usr/bin/env python3
"""
Script to test the business accounts fix - verify that duplicates are removed
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.services.business_account_service import BusinessAccountService
from app.models.business_account import BusinessAccount

def test_business_accounts_fix():
    """Test that business accounts are properly filtered and deduplicated."""
    db = SessionLocal()
    try:
        repository = BusinessAccountRepository(db)
        service = BusinessAccountService(db)

        print("Testing business accounts fix...")

        # Get all users to test with
        from app.models.user import User
        users = db.query(User).all()

        if not users:
            print("No users found in database. Please create a test user first.")
            return

        for user in users:
            print(f"\nTesting for user: {user.username or user.id}")

            # Test repository method
            repo_accounts = repository.get_all_business_accounts(user.id)
            print(f"  Repository returned {len(repo_accounts)} accounts")

            # Check for duplicates by connection_id
            connection_ids = [acc.business_connection_id for acc in repo_accounts]
            unique_connection_ids = set(connection_ids)

            if len(connection_ids) != len(unique_connection_ids):
                print("  ❌ Repository: Found duplicates!")
                duplicates = [cid for cid in connection_ids if connection_ids.count(cid) > 1]
                print(f"    Duplicate connection IDs: {set(duplicates)}")
            else:
                print("  ✅ Repository: No duplicates found")

            # Test service method
            service_accounts = service.get_all_business_accounts(user.id)
            print(f"  Service returned {len(service_accounts)} accounts")

            # Check for duplicates by connection_id
            service_connection_ids = [acc.business_connection_id for acc in service_accounts]
            service_unique_connection_ids = set(service_connection_ids)

            if len(service_connection_ids) != len(service_unique_connection_ids):
                print("  ❌ Service: Found duplicates!")
                duplicates = [cid for cid in service_connection_ids if service_connection_ids.count(cid) > 1]
                print(f"    Duplicate connection IDs: {set(duplicates)}")
            else:
                print("  ✅ Service: No duplicates found")

            # Show details of accounts
            if service_accounts:
                print("  Account details:")
                for acc in service_accounts:
                    status = "активен" if acc.is_enabled else "отключен"
                    print(f"    - {acc.first_name} {acc.last_name or ''} (@{acc.username}) [{status}] - ID: {acc.business_connection_id}")

        print("\n" + "="*50)
        print("Test completed!")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_business_accounts_fix()
