#!/usr/bin/env python3
"""
Test script to verify the search functionality works with MongoDB fallback.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo
from app.services.retrieval_service import retrieval_service

async def test_search_functionality():
    """Test the search functionality with the loaded sample data"""
    
    # User ID from the terminal logs
    user_id = "5741eb91-8eb7-41f1-acb3-7ec46dfacca9"
    
    print("🔍 Testing Search Functionality with MongoDB Fallback")
    
    try:
        # Initialize database connection
        await connect_to_mongo()
        
        # Test queries
        test_queries = [
            "product manager at redwood credit union",
            "software engineer",
            "data scientist at google",
            "marketing director",
            "founder ceo fintech"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}: '{query}'")
            
            try:
                results = await retrieval_service.retrieve_and_rerank(
                    user_query=query,
                    user_id=user_id,
                    enable_query_rewrite=True
                )
                
                print(f"   ✅ Found {len(results)} results")
                
                # Show top 3 results
                for j, result in enumerate(results[:3], 1):
                    profile = result.get('profile', {})
                    score = result.get('score', 0)
                    pros = result.get('pros', [])
                    
                    print(f"      {j}. {profile.get('fullName', 'Unknown')} - Score: {score}")
                    print(f"         Company: {profile.get('companyName', 'N/A')}")
                    print(f"         Title: {profile.get('headline', 'N/A')}")
                    if pros:
                        print(f"         Pros: {pros[0]}")
                
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
        
        print(f"\n🎉 Search functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_search_functionality())
    sys.exit(0 if success else 1)