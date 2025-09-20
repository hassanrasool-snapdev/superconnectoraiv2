#!/usr/bin/env python3

import asyncio
import sys
import os
from datetime import datetime, timedelta
import uuid

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.db import get_database
from app.models.warm_intro_request import WarmIntroStatus

async def create_test_warm_intro_request():
    """Create a test warm intro request for testing email functionality"""
    try:
        # Get database connection
        db = get_database()
        
        # Create a test warm intro request
        test_request = {
            "id": str(uuid.uuid4()),
            "user_id": "ha_user_id",  # Ha's user ID
            "requester_name": "Test User",
            "connection_name": "Jane Smith",
            "status": WarmIntroStatus.pending.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "follow_up_sent_date": None,
            "follow_up_skipped": False
        }
        
        # Insert the request
        result = await db.warm_intro_requests.insert_one(test_request)
        
        if result.inserted_id:
            print("✅ SUCCESS: Test warm intro request created!")
            print(f"📧 Request: {test_request['requester_name']} → {test_request['connection_name']}")
            print(f"🆔 ID: {test_request['id']}")
            print(f"📅 Created: {test_request['created_at']}")
            print("\n🧪 Now you can test the warm intro request functionality!")
            print("   Go to: http://localhost:3000/warm-intro-requests")
            return True
        else:
            print("❌ Failed to create test request")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test request: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(create_test_warm_intro_request())