#!/usr/bin/env python3
"""
Script to create 2 fresh test warm intro requests for testing the updated Send Email functionality.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta
from bson import ObjectId

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection

async def create_fresh_test_records():
    """Create 2 fresh test warm intro requests for testing."""
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    print("🧹 Cleaning up old test records...")
    
    # Remove old test records
    old_test_ids = ["test-request-123", "followup-yes-test", "followup-no-test"]
    old_user_ids = ["test-user-123", "followup-user-1", "followup-user-2"]
    
    for test_id in old_test_ids:
        await db.warm_intro_requests.delete_many({"id": test_id})
        
    for user_id in old_user_ids:
        await db.users.delete_many({"id": user_id})
    
    print("✅ Old test records cleaned up")
    
    # Calculate dates >14 days ago
    now = datetime.now(timezone.utc)
    created_date = now - timedelta(days=18)  # 18 days ago to ensure eligibility
    
    # Create fresh test users
    test_users = [
        {
            "_id": ObjectId(),
            "id": "fresh-user-1",
            "email": "sarah.martinez@example.com",
            "name": "Sarah Martinez",
            "created_at": created_date
        },
        {
            "_id": ObjectId(),
            "id": "fresh-user-2", 
            "email": "david.chen@example.com",
            "name": "David Chen",
            "created_at": created_date
        }
    ]
    
    # Insert fresh test users
    for user in test_users:
        # Remove existing user first
        await db.users.delete_many({"id": user["id"]})
        # Insert new user
        await db.users.insert_one(user)
        print(f"✅ Created fresh test user: {user['email']}")
    
    # Create fresh test warm intro requests (>14 days old for follow-up)
    test_requests = [
        {
            "_id": ObjectId(),
            "id": "fresh-request-1",
            "user_id": "fresh-user-1",
            "requester_id": "fresh-user-1",
            "requester_name": "Sarah Martinez",
            "requester_email": "sarah.martinez@example.com",
            "connection_name": "Emily Rodriguez",
            "target_name": "Emily Rodriguez",
            "connection_email": "emily.rodriguez@techstartup.com",
            "message": "I'd love to connect Sarah with Emily to discuss potential partnerships in the fintech space.",
            "status": "pending",
            "created_at": created_date,
            "user_responded": False,
            "follow_up_sent": False,
            "follow_up_sent_date": None,
            "follow_up_skipped": False
        },
        {
            "_id": ObjectId(),
            "id": "fresh-request-2",
            "user_id": "fresh-user-2",
            "requester_id": "fresh-user-2", 
            "requester_name": "David Chen",
            "requester_email": "david.chen@example.com",
            "connection_name": "Alex Thompson",
            "target_name": "Alex Thompson",
            "connection_email": "alex.thompson@innovate.io",
            "message": "David would benefit from connecting with Alex about AI/ML opportunities in healthcare.",
            "status": "pending",
            "created_at": created_date,
            "user_responded": False,
            "follow_up_sent": False,
            "follow_up_sent_date": None,
            "follow_up_skipped": False
        }
    ]
    
    # Insert fresh test requests
    for request in test_requests:
        # Remove existing request first
        await db.warm_intro_requests.delete_many({"id": request["id"]})
        # Insert new request
        await db.warm_intro_requests.insert_one(request)
        print(f"✅ Created fresh warm intro request: {request['id']}")
        print(f"   👤 {request['requester_name']} → {request['connection_name']}")
        print(f"   📅 Created: {request['created_at'].strftime('%Y-%m-%d')} ({(now - request['created_at']).days} days ago)")
    
    print(f"\n🎯 Fresh Test Records Ready!")
    print(f"   📊 Created 2 fresh test users")
    print(f"   📊 Created 2 fresh warm intro requests ({(now - created_date).days} days old)")
    print(f"   ✅ Both requests are eligible for follow-up (>14 days)")
    print(f"   🔗 Visit: http://localhost:3000/admin/follow-ups")
    print(f"\n📧 Test Records:")
    print(f"   1. Sarah Martinez → Emily Rodriguez (sarah.martinez@example.com)")
    print(f"   2. David Chen → Alex Thompson (david.chen@example.com)")
    print(f"\n🚀 Ready to test the updated 'Send Email' button!")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_fresh_test_records())