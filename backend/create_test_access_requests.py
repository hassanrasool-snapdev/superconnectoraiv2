import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo
from app.models.access_request import AccessRequestCreate, AccessRequestInDB, AccessRequestStatus
from datetime import datetime

async def create_test_access_requests():
    """Create some test access requests for testing email functionality"""
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Test access requests
    test_requests = [
        {
            "email": "test1@example.com",
            "full_name": "John Doe",
            "reason": "I would like to test the email notification system",
            "organization": "Test Company"
        },
        {
            "email": "test2@example.com", 
            "full_name": "Jane Smith",
            "reason": "Testing the denial email functionality",
            "organization": "Demo Corp"
        }
    ]
    
    print("Creating test access requests...")
    
    for req_data in test_requests:
        # Check if request already exists
        existing = await db.access_requests.find_one({"email": req_data["email"]})
        if existing:
            print(f"Access request for {req_data['email']} already exists, skipping...")
            continue
            
        # Create new access request
        access_request = AccessRequestInDB(
            email=req_data["email"],
            full_name=req_data["full_name"],
            reason=req_data["reason"],
            organization=req_data["organization"],
            status=AccessRequestStatus.pending,
            created_at=datetime.utcnow()
        )
        
        request_dict = access_request.model_dump()
        request_dict["id"] = str(request_dict["id"])
        
        await db.access_requests.insert_one(request_dict)
        print(f"Created access request for {req_data['full_name']} ({req_data['email']})")
    
    print("Test access requests created successfully!")

if __name__ == "__main__":
    asyncio.run(create_test_access_requests())