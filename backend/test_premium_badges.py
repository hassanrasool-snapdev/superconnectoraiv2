import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import random

async def set_premium_status():
    """Set some connections to premium status for testing"""
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    db = client[settings.DATABASE_NAME]
    connections_collection = db["connections"]
    
    # Get all connections
    connections = await connections_collection.find({}).to_list(length=None)
    print(f"Found {len(connections)} connections")
    
    if not connections:
        print("No connections found to update")
        return
    
    # Randomly select 20% of connections to be premium
    premium_count = max(1, len(connections) // 5)
    premium_connections = random.sample(connections, premium_count)
    
    # Update selected connections to premium
    for conn in premium_connections:
        await connections_collection.update_one(
            {"_id": conn["_id"]},
            {"$set": {
                "is_premium": True,
                "is_top_voice": random.choice([True, False]),
                "is_influencer": random.choice([True, False]),
                "is_hiring": random.choice([True, False]),
                "is_open_to_work": random.choice([True, False]),
                "is_creator": random.choice([True, False])
            }}
        )
        print(f"Set {conn.get('first_name', '')} {conn.get('last_name', '')} to premium")
    
    print(f"Updated {premium_count} connections to premium status")
    client.close()

if __name__ == "__main__":
    asyncio.run(set_premium_status())