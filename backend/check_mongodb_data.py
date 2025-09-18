import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_connections():
    # Connect to MongoDB
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client.superconnect_ai
    
    # Check connections
    total_count = await db.connections.count_documents({})
    print(f'Total connections: {total_count}')
    
    if total_count > 0:
        # Get a sample connection
        sample = await db.connections.find_one({})
        print(f'Sample connection keys: {list(sample.keys())}')
        print(f'Sample connection data:')
        for key, value in sample.items():
            if isinstance(value, str) and len(value) > 100:
                print(f'  {key}: {value[:100]}...')
            else:
                print(f'  {key}: {value}')
        
        # Check if any connections have user_id
        with_user_id = await db.connections.count_documents({"user_id": {"$exists": True}})
        print(f'Connections with user_id: {with_user_id}')
        
        # Search for "OpenAI" or "product" in various fields
        openai_search = await db.connections.count_documents({
            "$or": [
                {"companyName": {"$regex": "OpenAI", "$options": "i"}},
                {"companyName": {"$regex": "Open AI", "$options": "i"}},
                {"title": {"$regex": "product", "$options": "i"}},
                {"headline": {"$regex": "product", "$options": "i"}}
            ]
        })
        print(f'Connections matching OpenAI/product search: {openai_search}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_connections())