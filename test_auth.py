#!/usr/bin/env python3
"""
Script to test authentication functionality.
Run this to verify that login and cookie handling work correctly.
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASS = "admin123"

def test_login():
    """Test login endpoint and cookie handling."""
    print("🔐 Testing login functionality...")

    # Get CSRF token first
    try:
        csrf_response = requests.get(f"{API_BASE_URL}/api/v1/auth/csrf-token", timeout=5)
        if not csrf_response.ok:
            print("❌ Failed to get CSRF token")
            return False

        csrf_data = csrf_response.json()
        csrf_token = csrf_data.get('csrf_token')
        print(f"✅ Got CSRF token: {csrf_token[:10]}...")

    except Exception as e:
        print(f"❌ CSRF token request failed: {e}")
        return False

    # Login with credentials
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASS,
        "csrf_token": csrf_token
    }

    try:
        login_response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json=login_data,
            timeout=5
        )

        if login_response.ok:
            print("✅ Login successful")
            # Check if cookies were set
            cookies = login_response.cookies
            if 'access_token' in cookies:
                print("✅ Access token cookie set")
                return True
            else:
                print("❌ Access token cookie not found")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False

    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return False

def test_protected_endpoint():
    """Test accessing protected endpoint with cookies."""
    print("\n🔒 Testing protected endpoint access...")

    # First login to get cookies
    csrf_response = requests.get(f"{API_BASE_URL}/api/v1/auth/csrf-token", timeout=5)
    if not csrf_response.ok:
        print("❌ Failed to get CSRF token for protected test")
        return False

    csrf_data = csrf_response.json()
    csrf_token = csrf_data.get('csrf_token')

    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASS,
        "csrf_token": csrf_token
    }

    login_response = requests.post(
        f"{API_BASE_URL}/api/v1/auth/login",
        json=login_data,
        timeout=5
    )

    if not login_response.ok:
        print("❌ Could not login for protected endpoint test")
        return False

    # Use the session with cookies to access protected endpoint
    session = requests.Session()
    session.cookies.update(login_response.cookies)

    try:
        protected_response = session.get(
            f"{API_BASE_URL}/api/v1/business-accounts/",
            timeout=5
        )

        if protected_response.status_code == 200:
            print("✅ Protected endpoint accessible")
            return True
        elif protected_response.status_code == 401:
            print("❌ Protected endpoint returned 401 Unauthorized")
            return False
        else:
            print(f"⚠️ Protected endpoint returned {protected_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Protected endpoint request failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting authentication tests...")
    print(f"API URL: {API_BASE_URL}")
    print(f"Test user: {ADMIN_EMAIL}")
    print("-" * 50)

    # Test login
    login_success = test_login()

    if login_success:
        # Test protected endpoint
        protected_success = test_protected_endpoint()

        if protected_success:
            print("\n🎉 All tests passed! Authentication is working correctly.")
            return 0
        else:
            print("\n❌ Protected endpoint test failed.")
            return 1
    else:
        print("\n❌ Login test failed.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
