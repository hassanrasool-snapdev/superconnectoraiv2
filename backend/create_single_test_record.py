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

async def create_single_test_record():
    """Create one fresh test record for email client testing"""
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Get existing test user
    test_user_email = "manual.test@example.com"
    user = await db.users.find_one({"email": test_user_email})
    
    if not user:
        print("Test user not found. Please run create_manual_test_data.py first.")
        return
    
    user_id = user["id"]
    
    # Create one fresh test request
    test_request = {
        "id": str(uuid4()),
        "user_id": user_id,
        "requester_name": "David Kim",
        "requester_email": "david.kim@techcorp.com",
        "connection_name": "Jennifer Martinez",
        "connection_company": "Innovation Labs",
        "connection_role": "Head of Product",
        "introduction_reason": "David is launching a new SaaS product and wants to learn about product-market fit strategies",
        "context": "Jennifer has successfully launched multiple B2B SaaS products and could provide valuable insights",
        "status": "pending",
        "created_at": datetime.utcnow() - timedelta(days=17),  # 17 days old
        "updated_at": datetime.utcnow() - timedelta(days=17),
        "follow_up_sent": False,
        "follow_up_sent_date": None,
        "follow_up_skipped": False,
        "follow_up_skipped_date": None,
        "follow_up_skipped_by": None
    }
    
    # Insert the test request
    await db.warm_intro_requests.insert_one(test_request)
    
    print("="*60)
    print("🎯 NEW TEST RECORD CREATED!")
    print("="*60)
    print("📧 FRESH REQUEST FOR EMAIL CLIENT TESTING:")
    print("   • David Kim → Jennifer Martinez")
    print("   • 17 days old")
    print("   • SaaS product launch consultation")
    print()
    print("🚀 Now you have:")
    print("   1. Maria Rodriguez → James Thompson (for Skip testing)")
    print("   2. David Kim → Jennifer Martinez (for Send Email testing)")
    print()
    print("💡 Test the 'Send Email' button on David Kim's request!")
    print("="*60)
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_single_test_record())