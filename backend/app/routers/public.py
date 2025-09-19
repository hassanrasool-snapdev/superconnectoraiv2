from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.follow_up_email_service import record_user_response
from app.core.db import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public", tags=["public"])

class FollowUpResponse(BaseModel):
    connected: bool

class FollowUpResponseResult(BaseModel):
    message: str
    connected: bool
    success: bool

@router.post("/warm-intro-requests/{request_id}/respond", response_model=FollowUpResponseResult)
async def respond_to_follow_up_email(
    request_id: str,
    response: FollowUpResponse,
    db = Depends(get_database)
):
    """
    Record user response to a follow-up email.
    
    This endpoint is called when a user clicks on the "Yes" or "No" links in the follow-up email.
    It does not require authentication since it's accessed via email links.
    
    Args:
        request_id: The ID of the warm intro request
        response: The user's response (connected: true/false)
        db: Database dependency
    
    Returns:
        FollowUpResponseResult: Success message and response details
    """
    try:
        logger.info(f"Processing follow-up response for request {request_id}: connected={response.connected}")
        
        result = await record_user_response(
            db=db,
            request_id=request_id,
            connected=response.connected
        )
        
        if result["success"]:
            message = (
                "Thank you for letting us know you successfully connected!"
                if response.connected
                else "Thank you for your response. We understand connections don't always work out immediately."
            )
            
            logger.info(f"Successfully recorded response for request {request_id}")
            
            return FollowUpResponseResult(
                message=message,
                connected=response.connected,
                success=True
            )
        else:
            # Handle different error types with specific messages
            if result["error"] == "request_not_found":
                logger.warning(f"Request {request_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Warm intro request not found. The link may be invalid or expired."
                )
            elif result["error"] == "already_responded":
                logger.warning(f"User already responded to request {request_id}")
                # For already responded, return success with a different message
                previous_response = result.get("previous_response", {})
                previous_connected = previous_response.get("connected", False)
                
                message = (
                    f"You have already responded to this follow-up email. "
                    f"Your previous response was: {'Yes, we connected' if previous_connected else 'No, not yet'}."
                )
                
                return FollowUpResponseResult(
                    message=message,
                    connected=previous_connected,
                    success=True  # Still return success since the response was previously recorded
                )
            else:
                logger.error(f"Failed to record response for request {request_id}: {result['message']}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing follow-up response for request {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record your response. Please try again or contact support."
        )

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