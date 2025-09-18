import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_production_database():
    """
    Test connection to production database and analyze the data structure
    """
    
    # Current database URL from .env
    current_db_url = os.getenv("DATABASE_URL")
    print(f"Current DATABASE_URL: {current_db_url}")
    
    try:
        # Connect to current database
        client = AsyncIOMotorClient(current_db_url)
        db = client.superconnect_ai
        
        # Get connection count
        total_connections = await db.connections.count_documents({})
        print(f"\n📊 Current Database Stats:")
        print(f"   Total connections: {total_connections}")
        
        if total_connections > 0:
            # Sample some connections
            sample_connections = await db.connections.find({}).limit(5).to_list(length=5)
            print(f"\n📋 Sample connections:")
            for i, conn in enumerate(sample_connections, 1):
                print(f"   {i}. {conn.get('fullName', 'Unknown')} - {conn.get('title', 'Unknown')} at {conn.get('companyName', 'Unknown')}")
            
            # Check for user_id field distribution
            with_user_id = await db.connections.count_documents({"user_id": {"$exists": True}})
            print(f"\n🔍 Data Analysis:")
            print(f"   Connections with user_id: {with_user_id}")
            print(f"   Connections without user_id: {total_connections - with_user_id}")
            
            # Check for different user_ids
            if with_user_id > 0:
                user_ids = await db.connections.distinct("user_id")
                print(f"   Unique user_ids found: {len(user_ids)}")
                for user_id in user_ids[:3]:  # Show first 3
                    count = await db.connections.count_documents({"user_id": user_id})
                    print(f"     - {user_id}: {count} connections")
            
            # Check data quality
            sample_conn = sample_connections[0] if sample_connections else {}
            print(f"\n📝 Sample connection structure:")
            for key, value in sample_conn.items():
                if isinstance(value, str) and len(value) > 50:
                    print(f"   {key}: {value[:50]}...")
                else:
                    print(f"   {key}: {value}")
        
        client.close()
        
        print(f"\n✅ Database connection successful!")
        
        if total_connections < 1000:
            print(f"⚠️  This appears to be a development database with limited data.")
            print(f"   Production database likely has 15,000+ connections.")
            print(f"   Consider checking Vercel environment variables for production DATABASE_URL.")
        else:
            print(f"🎉 This appears to be the production database with full dataset!")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"\n💡 Troubleshooting steps:")
        print(f"   1. Check if DATABASE_URL is set correctly in .env")
        print(f"   2. Verify network connectivity to MongoDB")
        print(f"   3. Check if IP address is whitelisted in MongoDB Atlas")

if __name__ == "__main__":
    asyncio.run(test_production_database())