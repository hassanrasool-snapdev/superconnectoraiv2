from fastapi import APIRouter, Depends, HTTPException
from app.core.db import get_database
from app.services.auth_service import get_current_user
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/filter-options")
async def get_dynamic_filter_options(
    current_user=Depends(get_current_user),
    db=Depends(get_database)
) -> Dict[str, Any]:
    """
    Get dynamic filter options based on the current user's actual connection data.
    This ensures filters are inclusive of all values in the user's network.
    """
    try:
        # Get unique industries from user's connections
        industries_pipeline = [
            {"$match": {"user_id": current_user["id"]}},
            {"$group": {"_id": "$company_industry"}},
            {"$match": {"_id": {"$ne": None, "$ne": ""}}},
            {"$sort": {"_id": 1}}
        ]
        
        # Get unique company sizes
        company_sizes_pipeline = [
            {"$match": {"user_id": current_user["id"]}},
            {"$group": {"_id": "$company_size"}},
            {"$match": {"_id": {"$ne": None, "$ne": ""}}},
            {"$sort": {"_id": 1}}
        ]
        
        # Get unique locations (cities, states, countries)
        locations_pipeline = [
            {"$match": {"user_id": current_user["id"]}},
            {"$group": {
                "_id": None,
                "cities": {"$addToSet": "$city"},
                "states": {"$addToSet": "$state"},
                "countries": {"$addToSet": "$country"}
            }}
        ]
        
        # Execute aggregation pipelines
        industries_cursor = db.connections.aggregate(industries_pipeline)
        company_sizes_cursor = db.connections.aggregate(company_sizes_pipeline)
        locations_cursor = db.connections.aggregate(locations_pipeline)
        
        # Extract results
        industries = [doc["_id"] for doc in await industries_cursor.to_list(length=None)]
        company_sizes = [doc["_id"] for doc in await company_sizes_cursor.to_list(length=None)]
        
        locations_data = await locations_cursor.to_list(length=1)
        locations = []
        if locations_data:
            # Combine cities, states, and countries, removing None/empty values
            all_locations = set()
            for location_type in ['cities', 'states', 'countries']:
                if location_type in locations_data[0]:
                    all_locations.update([loc for loc in locations_data[0][location_type] if loc])
            locations = sorted(list(all_locations))
        
        # Get counts for professional status flags
        status_pipeline = [
            {"$match": {"user_id": current_user["id"]}},
            {"$group": {
                "_id": None,
                "hiring_count": {"$sum": {"$cond": [{"$eq": ["$is_hiring", True]}, 1, 0]}},
                "open_to_work_count": {"$sum": {"$cond": [{"$eq": ["$is_open_to_work", True]}, 1, 0]}},
                "company_owner_count": {"$sum": {"$cond": [{"$eq": ["$is_company_owner", True]}, 1, 0]}},
                "pe_vc_count": {"$sum": {"$cond": [{"$eq": ["$has_pe_vc_role", True]}, 1, 0]}}
            }}
        ]
        
        status_cursor = db.connections.aggregate(status_pipeline)
        status_data = await status_cursor.to_list(length=1)
        
        # Get total connections count for context
        total_connections = await db.connections.count_documents({"user_id": current_user["id"]})
        
        return {
            "industries": industries,
            "company_sizes": company_sizes,
            "locations": locations,
            "professional_status_counts": status_data[0] if status_data else {},
            "total_connections": total_connections,
            "generated_from": "user_network_data",
            "user_id": current_user["id"]
        }
        
    except Exception as e:
        logger.error(f"Error generating dynamic filter options: {e}")
        # Fallback to static options if dynamic generation fails
        return {
            "industries": [
                'Technology', 'Finance', 'Healthcare', 'Education', 'Retail',
                'Manufacturing', 'Real Estate', 'Consulting', 'Media & Entertainment',
                'Non-profit', 'Government', 'Energy', 'Transportation', 'Food & Beverage',
                'Fashion', 'Sports', 'Travel & Tourism'
            ],
            "company_sizes": [
                '1-10 employees', '11-50 employees', '51-200 employees',
                '201-500 employees', '501-1000 employees', '1001-5000 employees',
                '5001-10000 employees', '10000+ employees'
            ],
            "locations": [
                'San Francisco Bay Area', 'New York City', 'Los Angeles', 'Chicago',
                'Boston', 'Seattle', 'Austin', 'Denver', 'Miami', 'Atlanta',
                'London', 'Paris', 'Berlin', 'Toronto', 'Sydney', 'Singapore',
                'Tokyo', 'Remote'
            ],
            "professional_status_counts": {},
            "total_connections": 0,
            "generated_from": "static_fallback",
            "error": str(e)
        }