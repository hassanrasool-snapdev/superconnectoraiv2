import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, close_mongo_connection, get_database

async def check_request_status():
    """Check the status of the test request"""
    print("Checking request status...")
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    # Find the specific request we tested
    request_id = "e9d641d5-8822-4a2b-aaee-a5a90fe733cd"
    request = await db.warm_intro_requests.find_one({"id": request_id})
    
    if request:
        print(f"✅ Found request: {request_id}")
        print(f"   Requester: {request.get('requester_name', 'N/A')}")
        print(f"   Connection: {request.get('connection_name', 'N/A')}")
        print(f"   Status: {request.get('status', 'N/A')}")
        print(f"   User Responded: {request.get('user_responded', 'N/A')}")
        print(f"   Response Date: {request.get('response_date', 'N/A')}")
        print(f"   Follow-up Sent Date: {request.get('follow_up_sent_date', 'N/A')}")
        print(f"   Connected Date: {request.get('connected_date', 'N/A')}")
        print(f"   Created At: {request.get('created_at', 'N/A')}")
        print(f"   Updated At: {request.get('updated_at', 'N/A')}")
        
        # Check if the response was recorded
        if request.get('user_responded') is True:
            print("\n🎉 SUCCESS: User response was recorded!")
            if request.get('status') == 'connected':
                print("🎉 SUCCESS: Status was updated to 'connected'!")
            else:
                print(f"⚠️  Status is '{request.get('status')}' (expected 'connected')")
        else:
            print("\n❌ ISSUE: User response was not recorded")
    else:
        print(f"❌ Request not found: {request_id}")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_request_status())