import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo
from app.models.warm_intro_request import WarmIntroStatus

async def create_14_day_follow_up_test():
    """Create a warm intro request that's 14+ days old for follow-up testing"""
    
    await connect_to_mongo()
    db = get_database()
    
    # Get a test user (we'll use the existing test user)
    test_user = await db.users.find_one({"email": "test@example.com"})
    if not test_user:
        print("❌ Test user not found. Please create a test user first.")
        return
    
    user_id = test_user.get("id") or test_user.get("_id")
    print(f"📧 Using test user: {test_user['email']} (ID: {user_id})")
    
    # Create a warm intro request that's 15 days old (to ensure it's eligible for follow-up)
    created_date = datetime.utcnow() - timedelta(days=15)
    request_id = str(uuid4())
    
    warm_intro_request = {
        "id": request_id,
        "user_id": user_id,
        "requester_name": "John Smith",
        "connection_name": "Sarah Johnson",
        "requester_first_name": "John",
        "requester_last_name": "Smith", 
        "connection_first_name": "Sarah",
        "connection_last_name": "Johnson",
        "status": WarmIntroStatus.pending.value,
        "outcome": None,
        "outcome_date": None,
        "created_at": created_date,
        "updated_at": created_date,
        "connected_date": None,
        "declined_date": None,
        "follow_up_sent_date": None,  # This is key - no follow-up sent yet
        "follow_up_skipped": None,    # Not skipped
        "follow_up_skipped_date": None,
        "follow_up_skipped_by": None
    }
    
    # Insert the warm intro request
    await db.warm_intro_requests.insert_one(warm_intro_request)
    
    print(f"✅ Created 14-day follow-up test request:")
    print(f"   🆔 Request ID: {request_id}")
    print(f"   👤 Requester: {warm_intro_request['requester_name']}")
    print(f"   🤝 Connection: {warm_intro_request['connection_name']}")
    print(f"   📅 Created: {created_date.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"   📊 Status: {warm_intro_request['status']}")
    print(f"   📧 User Email: {test_user['email']}")
    print(f"   ⏰ Days Old: {(datetime.utcnow() - created_date).days}")
    
    # Verify it would be picked up by the follow-up system
    cutoff_date = datetime.utcnow() - timedelta(days=14)
    eligible_requests = await db.warm_intro_requests.find({
        "created_at": {"$lte": cutoff_date},
        "follow_up_sent_date": None,
        "follow_up_skipped": {"$ne": True},
        "status": WarmIntroStatus.pending.value
    }).to_list(length=None)
    
    print(f"\n🔍 Verification:")
    print(f"   📊 Total eligible follow-up requests: {len(eligible_requests)}")
    
    # Check if our new request is in the list
    our_request = next((req for req in eligible_requests if req["id"] == request_id), None)
    if our_request:
        print(f"   ✅ Our test request is eligible for follow-up")
    else:
        print(f"   ❌ Our test request is NOT eligible for follow-up")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Go to the admin follow-ups page: http://localhost:3000/admin/follow-ups")
    print(f"   2. You should see the request for John Smith → Sarah Johnson")
    print(f"   3. Click 'Send Email' to test the follow-up email functionality")
    print(f"   4. Or click 'Skip' to mark it as skipped")

if __name__ == "__main__":
    asyncio.run(create_14_day_follow_up_test())