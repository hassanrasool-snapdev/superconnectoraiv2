#!/usr/bin/env python3
"""
Script to load exactly 5 test records into the Access Request queue.
"""

import asyncio
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection
from app.models.access_request import AccessRequestCreate, AccessRequestInDB, AccessRequestStatus

async def load_5_test_access_requests():
    """Load exactly 5 test access request records"""
    
    try:
        # Initialize database connection
        await connect_to_mongo()
        
        # Get database connection
        db = get_database()
        
        # 5 test access requests with diverse profiles
        test_requests = [
            {
                "full_name": "Alex Rodriguez",
                "email": "alex.rodriguez.test@example.com",
                "organization": "TechStart Ventures",
                "reason": "As a venture capitalist, I'm looking to connect with innovative entrepreneurs and startup founders to identify promising investment opportunities and provide mentorship."
            },
            {
                "full_name": "Maria Thompson",
                "email": "maria.thompson.test@example.com",
                "organization": "Global Health Solutions",
                "reason": "I'm a healthcare executive seeking to network with other industry leaders, researchers, and policy makers to advance healthcare innovation and improve patient outcomes."
            },
            {
                "full_name": "David Kim",
                "email": "david.kim.test@example.com",
                "organization": "AI Research Institute",
                "reason": "As an AI researcher, I want to connect with fellow scientists, engineers, and industry professionals to collaborate on cutting-edge machine learning projects and share research insights."
            },
            {
                "full_name": "Jennifer Walsh",
                "email": "jennifer.walsh.test@example.com",
                "organization": "Sustainable Energy Corp",
                "reason": "I'm working in renewable energy and looking to connect with environmental advocates, clean tech entrepreneurs, and sustainability experts to drive the green energy transition."
            },
            {
                "full_name": "Robert Chen",
                "email": "robert.chen.test@example.com",
                "organization": "Financial Analytics Group",
                "reason": "As a financial analyst, I'm seeking connections with investment professionals, fintech innovators, and economic researchers to stay ahead of market trends and opportunities."
            }
        ]
        
        print("Loading 5 test access requests into the queue...")
        
        # Clear any existing test requests with these emails first
        test_emails = [req["email"] for req in test_requests]
        deleted_count = await db.access_requests.delete_many({
            "email": {"$in": test_emails}
        })
        if deleted_count.deleted_count > 0:
            print(f"Cleared {deleted_count.deleted_count} existing test requests with matching emails")
        
        created_requests = []
        
        for i, request_data in enumerate(test_requests):
            # Create access request object
            access_request = AccessRequestInDB(
                full_name=request_data["full_name"],
                email=request_data["email"],
                organization=request_data["organization"],
                reason=request_data["reason"],
                status=AccessRequestStatus.pending
            )
            
            # Convert to dict for MongoDB
            request_dict = access_request.model_dump()
            request_dict["id"] = str(request_dict["id"])
            
            # Insert into database
            await db.access_requests.insert_one(request_dict)
            created_requests.append(request_dict)
            
            print(f"✓ Loaded request {i+1}/5: {request_data['full_name']} ({request_data['email']})")
        
        print(f"\n✅ Successfully loaded {len(created_requests)} test access requests into the queue")
        
        # Display summary
        print("\n" + "="*70)
        print("ACCESS REQUEST QUEUE - 5 TEST RECORDS LOADED")
        print("="*70)
        for i, req in enumerate(created_requests, 1):
            print(f"{i}. {req['full_name']}")
            print(f"   Email: {req['email']}")
            print(f"   Organization: {req['organization']}")
            print(f"   Status: {req['status']}")
            print(f"   ID: {req['id']}")
            print()
        
        # Verify the requests were created
        total_pending = await db.access_requests.count_documents({
            "status": AccessRequestStatus.pending.value
        })
        
        test_pending = await db.access_requests.count_documents({
            "status": AccessRequestStatus.pending.value,
            "email": {"$in": test_emails}
        })
        
        print(f"✅ Verification: {test_pending}/5 test requests are pending")
        print(f"📊 Total pending access requests in queue: {total_pending}")
        print("="*70)
        
        return created_requests
        
    except Exception as e:
        print(f"❌ Error loading test access requests: {e}")
        raise
    finally:
        # Close database connection
        await close_mongo_connection()

async def main():
    """Main function"""
    try:
        await load_5_test_access_requests()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())