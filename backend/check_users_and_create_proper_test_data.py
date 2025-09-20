#!/usr/bin/env python3

import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo

async def main():
    print("🔍 Checking existing users and creating proper test data...")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database successfully!")
        
        # Check existing users
        print("\n📋 EXISTING USERS:")
        users = await db.users.find({}).to_list(length=None)
        
        if not users:
            print("❌ No users found in database!")
            return
            
        for i, user in enumerate(users, 1):
            print(f"{i}. Email: {user.get('email', 'N/A')}")
            print(f"   Name: {user.get('name', 'N/A')}")
            print(f"   ID: {str(user.get('_id', 'N/A'))}")
            print("   ---")
        
        # Use the first user as requester for test data
        if len(users) >= 1:
            requester = users[0]
            requester_email = requester.get('email', 'test@example.com')
            requester_name = requester.get('name', 'Test User')
            requester_id = str(requester.get('_id'))
            
            print(f"\n🎯 Using {requester_name} ({requester_email}) as requester for test data")
            
            # Clear existing test data first
            print("\n🧹 Clearing existing test data...")
            await db.warm_intro_requests.delete_many({
                "requester_email": {"$in": [
                    "alice.johnson@example.com",
                    "sarah.chen@example.com", 
                    "david.park@example.com",
                    "lisa.wang@example.com"
                ]}
            })
            await db.follow_up_emails.delete_many({
                "warm_intro_request_id": {"$regex": "^(c2c6d9e5|d9490df3|88c5fe2d)"}
            })
            print("✅ Cleared existing test data")
            
            # Create warm intro request (for regression testing)
            print("\n📧 Creating warm intro request...")
            warm_intro_id = str(uuid.uuid4())
            warm_intro_request = {
                "id": warm_intro_id,
                "_id": warm_intro_id,
                "requester_email": requester_email,
                "requester_name": requester_name,
                "user_id": requester_id,
                "requester_id": requester_id,  # Keep both for compatibility
                "connection_name": "Bob Wilson",
                "target_name": "Bob Wilson",
                "target_email": "bob.wilson@example.com",
                "target_company": "Wilson Corp",
                "target_title": "VP of Sales",
                "message": "I'd love to connect with Bob about potential collaboration opportunities.",
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            
            await db.warm_intro_requests.insert_one(warm_intro_request)
            print(f"✅ Created warm intro request: {requester_name} → Bob Wilson")
            
            # Create follow-up eligible requests (17 days old)
            print("\n📧 Creating follow-up eligible requests...")
            
            follow_up_requests = [
                {
                    "id": str(uuid.uuid4()),
                    "_id": str(uuid.uuid4()),
                    "requester_email": requester_email,
                    "requester_name": requester_name,
                    "user_id": requester_id,
                    "requester_id": requester_id,  # Keep both for compatibility
                    "connection_name": "Michael Rodriguez",
                    "target_name": "Michael Rodriguez",
                    "target_email": "michael.rodriguez@example.com",
                    "target_company": "Rodriguez Industries",
                    "target_title": "CEO",
                    "message": "Looking to discuss partnership opportunities.",
                    "status": "pending",
                    "created_at": datetime.utcnow() - timedelta(days=17),
                    "updated_at": datetime.utcnow() - timedelta(days=17),
                },
                {
                    "id": str(uuid.uuid4()),
                    "_id": str(uuid.uuid4()),
                    "requester_email": requester_email,
                    "requester_name": requester_name,
                    "user_id": requester_id,
                    "requester_id": requester_id,  # Keep both for compatibility
                    "connection_name": "Emma Thompson",
                    "target_name": "Emma Thompson",
                    "target_email": "emma.thompson@example.com",
                    "target_company": "Thompson Tech",
                    "target_title": "CTO",
                    "message": "Interested in exploring technical collaboration.",
                    "status": "pending",
                    "created_at": datetime.utcnow() - timedelta(days=18),
                    "updated_at": datetime.utcnow() - timedelta(days=18),
                },
                {
                    "id": str(uuid.uuid4()),
                    "_id": str(uuid.uuid4()),
                    "requester_email": requester_email,
                    "requester_name": requester_name,
                    "user_id": requester_id,
                    "requester_id": requester_id,  # Keep both for compatibility
                    "connection_name": "James Anderson",
                    "target_name": "James Anderson",
                    "target_email": "james.anderson@example.com",
                    "target_company": "Anderson Ventures",
                    "target_title": "Managing Partner",
                    "message": "Would like to discuss investment opportunities.",
                    "status": "pending",
                    "created_at": datetime.utcnow() - timedelta(days=19),
                    "updated_at": datetime.utcnow() - timedelta(days=19),
                }
            ]
            
            for request in follow_up_requests:
                await db.warm_intro_requests.insert_one(request)
                print(f"✅ Created follow-up request: {requester_name} → {request['target_name']} ({request['created_at'].strftime('%Y-%m-%d')})")
            
            print("\n🎉 COMPREHENSIVE TEST DATA CREATED SUCCESSFULLY!")
            print("=" * 60)
            print("\n🧪 NOW YOU CAN TEST:")
            print("1. Warm Intro Requests (Regression Test):")
            print("   → Go to: http://localhost:3000/warm-intro-requests")
            print(f"   → Should see: {requester_name} → Bob Wilson")
            print("\n2. Follow-Up Emails (Main Testing):")
            print("   → Go to: http://localhost:3000/admin/follow-ups")
            print("   → Should see 3 requests ready for follow-up")
            print("   → Test both 'Send Email' and 'Test' buttons")
            print("\n✅ All test data uses real user references!")
            
        else:
            print("❌ Need at least 1 user in database to create test data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())