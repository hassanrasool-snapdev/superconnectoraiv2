#!/usr/bin/env python3
"""
Create a sample test record for testing the 14-day email follow-up process
This creates a warm intro request that's 15 days old and ready for follow-up testing
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

async def create_sample_test_record():
    """Create a sample warm intro request that's 15 days old for follow-up testing"""
    
    print("🚀 Creating sample test record for 14-day email follow-up testing...")
    
    await connect_to_mongo()
    db = get_database()
    
    # First, let's find or create a test user
    test_email = "testuser@example.com"
    test_user = await db.users.find_one({"email": test_email})
    
    if not test_user:
        # Create a test user
        from app.core.security import get_password_hash
        test_user_id = str(uuid4())
        test_user_data = {
            "id": test_user_id,
            "email": test_email,
            "hashed_password": get_password_hash("testpassword123"),
            "role": "user",
            "status": "active",
            "is_premium": False,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        await db.users.insert_one(test_user_data)
        print(f"✅ Created test user: {test_email}")
        user_id = test_user_id
    else:
        user_id = test_user.get("id") or str(test_user.get("_id"))
        print(f"✅ Using existing test user: {test_email}")
    
    # Create a warm intro request that's 15 days old (eligible for follow-up)
    created_date = datetime.utcnow() - timedelta(days=15)
    request_id = str(uuid4())
    
    # Clear any existing test records for this user to avoid confusion
    await db.warm_intro_requests.delete_many({
        "user_id": user_id,
        "requester_name": {"$in": ["Test Requester", "John Doe"]}
    })
    
    warm_intro_request = {
        "id": request_id,
        "user_id": user_id,
        "requester_name": "Test Requester",
        "connection_name": "Jane Smith",
        "requester_first_name": "Test",
        "requester_last_name": "Requester", 
        "connection_first_name": "Jane",
        "connection_last_name": "Smith",
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
    
    print(f"\n✅ Created sample test record for 14-day follow-up:")
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
        print(f"   ✅ Your test record is eligible for follow-up")
    else:
        print(f"   ❌ Your test record is NOT eligible for follow-up")
    
    print(f"\n🎯 How to test the 14-day email process:")
    print(f"   1. Go to the admin follow-ups page: http://localhost:3000/admin/follow-ups")
    print(f"   2. Login with admin credentials")
    print(f"   3. You should see the request: 'Test Requester → Jane Smith'")
    print(f"   4. Click 'Send Email' to test the follow-up email functionality")
    print(f"   5. The email will be sent to: {test_email}")
    print(f"   6. Check the email content and response URLs")
    
    print(f"\n📧 Test User Login Credentials:")
    print(f"   Email: {test_email}")
    print(f"   Password: testpassword123")
    
    print(f"\n✨ Sample test record created successfully!")

if __name__ == "__main__":
    asyncio.run(create_sample_test_record())