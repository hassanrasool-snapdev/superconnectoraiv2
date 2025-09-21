#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo

async def main():
    print("🔍 FINAL CONNECTIONS DATABASE CHECK...")
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
            return
        
        # Show sample connections - check both possible field name formats
        print(f"\n📋 SAMPLE CONNECTIONS:")
        sample_connections = await db.connections.find({}).limit(5).to_list(length=5)
        for i, conn in enumerate(sample_connections, 1):
            # Try both field name formats
            name = conn.get('name') or conn.get('fullName', 'Unknown')
            company = conn.get('company') or conn.get('companyName', 'Unknown')
            title = conn.get('title') or conn.get('headline', 'Unknown')
            linkedin = conn.get('linkedin_url', 'N/A')
            location = conn.get('location', 'N/A')
            
            print(f"  {i}. {name}")
            print(f"     Company: {company}")
            print(f"     Title: {title}")
            print(f"     LinkedIn: {linkedin}")
            print(f"     Location: {location}")
            print("     ---")
        
        # Data quality check - check both field formats
        print(f"\n🔍 DATA QUALITY CHECK:")
        
        # Check for empty names (both formats)
        empty_names_old = await db.connections.count_documents({
            "$or": [
                {"fullName": {"$in": ["", None, "Unknown"]}},
                {"fullName": {"$regex": "^\\s*$"}}
            ]
        })
        empty_names_new = await db.connections.count_documents({
            "$or": [
                {"name": {"$in": ["", None, "Unknown"]}},
                {"name": {"$regex": "^\\s*$"}}
            ]
        })
        
        # Check for empty companies (both formats)
        empty_companies_old = await db.connections.count_documents({
            "$or": [
                {"companyName": {"$in": ["", None, "Unknown"]}},
                {"companyName": {"$regex": "^\\s*$"}}
            ]
        })
        empty_companies_new = await db.connections.count_documents({
            "$or": [
                {"company": {"$in": ["", None, "Unknown"]}},
                {"company": {"$regex": "^\\s*$"}}
            ]
        })
        
        print(f"  Empty names (fullName field): {empty_names_old}")
        print(f"  Empty names (name field): {empty_names_new}")
        print(f"  Empty companies (companyName field): {empty_companies_old}")
        print(f"  Empty companies (company field): {empty_companies_new}")
        
        # Check for well-known companies
        openai_count = await db.connections.count_documents({
            "$or": [
                {"company": {"$regex": "OpenAI", "$options": "i"}},
                {"companyName": {"$regex": "OpenAI", "$options": "i"}}
            ]
        })
        google_count = await db.connections.count_documents({
            "$or": [
                {"company": {"$regex": "Google", "$options": "i"}},
                {"companyName": {"$regex": "Google", "$options": "i"}}
            ]
        })
        microsoft_count = await db.connections.count_documents({
            "$or": [
                {"company": {"$regex": "Microsoft", "$options": "i"}},
                {"companyName": {"$regex": "Microsoft", "$options": "i"}}
            ]
        })
        
        print(f"  OpenAI connections: {openai_count}")
        print(f"  Google connections: {google_count}")
        print(f"  Microsoft connections: {microsoft_count}")
        
        # Test search for "Product Manager at OpenAI"
        print(f"\n🔍 SEARCH TEST - 'Product Manager at OpenAI':")
        openai_pm_results = await db.connections.find({
            "$and": [
                {
                    "$or": [
                        {"company": {"$regex": "OpenAI", "$options": "i"}},
                        {"companyName": {"$regex": "OpenAI", "$options": "i"}}
                    ]
                },
                {
                    "$or": [
                        {"title": {"$regex": "Product.*Manager", "$options": "i"}},
                        {"headline": {"$regex": "Product.*Manager", "$options": "i"}}
                    ]
                }
            ]
        }).limit(3).to_list(length=3)
        
        print(f"Found {len(openai_pm_results)} OpenAI Product Managers:")
        for result in openai_pm_results:
            name = result.get('name') or result.get('fullName', 'Unknown')
            company = result.get('company') or result.get('companyName', 'Unknown')
            title = result.get('title') or result.get('headline', 'Unknown')
            print(f"  - {name} - {title} at {company}")
        
        print(f"\n🎯 FINAL DIAGNOSIS:")
        if total_connections < 1000:
            print("❌ PROBLEM: Very few connections in database")
        elif empty_names_old > total_connections * 0.9 and empty_names_new > total_connections * 0.9:
            print("❌ PROBLEM: Most connections have empty names")
        elif empty_companies_old > total_connections * 0.9 and empty_companies_new > total_connections * 0.9:
            print("❌ PROBLEM: Most connections have empty companies")
        elif openai_count == 0:
            print("⚠️  WARNING: No OpenAI connections found - may indicate data quality issues")
        else:
            print("✅ SUCCESS: Database appears to have good quality data!")
            print(f"   - {total_connections} total connections")
            print(f"   - {openai_count} OpenAI connections")
            print(f"   - {google_count} Google connections")
            print(f"   - {microsoft_count} Microsoft connections")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())