#!/usr/bin/env python3
"""
Script to add one more test warm intro request for testing.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta
from bson import ObjectId

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection

async def add_one_test_record():
    """Add one more test warm intro request for testing."""
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Calculate dates >14 days ago
    now = datetime.now(timezone.utc)
    created_date = now - timedelta(days=17)  # 17 days ago to ensure eligibility
    
    # Create one more test user
    test_user = {
        "_id": ObjectId(),
        "id": "fresh-user-3",
        "email": "maria.gonzalez@example.com",
        "name": "Maria Gonzalez",
        "created_at": created_date
    }
    
    # Insert test user
    await db.users.insert_one(test_user)
    print(f"✅ Created test user: {test_user['email']}")
    
    # Create test warm intro request (>14 days old for follow-up)
    test_request = {
        "_id": ObjectId(),
        "id": "fresh-request-3",
        "user_id": "fresh-user-3",
        "requester_id": "fresh-user-3",
        "requester_name": "Maria Gonzalez",
        "requester_email": "maria.gonzalez@example.com",
        "connection_name": "James Wilson",
        "target_name": "James Wilson",
        "connection_email": "james.wilson@venture.capital",
        "message": "Maria would love to connect with James about venture capital opportunities in the EdTech space.",
        "status": "pending",
        "created_at": created_date,
        "user_responded": False,
        "follow_up_sent": False,
        "follow_up_sent_date": None,
        "follow_up_skipped": False
    }
    
    # Insert test request
    await db.warm_intro_requests.insert_one(test_request)
    print(f"✅ Created warm intro request: {test_request['id']}")
    print(f"   👤 {test_request['requester_name']} → {test_request['connection_name']}")
    print(f"   📅 Created: {test_request['created_at'].strftime('%Y-%m-%d')} ({(now - test_request['created_at']).days} days ago)")
    
    print(f"\n🎯 Additional Test Record Ready!")
    print(f"   📧 Maria Gonzalez → James Wilson (maria.gonzalez@example.com)")
    print(f"   🔗 Visit: http://localhost:3000/admin/follow-ups")
    print(f"   🚀 Ready to test the fixed 'Send Email' button with response links!")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(add_one_test_record())