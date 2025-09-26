#!/usr/bin/env python3
"""
Verify the fresh test record is ready for 14-day follow-up testing
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo
from app.models.warm_intro_request import WarmIntroStatus

async def verify_fresh_test():
    """Verify the fresh test record is properly set up for follow-up testing"""
    
    print("🔍 Verifying fresh test record for 14-day follow-up testing...")
    
    await connect_to_mongo()
    db = get_database()
    
    # Find our fresh test record
    test_record = await db.warm_intro_requests.find_one({
        "requester_name": "Fresh Test Requester",
        "connection_name": "Alex Johnson"
    })
    
    if not test_record:
        print("❌ Fresh test record not found!")
        return
    
    print(f"✅ Found fresh test record:")
    print(f"   🆔 Request ID: {test_record['id']}")
    print(f"   👤 Requester: {test_record['requester_name']}")
    print(f"   🤝 Connection: {test_record['connection_name']}")
    print(f"   📅 Created: {test_record['created_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"   📊 Status: {test_record['status']}")
    print(f"   ⏰ Days Old: {(datetime.utcnow() - test_record['created_at']).days}")
    
    # Check follow-up eligibility
    cutoff_date = datetime.utcnow() - timedelta(days=14)
    is_eligible = (
        test_record['created_at'] <= cutoff_date and
        test_record.get('follow_up_sent_date') is None and
        test_record.get('follow_up_skipped') != True and
        test_record['status'] == WarmIntroStatus.pending.value
    )
    
    print(f"\n🎯 Follow-up Eligibility Check:")
    print(f"   📅 Created before cutoff: {'✅' if test_record['created_at'] <= cutoff_date else '❌'}")
    print(f"   📧 No follow-up sent yet: {'✅' if test_record.get('follow_up_sent_date') is None else '❌'}")
    print(f"   🚫 Not skipped: {'✅' if test_record.get('follow_up_skipped') != True else '❌'}")
    print(f"   📊 Status is pending: {'✅' if test_record['status'] == WarmIntroStatus.pending.value else '❌'}")
    print(f"   🎉 Overall eligible: {'✅' if is_eligible else '❌'}")
    
    if is_eligible:
        print(f"\n🚀 Ready for testing! Next steps:")
        print(f"   1. Go to: http://localhost:3000/admin/follow-ups")
        print(f"   2. Login as admin")
        print(f"   3. Look for: 'Fresh Test Requester → Alex Johnson'")
        print(f"   4. Click 'Send Email' to test the follow-up")
        print(f"   5. Email will be sent to: testuser@example.com")
        print(f"\n📧 Test User Credentials:")
        print(f"   Email: testuser@example.com")
        print(f"   Password: testpassword123")
    else:
        print(f"\n❌ Record is not eligible for follow-up. Check the conditions above.")

if __name__ == "__main__":
    asyncio.run(verify_fresh_test())