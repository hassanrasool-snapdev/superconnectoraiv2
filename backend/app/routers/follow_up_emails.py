from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from app.models.follow_up_email import (
    FollowUpEmailCreate, 
    FollowUpEmailInDB, 
    FollowUpStatus,
    FollowUpEmailUpdate
)
from app.models.user import UserInDB
from app.services.auth_service import get_current_user
from app.services.follow_up_email_service import (
    schedule_follow_up_email,
    get_pending_follow_ups,
    send_follow_up_email,
    cancel_follow_up_email,
    get_follow_ups_by_warm_intro,
    get_follow_up_stats,
    process_pending_follow_ups,
    process_automated_follow_ups
)
from app.services.scheduler_service import get_scheduler_status, trigger_manual_follow_up_processing
from app.core.db import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/follow-up-emails", tags=["follow-up-emails"])

@router.post("/schedule", response_model=dict)
async def schedule_follow_up(
    follow_up_data: FollowUpEmailCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Schedule a follow-up email for a warm intro request"""
    try:
        # Only admin users can schedule follow-up emails
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can schedule follow-up emails"
            )
        
        result = await schedule_follow_up_email(
            db=db,
            warm_intro_request_id=follow_up_data.warm_intro_request_id,
            requester_email=follow_up_data.requester_email,
            requester_name=follow_up_data.requester_name,
            connection_name=follow_up_data.connection_name,
            facilitator_email=follow_up_data.facilitator_email,
            follow_up_days=follow_up_data.follow_up_days
        )
        
        return {
            "message": "Follow-up email scheduled successfully",
            "follow_up_id": result["id"],
            "scheduled_date": result["scheduled_date"]
        }
        
    except Exception as e:
        logger.error(f"Error scheduling follow-up email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule follow-up email: {str(e)}"
        )

@router.get("/pending", response_model=List[dict])
async def get_pending_follow_up_emails(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all pending follow-up emails"""
    try:
        # Only admin users can view pending follow-up emails
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can view pending follow-up emails"
            )
        
        pending_emails = await get_pending_follow_ups(db)
        return pending_emails
        
    except Exception as e:
        logger.error(f"Error getting pending follow-up emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending follow-up emails: {str(e)}"
        )

@router.post("/send/{follow_up_id}")
async def send_follow_up(
    follow_up_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Manually send a follow-up email"""
    try:
        # Only admin users can manually send follow-up emails
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can send follow-up emails"
            )
        
        success = await send_follow_up_email(db, follow_up_id)
        
        if success:
            return {"message": "Follow-up email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send follow-up email"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending follow-up email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send follow-up email: {str(e)}"
        )

@router.post("/cancel/{follow_up_id}")
async def cancel_follow_up(
    follow_up_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Cancel a scheduled follow-up email"""
    try:
        # Only admin users can cancel follow-up emails
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can cancel follow-up emails"
            )
        
        success = await cancel_follow_up_email(db, follow_up_id)
        
        if success:
            return {"message": "Follow-up email cancelled successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Follow-up email not found or already processed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling follow-up email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel follow-up email: {str(e)}"
        )

@router.get("/warm-intro/{warm_intro_id}", response_model=List[dict])
async def get_follow_ups_for_warm_intro(
    warm_intro_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all follow-up emails for a specific warm intro request"""
    try:
        # Users can view follow-ups for their own warm intro requests
        # Admins can view all follow-ups
        follow_ups = await get_follow_ups_by_warm_intro(db, warm_intro_id)
        
        # If not admin, filter to only show follow-ups for the current user's requests
        if current_user.role != "admin":
            # In a real implementation, you'd verify the warm intro belongs to the current user
            # For now, we'll allow all authenticated users to view
            pass
        
        return follow_ups
        
    except Exception as e:
        logger.error(f"Error getting follow-ups for warm intro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get follow-ups for warm intro: {str(e)}"
        )

@router.get("/stats", response_model=dict)
async def get_follow_up_email_stats(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get statistics about follow-up emails"""
    try:
        # Only admin users can view follow-up email stats
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can view follow-up email statistics"
            )
        
        stats = await get_follow_up_stats(db)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting follow-up email stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get follow-up email statistics: {str(e)}"
        )

@router.post("/process-pending")
async def process_pending_follow_up_emails(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger processing of pending follow-up emails"""
    try:
        # Only admin users can trigger follow-up email processing
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can trigger follow-up email processing"
            )
        
        # Add the processing task to background tasks
        background_tasks.add_task(process_pending_follow_ups)
        
        return {"message": "Follow-up email processing started in background"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering follow-up email processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger follow-up email processing: {str(e)}"
        )

@router.get("/", response_model=List[dict])
async def get_all_follow_up_emails(
    status_filter: Optional[FollowUpStatus] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all follow-up emails with optional filtering"""
    try:
        # Only admin users can view all follow-up emails
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can view all follow-up emails"
            )
        
        # Build query
        query = {}
        if status_filter:
            query["status"] = status_filter.value
        
        # Get follow-up emails with pagination
        cursor = db.follow_up_emails.find(query).skip(offset).limit(limit)
        follow_ups = await cursor.to_list(length=None)
        
        return follow_ups
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting follow-up emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get follow-up emails: {str(e)}"
        )

@router.get("/scheduler/status")
async def get_follow_up_scheduler_status(
    current_user: dict = Depends(get_current_user)
):
    """Get the status of the follow-up email scheduler"""
    try:
        # Only admin users can view scheduler status
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can view scheduler status"
            )
        
        status_info = await get_scheduler_status()
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )

@router.post("/process-all")
async def manually_process_all_follow_ups(
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger processing of all follow-up emails (both legacy and automated)"""
    try:
        # Only admin users can trigger manual processing
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can trigger manual follow-up processing"
            )
        
        result = await trigger_manual_follow_up_processing()
        
        if result["success"]:
            return {
                "message": "Follow-up processing completed successfully",
                "legacy_processed": result["legacy_processed"],
                "automated_processed": result["automated_processed"],
                "total_processed": result["total_processed"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Follow-up processing failed: {result['error']}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual follow-up processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger manual processing: {str(e)}"
        )

@router.post("/process-automated")
async def manually_process_automated_follow_ups(
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger processing of automated follow-up emails only"""
    try:
        # Only admin users can trigger manual processing
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can trigger automated follow-up processing"
            )
        
        processed_count = await process_automated_follow_ups()
        
        return {
            "message": "Automated follow-up processing completed successfully",
            "processed_count": processed_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering automated follow-up processing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger automated processing: {str(e)}"
        )