#!/usr/bin/env python3
"""
Load 5 Test Records in the Follow-up Emails Queue
================================================

This script creates exactly 5 warm intro requests that are eligible for follow-up emails.
These records will be older than 14 days and have no follow-up sent yet, making them
appear in the follow-up emails queue.

Requirements:
- MongoDB connection configured in .env file
- Backend dependencies installed

Usage:
python load_5_follow_up_test_records.py
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, get_database, close_mongo_connection
from app.models.warm_intro_request import WarmIntroStatus

async def create_test_users():
    """Create test users for the follow-up email test records"""
    db = get_database()
    
    test_users = [
        {
            "id": str(uuid4()),
            "email": "alice.followup@test.com",
            "name": "Alice Johnson",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "role": "user"
        },
        {
            "id": str(uuid4()),
            "email": "bob.followup@test.com", 
            "name": "Bob Smith",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "role": "user"
        },
        {
            "id": str(uuid4()),
            "email": "carol.followup@test.com",
            "name": "Carol Davis",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "role": "user"
        },
        {
            "id": str(uuid4()),
            "email": "david.followup@test.com",
            "name": "David Wilson",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "role": "user"
        },
        {
            "id": str(uuid4()),
            "email": "emma.followup@test.com",
            "name": "Emma Brown",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "role": "user"
        }
    ]
    
    created_users = []
    for user in test_users:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user["email"]})
        if not existing_user:
            await db.users.insert_one(user)
            print(f"✅ Created test user: {user['email']}")
            created_users.append(user)
        else:
            print(f"♻️  Using existing test user: {user['email']}")
            created_users.append(existing_user)
    
    return created_users

async def create_follow_up_test_records():
    """Create exactly 5 warm intro requests eligible for follow-up emails"""
    
    print("🔌 Connecting to database...")
    await connect_to_mongo()
    db = get_database()
    
    # Create test users first
    print("\n👥 Creating test users...")
    users = await create_test_users()
    
    # Create 5 warm intro requests with different ages (all > 14 days)
    test_requests = []
    connection_names = [
        "Sarah Chen", "Michael Rodriguez", "Jennifer Kim", 
        "Alex Thompson", "Maria Garcia"
    ]
    
    for i, (user, connection_name) in enumerate(zip(users, connection_names)):
        # Create requests with different ages: 15, 18, 21, 25, 30 days old
        days_old = 15 + (i * 3) + (i * 2)  # 15, 20, 25, 30, 35 days
        created_date = datetime.utcnow() - timedelta(days=days_old)
        
        request_id = str(uuid4())
        warm_intro_request = {
            "id": request_id,
            "user_id": user["id"],
            "requester_name": user["name"],
            "connection_name": connection_name,
            "requester_first_name": user["name"].split()[0],
            "requester_last_name": user["name"].split()[1],
            "connection_first_name": connection_name.split()[0],
            "connection_last_name": connection_name.split()[1],
            "status": WarmIntroStatus.pending.value,
            "created_at": created_date,
            "updated_at": created_date,
            "connected_date": None,
            "declined_date": None,
            "follow_up_sent_date": None,  # Key: no follow-up sent yet
            "follow_up_skipped": None,
            "follow_up_skipped_date": None,
            "follow_up_skipped_by": None,
            "outcome": None,
            "outcome_date": None
        }
        
        test_requests.append(warm_intro_request)
    
    # Insert all test requests
    print(f"\n📝 Creating {len(test_requests)} follow-up test records...")
    for i, request in enumerate(test_requests, 1):
        # Check if similar request already exists
        existing_request = await db.warm_intro_requests.find_one({
            "user_id": request["user_id"],
            "requester_name": request["requester_name"],
            "connection_name": request["connection_name"]
        })
        
        if existing_request:
            print(f"♻️  Updating existing request {i}/5: {request['requester_name']} → {request['connection_name']}")
            await db.warm_intro_requests.update_one(
                {"id": existing_request["id"]},
                {"$set": {
                    "created_at": request["created_at"],
                    "updated_at": request["updated_at"],
                    "follow_up_sent_date": None,
                    "status": WarmIntroStatus.pending.value
                }}
            )
        else:
            await db.warm_intro_requests.insert_one(request)
            print(f"✅ Created request {i}/5: {request['requester_name']} → {request['connection_name']}")
        
        days_old = (datetime.utcnow() - request['created_at']).days
        print(f"   📅 Age: {days_old} days old (eligible for follow-up)")
    
    return test_requests

async def verify_follow_up_queue():
    """Verify that the 5 test records are in the follow-up queue"""
    print("\n🔍 Verifying follow-up queue...")
    
    db = get_database()
    cutoff_date = datetime.utcnow() - timedelta(days=14)
    
    # Find all eligible requests for follow-up
    cursor = db.warm_intro_requests.find({
        "created_at": {"$lte": cutoff_date},
        "follow_up_sent_date": None,
        "follow_up_skipped": {"$ne": True},
        "status": WarmIntroStatus.pending.value
    })
    
    eligible_requests = await cursor.to_list(length=None)
    
    print(f"📊 Found {len(eligible_requests)} total eligible requests in follow-up queue")
    
    # Show our test records specifically
    test_emails = [
        "alice.followup@test.com", "bob.followup@test.com", "carol.followup@test.com",
        "david.followup@test.com", "emma.followup@test.com"
    ]
    
    test_count = 0
    for request in eligible_requests:
        # Get user email for this request
        user = await db.users.find_one({"id": request["user_id"]})
        if user and user["email"] in test_emails:
            test_count += 1
            days_old = (datetime.utcnow() - request['created_at']).days
            print(f"   ✅ {request['requester_name']} → {request['connection_name']} ({days_old} days old)")
    
    print(f"\n🎯 Test Records in Queue: {test_count}/5")
    
    if test_count == 5:
        print("✅ SUCCESS: All 5 test records are in the follow-up emails queue!")
    else:
        print(f"⚠️  WARNING: Only {test_count} test records found in queue")
    
    return test_count

async def main():
    """Main function to load 5 test records in follow-up emails queue"""
    try:
        print("📧 LOADING 5 TEST RECORDS IN FOLLOW-UP EMAILS QUEUE")
        print("=" * 60)
        print("Creating warm intro requests eligible for follow-up emails...")
        print()
        
        # Create the test records
        test_requests = await create_follow_up_test_records()
        
        # Verify they're in the queue
        queue_count = await verify_follow_up_queue()
        
        print("\n" + "=" * 60)
        print("🎉 FOLLOW-UP EMAIL QUEUE LOADING COMPLETE!")
        print("=" * 60)
        print(f"📝 Created: {len(test_requests)} warm intro requests")
        print(f"📧 In Queue: {queue_count} eligible for follow-up emails")
        print(f"⏰ Age Range: 15-35 days old (all > 14 day threshold)")
        print(f"📊 Status: All pending, no follow-ups sent yet")
        print()
        
        if queue_count == 5:
            print("🚀 NEXT STEPS:")
            print("=" * 30)
            print("1. Access the admin follow-ups interface:")
            print("   http://localhost:3000/admin/follow-ups")
            print()
            print("2. Or test the follow-up API directly:")
            print("   python test_follow_up_email_api.py")
            print()
            print("3. Or trigger follow-up processing:")
            print("   python trigger_follow_up.py")
            print("=" * 30)
        
        return queue_count
        
    except Exception as e:
        print(f"❌ Error loading test records: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    print("🔧 FOLLOW-UP EMAIL QUEUE TEST DATA LOADER")
    print("=" * 50)
    print("This script loads exactly 5 test records into the")
    print("follow-up emails queue for testing purposes.")
    print()
    
    result = asyncio.run(main())
    
    if result == 5:
        print("\n✨ SUCCESS! 5 test records loaded in follow-up emails queue.")
        print("Ready for follow-up email testing!")
    else:
        print(f"\n💥 PARTIAL SUCCESS: {result}/5 records loaded.")
        print("Check the error messages above.")