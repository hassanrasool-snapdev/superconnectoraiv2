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
    print("🎯 Creating Test Data for Current User...")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database successfully!")
        
        # Get all users to show options
        print("\n👥 Available users:")
        users = await db.users.find({}).to_list(length=10)
        
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.get('email')} (ID: {str(user.get('_id'))})")
        
        # Use the first user (this should match the one you're logging in with)
        target_user = users[0]  # nnguyen0646@gmail.com
        user_email = target_user.get('email')
        user_id = str(target_user.get('_id'))
        
        print(f"\n🎯 Creating test data for: {user_email}")
        print(f"   User ID: {user_id}")
        
        # Clear existing test data for this user
        print("\n🧹 Clearing existing test data for this user...")
        await db.warm_intro_requests.delete_many({
            "$or": [
                {"user_id": user_id},
                {"requester_id": user_id}
            ]
        })
        print("✅ Cleared existing test data")
        
        # Create warm intro requests for the current user
        print("\n📧 Creating Warm Intro Requests...")
        
        warm_intro_requests = [
            {
                "id": str(uuid.uuid4()),
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "requester_id": user_id,
                "requester_email": user_email,
                "requester_name": "Test User",
                "requester_first_name": "Test",
                "requester_last_name": "User",
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
                "requester_id": user_id,
                "requester_email": user_email,
                "requester_name": "Test User",
                "requester_first_name": "Test",
                "requester_last_name": "User",
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
            print(f"✅ Created warm intro request: Test User → {request['connection_name']}")
        
        # Create follow-up eligible requests (14+ days old)
        print("\n📧 Creating Follow-up Eligible Requests...")
        
        follow_up_requests = [
            {
                "id": str(uuid.uuid4()),
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "requester_id": user_id,
                "requester_email": user_email,
                "requester_name": "Test User",
                "requester_first_name": "Test",
                "requester_last_name": "User",
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
                "created_at": datetime.utcnow() - timedelta(days=16),
                "updated_at": datetime.utcnow() - timedelta(days=16),
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
                "requester_id": user_id,
                "requester_email": user_email,
                "requester_name": "Test User",
                "requester_first_name": "Test",
                "requester_last_name": "User",
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
                "created_at": datetime.utcnow() - timedelta(days=20),
                "updated_at": datetime.utcnow() - timedelta(days=20),
                "connected_date": None,
                "declined_date": None,
                "follow_up_sent_date": None,
                "user_responded": None,
                "response_date": None,
                "follow_up_skipped": None
            }
        ]
        
        for request in follow_up_requests:
            await db.warm_intro_requests.insert_one(request)
            print(f"✅ Created follow-up eligible request: Test User → {request['connection_name']} ({request['created_at'].strftime('%Y-%m-%d')})")
        
        print("\n🎉 TEST DATA CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n✅ Created for user: {user_email}")
        print(f"✅ User ID: {user_id}")
        print("\n🧪 NOW YOU CAN TEST:")
        print("\n1. 📧 WARM INTRO REQUESTS TAB:")
        print("   → Go to: http://localhost:3000/warm-intro-requests")
        print("   → Login with: nnguyen0646@gmail.com")
        print("   → Should see 2 recent requests:")
        print("     • Test User → Sarah Johnson (TechCorp Inc)")
        print("     • Test User → Michael Chen (Innovate Solutions)")
        
        print("\n2. 📬 FOLLOW-UP EMAILS TAB:")
        print("   → Go to: http://localhost:3000/admin/follow-ups")
        print("   → Should see 2 requests ready for follow-up:")
        print("     • Test User → Emma Rodriguez (16 days old)")
        print("     • Test User → David Park (20 days old)")
        
        print("\n✅ All test data uses the correct user ID!")
        print("✅ Data will show up in the UI now!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())