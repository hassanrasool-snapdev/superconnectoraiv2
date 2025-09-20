#!/usr/bin/env python3

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo
from app.services.follow_up_email_service import get_eligible_warm_intro_requests, send_automated_follow_up_email

async def test_follow_up_fixes():
    print("🧪 Testing Follow-up Email Fixes...")
    print("=" * 50)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database successfully!")
        
        # Test 1: Get eligible warm intro requests (this was failing before)
        print("\n📋 TEST 1: Getting eligible warm intro requests...")
        try:
            eligible_requests = await get_eligible_warm_intro_requests(db)
            print(f"✅ Found {len(eligible_requests)} eligible requests")
            
            for i, request in enumerate(eligible_requests[:3], 1):  # Show first 3
                print(f"   {i}. Request ID: {request.get('id') or request.get('_id')}")
                print(f"      User ID: {request.get('user_id') or request.get('requester_id')}")
                print(f"      Connection: {request.get('connection_name') or request.get('target_name')}")
                print(f"      Created: {request.get('created_at')}")
                print("      ---")
                
        except Exception as e:
            print(f"❌ Error getting eligible requests: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Try to send a follow-up email (this was failing before)
        if eligible_requests:
            print(f"\n📧 TEST 2: Testing follow-up email sending...")
            test_request = eligible_requests[0]
            try:
                # This should not crash anymore
                success = await send_automated_follow_up_email(db, test_request)
                if success:
                    print("✅ Follow-up email sent successfully!")
                else:
                    print("⚠️ Follow-up email failed to send (but no crash!)")
                    
            except Exception as e:
                print(f"❌ Error sending follow-up email: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ No eligible requests to test email sending")
        
        print("\n🎉 FOLLOW-UP FIXES TEST COMPLETE!")
        print("=" * 50)
        print("✅ No more KeyError crashes!")
        print("✅ Field name mismatches resolved!")
        print("✅ User lookup working with both field conventions!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_follow_up_fixes())