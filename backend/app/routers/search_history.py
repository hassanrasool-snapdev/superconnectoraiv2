from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from uuid import UUID

from app.services.auth_service import get_current_user
from app.services import search_history_service
from app.core.db import get_database

router = APIRouter()

@router.get("/search-history", response_model=List[dict])
async def get_search_history(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database),
    limit: int = Query(50, ge=1, le=100)
):
    """Get user's search history"""
    try:
        user_id = UUID(current_user["id"])
        search_history = await search_history_service.get_user_search_history(db, user_id, limit)
        return search_history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search history: {str(e)}"
        )

@router.delete("/search-history/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_history_entry(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a specific search history entry"""
    try:
        user_id = UUID(current_user["id"])
        deleted = await search_history_service.delete_search_history_entry(db, user_id, search_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Search history entry not found"
            )
        
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete search history entry: {str(e)}"
        )

@router.delete("/search-history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_search_history(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Clear all search history for the current user"""
    try:
        user_id = UUID(current_user["id"])
        deleted_count = await search_history_service.clear_user_search_history(db, user_id)
        return {"deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear search history: {str(e)}"
        )