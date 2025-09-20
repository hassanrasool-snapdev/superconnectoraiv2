#!/usr/bin/env python3
"""
Script to test the approval endpoint directly to debug the issue.
"""

import asyncio
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection
from app.services.access_request_service import approve_access_request_and_create_user

async def test_approval_endpoint():
    """Test the approval endpoint directly"""
    
    try:
        # Initialize database connection
        await connect_to_mongo()
        
        # Get database connection
        db = get_database()
        
        print("Testing approval endpoint...")
        print("="*60)
        
        # Get a test access request
        test_request = await db.access_requests.find_one({
            "email": {"$regex": ".*\\.test@example\\.com$"},
            "status": "pending"
        })
        
        if not test_request:
            print("❌ No pending test requests found. Please run create_test_access_requests.py first.")
            return
        
        print(f"Found test request: {test_request['full_name']} ({test_request['email']})")
        print(f"Request ID: {test_request['id']}")
        
        # Create a fake admin ID for testing
        admin_id = str(uuid4())
        
        try:
            # Test the approval function directly
            print("\nTesting approve_access_request_and_create_user function...")
            user_dict, temp_password, email_template = await approve_access_request_and_create_user(
                db, test_request['id'], admin_id
            )
            
            print("✅ Approval function succeeded!")
            print(f"User created: {user_dict['email']}")
            print(f"Temp password: {temp_password}")
            print(f"Email template generated: {'Yes' if email_template else 'No'}")
            
            if email_template:
                print(f"Email to: {email_template['to']}")
                print(f"Email subject: {email_template['subject']}")
                print(f"Email body preview: {email_template['body'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error in approval function: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close database connection
        await close_mongo_connection()

async def main():
    """Main function"""
    try:
        await test_approval_endpoint()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())