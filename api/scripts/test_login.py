"""Test login functionality."""

import requests

BASE_URL = "http://localhost:5500/api/v1"

def test_login():
    """Test management user login."""
    print("Testing login with form data...")
    
    # Test with correct credentials
    response = requests.post(
        f"{BASE_URL}/management/auth/login",
        data={
            "username": "admin@wathq.sa",  # Email as username
            "password": "Admin@123"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            print("✓ Login successful!")
            print(f"Token: {data['access_token'][:20]}...")
            return data["access_token"]
        else:
            print("✗ No access token in response")
    else:
        print("✗ Login failed")
    
    return None

def test_invalid_login():
    """Test login with invalid credentials."""
    print("\nTesting login with invalid credentials...")
    
    response = requests.post(
        f"{BASE_URL}/management/auth/login",
        data={
            "username": "admin@wathq.sa",
            "password": "WrongPassword"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 401:
        print("✓ Invalid credentials properly rejected")
    else:
        print("✗ Invalid credentials not rejected properly")

def test_protected_endpoint(token):
    """Test accessing a protected endpoint."""
    print("\nTesting protected endpoint with token...")
    
    response = requests.get(
        f"{BASE_URL}/management/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Protected endpoint accessible with token")
    else:
        print("✗ Protected endpoint not accessible")
        print(f"Response: {response.text[:200]}")

def main():
    """Run all tests."""
    print("=" * 50)
    print("Login API Tests")
    print("=" * 50)
    
    # Test valid login
    token = test_login()
    
    # Test invalid login
    test_invalid_login()
    
    # Test protected endpoint if login was successful
    if token:
        test_protected_endpoint(token)
    
    print("\n" + "=" * 50)
    print("Tests completed")
    print("=" * 50)

if __name__ == "__main__":
    main()
