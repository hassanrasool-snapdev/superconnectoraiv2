#!/usr/bin/env python3
"""
Create 3 test transactions in the follow-up email queue for testing email capability
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database
from app.models.warm_intro_request import WarmIntroStatus
from app.models.user import UserInDB
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_test_user(db, email: str, name: str) -> str:
    """Create a test user and return their ID"""
    user_id = str(uuid4())
    
    user_data = {
        "id": user_id,
        "email": email,
        "name": name,
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "hashed_password": "dummy_hash_for_testing"
    }
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        logger.info(f"User {email} already exists, using existing user")
        return existing_user["id"]
    
    await db.users.insert_one(user_data)
    logger.info(f"Created test user: {email} with ID: {user_id}")
    return user_id

async def create_test_warm_intro_request(db, user_id: str, requester_name: str, connection_name: str, days_old: int) -> str:
    """Create a test warm intro request that's eligible for follow-up"""
    request_id = str(uuid4())
    created_date = datetime.utcnow() - timedelta(days=days_old)
    
    warm_intro_data = {
        "id": request_id,
        "user_id": user_id,
        "requester_name": requester_name,
        "requester_email": f"{requester_name.lower().replace(' ', '.')}@test.com",
        "connection_name": connection_name,
        "target_name": connection_name,  # For compatibility
        "message": f"I would like to connect with {connection_name} for networking purposes.",
        "status": WarmIntroStatus.pending.value,
        "created_at": created_date,
        "updated_at": created_date,
        "follow_up_sent_date": None,  # No follow-up sent yet
        "follow_up_skipped": False,   # Not skipped
        "priority": "medium"
    }
    
    await db.warm_intro_requests.insert_one(warm_intro_data)
    logger.info(f"Created warm intro request: {request_id} for {requester_name} -> {connection_name} ({days_old} days old)")
    return request_id

async def main():
    """Create 3 test transactions for follow-up email testing"""
    try:
        # Initialize database connection
        from app.core.db import connect_to_mongo
        await connect_to_mongo()
        db = get_database()
        logger.info("Connected to database")
        
        # Test data for 3 different scenarios
        test_scenarios = [
            {
                "email": "alice.johnson@test.com",
                "name": "Alice Johnson",
                "requester_name": "Alice Johnson",
                "connection_name": "Sarah Chen",
                "days_old": 15  # Just over the 14-day threshold
            },
            {
                "email": "bob.smith@test.com", 
                "name": "Bob Smith",
                "requester_name": "Bob Smith",
                "connection_name": "Michael Rodriguez",
                "days_old": 21  # 3 weeks old
            },
            {
                "email": "carol.davis@test.com",
                "name": "Carol Davis", 
                "requester_name": "Carol Davis",
                "connection_name": "Jennifer Kim",
                "days_old": 30  # 1 month old
            }
        ]
        
        created_requests = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            logger.info(f"\n--- Creating Test Transaction {i} ---")
            
            # Create test user
            user_id = await create_test_user(
                db, 
                scenario["email"], 
                scenario["name"]
            )
            
            # Create warm intro request eligible for follow-up
            request_id = await create_test_warm_intro_request(
                db,
                user_id,
                scenario["requester_name"],
                scenario["connection_name"],
                scenario["days_old"]
            )
            
            created_requests.append({
                "request_id": request_id,
                "user_email": scenario["email"],
                "requester_name": scenario["requester_name"],
                "connection_name": scenario["connection_name"],
                "days_old": scenario["days_old"]
            })
        
        logger.info(f"\n=== Successfully Created {len(created_requests)} Test Transactions ===")
        for i, request in enumerate(created_requests, 1):
            logger.info(f"Transaction {i}:")
            logger.info(f"  Request ID: {request['request_id']}")
            logger.info(f"  User Email: {request['user_email']}")
            logger.info(f"  Requester: {request['requester_name']}")
            logger.info(f"  Connection: {request['connection_name']}")
            logger.info(f"  Days Old: {request['days_old']}")
        
        logger.info("\nThese requests are now eligible for follow-up emails!")
        logger.info("You can test the email capability by:")
        logger.info("1. Going to the admin follow-ups page")
        logger.info("2. Viewing the candidates list")
        logger.info("3. Sending follow-up emails for these test transactions")
        
        return created_requests
        
    except Exception as e:
        logger.error(f"Error creating test transactions: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())