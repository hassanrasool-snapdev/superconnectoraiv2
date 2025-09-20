import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection
from app.models.user import UserInDB, UserRole
from app.core import security

async def create_test_data():
    """Create test data for follow-up email testing"""
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Create test user if doesn't exist
    test_user_email = "testuser@example.com"
    existing_user = await db.users.find_one({"email": test_user_email})
    
    if not existing_user:
        # Create test user
        hashed_password = security.get_password_hash("testpass123")
        test_user = {
            "id": str(uuid4()),
            "email": test_user_email,
            "hashed_password": hashed_password,
            "role": UserRole.user.value,
            "status": "active",
            "is_premium": False,
            "invitation_id": None,
            "must_change_password": False,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        await db.users.insert_one(test_user)
        print(f"Created test user: {test_user_email}")
        user_id = test_user["id"]
    else:
        user_id = existing_user["id"]
        print(f"Using existing test user: {test_user_email}")
    
    # Create two test warm intro requests that are 15+ days old
    test_requests = [
        {
            "id": str(uuid4()),
            "user_id": user_id,
            "requester_name": "John Smith",
            "requester_email": "john.smith@example.com",
            "connection_name": "Sarah Johnson",
            "connection_company": "TechCorp Inc",
            "connection_role": "VP of Engineering",
            "introduction_reason": "John is looking to discuss potential collaboration opportunities in AI/ML space",
            "context": "Both work in similar tech domains and could benefit from knowledge sharing",
            "status": "pending",
            "created_at": datetime.utcnow() - timedelta(days=15),  # 15 days old
            "updated_at": datetime.utcnow() - timedelta(days=15),
            "follow_up_sent": False,
            "follow_up_sent_date": None,
            "follow_up_skipped": False,
            "follow_up_skipped_date": None,
            "follow_up_skipped_by": None
        },
        {
            "id": str(uuid4()),
            "user_id": user_id,
            "requester_name": "Emily Davis",
            "requester_email": "emily.davis@startup.com",
            "connection_name": "Michael Chen",
            "connection_company": "InnovateLabs",
            "connection_role": "CTO",
            "introduction_reason": "Emily wants to learn about scaling engineering teams from 10 to 100+ people",
            "context": "Michael has successfully scaled multiple engineering organizations",
            "status": "pending",
            "created_at": datetime.utcnow() - timedelta(days=18),  # 18 days old
            "updated_at": datetime.utcnow() - timedelta(days=18),
            "follow_up_sent": False,
            "follow_up_sent_date": None,
            "follow_up_skipped": False,
            "follow_up_skipped_date": None,
            "follow_up_skipped_by": None
        }
    ]
    
    # Insert test requests
    for request in test_requests:
        # Check if request already exists
        existing = await db.warm_intro_requests.find_one({"id": request["id"]})
        if not existing:
            await db.warm_intro_requests.insert_one(request)
            print(f"Created test request: {request['requester_name']} -> {request['connection_name']}")
        else:
            print(f"Test request already exists: {request['requester_name']} -> {request['connection_name']}")
    
    print("\nTest data creation complete!")
    print("You should now see 2 requests in the Follow-Up Email Management dashboard.")
    print("- Request 1: John Smith -> Sarah Johnson (15 days old)")
    print("- Request 2: Emily Davis -> Michael Chen (18 days old)")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_test_data())