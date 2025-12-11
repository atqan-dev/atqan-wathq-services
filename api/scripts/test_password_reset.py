"""Test password reset functionality."""

import requests
import json
import time

BASE_URL = "http://localhost:5500/api/v1"

def test_forgot_password():
    """Test forgot password endpoint."""
    print("Testing forgot password...")
    
    response = requests.post(
        f"{BASE_URL}/management/password/forgot-password",
        json={"email": "admin@wathq.sa"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✓ Forgot password request successful")
        # In a real scenario, check email or logs for the reset token
        print("\n⚠️  Check the backend console for the reset link/token")
    else:
        print("✗ Forgot password request failed")
    
    return response.status_code == 200


def test_reset_with_invalid_token():
    """Test reset password with invalid token."""
    print("\nTesting reset with invalid token...")
    
    response = requests.post(
        f"{BASE_URL}/management/password/reset-password",
        json={
            "token": "invalid_token_12345",
            "new_password": "NewPassword123!"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400:
        print("✓ Invalid token properly rejected")
    else:
        print("✗ Invalid token not rejected properly")
    
    return response.status_code == 400


def test_validate_invalid_token():
    """Test token validation with invalid token."""
    print("\nTesting token validation with invalid token...")
    
    response = requests.post(
        f"{BASE_URL}/management/password/validate-token",
        params={"token": "invalid_token_12345"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400:
        print("✓ Invalid token validation working")
    else:
        print("✗ Invalid token validation not working")
    
    return response.status_code == 400


def main():
    """Run all tests."""
    print("=" * 50)
    print("Password Reset API Tests")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 3
    
    # Test 1: Forgot password
    if test_forgot_password():
        tests_passed += 1
    
    # Test 2: Reset with invalid token
    if test_reset_with_invalid_token():
        tests_passed += 1
    
    # Test 3: Validate invalid token
    if test_validate_invalid_token():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print("=" * 50)
    
    if tests_passed == tests_total:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed")
    
    print("\n📝 Note: To fully test the reset flow:")
    print("1. Run test_forgot_password() and get the token from backend console")
    print("2. Use that token to test the actual reset")


if __name__ == "__main__":
    main()
