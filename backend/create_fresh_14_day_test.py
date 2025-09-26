#!/usr/bin/env python3
"""
Create a fresh sample test record for testing the 14-day email follow-up process
This creates a new warm intro request that's 15 days old and ready for follow-up testing
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo
from app.models.warm_intro_request import WarmIntroStatus

async def create_fresh_test_record():
    """Create a fresh warm intro request that's 15 days old for follow-up testing"""
    
    print("🚀 Creating fresh sample test record for 14-day email follow-up testing...")
    
    await connect_to_mongo()
    db = get_database()
    
    # Use the existing test user
    test_email = "testuser@example.com"
    test_user = await db.users.find_one({"email": test_email})
    
    if not test_user:
        print("❌ Test user not found! Please run create_sample_14_day_test_record.py first.")
        return
    
    user_id = test_user.get("id") or str(test_user.get("_id"))
    print(f"✅ Using existing test user: {test_email}")
    
    # Create a new warm intro request that's 15 days old (eligible for follow-up)
    created_date = datetime.utcnow() - timedelta(days=15)
    request_id = str(uuid4())
    
    # Clear any existing test records for this user to avoid confusion
    await db.warm_intro_requests.delete_many({
        "user_id": user_id,
        "requester_name": {"$in": ["Fresh Test Requester", "Test Requester"]}
    })
    
    warm_intro_request = {
        "id": request_id,
        "user_id": user_id,
        "requester_name": "Fresh Test Requester",
        "connection_name": "Alex Johnson",
        "requester_first_name": "Fresh Test",
        "requester_last_name": "Requester", 
        "connection_first_name": "Alex",
        "connection_last_name": "Johnson",
        "status": WarmIntroStatus.pending.value,
        "outcome": None,
        "outcome_date": None,
        "created_at": created_date,
        "updated_at": created_date,
        "connected_date": None,
        "declined_date": None,
        "follow_up_sent_date": None,  # Key: no follow-up sent yet
        "follow_up_skipped": None,    # Not skipped
        "follow_up_skipped_date": None,
        "follow_up_skipped_by": None
    }
    
    # Insert the warm intro request
    await db.warm_intro_requests.insert_one(warm_intro_request)
    
    print(f"\n✅ Created fresh sample test record for 14-day follow-up:")
    print(f"   🆔 Request ID: {request_id}")
    print(f"   👤 Requester: {warm_intro_request['requester_name']}")
    print(f"   🤝 Connection: {warm_intro_request['connection_name']}")
    print(f"   📅 Created: {created_date.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"   📊 Status: {warm_intro_request['status']}")
    print(f"   📧 User Email: {test_email}")
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
        print(f"   ✅ Your fresh test record is eligible for follow-up")
    else:
        print(f"   ❌ Your fresh test record is NOT eligible for follow-up")
    
    print(f"\n🎯 How to test the 14-day email process:")
    print(f"   1. Go to the admin follow-ups page: http://localhost:3000/admin/follow-ups")
    print(f"   2. Login with admin credentials")
    print(f"   3. You should see the request: 'Fresh Test Requester → Alex Johnson'")
    print(f"   4. Click 'Send Email' to test the follow-up email functionality")
    print(f"   5. The email will be sent to: {test_email}")
    print(f"   6. Check the email content and response URLs")
    
    print(f"\n📧 Test User Login Credentials:")
    print(f"   Email: {test_email}")
    print(f"   Password: testpassword123")
    
    print(f"\n✨ Fresh sample test record created successfully!")

if __name__ == "__main__":
    asyncio.run(create_fresh_test_record())