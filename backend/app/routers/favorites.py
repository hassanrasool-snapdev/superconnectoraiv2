from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from pydantic import BaseModel

from app.services.auth_service import get_current_user
from app.services import favorites_service
from app.core.db import get_database

router = APIRouter()

class FavoriteRequest(BaseModel):
    connection_id: UUID

@router.post("/favorites", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_favorite_connection(
    favorite_request: FavoriteRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Add a connection to favorites"""
    try:
        user_id = UUID(current_user["id"])
        favorite = await favorites_service.add_favorite_connection(db, user_id, favorite_request.connection_id)
        return favorite
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add favorite: {str(e)}"
        )

@router.delete("/favorites/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite_connection(
    connection_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Remove a connection from favorites"""
    try:
        user_id = UUID(current_user["id"])
        removed = await favorites_service.remove_favorite_connection(db, user_id, connection_id)
        
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite connection not found"
            )
        
        return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove favorite: {str(e)}"
        )

@router.get("/favorites", response_model=List[dict])
async def get_favorite_connections(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all favorite connections for the current user"""
    try:
        user_id = UUID(current_user["id"])
        favorites = await favorites_service.get_user_favorite_connections(db, user_id)
        return favorites
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get favorite connections: {str(e)}"
        )

@router.get("/favorites/{connection_id}/check", response_model=dict)
async def check_favorite_status(
    connection_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Check if a connection is favorited"""
    try:
        user_id = UUID(current_user["id"])
        is_favorited = await favorites_service.is_connection_favorited(db, user_id, connection_id)
        return {"is_favorited": is_favorited}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check favorite status: {str(e)}"
        )

@router.get("/favorites/count", response_model=dict)
async def get_favorites_count(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get count of user's favorite connections"""
    try:
        user_id = UUID(current_user["id"])
        count = await favorites_service.get_user_favorites_count(db, user_id)
        return {"count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get favorites count: {str(e)}"
        )