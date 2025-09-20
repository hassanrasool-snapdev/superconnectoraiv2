import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.warm_intro_request import WarmIntroStatus

async def create_bryan_hugh_test_record():
    """Create a test warm intro request for Bryan Haas asking for Hugh Molotsi, dated 15 days ago"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(
        settings.DATABASE_URL,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    db = client[settings.DATABASE_NAME]
    
    # Calculate date 15 days ago
    fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
    
    # Create the warm intro request record
    warm_intro_request = {
        "id": str(uuid4()),
        "user_id": "bryan_user_id",  # Using a test user ID for Bryan
        "requester_name": "Bryan Haas",
        "connection_name": "Hugh Molotsi",
        "requester_first_name": "Bryan",
        "requester_last_name": "Haas",
        "connection_first_name": "Hugh",
        "connection_last_name": "Molotsi",
        "status": WarmIntroStatus.connected.value,  # Set to connected so it's eligible for follow-up
        "outcome": "Successfully connected via warm introduction",
        "outcome_date": fifteen_days_ago,
        "created_at": fifteen_days_ago,
        "updated_at": fifteen_days_ago,
        "connected_date": fifteen_days_ago,
        "declined_date": None,
        "follow_up_sent_date": None,  # This should be None so it's eligible for follow-up
        "follow_up_skipped": None,
        "follow_up_skipped_date": None,
        "follow_up_skipped_by": None
    }
    
    # Insert the record
    result = await db.warm_intro_requests.insert_one(warm_intro_request)
    
    if result.inserted_id:
        print(f"✅ Successfully created warm intro request:")
        print(f"   ID: {warm_intro_request['id']}")
        print(f"   Requester: {warm_intro_request['requester_name']}")
        print(f"   Connection: {warm_intro_request['connection_name']}")
        print(f"   Created: {warm_intro_request['created_at']}")
        print(f"   Status: {warm_intro_request['status']}")
        print(f"   Connected Date: {warm_intro_request['connected_date']}")
        print(f"   Follow-up Sent: {warm_intro_request['follow_up_sent_date']}")
        print(f"\n🔄 This record should be eligible for follow-up email processing!")
    else:
        print("❌ Failed to create warm intro request")
    
    # Close the connection
    client.close()

if __name__ == "__main__":
    asyncio.run(create_bryan_hugh_test_record())