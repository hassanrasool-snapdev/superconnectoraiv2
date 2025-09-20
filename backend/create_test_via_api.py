#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

def create_test_data_via_api():
    """Create test data using HTTP API calls"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # First, let's get an admin token (assuming Ha's credentials)
    # For now, we'll create the data directly via database if API auth is complex
    
    print("🎯 Creating test data via direct database insertion...")
    print("=" * 60)
    
    # Since API requires authentication, let's use a simpler approach
    # Let's create a script that uses the same pattern as the working create_single_test_record.py
    
    import sys
    import os
    import asyncio
    from datetime import datetime, timedelta
    import uuid
    
    # Add the app directory to Python path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
    
    try:
        from app.core.db import connect_to_mongo, get_database
        from app.models.warm_intro_request import WarmIntroStatus
        
        async def create_data():
            # Connect to database first
            await connect_to_mongo()
            db = get_database()
            
            print("✅ Connected to database successfully!")
            
            # Create 1 warm intro request for regression testing
            warm_intro_request = {
                "id": str(uuid.uuid4()),
                "user_id": "ha_user_id",  # Ha's user ID
                "requester_name": "Alice Johnson",
                "connection_name": "Bob Wilson",
                "status": WarmIntroStatus.pending.value,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "follow_up_sent_date": None,
                "follow_up_skipped": False
            }
            
            # Insert warm intro request
            result1 = await db.warm_intro_requests.insert_one(warm_intro_request)
            
            if result1.inserted_id:
                print("✅ SUCCESS: Warm intro request created!")
                print(f"📧 Request: {warm_intro_request['requester_name']} → {warm_intro_request['connection_name']}")
                print()
            
            # Create 3 follow-up email test records (old warm intro requests eligible for follow-up)
            follow_up_requests = []
            names = [
                ("Sarah Chen", "Michael Rodriguez"),
                ("David Park", "Emma Thompson"),
                ("Lisa Wang", "James Anderson")
            ]
            
            for requester, connection in names:
                request = {
                    "id": str(uuid.uuid4()),
                    "user_id": "ha_user_id",  # Ha's user ID
                    "requester_name": requester,
                    "connection_name": connection,
                    "status": WarmIntroStatus.pending.value,
                    "created_at": datetime.utcnow() - timedelta(days=17),  # 17 days old
                    "updated_at": datetime.utcnow() - timedelta(days=17),
                    "follow_up_sent_date": None,
                    "follow_up_skipped": False
                }
                follow_up_requests.append(request)
            
            # Insert follow-up requests
            if follow_up_requests:
                result2 = await db.warm_intro_requests.insert_many(follow_up_requests)
                
                if result2.inserted_ids:
                    print("✅ SUCCESS: Follow-up email test records created!")
                    for i, request in enumerate(follow_up_requests):
                        print(f"📧 Request {i+1}: {request['requester_name']} → {request['connection_name']} (17 days old)")
                    print()
            
            print("🎉 COMPREHENSIVE TEST DATA CREATED SUCCESSFULLY!")
            print("=" * 60)
            print()
            print("🧪 NOW YOU CAN TEST:")
            print("1. Warm Intro Requests (Regression Test):")
            print("   → Go to: http://localhost:3000/warm-intro-requests")
            print("   → Should see: Alice Johnson → Bob Wilson")
            print()
            print("2. Follow-Up Emails (Main Testing):")
            print("   → Go to: http://localhost:3000/admin/follow-ups")
            print("   → Should see 3 requests ready for follow-up")
            print("   → Test both 'Send Email' and 'Test' buttons")
            print()
            print("✅ All test data is ready for comprehensive testing!")
            
            return True
        
        # Run the async function
        return asyncio.run(create_data())
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        return False

if __name__ == "__main__":
    create_test_data_via_api()