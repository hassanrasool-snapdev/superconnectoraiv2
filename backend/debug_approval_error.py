import asyncio
import sys
import os
import requests
import json

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, close_mongo_connection, get_database

async def debug_approval_error():
    """Debug the 400 error when approving access requests"""
    print("Debugging approval error...")
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    # Find a test access request
    access_request = await db.access_requests.find_one({"status": "pending"})
    if not access_request:
        print("❌ No pending access requests found")
        await close_mongo_connection()
        return
    
    print(f"Found access request: {access_request['full_name']} ({access_request['email']})")
    print(f"Request ID: {access_request['id']}")
    
    # Test the API endpoint directly
    api_url = f"http://localhost:8000/api/v1/admin/access-requests/{access_request['id']}/approve"
    
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
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(debug_approval_error())