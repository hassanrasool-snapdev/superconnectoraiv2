#!/usr/bin/env python3
"""
🌱 SEED TEST DATA FOR FOLLOW-UP EMAIL FEATURE
==============================================

This script creates sample WarmIntroRequest data that is older than 14 days
and has not yet been responded to, making it eligible for automated follow-up emails.

WHAT THIS SCRIPT DOES:
1. Creates a test user (if not exists)
2. Creates a WarmIntroRequest with a timestamp 15 days in the past
3. Sets up the data so it's immediately eligible for follow-up processing

REQUIREMENTS:
- MongoDB connection configured in .env file
- Backend dependencies installed (pip install -r requirements.txt)

USAGE:
1. Run this script: python seed_test_follow_up.py
2. Then run the trigger script: python trigger_follow_up.py
3. Test the response links in your browser

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

async def create_test_warm_intro_request():
    """Create a sample WarmIntroRequest for testing follow-up emails"""
    
    print("🔌 Connecting to database...")
    await connect_to_mongo()
    db = get_database()
    
    # Create a test user first (if not exists)
    test_user_id = str(uuid4())
    test_user_email = "test.followup@example.com"
    
    test_user = {
        "id": test_user_id,
        "email": test_user_email,
        "name": "Follow-up Test User",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
        "role": "user"
    }
    
    # Check if test user already exists
    existing_user = await db.users.find_one({"email": test_user_email})
    if not existing_user:
        await db.users.insert_one(test_user)
        print(f"✅ Created test user: {test_user_email}")
    else:
        test_user_id = existing_user["id"]
        print(f"♻️  Using existing test user: {test_user_email}")
    
    # Create warm intro request with timestamp 15 days in the past
    request_id = str(uuid4())
    fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
    
    warm_intro_request = {
        "id": request_id,
        "user_id": test_user_id,
        "requester_name": "Alice Johnson",
        "connection_name": "Bob Wilson",
        "requester_first_name": "Alice",
        "requester_last_name": "Johnson",
        "connection_first_name": "Bob",
        "connection_last_name": "Wilson",
        "status": WarmIntroStatus.pending.value,
        "created_at": fifteen_days_ago,
        "updated_at": fifteen_days_ago,
        "connected_date": None,
        "declined_date": None,
        "follow_up_sent_date": None,  # This is key - no follow-up sent yet
        "user_responded": None,
        "response_date": None
    }
    
    # Check if a similar request already exists
    existing_request = await db.warm_intro_requests.find_one({
        "user_id": test_user_id,
        "requester_name": "Alice Johnson",
        "connection_name": "Bob Wilson"
    })
    
    if existing_request:
        print("♻️  Similar test request already exists, updating it...")
        await db.warm_intro_requests.update_one(
            {"id": existing_request["id"]},
            {"$set": {
                "created_at": fifteen_days_ago,
                "updated_at": fifteen_days_ago,
                "follow_up_sent_date": None,
                "user_responded": None,
                "response_date": None,
                "status": WarmIntroStatus.pending.value
            }}
        )
        request_id = existing_request["id"]
    else:
        # Insert the new warm intro request
        await db.warm_intro_requests.insert_one(warm_intro_request)
        print("✅ Created new test warm intro request")
    
    print("\n" + "=" * 70)
    print("🎉 TEST DATA SETUP COMPLETE!")
    print("=" * 70)
    print(f"📋 Request ID: {request_id}")
    print(f"👤 User ID: {test_user_id}")
    print(f"📧 User Email: {test_user_email}")
    print(f"🙋 Requester: {warm_intro_request['requester_name']}")
    print(f"🤝 Connection: {warm_intro_request['connection_name']}")
    print(f"📊 Status: {warm_intro_request['status']}")
    print(f"📅 Created: {fifteen_days_ago.strftime('%Y-%m-%d %H:%M:%S')} (15 days ago)")
    print(f"📬 Follow-up Sent: {warm_intro_request['follow_up_sent_date']}")
    print("=" * 70)
    
    # Close database connection
    await close_mongo_connection()
    
    return request_id

async def verify_setup():
    """Verify that the test data is properly set up"""
    print("\n🔍 Verifying test data setup...")
    
    await connect_to_mongo()
    db = get_database()
    
    # Check for eligible requests
    cutoff_date = datetime.utcnow() - timedelta(days=14)
    
    cursor = db.warm_intro_requests.find({
        "created_at": {"$lte": cutoff_date},
        "follow_up_sent_date": None,
        "status": WarmIntroStatus.pending.value
    })
    
    eligible_requests = await cursor.to_list(length=None)
    
    if eligible_requests:
        print(f"✅ Found {len(eligible_requests)} eligible request(s) for follow-up")
        for req in eligible_requests:
            days_old = (datetime.utcnow() - req['created_at']).days
            print(f"   • {req['requester_name']} → {req['connection_name']} ({days_old} days old)")
    else:
        print("❌ No eligible requests found. Something went wrong!")
    
    await close_mongo_connection()
    return len(eligible_requests)

async def main():
    """Main function to run the seeding script"""
    try:
        print("🌱 FOLLOW-UP EMAIL TEST DATA SEEDER")
        print("=" * 40)
        print("Setting up test data for follow-up email feature...")
        print()
        
        request_id = await create_test_warm_intro_request()
        eligible_count = await verify_setup()
        
        if eligible_count > 0:
            print("\n🚀 NEXT STEPS:")
            print("=" * 40)
            print("1. Run the trigger script:")
            print("   python trigger_follow_up.py")
            print()
            print("2. The trigger script will:")
            print("   • Find eligible requests (15+ days old)")
            print("   • Generate follow-up email content")
            print("   • Display the email content in console")
            print("   • Show response links for testing")
            print()
            print("3. Test the response links:")
            print("   • Copy the 'YES' and 'NO' links from trigger output")
            print("   • Follow-up emails now ask users to reply directly")
            print("   • The warm-intro-response pages have been removed")
            print("   • Test the donate page link")
            print()
            print("4. Check database updates:")
            print("   • Verify follow_up_sent_date is updated")
            print("   • Verify user responses are recorded")
            print("=" * 40)
        
        return request_id
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🔧 MANUAL TESTING SETUP FOR FOLLOW-UP EMAILS")
    print("=" * 50)
    print("This script prepares test data for manual testing of the")
    print("automated follow-up email feature.")
    print()
    
    result = asyncio.run(main())
    
    if result:
        print("\n✨ SUCCESS! Test data is ready.")
        print("Run 'python trigger_follow_up.py' next.")
    else:
        print("\n💥 FAILED! Check the error messages above.")