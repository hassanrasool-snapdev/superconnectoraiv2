from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.services.auth_service import get_current_user
from app.services import tips_service
from app.models.tip import TipCreate, TipPublic
from app.core.db import get_database

router = APIRouter()

@router.post("/tips", response_model=TipPublic, status_code=status.HTTP_201_CREATED)
async def create_tip(
    tip_data: TipCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new tip"""
    try:
        user_id = UUID(current_user["id"])
        tip = await tips_service.create_tip(db, user_id, tip_data)
        return TipPublic(**tip)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tip: {str(e)}"
        )

@router.get("/tips", response_model=List[TipPublic])
async def get_tipping_history(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's tipping history"""
    try:
        user_id = UUID(current_user["id"])
        tips = await tips_service.get_user_tipping_history(db, user_id)
        return [TipPublic(**tip) for tip in tips]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tipping history: {str(e)}"
        )