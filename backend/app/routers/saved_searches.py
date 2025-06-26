from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.services.auth_service import get_current_user
from app.services import saved_searches_service
from app.models.saved_search import SavedSearchCreate, SavedSearchPublic
from app.core.db import get_database

router = APIRouter()

class SavedSearchUpdate(BaseModel):
    name: str = None
    query: str = None
    filters: dict = None

@router.post("/saved-searches", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_saved_search(
    saved_search_data: SavedSearchCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new saved search"""
    try:
        user_id = UUID(current_user["id"])
        saved_search = await saved_searches_service.create_saved_search(db, user_id, saved_search_data)
        return saved_search
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create saved search: {str(e)}"
        )

@router.get("/saved-searches", response_model=List[dict])
async def get_saved_searches(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all saved searches for the current user"""
    try:
        user_id = UUID(current_user["id"])
        saved_searches = await saved_searches_service.get_user_saved_searches(db, user_id)
        return saved_searches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get saved searches: {str(e)}"
        )

@router.get("/saved-searches/{search_id}", response_model=dict)
async def get_saved_search(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get a specific saved search by ID"""
    try:
        user_id = UUID(current_user["id"])
        saved_search = await saved_searches_service.get_saved_search_by_id(db, user_id, search_id)
        
        if not saved_search:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )
        
        return saved_search
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get saved search: {str(e)}"
        )

@router.put("/saved-searches/{search_id}", response_model=dict)
async def update_saved_search(
    search_id: UUID,
    update_data: SavedSearchUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update a saved search"""
    try:
        user_id = UUID(current_user["id"])
        
        # Only include non-None fields in the update
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        saved_search = await saved_searches_service.update_saved_search(db, user_id, search_id, update_dict)
        
        if not saved_search:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )
        
        return saved_search
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update saved search: {str(e)}"
        )

@router.delete("/saved-searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a saved search"""
    try:
        user_id = UUID(current_user["id"])
        deleted = await saved_searches_service.delete_saved_search(db, user_id, search_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved search not found"
            )
        
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete saved search: {str(e)}"
        )