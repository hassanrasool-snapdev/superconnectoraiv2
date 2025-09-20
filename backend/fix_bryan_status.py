import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def fix_bryan_status():
    """Update Bryan's record to have pending status so it's eligible for follow-up"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(
        settings.DATABASE_URL,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    db = client[settings.DATABASE_NAME]
    
    try:
        print("🔧 Updating Bryan's record status to 'pending' for follow-up eligibility...")
        
        # Update the record status to pending
        result = await db.warm_intro_requests.update_one(
            {
                "requester_name": "Bryan Haas",
                "connection_name": "Hugh Molotsi"
            },
            {
                "$set": {
                    "status": "pending"  # This is what makes it eligible for follow-up
                }
            }
        )
        
        if result.matched_count > 0:
            print(f"✅ Successfully updated record status to 'pending'!")
            
            # Verify the update
            updated_record = await db.warm_intro_requests.find_one({
                "requester_name": "Bryan Haas",
                "connection_name": "Hugh Molotsi"
            })
            
            if updated_record:
                print(f"\n📋 Verification:")
                print(f"   ID: {updated_record['id']}")
                print(f"   Status: {updated_record['status']}")
                print(f"   Created: {updated_record['created_at']}")
                print(f"   Follow-up sent: {updated_record.get('follow_up_sent_date', 'None')}")
                print(f"   Follow-up skipped: {updated_record.get('follow_up_skipped', 'None')}")
        else:
            print("❌ No record found to update")
    
    except Exception as e:
        print(f"❌ Error updating record: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_bryan_status())