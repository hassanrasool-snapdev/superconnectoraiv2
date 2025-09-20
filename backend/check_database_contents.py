#!/usr/bin/env python3

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo

async def main():
    print("🔍 CHECKING DATABASE CONTENTS...")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database successfully!")
        
        # Check warm intro requests
        print("\n📋 WARM INTRO REQUESTS IN DATABASE:")
        warm_intro_requests = await db.warm_intro_requests.find({}).to_list(length=None)
        print(f"Total warm intro requests: {len(warm_intro_requests)}")
        
        if warm_intro_requests:
            print("\nFirst 5 records:")
            for i, request in enumerate(warm_intro_requests[:5], 1):
                print(f"{i}. ID: {request.get('id', request.get('_id'))}")
                print(f"   User ID: {request.get('user_id', request.get('requester_id'))}")
                print(f"   Requester: {request.get('requester_name')}")
                print(f"   Connection: {request.get('connection_name', request.get('target_name'))}")
                print(f"   Email: {request.get('requester_email')}")
                print(f"   Created: {request.get('created_at')}")
                print(f"   Status: {request.get('status')}")
                print("   ---")
        else:
            print("❌ NO WARM INTRO REQUESTS FOUND!")
        
        # Check follow-up emails
        print("\n📧 FOLLOW-UP EMAILS IN DATABASE:")
        follow_up_emails = await db.follow_up_emails.find({}).to_list(length=None)
        print(f"Total follow-up emails: {len(follow_up_emails)}")
        
        if follow_up_emails:
            print("\nFirst 5 records:")
            for i, email in enumerate(follow_up_emails[:5], 1):
                print(f"{i}. ID: {email.get('id', email.get('_id'))}")
                print(f"   Warm Intro ID: {email.get('warm_intro_request_id')}")
                print(f"   Requester: {email.get('requester_name')}")
                print(f"   Status: {email.get('status')}")
                print(f"   Scheduled: {email.get('scheduled_date')}")
                print("   ---")
        else:
            print("❌ NO FOLLOW-UP EMAILS FOUND!")
        
        # Check users
        print("\n👥 USERS IN DATABASE:")
        users = await db.users.find({}).to_list(length=5)
        print(f"Total users (showing first 5): {len(users)}")
        
        for i, user in enumerate(users, 1):
            print(f"{i}. Email: {user.get('email')}")
            print(f"   ID: {str(user.get('_id'))}")
            print(f"   Name: {user.get('name', 'N/A')}")
            print("   ---")
        
        # Check for eligible follow-up requests (14+ days old)
        print("\n⏰ FOLLOW-UP ELIGIBLE REQUESTS (14+ days old):")
        cutoff_date = datetime.utcnow() - timedelta(days=14)
        eligible_requests = await db.warm_intro_requests.find({
            "created_at": {"$lte": cutoff_date},
            "follow_up_sent_date": None,
            "follow_up_skipped": {"$ne": True}
        }).to_list(length=None)
        
        print(f"Eligible requests: {len(eligible_requests)}")
        
        if eligible_requests:
            for i, request in enumerate(eligible_requests[:5], 1):
                days_old = (datetime.utcnow() - request.get('created_at')).days
                print(f"{i}. {request.get('requester_name')} → {request.get('connection_name', request.get('target_name'))}")
                print(f"   Days old: {days_old}")
                print(f"   User ID: {request.get('user_id', request.get('requester_id'))}")
                print("   ---")
        
        # Test the API query that the frontend uses
        print("\n🔍 TESTING API QUERIES:")
        
        # Test warm intro requests query (what the frontend calls)
        print("\n1. Testing warm intro requests query (frontend API):")
        try:
            # This mimics what the frontend API endpoint does
            cursor = db.warm_intro_requests.find({}).sort("created_at", -1).limit(10)
            api_requests = await cursor.to_list(length=None)
            print(f"   API would return: {len(api_requests)} requests")
            
            for request in api_requests[:3]:
                print(f"   - {request.get('requester_name')} → {request.get('connection_name', request.get('target_name'))}")
        except Exception as e:
            print(f"   ❌ API query failed: {e}")
        
        # Test follow-up candidates query (what the admin page calls)
        print("\n2. Testing follow-up candidates query (admin API):")
        try:
            from app.services.follow_up_email_service import get_eligible_warm_intro_requests
            candidates = await get_eligible_warm_intro_requests(db)
            print(f"   API would return: {len(candidates)} candidates")
            
            for candidate in candidates[:3]:
                print(f"   - {candidate.get('requester_name')} → {candidate.get('connection_name', candidate.get('target_name'))}")
        except Exception as e:
            print(f"   ❌ Candidates query failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🎯 DIAGNOSIS:")
        if not warm_intro_requests:
            print("❌ PROBLEM: No warm intro requests in database!")
            print("   SOLUTION: Need to create test data")
        elif not eligible_requests:
            print("❌ PROBLEM: No follow-up eligible requests (14+ days old)!")
            print("   SOLUTION: Need to create older test data")
        else:
            print("✅ Data exists in database")
            print("❌ PROBLEM: Likely frontend/API issue or authentication")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())