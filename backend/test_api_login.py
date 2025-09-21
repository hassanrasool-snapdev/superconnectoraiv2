#!/usr/bin/env python3

import requests
import json

def test_api_login():
    """Test the API login endpoint with the test user credentials"""
    
    # API endpoint
    login_url = "http://localhost:8000/api/v1/auth/login"
    
    # Test credentials
    credentials = {
        "username": "test@example.com",
        "password": "testpass123"
    }
    
    print(f"🔍 Testing API login at: {login_url}")
    print(f"📧 Email: {credentials['username']}")
    
    try:
        # Make the login request
        response = requests.post(
            login_url,
            data=credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful!")
            print(f"🔑 Access Token: {token_data.get('access_token', 'N/A')[:50]}...")
            print(f"🏷️  Token Type: {token_data.get('token_type', 'N/A')}")
            
            # Test a protected endpoint with the token
            test_protected_endpoint(token_data.get('access_token'))
            
        else:
            print(f"❌ Login failed!")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed! Is the server running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_protected_endpoint(access_token):
    """Test a protected endpoint to verify the token works"""
    
    if not access_token:
        print(f"⚠️  No access token to test protected endpoint")
        return
    
    # Test the user profile endpoint
    profile_url = "http://localhost:8000/api/v1/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print(f"\n🔍 Testing protected endpoint: {profile_url}")
    
    try:
        response = requests.get(profile_url, headers=headers)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Protected endpoint access successful!")
            print(f"👤 User ID: {user_data.get('id', 'N/A')}")
            print(f"📧 Email: {user_data.get('email', 'N/A')}")
            print(f"🎭 Role: {user_data.get('role', 'N/A')}")
            print(f"📊 Status: {user_data.get('status', 'N/A')}")
        else:
            print(f"❌ Protected endpoint access failed!")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing protected endpoint: {e}")

if __name__ == "__main__":
    test_api_login()