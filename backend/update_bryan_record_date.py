import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def update_bryan_record_date():
    """Update the Bryan Haas -> Hugh Molotsi record to be 15 days old"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(
        settings.DATABASE_URL,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    db = client[settings.DATABASE_NAME]
    
    try:
        print("🔧 Updating Bryan Haas -> Hugh Molotsi record to be 15 days old...")
        
        # Calculate date 15 days ago
        fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
        
        # Find and update the record
        result = await db.warm_intro_requests.update_one(
            {
                "requester_name": "Bryan Haas",
                "connection_name": "Hugh Molotsi"
            },
            {
                "$set": {
                    "created_at": fifteen_days_ago,
                    "updated_at": fifteen_days_ago,
                    "connected_date": fifteen_days_ago,
                    "outcome_date": fifteen_days_ago
                }
            }
        )
        
        if result.matched_count > 0:
            print(f"✅ Successfully updated record!")
            print(f"   New created_at: {fifteen_days_ago}")
            print(f"   Days ago: {(datetime.utcnow() - fifteen_days_ago).days}")
            
            # Verify the update
            updated_record = await db.warm_intro_requests.find_one({
                "requester_name": "Bryan Haas",
                "connection_name": "Hugh Molotsi"
            })
            
            if updated_record:
                print(f"\n📋 Verification:")
                print(f"   ID: {updated_record['id']}")
                print(f"   Created: {updated_record['created_at']}")
                print(f"   Status: {updated_record['status']}")
                print(f"   Follow-up sent: {updated_record.get('follow_up_sent_date', 'None')}")
                print(f"   Days since created: {(datetime.utcnow() - updated_record['created_at']).days}")
        else:
            print("❌ No record found to update")
    
    except Exception as e:
        print(f"❌ Error updating record: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_bryan_record_date())