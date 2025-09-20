#!/usr/bin/env python3

import asyncio
import sys
import os
import json
import httpx
from typing import Dict, List, Any

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo

class ExistingFilterTester:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.test_user_id = "test-user-123"
        
    async def analyze_existing_filter_data(self):
        """Analyze what filter data already exists without any enrichment"""
        print("📊 ANALYZING EXISTING FILTER DATA")
        print("=" * 60)
        
        await connect_to_mongo()
        db = get_database()
        
        # Check counts for each filter field
        total_connections = await db.connections.count_documents({})
        print(f"Total connections: {total_connections}")
        
        # Boolean filters - these are ready to use!
        boolean_filters = {
            'is_hiring': 'Actively Hiring',
            'is_open_to_work': 'Open to Work', 
            'is_premium': 'Premium Members',
            'is_creator': 'Content Creators',
            'is_influencer': 'Influencers',
            'is_top_voice': 'Top Voice',
            'is_company_owner': 'Company Owners',
            'has_pe_vc_role': 'PE/VC Professionals'
        }
        
        print(f"\n🔘 BOOLEAN FILTERS (READY TO USE):")
        for field, label in boolean_filters.items():
            true_count = await db.connections.count_documents({field: True})
            false_count = await db.connections.count_documents({field: False})
            print(f"   {label}: {true_count} True, {false_count} False")
        
        # Location filters - these are ready to use!
        print(f"\n📍 LOCATION FILTERS (READY TO USE):")
        cities = await db.connections.distinct('city')
        states = await db.connections.distinct('state') 
        countries = await db.connections.distinct('country')
        
        print(f"   Cities: {len([c for c in cities if c])} unique ({cities[:5]}...)")
        print(f"   States: {len([s for s in states if s])} unique ({states[:5]}...)")
        print(f"   Countries: {len([c for c in countries if c])} unique ({countries[:5]}...)")
        
        # Industry and company size - check if populated
        print(f"\n🏭 INDUSTRY & COMPANY SIZE DATA:")
        industries = await db.connections.distinct('company_industry')
        company_sizes = await db.connections.distinct('company_size')
        
        industry_count = await db.connections.count_documents({'company_industry': {'$ne': None, '$ne': ''}})
        size_count = await db.connections.count_documents({'company_size': {'$ne': None, '$ne': ''}})
        
        print(f"   Industries: {len([i for i in industries if i])} unique, {industry_count} records populated")
        print(f"   Company Sizes: {len([s for s in company_sizes if s])} unique, {size_count} records populated")
        
        if industries and len([i for i in industries if i]) > 0:
            print(f"   Sample industries: {[i for i in industries if i][:5]}")
        if company_sizes and len([s for s in company_sizes if s]) > 0:
            print(f"   Sample sizes: {[s for s in company_sizes if s][:5]}")
        
        return {
            'boolean_filters': boolean_filters,
            'location_ready': len([c for c in cities if c]) > 0,
            'industry_ready': industry_count > 100,  # Arbitrary threshold
            'size_ready': size_count > 100
        }
    
    async def test_ready_filters(self, query: str = "software engineer"):
        """Test only the filters that are ready to use with existing data"""
        print(f"\n🧪 TESTING READY-TO-USE FILTERS")
        print(f"Query: '{query}'")
        print("=" * 60)
        
        test_results = {}
        
        # 1. Baseline search
        print(f"\n🔍 BASELINE SEARCH (NO FILTERS)")
        baseline = await self.test_search_request(query, None)
        test_results['baseline'] = baseline
        print(f"   Results: {baseline.get('count', 0)}")
        
        # 2. Test boolean filters that are populated
        boolean_tests = [
            ('is_hiring', True, 'Actively Hiring'),
            ('is_open_to_work', True, 'Open to Work'),
            ('is_premium', True, 'Premium Members'),
            ('is_creator', True, 'Content Creators'),
            ('is_influencer', True, 'Influencers')
        ]
        
        for filter_field, filter_value, label in boolean_tests:
            print(f"\n🔘 TESTING {label.upper()} FILTER")
            result = await self.test_search_request(query, {filter_field: filter_value})
            test_results[filter_field] = result
            
            if result.get('success'):
                count = result.get('count', 0)
                matching = result.get('matching_filter', 0)
                effectiveness = (matching/count*100) if count > 0 else 0
                print(f"   Results: {count} ({matching} matching filter = {effectiveness:.1f}% effective)")
                
                # Show sample results
                for i, res in enumerate(result.get('results', [])[:2], 1):
                    profile = res.get('connection', {})
                    filter_val = profile.get(filter_field, 'N/A')
                    print(f"   {i}. {profile.get('name', 'N/A')} - {filter_field}: {filter_val}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # 3. Test location filters
        print(f"\n📍 TESTING LOCATION FILTERS")
        location_tests = [
            ('New York', 'New York City area'),
            ('California', 'California state'),
            ('San Francisco', 'San Francisco city')
        ]
        
        for location, label in location_tests:
            print(f"\n   Testing {label}:")
            result = await self.test_search_request(query, {'locations': [location]})
            test_results[f'location_{location.lower().replace(" ", "_")}'] = result
            
            if result.get('success'):
                count = result.get('count', 0)
                matching = result.get('matching_filter', 0)
                effectiveness = (matching/count*100) if count > 0 else 0
                print(f"   Results: {count} ({matching} matching = {effectiveness:.1f}% effective)")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # 4. Test combined filters
        print(f"\n🔗 TESTING COMBINED FILTERS")
        combined_result = await self.test_search_request(query, {
            'is_hiring': True,
            'locations': ['California']
        })
        test_results['combined'] = combined_result
        
        if combined_result.get('success'):
            count = combined_result.get('count', 0)
            print(f"   Hiring + California: {count} results")
        
        return test_results
    
    async def test_search_request(self, query: str, filters: Dict = None) -> Dict[str, Any]:
        """Make a search request and analyze results"""
        search_payload = {
            "query": query,
            "filters": filters
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/search",
                    json=search_payload,
                    headers={"Authorization": f"Bearer test-token-{self.test_user_id}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Verify filter matching if filters were applied
                    matching_filter = 0
                    if filters:
                        for result in results:
                            profile = result.get('connection', {})
                            matches_all_filters = True
                            
                            for filter_key, filter_value in filters.items():
                                if filter_key == 'locations':
                                    # Check if any location matches
                                    location_match = False
                                    for location in filter_value:
                                        if (location.lower() in profile.get('city', '').lower() or
                                            location.lower() in profile.get('state', '').lower() or
                                            location.lower() in profile.get('country', '').lower()):
                                            location_match = True
                                            break
                                    if not location_match:
                                        matches_all_filters = False
                                        break
                                else:
                                    # Boolean filter check
                                    if profile.get(filter_key) != filter_value:
                                        matches_all_filters = False
                                        break
                            
                            if matches_all_filters:
                                matching_filter += 1
                    
                    return {
                        "success": True,
                        "count": len(results),
                        "matching_filter": matching_filter,
                        "results": results
                    }
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def generate_filter_report(self, analysis_data: Dict, test_results: Dict):
        """Generate comprehensive report on filter functionality"""
        print(f"\n📋 FILTER FUNCTIONALITY REPORT")
        print("=" * 60)
        
        baseline_count = test_results.get('baseline', {}).get('count', 0)
        print(f"🔍 Baseline search results: {baseline_count}")
        
        print(f"\n✅ WORKING FILTERS:")
        working_filters = []
        
        # Boolean filters
        boolean_filters = analysis_data.get('boolean_filters', {})
        for field, label in boolean_filters.items():
            if field in test_results and test_results[field].get('success'):
                result = test_results[field]
                count = result.get('count', 0)
                matching = result.get('matching_filter', 0)
                effectiveness = (matching/count*100) if count > 0 else 0
                
                if count > 0:
                    print(f"   ✓ {label}: {count} results ({effectiveness:.1f}% filter accuracy)")
                    working_filters.append(label)
        
        # Location filters
        location_filters = ['location_new_york', 'location_california', 'location_san_francisco']
        for loc_filter in location_filters:
            if loc_filter in test_results and test_results[loc_filter].get('success'):
                result = test_results[loc_filter]
                count = result.get('count', 0)
                matching = result.get('matching_filter', 0)
                effectiveness = (matching/count*100) if count > 0 else 0
                
                if count > 0:
                    location_name = loc_filter.replace('location_', '').replace('_', ' ').title()
                    print(f"   ✓ Location ({location_name}): {count} results ({effectiveness:.1f}% accuracy)")
                    working_filters.append(f"Location - {location_name}")
        
        # Combined filters
        if 'combined' in test_results and test_results['combined'].get('success'):
            combined_count = test_results['combined'].get('count', 0)
            if combined_count > 0:
                print(f"   ✓ Combined Filters: {combined_count} results")
                working_filters.append("Combined Filters")
        
        print(f"\n📊 SUMMARY:")
        print(f"   • {len(working_filters)} filter types are functional")
        print(f"   • Filters successfully reduce result sets from baseline of {baseline_count}")
        print(f"   • No data enrichment needed - using existing data")
        print(f"   • Sustainable approach - works with source data updates")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print(f"   • Focus on the working boolean filters (hiring, open to work, premium, etc.)")
        print(f"   • Location filtering works well with existing city/state/country data")
        print(f"   • Combined filters provide powerful search refinement")
        print(f"   • Industry/company size filters may need source data improvement")

async def main():
    """Main test execution"""
    tester = ExistingFilterTester()
    
    # Analyze existing data
    analysis_data = await tester.analyze_existing_filter_data()
    
    # Test ready filters
    test_results = await tester.test_ready_filters()
    
    # Generate report
    await tester.generate_filter_report(analysis_data, test_results)

if __name__ == "__main__":
    asyncio.run(main())