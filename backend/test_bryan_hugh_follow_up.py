import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.follow_up_email_service import (
    get_eligible_warm_intro_requests,
    prepare_manual_follow_up_email,
    generate_automated_follow_up_content
)

async def test_bryan_hugh_follow_up():
    """Test the follow-up email functionality with Bryan Haas -> Hugh Molotsi record"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(
        settings.DATABASE_URL,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    db = client[settings.DATABASE_NAME]
    
    try:
        print("🧪 Testing Follow-up Email Functionality")
        print("=" * 50)
        
        # Step 1: Check if our test record was created
        print("\n📋 Step 1: Looking for Bryan Haas -> Hugh Molotsi record...")
        bryan_record = await db.warm_intro_requests.find_one({
            "requester_name": "Bryan Haas",
            "connection_name": "Hugh Molotsi"
        })
        
        if bryan_record:
            print(f"✅ Found record: {bryan_record['id']}")
            print(f"   Created: {bryan_record['created_at']}")
            print(f"   Status: {bryan_record['status']}")
            print(f"   Follow-up sent: {bryan_record.get('follow_up_sent_date', 'None')}")
        else:
            print("❌ Bryan Haas -> Hugh Molotsi record not found")
            print("   Creating test record now...")
            
            # Create the test record
            fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
            test_record = {
                "id": "bryan-hugh-test-" + str(int(datetime.utcnow().timestamp())),
                "user_id": "bryan_user_id",
                "requester_name": "Bryan Haas",
                "connection_name": "Hugh Molotsi",
                "requester_first_name": "Bryan",
                "requester_last_name": "Haas",
                "connection_first_name": "Hugh",
                "connection_last_name": "Molotsi",
                "status": "connected",
                "outcome": "Successfully connected via warm introduction",
                "outcome_date": fifteen_days_ago,
                "created_at": fifteen_days_ago,
                "updated_at": fifteen_days_ago,
                "connected_date": fifteen_days_ago,
                "declined_date": None,
                "follow_up_sent_date": None,
                "follow_up_skipped": None,
                "follow_up_skipped_date": None,
                "follow_up_skipped_by": None
            }
            
            await db.warm_intro_requests.insert_one(test_record)
            bryan_record = test_record
            print(f"✅ Created test record: {bryan_record['id']}")
        
        # Step 2: Check if it's eligible for follow-up
        print("\n📧 Step 2: Checking eligibility for follow-up...")
        eligible_requests = await get_eligible_warm_intro_requests(db)
        
        bryan_eligible = None
        for request in eligible_requests:
            if (request.get('requester_name') == 'Bryan Haas' and 
                request.get('connection_name') == 'Hugh Molotsi'):
                bryan_eligible = request
                break
        
        if bryan_eligible:
            print(f"✅ Bryan's request is eligible for follow-up!")
            print(f"   Days since created: {(datetime.utcnow() - bryan_eligible['created_at']).days}")
        else:
            print("❌ Bryan's request is not eligible for follow-up")
            print(f"   Total eligible requests: {len(eligible_requests)}")
            return
        
        # Step 3: Generate follow-up email content
        print("\n✉️  Step 3: Generating follow-up email content...")
        email_content = generate_automated_follow_up_content(
            requester_name="Bryan Haas",
            connection_name="Hugh Molotsi", 
            request_id=bryan_record['id']
        )
        
        print("✅ Generated email content:")
        print("-" * 40)
        print(email_content)
        print("-" * 40)
        
        # Step 4: Test the manual follow-up preparation
        print("\n🔧 Step 4: Testing manual follow-up preparation...")
        result = await prepare_manual_follow_up_email(db, bryan_eligible)
        
        if result.get('success'):
            print("✅ Manual follow-up preparation successful!")
            print(f"   Subject: {result.get('subject', 'N/A')}")
            print(f"   To: {result.get('to_email', 'N/A')}")
        else:
            print(f"❌ Manual follow-up preparation failed: {result.get('error', 'Unknown error')}")
        
        print("\n🎉 Follow-up email functionality test completed!")
        print("\n📋 Summary:")
        print(f"   • Test record exists: ✅")
        print(f"   • Eligible for follow-up: ✅")
        print(f"   • Email content generated: ✅")
        print(f"   • Manual preparation: {'✅' if result.get('success') else '❌'}")
        
        print(f"\n🌐 You can now test the follow-up functionality in the admin panel:")
        print(f"   http://localhost:3000/admin/follow-ups")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_bryan_hugh_follow_up())