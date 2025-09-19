#!/usr/bin/env python3
"""
Test script to verify the follow-up email implementation
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database
from app.services.follow_up_email_service import (
    get_eligible_warm_intro_requests,
    send_automated_follow_up_email,
    record_user_response,
    process_automated_follow_ups
)
from app.services.scheduler_service import get_scheduler_status, trigger_manual_follow_up_processing
from app.models.warm_intro_request import WarmIntroStatus

async def test_follow_up_implementation():
    """Test the follow-up email implementation"""
    print("🧪 Testing Follow-up Email Implementation")
    print("=" * 50)
    
    try:
        # Initialize database connection
        from app.core.db import connect_to_mongo
        await connect_to_mongo()
        
        # Get database connection
        db = get_database()
        print("✅ Database connection established")
        
        # Test 1: Check scheduler status
        print("\n📊 Testing scheduler status...")
        scheduler_status = await get_scheduler_status()
        print(f"   Scheduler running: {scheduler_status['running']}")
        print(f"   Check interval: {scheduler_status['check_interval']} seconds")
        print(f"   Current time: {scheduler_status['current_time']}")
        
        # Test 2: Check for eligible warm intro requests
        print("\n🔍 Checking for eligible warm intro requests...")
        eligible_requests = await get_eligible_warm_intro_requests(db)
        print(f"   Found {len(eligible_requests)} eligible requests")
        
        if eligible_requests:
            print("   Sample eligible request:")
            sample = eligible_requests[0]
            print(f"     ID: {sample['id']}")
            print(f"     Requester: {sample['requester_name']}")
            print(f"     Connection: {sample['connection_name']}")
            print(f"     Created: {sample['created_at']}")
        
        # Test 3: Test user response recording (with a fake request ID)
        print("\n📝 Testing user response recording...")
        test_request_id = str(uuid4())
        
        # First, create a test warm intro request
        test_request = {
            "id": test_request_id,
            "user_id": str(uuid4()),
            "requester_name": "Test User",
            "connection_name": "Test Connection",
            "status": WarmIntroStatus.pending.value,
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow() - timedelta(days=15),
            "follow_up_sent_date": None,
            "user_responded": None,
            "response_date": None
        }
        
        await db.warm_intro_requests.insert_one(test_request)
        print(f"   Created test request: {test_request_id}")
        
        # Test recording a positive response
        success = await record_user_response(db, test_request_id, connected=True)
        print(f"   Response recording success: {success}")
        
        # Verify the response was recorded
        updated_request = await db.warm_intro_requests.find_one({"id": test_request_id})
        if updated_request:
            print(f"   User responded: {updated_request.get('user_responded', False)}")
            print(f"   Status: {updated_request.get('status', 'unknown')}")
            print(f"   Response date: {updated_request.get('response_date', 'None')}")
        
        # Test 4: Test duplicate response prevention
        print("\n🚫 Testing duplicate response prevention...")
        duplicate_success = await record_user_response(db, test_request_id, connected=False)
        print(f"   Duplicate response blocked: {not duplicate_success}")
        
        # Test 5: Test manual processing trigger
        print("\n⚡ Testing manual processing trigger...")
        processing_result = await trigger_manual_follow_up_processing()
        print(f"   Processing success: {processing_result['success']}")
        if processing_result['success']:
            print(f"   Legacy processed: {processing_result['legacy_processed']}")
            print(f"   Automated processed: {processing_result['automated_processed']}")
            print(f"   Total processed: {processing_result['total_processed']}")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        await db.warm_intro_requests.delete_one({"id": test_request_id})
        print("   Test request deleted")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    return True

async def test_api_endpoints():
    """Test the API endpoints (requires running server)"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 30)
    
    try:
        import httpx
        
        base_url = "http://localhost:8000/api/v1"
        
        # Test public health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/public/health")
            print(f"Public health endpoint: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
        
        print("✅ API endpoint tests completed")
        
    except ImportError:
        print("⚠️  httpx not available, skipping API tests")
        print("   Install with: pip install httpx")
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Starting Follow-up Email Implementation Tests")
    print("=" * 60)
    
    # Run the async tests
    success = asyncio.run(test_follow_up_implementation())
    
    if success:
        print("\n🎉 Implementation test completed successfully!")
        print("\nNext steps:")
        print("1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("2. Test the public endpoint: GET /api/v1/public/health")
        print("3. Test user response: POST /api/v1/public/warm-intro-requests/{id}/respond")
        print("4. Monitor scheduler logs for automated processing")
    else:
        print("\n💥 Implementation test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()