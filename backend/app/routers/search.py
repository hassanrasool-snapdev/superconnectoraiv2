from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
import anthropic
from datetime import datetime

from app.services.auth_service import get_current_user
from app.services import connections_service, search_history_service
from app.services.ai_service import search_connections
from app.models.search_history import SearchHistoryCreate
from app.core.db import get_database

router = APIRouter()

class SearchFilters(BaseModel):
    industries: Optional[List[str]] = None
    company_sizes: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None

class SearchRequest(BaseModel):
    query: str
    filters: Optional[SearchFilters] = None

class SearchResult(BaseModel):
    connection: dict
    score: int
    summary: str
    pros: list
    cons: list

@router.post("/search", response_model=List[SearchResult])
async def ai_search_connections(
    search_request: SearchRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Perform AI-powered search on user's connections
    """
    if not search_request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )
    
    try:
        # Get user's connections (limit to reasonable number for AI analysis)
        user_id = current_user["id"]
        connections = await connections_service.get_user_connections(db, user_id, page=1, limit=200)
        
        if not connections:
            return []
        
        # Apply filters if provided
        if search_request.filters:
            connections = apply_search_filters(connections, search_request.filters)
        
        # Use AI to search and rank connections
        search_results = await search_connections(search_request.query, connections)
        
        # Save search to history
        try:
            history_entry = SearchHistoryCreate(
                query=search_request.query,
                filters=search_request.filters.model_dump() if search_request.filters else None,
                results_count=len(search_results)
            )
            await search_history_service.create_search_history_entry(db, UUID(user_id), history_entry)
        except Exception as history_error:
            print(f"Failed to save search history: {history_error}")
            # Don't fail the search if history saving fails
        
        return search_results
        
    except Exception as e:
        print(f"Search router error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

def apply_search_filters(connections: List[dict], filters: SearchFilters) -> List[dict]:
    """Apply advanced filters to connection list"""
    filtered_connections = connections
    
    # Filter by industries
    if filters.industries:
        filtered_connections = [
            conn for conn in filtered_connections
            if conn.get('company_industry') and any(
                industry.lower() in conn.get('company_industry', '').lower()
                for industry in filters.industries
            )
        ]
    
    # Filter by company sizes
    if filters.company_sizes:
        filtered_connections = [
            conn for conn in filtered_connections
            if conn.get('company_size') and conn.get('company_size') in filters.company_sizes
        ]
    
    # Filter by locations
    if filters.locations:
        filtered_connections = [
            conn for conn in filtered_connections
            if conn.get('city') and any(
                location.lower() in conn.get('city', '').lower() or
                location.lower() in conn.get('state', '').lower() or
                location.lower() in conn.get('country', '').lower()
                for location in filters.locations
            )
        ]
    
    # Filter by connection date range
    if filters.date_range_start or filters.date_range_end:
        filtered_connections = [
            conn for conn in filtered_connections
            if is_connection_in_date_range(conn, filters.date_range_start, filters.date_range_end)
        ]
    
    # Filter by follower count
    if filters.min_followers is not None or filters.max_followers is not None:
        filtered_connections = [
            conn for conn in filtered_connections
            if is_follower_count_in_range(conn, filters.min_followers, filters.max_followers)
        ]
    
    return filtered_connections

def is_connection_in_date_range(connection: dict, start_date: Optional[str], end_date: Optional[str]) -> bool:
    """Check if connection date is within specified range"""
    connected_on = connection.get('connected_on')
    if not connected_on:
        return False
    
    try:
        # Parse connection date (assuming format like "2023-01-15" or similar)
        conn_date = datetime.fromisoformat(connected_on.replace('Z', ''))
        
        if start_date:
            start = datetime.fromisoformat(start_date)
            if conn_date < start:
                return False
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            if conn_date > end:
                return False
        
        return True
    except (ValueError, AttributeError):
        return False

def is_follower_count_in_range(connection: dict, min_followers: Optional[int], max_followers: Optional[int]) -> bool:
    """Check if follower count is within specified range"""
    followers_str = connection.get('followers')
    if not followers_str:
        return False
    
    try:
        # Extract numeric value from followers string (e.g., "1,234" -> 1234)
        followers_count = int(followers_str.replace(',', '').replace('+', ''))
        
        if min_followers is not None and followers_count < min_followers:
            return False
        
        if max_followers is not None and followers_count > max_followers:
            return False
        
        return True
    except (ValueError, AttributeError):
        return False