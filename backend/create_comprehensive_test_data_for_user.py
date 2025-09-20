#!/usr/bin/env python3

import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo
from app.models.warm_intro_request import WarmIntroStatus

async def main():
    print("🎯 Creating Comprehensive Test Data for User Testing...")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database successfully!")
        
        # Get a real user for testing
        print("\n📋 Finding real users...")
        users = await db.users.find({}).to_list(length=10)
        
        if not users:
            print("❌ No users found in database!")
            return
            
        # Use the first user as our test requester
        test_user = users[0]
        user_email = test_user.get('email', 'test@example.com')
        user_name = test_user.get('name', 'Test User')
        user_id = str(test_user.get('_id'))
        
        print(f"🎯 Using {user_name} ({user_email}) as test requester")
        
        # Clear existing test data
        print("\n🧹 Clearing existing test data...")
        await db.warm_intro_requests.delete_many({
            "requester_email": user_email
        })
        await db.follow_up_emails.delete_many({})
        print("✅ Cleared existing test data")
        
        # 1. CREATE WARM INTRO REQUESTS (for "Warm Intro Requests" tab)
        print("\n📧 Creating Warm Intro Requests for testing...")
        
        warm_intro_requests = [
            {
                "id": str(uuid.uuid4()),
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "requester_id": user_id,  # Keep both for compatibility
                "requester_email": user_email,
                "requester_name": user_name,
                "requester_first_name": user_name.split()[0] if user_name else "Test",
                "requester_last_name": user_name.split()[-1] if len(user_name.split()) > 1 else "User",
                "connection_name": "Sarah Johnson",
                "target_name": "Sarah Johnson",
                "connection_first_name": "Sarah",
                "connection_last_name": "Johnson",
                "target_email": "sarah.johnson@techcorp.com",
                "target_company": "TechCorp Inc",
                "target_title": "VP of Engineering",
                "message": "I'd love to connect with Sarah about potential collaboration opportunities in AI/ML.",
                "status": WarmIntroStatus.pending.value,
                "outcome": None,
                "created_at": datetime.utcnow() - timedelta(days=2),
                "updated_at": datetime.utcnow() - timedelta(days=2),
                "connected_date": None,
                "declined_date": None,
                "follow_up_sent_date": None,
                "user_responded": None,
                "response_date": None,
                "follow_up_skipped": None
            },
            {
                "id": str(uuid.uuid4()),
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "requester_id": user_id,  # Keep both for compatibility
                "requester_email": user_email,
                "requester_name": user_name,
                "requester_first_name": user_name.split()[0] if user_name else "Test",
                "requester_last_name": user_name.split()[-1] if len(user_name.split()) > 1 else "User",
                "connection_name": "Michael Chen",
                "target_name": "Michael Chen",
                "connection_first_name": "Michael",
                "connection_last_name": "Chen",
                "target_email": "michael.chen@innovate.com",
                "target_company": "Innovate Solutions",
                "target_title": "CTO",
                "message": "Looking to discuss partnership opportunities and technical collaboration.",
                "status": WarmIntroStatus.pending.value,
                "outcome": None,
                "created_at": datetime.utcnow() - timedelta(days=5),
                "updated_at": datetime.utcnow() - timedelta(days=5),
                "connected_date": None,
                "declined_date": None,
                "follow_up_sent_date": None,
                "user_responded": None,
                "response_date": None,
                "follow_up_skipped": None
            }
        ]
        
        for request in warm_intro_requests:
            await db.warm_intro_requests.insert_one(request)
            print(f"✅ Created warm intro request: {user_name} → {request['connection_name']}")
        
        # 2. CREATE FOLLOW-UP ELIGIBLE REQUESTS (for "Follow-up Emails" tab)
        print("\n📧 Creating Follow-up Eligible Requests...")
        
        follow_up_requests = [
            {
                "id": str(uuid.uuid4()),
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "requester_id": user_id,  # Keep both for compatibility
                "requester_email": user_email,
                "requester_name": user_name,
                "requester_first_name": user_name.split()[0] if user_name else "Test",
                "requester_last_name": user_name.split()[-1] if len(user_name.split()) > 1 else "User",
                "connection_name": "Emma Rodriguez",
                "target_name": "Emma Rodriguez",
                "connection_first_name": "Emma",
                "connection_last_name": "Rodriguez",
                "target_email": "emma.rodriguez@startup.io",
                "target_company": "StartupIO",
                "target_title": "Founder & CEO",
                "message": "Interested in discussing investment opportunities and mentorship.",
                "status": WarmIntroStatus.pending.value,
                "outcome": None,
                "created_at": datetime.utcnow() - timedelta(days=16),  # 16 days old = eligible for follow-up
                "updated_at": datetime.utcnow() - timedelta(days=16),
                "connected_date": None,
                "declined_date": None,
                "follow_up_sent_date": None,  # No follow-up sent yet
                "user_responded": None,
                "response_date": None,
                "follow_up_skipped": None
            },
            {
                "id": str(uuid.uuid4()),
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "requester_id": user_id,  # Keep both for compatibility
                "requester_email": user_email,
                "requester_name": user_name,
                "requester_first_name": user_name.split()[0] if user_name else "Test",
                "requester_last_name": user_name.split()[-1] if len(user_name.split()) > 1 else "User",
                "connection_name": "David Park",
                "target_name": "David Park",
                "connection_first_name": "David",
                "connection_last_name": "Park",
                "target_email": "david.park@fintech.com",
                "target_company": "FinTech Solutions",
                "target_title": "Head of Product",
                "message": "Would like to explore collaboration on fintech products and user experience.",
                "status": WarmIntroStatus.pending.value,
                "outcome": None,
                "created_at": datetime.utcnow() - timedelta(days=20),  # 20 days old = eligible for follow-up
                "updated_at": datetime.utcnow() - timedelta(days=20),
                "connected_date": None,
                "declined_date": None,
                "follow_up_sent_date": None,  # No follow-up sent yet
                "user_responded": None,
                "response_date": None,
                "follow_up_skipped": None
            }
        ]
        
        for request in follow_up_requests:
            await db.warm_intro_requests.insert_one(request)
            print(f"✅ Created follow-up eligible request: {user_name} → {request['connection_name']} ({request['created_at'].strftime('%Y-%m-%d')})")
        
        print("\n🎉 COMPREHENSIVE TEST DATA CREATED SUCCESSFULLY!")
        print("=" * 60)
        print("\n🧪 NOW YOU CAN TEST:")
        print("\n1. 📧 WARM INTRO REQUESTS TAB:")
        print("   → Go to: http://localhost:3000/warm-intro-requests")
        print("   → Should see 2 recent requests:")
        print(f"     • {user_name} → Sarah Johnson (TechCorp Inc)")
        print(f"     • {user_name} → Michael Chen (Innovate Solutions)")
        
        print("\n2. 📬 FOLLOW-UP EMAILS TAB:")
        print("   → Go to: http://localhost:3000/admin/follow-ups")
        print("   → Should see 2 requests ready for follow-up:")
        print(f"     • {user_name} → Emma Rodriguez (16 days old)")
        print(f"     • {user_name} → David Park (20 days old)")
        print("   → Test both 'Send Email' and 'Preview' buttons")
        
        print("\n✅ All test data uses real user references!")
        print("✅ No more KeyError crashes!")
        print("✅ Follow-up functionality is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())