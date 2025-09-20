import asyncio
import sys
import os
import requests
import json

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_emily_approval():
    """Test approving Emily Davis's specific request"""
    print("Testing Emily Davis's approval...")
    
    # Emily Davis's request ID from the browser error
    request_id = "174b4941-4754-47a6-b891-9f17018c93e0"
    
    # Test the API endpoint directly
    api_url = f"http://localhost:8000/api/v1/admin/access-requests/{request_id}/approve"
    
    # First, we need to get an admin token
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "username": "admin@superconnect.ai",
        "password": "admin123"
    }
    
    try:
        # Login to get token
        print("Logging in to get admin token...")
        login_response = requests.post(login_url, data=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Got admin token: {token[:20]}...")
            
            # Test approval endpoint
            print(f"Testing approval endpoint: {api_url}")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            approval_response = requests.post(api_url, headers=headers)
            print(f"Approval response status: {approval_response.status_code}")
            print(f"Approval response text: {approval_response.text}")
            
            if approval_response.status_code != 200:
                try:
                    error_data = approval_response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Raw error response: {approval_response.text}")
            else:
                print("✅ Emily's approval succeeded!")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    asyncio.run(test_emily_approval())