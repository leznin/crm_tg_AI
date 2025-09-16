#!/usr/bin/env python3
"""
Test API endpoint for business accounts
"""
import sys
import os
import requests

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_business_accounts():
    """Test the business accounts API endpoint."""
    base_url = "http://localhost:8000"

    print("Testing business accounts API...")

    try:
        # First, we need to authenticate
        # For testing purposes, let's try without authentication first
        response = requests.get(f"{base_url}/api/v1/business-accounts/", allow_redirects=False)

        if response.status_code == 401:
            print("❌ Authentication required")
            print("Please log in through the frontend to test this endpoint")
            return
        elif response.status_code == 200:
            data = response.json()
            print("✅ API call successful!")
            print(f"Found {len(data.get('accounts', []))} business accounts")

            for account in data.get('accounts', []):
                print(f"  - {account['first_name']} {account.get('last_name', '')} (@{account.get('username', 'no_username')})")

        else:
            print(f"❌ API error: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_business_accounts()
