#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo

async def main():
    print("🔍 CHECKING CONNECTIONS DATABASE...")
    print("=" * 60)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database successfully!")
        
        # Check connections count
        print("\n📊 CONNECTIONS IN DATABASE:")
        total_connections = await db.connections.count_documents({})
        print(f"Total connections: {total_connections}")
        
        if total_connections == 0:
            print("❌ NO CONNECTIONS FOUND IN DATABASE!")
            print("   This explains why users can't search for connections.")
        elif total_connections < 10000:
            print(f"⚠️  WARNING: Only {total_connections} connections found.")
            print("   Expected 15,000+ connections for production data.")
        else:
            print(f"✅ Good! Found {total_connections} connections.")
        
        # Show sample connections if any exist
        if total_connections > 0:
            print(f"\n📋 SAMPLE CONNECTIONS:")
            sample_connections = await db.connections.find({}).limit(5).to_list(length=5)
            for i, conn in enumerate(sample_connections, 1):
                print(f"  {i}. {conn.get('fullName', 'Unknown')} - {conn.get('title', 'Unknown')} at {conn.get('companyName', 'Unknown')}")
                print(f"     LinkedIn: {conn.get('linkedin_url', 'N/A')}")
                print(f"     City: {conn.get('city', 'N/A')}, Country: {conn.get('country', 'N/A')}")
                print("     ---")
        
        # Check for any connections with specific companies to validate data quality
        if total_connections > 0:
            print(f"\n🔍 DATA QUALITY CHECK:")
            
            # Check for well-known companies
            openai_count = await db.connections.count_documents({
                "companyName": {"$regex": "OpenAI", "$options": "i"}
            })
            google_count = await db.connections.count_documents({
                "companyName": {"$regex": "Google", "$options": "i"}
            })
            microsoft_count = await db.connections.count_documents({
                "companyName": {"$regex": "Microsoft", "$options": "i"}
            })
            
            print(f"  OpenAI connections: {openai_count}")
            print(f"  Google connections: {google_count}")
            print(f"  Microsoft connections: {microsoft_count}")
            
            # Check for empty/invalid data
            empty_names = await db.connections.count_documents({
                "$or": [
                    {"fullName": {"$in": ["", None]}},
                    {"fullName": {"$regex": "^\\s*$"}}
                ]
            })
            empty_companies = await db.connections.count_documents({
                "$or": [
                    {"companyName": {"$in": ["", None]}},
                    {"companyName": {"$regex": "^\\s*$"}}
                ]
            })
            
            print(f"  Connections with empty names: {empty_names}")
            print(f"  Connections with empty companies: {empty_companies}")
        
        print(f"\n🎯 DIAGNOSIS:")
        if total_connections == 0:
            print("❌ CRITICAL: No connections data in database!")
            print("   CAUSE: Production data was never loaded")
            print("   SOLUTION: Need to load the full connections dataset")
        elif total_connections < 1000:
            print("❌ PROBLEM: Very few connections in database")
            print("   CAUSE: Only test data was loaded, not production data")
            print("   SOLUTION: Need to load the full production dataset")
        elif total_connections < 10000:
            print("⚠️  WARNING: Partial data loaded")
            print("   CAUSE: Production data load may have been incomplete")
            print("   SOLUTION: Verify and reload full dataset if needed")
        else:
            print("✅ Connections data looks good!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())