from fastapi import APIRouter, Depends, HTTPException
from app.core.db import get_database
from app.services.auth_service import get_current_user
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/filter-options")
async def get_streamlined_filter_options(
    current_user=Depends(get_current_user),
    db=Depends(get_database)
) -> Dict[str, Any]:
    """
    Get streamlined filter options: only Open to Work and Country filters.
    This simplified approach ensures sustainable performance with CSV updates.
    """
    try:
        # Get unique countries from user's connections
        countries_pipeline = [
            {"$match": {"user_id": current_user["id"]}},
            {"$group": {"_id": "$country"}},
            {"$match": {"_id": {"$ne": None, "$ne": ""}}},
            {"$sort": {"_id": 1}}
        ]
        
        # Get counts for Open to Work status
        status_pipeline = [
            {"$match": {"user_id": current_user["id"]}},
            {"$group": {
                "_id": None,
                "open_to_work_count": {"$sum": {"$cond": [{"$eq": ["$is_open_to_work", True]}, 1, 0]}},
                "total_count": {"$sum": 1}
            }}
        ]
        
        # Execute aggregation pipelines
        countries_cursor = db.connections.aggregate(countries_pipeline)
        status_cursor = db.connections.aggregate(status_pipeline)
        
        # Extract results
        countries = [doc["_id"] for doc in await countries_cursor.to_list(length=None)]
        status_data = await status_cursor.to_list(length=1)
        
        # Get total connections count for context
        total_connections = await db.connections.count_documents({"user_id": current_user["id"]})
        
        return {
            "countries": countries,
            "open_to_work_count": status_data[0]["open_to_work_count"] if status_data else 0,
            "total_connections": total_connections,
            "generated_from": "streamlined_user_data",
            "user_id": current_user["id"]
        }
        
    except Exception as e:
        logger.error(f"Error generating streamlined filter options: {e}")
        # Fallback to static options if dynamic generation fails
        return {
            "countries": [
                'United States', 'Canada', 'United Kingdom', 'Germany', 'France',
                'Australia', 'India', 'Singapore', 'Netherlands', 'Switzerland',
                'Japan', 'Brazil', 'Mexico', 'Spain', 'Italy', 'Sweden',
                'Norway', 'Denmark', 'Belgium', 'Austria', 'Ireland', 'Israel',
                'South Korea', 'China', 'Hong Kong', 'New Zealand', 'Finland',
                'Portugal', 'Czech Republic', 'Poland', 'Russia', 'Ukraine',
                'South Africa', 'Argentina', 'Chile', 'Colombia'
            ],
            "open_to_work_count": 0,
            "total_connections": 0,
            "generated_from": "static_fallback",
            "error": str(e)
        }