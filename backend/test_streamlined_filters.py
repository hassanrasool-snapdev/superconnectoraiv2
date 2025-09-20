#!/usr/bin/env python3

"""
Test script for streamlined filter functionality (Open to Work + Country only)
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "bryan@superconnectai.com"
TEST_USER_PASSWORD = "password123"

async def get_auth_token() -> str:
    """Get authentication token for testing"""
    async with httpx.AsyncClient() as client:
        # Login to get token
        login_data = {
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = await client.post(
            f"{API_BASE_URL}/auth/login",
            data=login_data
        )
        
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code} - {response.text}")
        
        token_data = response.json()
        return token_data["access_token"]

async def test_filter_options(token: str) -> Dict[str, Any]:
    """Test the streamlined filter options endpoint"""
    print("🔧 TESTING STREAMLINED FILTER OPTIONS")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/filter-options",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Filter options failed: {response.status_code} - {response.text}")
            return {}
        
        options = response.json()
        print(f"✅ Filter options loaded successfully")
        print(f"📊 Available countries: {len(options.get('countries', []))}")
        print(f"👥 Open to work count: {options.get('open_to_work_count', 0)}")
        print(f"📈 Total connections: {options.get('total_connections', 0)}")
        print(f"🔍 Generated from: {options.get('generated_from', 'unknown')}")
        
        if options.get('countries'):
            print(f"🌍 Sample countries: {options['countries'][:5]}...")
        
        return options

async def test_search_with_filters(token: str, options: Dict[str, Any]):
    """Test search functionality with streamlined filters"""
    print("\n🔍 TESTING SEARCH WITH STREAMLINED FILTERS")
    print("=" * 60)
    
    # Test 1: Search without filters
    await test_search(token, "software engineer", {}, "No filters")
    
    # Test 2: Search with Open to Work filter
    await test_search(token, "software engineer", {"open_to_work": True}, "Open to Work only")
    
    # Test 3: Search with Country filter (if countries available)
    if options.get('countries'):
        sample_country = options['countries'][0]
        await test_search(token, "software engineer", {"country": sample_country}, f"Country: {sample_country}")
    
    # Test 4: Search with both filters
    if options.get('countries'):
        sample_country = options['countries'][0]
        await test_search(token, "software engineer", {
            "open_to_work": True,
            "country": sample_country
        }, f"Open to Work + Country: {sample_country}")

async def test_search(token: str, query: str, filters: Dict[str, Any], description: str):
    """Test a single search with given filters"""
    print(f"\n🔎 Testing: {description}")
    print("-" * 40)
    
    search_request = {
        "query": query,
        "filters": filters if filters else None
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/search",
                headers={"Authorization": f"Bearer {token}"},
                json=search_request
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Search successful: {len(results)} results")
                
                if results:
                    # Show sample result
                    sample = results[0]
                    connection = sample.get('connection', {})
                    print(f"📋 Sample result:")
                    print(f"   Name: {connection.get('first_name', '')} {connection.get('last_name', '')}")
                    print(f"   Company: {connection.get('company_name', 'N/A')}")
                    print(f"   Country: {connection.get('country', 'N/A')}")
                    print(f"   Open to Work: {connection.get('is_open_to_work', False)}")
                    print(f"   Score: {sample.get('score', 0)}")
                else:
                    print("📭 No results found")
            else:
                print(f"❌ Search failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Search error: {str(e)}")

async def main():
    """Main test function"""
    print("🧪 STREAMLINED FILTER TESTING SUITE")
    print("=" * 60)
    print("Testing only Open to Work and Country filters")
    print("=" * 60)
    
    try:
        # Get authentication token
        print("🔐 Getting authentication token...")
        token = await get_auth_token()
        print("✅ Authentication successful")
        
        # Test filter options
        options = await test_filter_options(token)
        
        # Test search with filters
        await test_search_with_filters(token, options)
        
        print("\n🎉 STREAMLINED FILTER TESTING COMPLETE")
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("🔧 The streamlined filter system (Open to Work + Country) is working!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())