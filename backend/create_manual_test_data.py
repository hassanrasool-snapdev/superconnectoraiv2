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

async def create_manual_test_data():
    """Create test data specifically for manual testing - these won't be auto-processed"""
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Create test user if doesn't exist
    test_user_email = "manual.test@example.com"
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
    
    # First, clear any existing manual test requests to start fresh
    await db.warm_intro_requests.delete_many({
        "requester_email": {"$in": ["alex.chen@techstartup.com", "maria.rodriguez@consulting.com"]}
    })
    print("Cleared any existing manual test requests")
    
    # Create two NEW test warm intro requests that are 15+ days old
    # These will be fresh and available for manual testing
    test_requests = [
        {
            "id": str(uuid4()),
            "user_id": user_id,
            "requester_name": "Alex Chen",
            "requester_email": "alex.chen@techstartup.com",
            "connection_name": "Dr. Lisa Wang",
            "connection_company": "Stanford AI Lab",
            "connection_role": "Research Director",
            "introduction_reason": "Alex is building an AI-powered healthcare platform and wants to discuss research collaboration opportunities",
            "context": "Both are working on AI applications in healthcare and could benefit from academic-industry partnership",
            "status": "pending",
            "created_at": datetime.utcnow() - timedelta(days=16),  # 16 days old
            "updated_at": datetime.utcnow() - timedelta(days=16),
            "follow_up_sent": False,
            "follow_up_sent_date": None,
            "follow_up_skipped": False,
            "follow_up_skipped_date": None,
            "follow_up_skipped_by": None
        },
        {
            "id": str(uuid4()),
            "user_id": user_id,
            "requester_name": "Maria Rodriguez",
            "requester_email": "maria.rodriguez@consulting.com",
            "connection_name": "James Thompson",
            "connection_company": "Global Ventures",
            "connection_role": "Managing Partner",
            "introduction_reason": "Maria is seeking Series A funding for her fintech startup and wants to pitch to experienced VCs",
            "context": "James has a track record of investing in fintech companies and could provide valuable insights",
            "status": "pending",
            "created_at": datetime.utcnow() - timedelta(days=20),  # 20 days old
            "updated_at": datetime.utcnow() - timedelta(days=20),
            "follow_up_sent": False,
            "follow_up_sent_date": None,
            "follow_up_skipped": False,
            "follow_up_skipped_date": None,
            "follow_up_skipped_by": None
        }
    ]
    
    # Insert test requests
    for request in test_requests:
        await db.warm_intro_requests.insert_one(request)
        print(f"Created manual test request: {request['requester_name']} -> {request['connection_name']} ({(datetime.utcnow() - request['created_at']).days} days old)")
    
    print("\n" + "="*60)
    print("🎯 MANUAL TEST DATA CREATED SUCCESSFULLY!")
    print("="*60)
    print("You now have 2 fresh requests ready for manual testing:")
    print()
    print("📧 REQUEST 1 - FOR MANUAL SENDING:")
    print("   • Alex Chen → Dr. Lisa Wang")
    print("   • 16 days old")
    print("   • AI healthcare collaboration")
    print()
    print("⏭️  REQUEST 2 - FOR MANUAL SKIPPING:")
    print("   • Maria Rodriguez → James Thompson") 
    print("   • 20 days old")
    print("   • Fintech Series A funding")
    print()
    print("🚀 Next Steps:")
    print("   1. Go to http://localhost:3000/admin/follow-ups")
    print("   2. Login as admin@superconnect.ai / admin123")
    print("   3. You should see 2 requests needing follow-up")
    print("   4. Test 'Preview' and 'Send' on Alex Chen's request")
    print("   5. Test 'Skip' on Maria Rodriguez's request")
    print("="*60)
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_manual_test_data())