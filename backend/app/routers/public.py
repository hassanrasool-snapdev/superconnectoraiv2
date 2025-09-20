from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.db import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/warm-intro-requests/{request_id}/status")
async def get_warm_intro_request_status(
    request_id: str,
    db = Depends(get_database)
):
    """
    Get the current status of a warm intro request.
    
    This is a public endpoint that can be used to check the status of a request
    without requiring authentication. Useful for email links and status pages.
    
    Args:
        request_id: The ID of the warm intro request
        db: Database dependency
    
    Returns:
        dict: Basic status information about the request
    """
    try:
        # Find the warm intro request
        request = await db.warm_intro_requests.find_one({"id": request_id})
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warm intro request not found"
            )
        
        return {
            "id": request["id"],
            "status": request["status"],
            "requester_name": request["requester_name"],
            "connection_name": request["connection_name"],
            "created_at": request["created_at"].isoformat() if request.get("created_at") else None,
            "user_responded": request.get("user_responded", False),
            "response_date": request["response_date"].isoformat() if request.get("response_date") else None,
            "follow_up_sent_date": request["follow_up_sent_date"].isoformat() if request.get("follow_up_sent_date") else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for request {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve request status"
        )

@router.get("/health")
async def public_health_check():
    """
    Public health check endpoint.
    
    Returns:
        dict: Simple health status
    """
    return {
        "status": "healthy",
        "service": "superconnector-ai-public-api",
        "timestamp": "2025-01-19T04:54:00Z"
    }