import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, close_mongo_connection, get_database

async def check_access_requests():
    """Check all access requests in the database"""
    print("Checking all access requests...")
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    # Find all access requests
    access_requests = await db.access_requests.find({}).to_list(length=None)
    
    print(f"Found {len(access_requests)} access requests:")
    print("=" * 80)
    
    for i, request in enumerate(access_requests, 1):
        print(f"{i}. {request['full_name']} ({request['email']})")
        print(f"   ID: {request['id']}")
        print(f"   Status: {request['status']}")
        print(f"   Organization: {request.get('organization', 'N/A')}")
        print(f"   Submitted: {request.get('created_at', 'N/A')}")
        print("-" * 40)
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_access_requests())