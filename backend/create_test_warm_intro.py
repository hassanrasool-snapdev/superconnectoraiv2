#!/usr/bin/env python3
"""
Script to create a test warm intro request for testing the manual email workflow.
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from bson import ObjectId

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection

async def create_test_data():
    """Create test warm intro request and user data."""
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Create a test user
    test_user = {
        "_id": ObjectId(),
        "id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "created_at": datetime.now(timezone.utc)
    }
    
    # Insert or update the test user
    await db.users.replace_one(
        {"id": test_user["id"]}, 
        test_user, 
        upsert=True
    )
    
    # Create a test warm intro request
    test_request = {
        "_id": ObjectId(),
        "id": "test-request-123",
        "user_id": test_user["id"],
        "requester_id": test_user["id"],
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "connection_name": "Jane Smith",
        "target_name": "Jane Smith",
        "connection_email": "jane@example.com",
        "message": "I'd like to connect with Jane about potential collaboration opportunities.",
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
        "user_responded": False,
        "follow_up_sent": True,
        "follow_up_sent_date": datetime.now(timezone.utc)
    }
    
    # Insert or update the test request
    await db.warm_intro_requests.replace_one(
        {"id": test_request["id"]}, 
        test_request, 
        upsert=True
    )
    
    print(f"✅ Created test user: {test_user['email']}")
    print(f"✅ Created test warm intro request: {test_request['id']}")
    print(f"📧 Follow-up emails will ask users to reply directly to the email")
    print(f"   The warm-intro-response pages have been removed from the system")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_test_data())