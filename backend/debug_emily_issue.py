import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, close_mongo_connection, get_database

async def debug_emily_issue():
    """Debug Emily Davis's specific issue"""
    print("Debugging Emily Davis's approval issue...")
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    emily_email = "emily.davis.test@example.com"
    emily_id = "174b4941-4754-47a6-b891-9f17018c93e0"
    
    # Check access request status
    print(f"\n1. Checking access request for {emily_email}...")
    access_request = await db.access_requests.find_one({"id": emily_id})
    if access_request:
        print(f"   ✅ Access request found")
        print(f"   Status: {access_request['status']}")
        print(f"   Email: {access_request['email']}")
        print(f"   Full Name: {access_request['full_name']}")
        print(f"   Created: {access_request.get('created_at', 'N/A')}")
        print(f"   Processed: {access_request.get('processed_at', 'N/A')}")
    else:
        print(f"   ❌ Access request not found")
    
    # Check if user already exists
    print(f"\n2. Checking if user exists for {emily_email}...")
    existing_user = await db.users.find_one({"email": emily_email})
    if existing_user:
        print(f"   ❌ User already exists!")
        print(f"   User ID: {existing_user['id']}")
        print(f"   Role: {existing_user['role']}")
        print(f"   Status: {existing_user['status']}")
        print(f"   Created: {existing_user.get('created_at', 'N/A')}")
    else:
        print(f"   ✅ No user exists with this email")
    
    # Check template files
    print(f"\n3. Checking template files...")
    template_path = os.path.join(os.path.dirname(__file__), 'app', 'templates', 'access-approved.html')
    if os.path.exists(template_path):
        print(f"   ✅ Template file exists: {template_path}")
    else:
        print(f"   ❌ Template file missing: {template_path}")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(debug_emily_issue())