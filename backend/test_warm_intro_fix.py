#!/usr/bin/env python3
"""
Test script to verify warm intro request creation works with authentication
"""
import asyncio
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

async def test_warm_intro_creation():
    """Test the complete flow of creating a warm intro request"""
    
    print("🧪 Testing Warm Intro Request Creation...")
    
    # Step 1: Login to get authentication token
    print("\n1. Logging in...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
            
        token_data = login_response.json()
        token = token_data.get("access_token")
        print(f"   ✅ Login successful, got token: {token[:20]}...")
        
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Step 2: Create warm intro request
    print("\n2. Creating warm intro request...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    warm_intro_data = {
        "requester_name": "Test User",
        "connection_name": "Maegan Cardillo",
        "status": "pending"
    }
    
    try:
        create_response = requests.post(
            f"{BASE_URL}/warm-intro-requests/", 
            headers=headers,
            json=warm_intro_data
        )
        print(f"   Create status: {create_response.status_code}")
        
        if create_response.status_code == 201:
            result = create_response.json()
            print(f"   ✅ Warm intro request created successfully!")
            print(f"   Request ID: {result.get('id')}")
            print(f"   Requester: {result.get('requester_name')}")
            print(f"   Connection: {result.get('connection_name')}")
            print(f"   Status: {result.get('status')}")
            request_id = result.get('id')
        else:
            print(f"   ❌ Creation failed: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Creation error: {e}")
        return False
    
    # Step 3: Verify the request appears in the list
    print("\n3. Verifying request appears in list...")
    try:
        list_response = requests.get(
            f"{BASE_URL}/warm-intro-requests/?page=1&limit=10",
            headers=headers
        )
        print(f"   List status: {list_response.status_code}")
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            total_requests = list_data.get('total', 0)
            items = list_data.get('items', [])
            
            print(f"   ✅ Found {total_requests} total requests")
            
            # Check if our request is in the list
            found_request = None
            for item in items:
                if item.get('id') == request_id:
                    found_request = item
                    break
            
            if found_request:
                print(f"   ✅ Our request found in the list!")
                print(f"   Connection: {found_request.get('connection_name')}")
                return True
            else:
                print(f"   ❌ Our request not found in the list")
                return False
        else:
            print(f"   ❌ List retrieval failed: {list_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ List retrieval error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_warm_intro_creation())
    
    if success:
        print("\n🎉 SUCCESS: Warm intro request creation is working properly!")
        print("   - Authentication is working")
        print("   - Database insertion is working") 
        print("   - Request appears in the list")
    else:
        print("\n❌ FAILURE: There are still issues with warm intro request creation")