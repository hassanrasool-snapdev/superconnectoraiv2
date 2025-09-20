#!/usr/bin/env python3
"""
Script to create test access request records for testing approval/denial workflow.
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

async def create_test_access_requests():
    """Create test access request records for approval/denial testing"""
    
    try:
        # Initialize database connection
        await connect_to_mongo()
        
        # Get database connection
        db = get_database()
        
        # Test data for access requests
        test_requests = [
            {
                "full_name": "John Smith",
                "email": "john.smith.test@example.com",
                "organization": "Tech Innovations Inc",
                "reason": "I would like to expand my professional network in the tech industry and connect with other senior engineers and CTOs for potential collaboration opportunities. I'm a Senior Software Engineer looking for collaboration opportunities."
            },
            {
                "full_name": "Sarah Johnson",
                "email": "sarah.johnson.test@example.com",
                "organization": "Marketing Solutions LLC",
                "reason": "Looking to connect with marketing professionals and business leaders to share insights and explore partnership opportunities in digital marketing. I work as a Marketing Director and want to expand my network."
            },
            {
                "full_name": "Michael Chen",
                "email": "michael.chen.test@example.com",
                "organization": "StartupXYZ",
                "reason": "As a startup founder, I'm seeking to connect with investors, mentors, and other entrepreneurs to grow my network and find potential advisors for my company. I'm the Founder & CEO of StartupXYZ."
            },
            {
                "full_name": "Emily Davis",
                "email": "emily.davis.test@example.com",
                "organization": "Global Consulting Group",
                "reason": "I want to connect with industry experts and thought leaders to stay updated on market trends and expand my consulting practice. I'm a Senior Consultant looking to grow my professional network."
            }
        ]
        
        print("Creating test access requests...")
        
        # Clear existing test requests first
        await db.access_requests.delete_many({
            "email": {"$regex": ".*\\.test@example\\.com$"}
        })
        print("Cleared existing test access requests")
        
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
            
            print(f"✓ Created access request {i+1}: {request_data['full_name']} ({request_data['email']})")
        
        print(f"\n✅ Successfully created {len(created_requests)} test access requests")
        print("\nTest requests created:")
        for req in created_requests:
            print(f"  - ID: {req['id']}")
            print(f"    Name: {req['full_name']}")
            print(f"    Email: {req['email']}")
            print(f"    Organization: {req['organization']}")
            print(f"    Status: {req['status']}")
            print()
        
        # Verify the requests were created
        count = await db.access_requests.count_documents({
            "status": AccessRequestStatus.pending.value,
            "email": {"$regex": ".*\\.test@example\\.com$"}
        })
        
        print(f"✅ Verification: {count} pending test access requests found in database")
        
        print("\n" + "="*60)
        print("TEST ACCESS REQUESTS READY FOR TESTING")
        print("="*60)
        print("You can now test the approval/denial process by:")
        print("1. Logging into the admin interface")
        print("2. Navigating to the access requests page")
        print("3. Approving or denying the test requests")
        print("4. Checking that email templates are generated correctly")
        print("="*60)
        
        return created_requests
        
    except Exception as e:
        print(f"❌ Error creating test access requests: {e}")
        raise
    finally:
        # Close database connection
        await close_mongo_connection()

async def main():
    """Main function"""
    try:
        await create_test_access_requests()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())