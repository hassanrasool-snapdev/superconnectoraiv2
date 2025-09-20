#!/usr/bin/env python3
"""
Quick verification script to check the follow-up email queue
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, get_database, close_mongo_connection
from app.services.follow_up_email_service import get_eligible_warm_intro_requests

async def verify_queue():
    """Verify the follow-up email queue contains our test records"""
    await connect_to_mongo()
    db = get_database()
    
    try:
        # Get all eligible requests
        eligible = await get_eligible_warm_intro_requests(db)
        print(f"Total eligible requests in follow-up queue: {len(eligible)}")
        
        # Check for our specific test records
        test_emails = [
            'alice.followup@test.com', 'bob.followup@test.com', 'carol.followup@test.com',
            'david.followup@test.com', 'emma.followup@test.com'
        ]
        
        test_count = 0
        print("\nOur test records in the queue:")
        
        for request in eligible:
            user = await db.users.find_one({'id': request['user_id']})
            if user and user['email'] in test_emails:
                test_count += 1
                days_old = (datetime.utcnow() - request['created_at']).days
                print(f"✅ {request['requester_name']} → {request['connection_name']} ({days_old} days old)")
        
        print(f"\nTest records found: {test_count}/5")
        
        if test_count == 5:
            print("🎉 SUCCESS: All 5 test records are properly loaded in the follow-up emails queue!")
        else:
            print(f"⚠️ WARNING: Only {test_count} test records found")
            
        return test_count
        
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    result = asyncio.run(verify_queue())