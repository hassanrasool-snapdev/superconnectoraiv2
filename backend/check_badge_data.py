import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check_premium_data():
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    db = client[settings.DATABASE_NAME]
    connections_collection = db["connections"]
    
    # Check for Deborah Liu specifically
    deborah = await connections_collection.find_one({
        "$or": [
            {"full_name": {"$regex": "deborah.*liu", "$options": "i"}},
            {"first_name": {"$regex": "deborah", "$options": "i"}, "last_name": {"$regex": "liu", "$options": "i"}}
        ]
    })
    
    if deborah:
        print("=== DEBORAH LIU DATA ===")
        print(f"Name: {deborah.get('full_name', 'N/A')}")
        print(f"is_premium: {deborah.get('is_premium', False)}")
        print(f"is_hiring: {deborah.get('is_hiring', False)}")
        print(f"is_open_to_work: {deborah.get('is_open_to_work', False)}")
        print(f"is_top_voice: {deborah.get('is_top_voice', False)}")
        print(f"is_influencer: {deborah.get('is_influencer', False)}")
        print(f"is_creator: {deborah.get('is_creator', False)}")
    else:
        print("Deborah Liu not found")
    
    # Check premium counts
    premium_count = await connections_collection.count_documents({"is_premium": True})
    total_count = await connections_collection.count_documents({})
    both_hiring_and_open = await connections_collection.count_documents({
        "is_hiring": True, 
        "is_open_to_work": True
    })
    
    print(f"\n=== PREMIUM DATA SUMMARY ===")
    print(f"Total connections: {total_count}")
    print(f"Premium connections: {premium_count}")
    print(f"Connections with both hiring and open_to_work: {both_hiring_and_open}")
    
    # Find some examples of people with both hiring and open_to_work
    if both_hiring_and_open > 0:
        print(f"\n=== EXAMPLES WITH BOTH HIRING AND OPEN_TO_WORK ===")
        examples = await connections_collection.find({
            "is_hiring": True, 
            "is_open_to_work": True
        }).limit(5).to_list(length=5)
        
        for example in examples:
            print(f"- {example.get('full_name', 'N/A')} ({example.get('company_name', 'N/A')})")
    
    # Check if we have any premium people at all
    print(f"\n=== SAMPLE PREMIUM MEMBERS ===")
    premium_examples = await connections_collection.find({"is_premium": True}).limit(5).to_list(length=5)
    for example in premium_examples:
        print(f"- {example.get('full_name', 'N/A')} ({example.get('company_name', 'N/A')})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_premium_data())