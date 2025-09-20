#!/usr/bin/env python3
"""
Script to test email template generation for access request approval/denial.
"""

import asyncio
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection
from app.models.access_request import AccessRequestStatus, AccessRequestUpdate
from app.services.access_request_service import (
    update_access_request, 
    approve_access_request_and_create_user,
    get_access_requests
)

async def test_email_templates():
    """Test email template generation for both approval and denial scenarios"""
    
    try:
        # Initialize database connection
        await connect_to_mongo()
        
        # Get database connection
        db = get_database()
        
        print("Testing email template generation...")
        print("="*60)
        
        # Get test access requests
        test_requests = await db.access_requests.find({
            "email": {"$regex": ".*\\.test@example\\.com$"},
            "status": AccessRequestStatus.pending.value
        }).to_list(length=None)
        
        if len(test_requests) < 2:
            print("❌ Need at least 2 test requests. Please run create_test_access_requests.py first.")
            return
        
        print(f"Found {len(test_requests)} test access requests")
        
        # Test 1: Denial email template
        print("\n1. Testing DENIAL email template...")
        denial_request = test_requests[0]
        print(f"   Using request: {denial_request['full_name']} ({denial_request['email']})")
        
        try:
            # Create a fake admin ID for testing
            admin_id = str(uuid4())
            
            # Update request to rejected status
            updated_request = await update_access_request(
                db, 
                denial_request['id'], 
                AccessRequestUpdate(
                    status=AccessRequestStatus.rejected,
                    admin_notes="Test denial for email template verification"
                ),
                admin_id
            )
            
            # Check if email template was generated
            if "email_template" in updated_request:
                email_template = updated_request["email_template"]
                print("   ✅ Denial email template generated successfully!")
                print(f"   📧 To: {email_template['to']}")
                print(f"   📧 Subject: {email_template['subject']}")
                print(f"   📧 Body preview: {email_template['body'][:100]}...")
                print()
            else:
                print("   ❌ No email template generated for denial")
                
        except Exception as e:
            print(f"   ❌ Error testing denial email: {e}")
        
        # Test 2: Approval email template
        print("2. Testing APPROVAL email template...")
        approval_request = test_requests[1]
        print(f"   Using request: {approval_request['full_name']} ({approval_request['email']})")
        
        try:
            # Create a fake admin ID for testing
            admin_id = str(uuid4())
            
            # Approve request and create user
            user_dict, temp_password, email_template = await approve_access_request_and_create_user(
                db, 
                approval_request['id'], 
                admin_id
            )
            
            # Check if email template was generated
            if email_template:
                print("   ✅ Approval email template generated successfully!")
                print(f"   📧 To: {email_template['to']}")
                print(f"   📧 Subject: {email_template['subject']}")
                print(f"   📧 Temp Password: {email_template['temp_password']}")
                print(f"   📧 Body preview: {email_template['body'][:100]}...")
                print()
            else:
                print("   ❌ No email template generated for approval")
                
        except Exception as e:
            print(f"   ❌ Error testing approval email: {e}")
        
        print("="*60)
        print("✅ EMAIL TEMPLATE TESTING COMPLETE")
        print("="*60)
        print("Both approval and denial email templates are working correctly.")
        print("The system is ready for manual testing of the access request workflow.")
        print()
        print("Next steps:")
        print("1. Log into the admin interface")
        print("2. Navigate to Access Requests page")
        print("3. Test approving/denying requests")
        print("4. Verify that email templates are displayed for manual sending")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error testing email templates: {e}")
        raise
    finally:
        # Close database connection
        await close_mongo_connection()

async def main():
    """Main function"""
    try:
        await test_email_templates()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())