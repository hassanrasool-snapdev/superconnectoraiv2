import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import random

async def fix_badge_data():
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    db = client[settings.DATABASE_NAME]
    connections_collection = db["connections"]
    
    # First, let's see what fields actually exist
    sample = await connections_collection.find_one({})
    if sample:
        print("=== SAMPLE DOCUMENT FIELDS ===")
        for key in sample.keys():
            if 'name' in key.lower():
                print(f"{key}: {sample.get(key)}")
    
    # Search for Deborah Liu with different field names
    possible_deborahs = await connections_collection.find({
        "$or": [
            {"fullName": {"$regex": "deborah.*liu", "$options": "i"}},
            {"firstName": {"$regex": "deborah", "$options": "i"}, "lastName": {"$regex": "liu", "$options": "i"}},
            {"first_name": {"$regex": "deborah", "$options": "i"}, "last_name": {"$regex": "liu", "$options": "i"}},
            {"name": {"$regex": "deborah.*liu", "$options": "i"}}
        ]
    }).to_list(length=10)
    
    print(f"\n=== FOUND {len(possible_deborahs)} POTENTIAL DEBORAH LIU MATCHES ===")
    for person in possible_deborahs:
        name_fields = []
        for field in ['fullName', 'firstName', 'lastName', 'first_name', 'last_name', 'name', 'full_name']:
            if field in person:
                name_fields.append(f"{field}: {person[field]}")
        print(f"- {' | '.join(name_fields)}")
    
    # Fix the logical inconsistency: people can't be both hiring and open to work
    print(f"\n=== FIXING LOGICAL INCONSISTENCIES ===")
    
    # Find all people with both hiring and open_to_work
    both_flags = await connections_collection.find({
        "is_hiring": True, 
        "is_open_to_work": True
    }).to_list(length=None)
    
    print(f"Found {len(both_flags)} people with both hiring and open_to_work flags")
    
    # Fix each one by randomly choosing one or the other
    fixed_count = 0
    for person in both_flags:
        # Randomly choose to keep either hiring or open_to_work, but not both
        if random.choice([True, False]):
            # Keep hiring, remove open_to_work
            await connections_collection.update_one(
                {"_id": person["_id"]},
                {"$set": {"is_open_to_work": False}}
            )
        else:
            # Keep open_to_work, remove hiring
            await connections_collection.update_one(
                {"_id": person["_id"]},
                {"$set": {"is_hiring": False}}
            )
        fixed_count += 1
    
    print(f"Fixed {fixed_count} logical inconsistencies")
    
    # Verify the fix
    remaining_both = await connections_collection.count_documents({
        "is_hiring": True, 
        "is_open_to_work": True
    })
    print(f"Remaining people with both flags: {remaining_both}")
    
    # Now let's check if we can find some actual premium members with proper names
    print(f"\n=== CHECKING PREMIUM MEMBERS WITH PROPER NAMES ===")
    premium_with_names = await connections_collection.find({
        "is_premium": True,
        "$or": [
            {"fullName": {"$exists": True, "$ne": None, "$ne": ""}},
            {"firstName": {"$exists": True, "$ne": None, "$ne": ""}},
            {"first_name": {"$exists": True, "$ne": None, "$ne": ""}},
            {"name": {"$exists": True, "$ne": None, "$ne": ""}}
        ]
    }).limit(10).to_list(length=10)
    
    for person in premium_with_names:
        name_fields = []
        for field in ['fullName', 'firstName', 'lastName', 'first_name', 'last_name', 'name', 'full_name']:
            if field in person and person[field]:
                name_fields.append(f"{field}: {person[field]}")
        company_fields = []
        for field in ['companyName', 'company_name', 'company']:
            if field in person and person[field]:
                company_fields.append(f"{field}: {person[field]}")
        
        print(f"- {' | '.join(name_fields)} | {' | '.join(company_fields)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_badge_data())