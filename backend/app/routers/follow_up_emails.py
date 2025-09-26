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
    process_manual_follow_ups
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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
        if current_user.get("role") != "admin":
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

@router.get("/admin/candidates", response_model=List[dict])
async def get_follow_up_candidates(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get warm intro requests that are eligible for follow-up emails (14+ days old)"""
    try:
        # Only admin users can view follow-up candidates
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can view follow-up candidates"
            )
        
        from app.services.follow_up_email_service import get_eligible_warm_intro_requests
        candidates = await get_eligible_warm_intro_requests(db)
        
        # Enrich with user information
        enriched_candidates = []
        for candidate in candidates:
            # Handle both field naming conventions
            user_id = candidate.get("user_id") or candidate.get("requester_id")
            
            if user_id:
                # Get user email - handle both _id and id field naming
                user = await db.users.find_one({"$or": [{"_id": user_id}, {"id": user_id}]})
                if user:
                    candidate["user_email"] = user["email"]
                    candidate["days_old"] = (datetime.utcnow() - candidate["created_at"]).days
                    
                    # Convert ObjectId to string for serialization
                    if "_id" in candidate:
                        candidate["_id"] = str(candidate["_id"])
                    
                    enriched_candidates.append(candidate)
                else:
                    logger.warning(f"User not found for candidate with user_id: {user_id}")
            else:
                logger.warning(f"No valid user_id found in candidate: {candidate}")
        
        return enriched_candidates
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting follow-up candidates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get follow-up candidates: {str(e)}"
        )

@router.post("/admin/send/{request_id}")
async def send_individual_follow_up(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Generate and provide follow-up email content for manual sending via email client"""
    try:
        # Only admin users can send follow-up emails
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can send follow-up emails"
            )
        
        from app.services.follow_up_email_service import generate_automated_follow_up_content
        
        # Get the warm intro request
        request = await db.warm_intro_requests.find_one({"id": request_id})
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warm intro request not found"
            )
        
        # Handle both field naming conventions
        user_id = request.get("user_id") or request.get("requester_id")
        request_id = request.get("id") or request.get("_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User ID not found in request"
            )
        
        # Get user email - handle both _id and id field naming
        user = await db.users.find_one({"$or": [{"_id": user_id}, {"id": user_id}]})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate email content with response links
        email_content = generate_automated_follow_up_content(
            request["requester_name"],
            request.get("connection_name") or request.get("target_name"),
            request_id
        )
        
        # Create simple plain text email with URLs formatted for better email client recognition
        # Generate donation URL
        donate_url = "http://localhost:3000/donate"
        
        # Generate response URLs
        yes_url = f"http://localhost:3000/warm-intro-response-demo?response=yes&request_id={request_id}"
        no_url = f"http://localhost:3000/warm-intro-response-demo?response=no&request_id={request_id}"
        
        # Create plain text email body with URLs formatted for maximum clickability
        plain_text_body = f"""Hello {request["requester_name"]},

Just checking in on your warm intro request to connect with {request.get("connection_name") or request.get("target_name")}. Were you able to connect?

Please reply to this email to let us know how the connection went. Your feedback helps us improve our service and track the success of our warm introductions.

If you need any further support with your networking goals, please don't hesitate to reach out.

Help keep Superconnector AI alive! If you found this service helpful, please consider making a donation:
{donate_url}

Thanks,
The Superconnector Team

This is an automated follow-up email from Superconnector AI.
If you no longer wish to receive these emails, please contact support."""
        
        # Mark as follow-up sent (admin handles actual sending via email client)
        await db.warm_intro_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "follow_up_sent_date": datetime.utcnow(),
                    "follow_up_sent_by": current_user["id"],
                    "follow_up_method": "manual",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Manual follow-up email marked as sent for warm intro request {request_id}")
        
        # Return in the same format as access requests
        return {
            "message": "Follow-up email ready for sending",
            "email_template": {
                "to": user["email"],
                "subject": "Following up on your introduction request",
                "body": plain_text_body
            }
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating follow-up email content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate follow-up email content: {str(e)}"
        )

@router.get("/admin/preview/{request_id}")
async def preview_follow_up_email(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Preview the follow-up email content for a specific warm intro request"""
    try:
        # Only admin users can preview follow-up emails
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can preview follow-up emails"
            )
        
        from app.services.follow_up_email_service import generate_automated_follow_up_content
        
        # Get the warm intro request
        request = await db.warm_intro_requests.find_one({"id": request_id})
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warm intro request not found"
            )
        
        # Handle both field naming conventions
        user_id = request.get("user_id") or request.get("requester_id")
        request_id = request.get("id") or request.get("_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User ID not found in request"
            )
        
        # Get user email - handle both _id and id field naming
        user = await db.users.find_one({"$or": [{"_id": user_id}, {"id": user_id}]})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate email content
        email_content = generate_automated_follow_up_content(
            request["requester_name"],
            request.get("connection_name") or request.get("target_name"),
            request_id
        )
        
        return {
            "to_email": user["email"],
            "subject": "Following up on your introduction request",
            "html_content": email_content,
            "request_id": request_id,
            "requester_name": request["requester_name"],
            "connection_name": request["connection_name"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing follow-up email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview follow-up email: {str(e)}"
        )

@router.post("/admin/skip/{request_id}")
async def skip_follow_up_email(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Mark a warm intro request as skipped for follow-up"""
    try:
        # Only admin users can skip follow-up emails
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can skip follow-up emails"
            )
        
        # Update the request to mark it as skipped
        result = await db.warm_intro_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "follow_up_skipped": True,
                    "follow_up_skipped_date": datetime.utcnow(),
                    "follow_up_skipped_by": current_user["id"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return {
                "message": "Follow-up email skipped successfully",
                "request_id": request_id,
                "skipped_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warm intro request not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error skipping follow-up email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to skip follow-up email: {str(e)}"
        )

@router.get("/pending/count", response_model=int)
async def get_pending_follow_up_emails_count(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get count of pending follow-up emails (scheduled status)"""
    try:
        # Only admin users can view pending follow-up email counts
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can view pending follow-up email counts"
            )
        
        # Count follow-up emails with "scheduled" status (which is pending)
        count = await db.follow_up_emails.count_documents({"status": "scheduled"})
        return count
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending follow-up emails count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending follow-up emails count: {str(e)}"
        )