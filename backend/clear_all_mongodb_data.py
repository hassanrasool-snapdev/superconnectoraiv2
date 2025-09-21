#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo, close_mongo_connection

async def clear_all_mongodb_data():
    """Clear all data from MongoDB collections"""
    print("🗑️  CLEARING ALL MONGODB DATA...")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database successfully!")
        
        # Get all collection names
        collections = await db.list_collection_names()
        print(f"📁 Found collections: {collections}")
        
        if not collections:
            print("ℹ️  No collections found in database")
            return True
        
        # Clear each collection
        total_deleted = 0
        for collection_name in collections:
            collection = db[collection_name]
            
            # Count documents before deletion
            count_before = await collection.count_documents({})
            
            if count_before > 0:
                # Delete all documents
                result = await collection.delete_many({})
                print(f"🗑️  Cleared {result.deleted_count} documents from '{collection_name}'")
                total_deleted += result.deleted_count
            else:
                print(f"ℹ️  Collection '{collection_name}' was already empty")
        
        print(f"\n✅ MONGODB CLEANUP COMPLETE!")
        print(f"📊 Total documents deleted: {total_deleted}")
        print(f"📁 Collections cleared: {len(collections)}")
        
        # Verify all collections are empty
        print(f"\n🔍 VERIFICATION:")
        all_empty = True
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            if count > 0:
                print(f"❌ Collection '{collection_name}' still has {count} documents")
                all_empty = False
            else:
                print(f"✅ Collection '{collection_name}' is empty")
        
        if all_empty:
            print(f"\n🎉 SUCCESS: All MongoDB collections are now empty!")
        else:
            print(f"\n❌ ERROR: Some collections still contain data")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error clearing MongoDB data: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    success = asyncio.run(clear_all_mongodb_data())
    sys.exit(0 if success else 1)