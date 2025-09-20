#!/usr/bin/env python3
"""
Script to create test warm intro requests that are >14 days old for follow-up testing.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta
from bson import ObjectId

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection

async def create_followup_test_data():
    """Create test warm intro requests that are >14 days old for follow-up testing."""
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Calculate dates >14 days ago
    now = datetime.now(timezone.utc)
    created_date = now - timedelta(days=16)  # 16 days ago
    
    # Create test users
    test_users = [
        {
            "_id": ObjectId(),
            "id": "followup-user-1",
            "email": "alice.johnson@example.com",
            "name": "Alice Johnson",
            "created_at": created_date
        },
        {
            "_id": ObjectId(),
            "id": "followup-user-2", 
            "email": "bob.smith@example.com",
            "name": "Bob Smith",
            "created_at": created_date
        }
    ]
    
    # Insert test users
    for user in test_users:
        await db.users.replace_one(
            {"id": user["id"]}, 
            user, 
            upsert=True
        )
        print(f"✅ Created test user: {user['email']}")
    
    # Create test warm intro requests (>14 days old for follow-up)
    test_requests = [
        {
            "_id": ObjectId(),
            "id": "followup-yes-test",
            "user_id": "followup-user-1",
            "requester_id": "followup-user-1",
            "requester_name": "Alice Johnson",
            "requester_email": "alice.johnson@example.com",
            "connection_name": "Sarah Wilson",
            "target_name": "Sarah Wilson",
            "connection_email": "sarah.wilson@techcorp.com",
            "message": "I'd love to connect Alice with Sarah to discuss potential collaboration on AI projects.",
            "status": "pending",
            "created_at": created_date,
            "user_responded": False,
            "follow_up_sent": False,
            "follow_up_sent_date": None
        },
        {
            "_id": ObjectId(),
            "id": "followup-no-test",
            "user_id": "followup-user-2",
            "requester_id": "followup-user-2", 
            "requester_name": "Bob Smith",
            "requester_email": "bob.smith@example.com",
            "connection_name": "Michael Chen",
            "target_name": "Michael Chen",
            "connection_email": "michael.chen@startup.io",
            "message": "Bob would benefit from connecting with Michael about startup funding opportunities.",
            "status": "pending",
            "created_at": created_date,
            "user_responded": False,
            "follow_up_sent": False,
            "follow_up_sent_date": None
        }
    ]
    
    # Insert test requests
    for request in test_requests:
        await db.warm_intro_requests.replace_one(
            {"id": request["id"]}, 
            request, 
            upsert=True
        )
        print(f"✅ Created test warm intro request: {request['id']}")
        print(f"   📅 Created: {request['created_at'].strftime('%Y-%m-%d')} ({(now - request['created_at']).days} days ago)")
    
    print(f"\n📧 Follow-up emails will now ask users to reply directly to the email")
    print(f"   The warm-intro-response pages have been removed from the system")
    
    print(f"\n📊 Summary:")
    print(f"   - Created 2 test users for follow-up testing")
    print(f"   - Created 2 warm intro requests (16 days old)")
    print(f"   - Both requests are eligible for follow-up (>14 days)")
    print(f"   - Use 'followup-yes-test' to test the 'Yes, We Connected' template")
    print(f"   - Use 'followup-no-test' to test the 'No, Not Yet' template")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_followup_test_data())