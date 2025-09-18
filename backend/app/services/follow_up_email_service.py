from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
import logging
from app.models.follow_up_email import (
    FollowUpEmailCreate, 
    FollowUpEmailInDB, 
    FollowUpStatus, 
    FollowUpEmailUpdate
)
from app.models.warm_intro_request import WarmIntroStatus
from app.core.db import get_database

logger = logging.getLogger(__name__)

async def schedule_follow_up_email(
    db, 
    warm_intro_request_id: str,
    requester_email: str,
    requester_name: str,
    connection_name: str,
    facilitator_email: str,
    follow_up_days: int = 14
) -> dict:
    """Schedule a follow-up email for a warm intro request"""
    
    # Calculate scheduled date
    scheduled_date = datetime.utcnow() + timedelta(days=follow_up_days)
    
    # Create follow-up email record
    follow_up_email = FollowUpEmailInDB(
        warm_intro_request_id=warm_intro_request_id,
        requester_email=requester_email,
        requester_name=requester_name,
        connection_name=connection_name,
        facilitator_email=facilitator_email,
        scheduled_date=scheduled_date,
        follow_up_days=follow_up_days
    )
    
    # Convert to dict for MongoDB
    follow_up_dict = follow_up_email.model_dump()
    follow_up_dict["id"] = str(follow_up_dict["id"])
    follow_up_dict["warm_intro_request_id"] = str(follow_up_dict["warm_intro_request_id"])
    
    await db.follow_up_emails.insert_one(follow_up_dict)
    
    logger.info(f"Scheduled follow-up email for warm intro {warm_intro_request_id} on {scheduled_date}")
    return follow_up_dict

async def get_pending_follow_ups(db) -> List[dict]:
    """Get all follow-up emails that are due to be sent"""
    current_time = datetime.utcnow()
    
    cursor = db.follow_up_emails.find({
        "status": FollowUpStatus.scheduled.value,
        "scheduled_date": {"$lte": current_time}
    })
    
    return await cursor.to_list(length=None)

async def send_follow_up_email(db, follow_up_id: str) -> bool:
    """Send a follow-up email and update its status"""
    try:
        # Get the follow-up email record
        follow_up = await db.follow_up_emails.find_one({"id": follow_up_id})
        if not follow_up:
            logger.error(f"Follow-up email {follow_up_id} not found")
            return False
        
        # Generate email content
        email_content = generate_follow_up_email_content(
            follow_up["requester_name"],
            follow_up["connection_name"],
            follow_up["facilitator_email"]
        )
        
        # In a real implementation, you would send the email here
        # For now, we'll simulate sending the email
        success = await simulate_email_send(
            to_email=follow_up["requester_email"],
            subject=f"Follow-up: Connection with {follow_up['connection_name']}",
            content=email_content
        )
        
        if success:
            # Update status to sent
            update = FollowUpEmailUpdate(
                status=FollowUpStatus.sent,
                sent_at=datetime.utcnow()
            )
            
            await db.follow_up_emails.update_one(
                {"id": follow_up_id},
                {"$set": update.model_dump(exclude_unset=True)}
            )
            
            logger.info(f"Follow-up email {follow_up_id} sent successfully")
            return True
        else:
            # Update status to failed
            update = FollowUpEmailUpdate(
                status=FollowUpStatus.failed,
                error_message="Failed to send email"
            )
            
            await db.follow_up_emails.update_one(
                {"id": follow_up_id},
                {"$set": update.model_dump(exclude_unset=True)}
            )
            
            logger.error(f"Failed to send follow-up email {follow_up_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending follow-up email {follow_up_id}: {str(e)}")
        
        # Update status to failed with error message
        update = FollowUpEmailUpdate(
            status=FollowUpStatus.failed,
            error_message=str(e)
        )
        
        await db.follow_up_emails.update_one(
            {"id": follow_up_id},
            {"$set": update.model_dump(exclude_unset=True)}
        )
        
        return False

def generate_follow_up_email_content(requester_name: str, connection_name: str, facilitator_name: str) -> str:
    """Generate the follow-up email content as specified in the PRD"""
    return f"""Hi {requester_name},

I just wanted to check in with you to make sure you were able to make the connection with {connection_name} that you requested and if there is anything further you need. Please let me know.

Thank you,
{facilitator_name}

P.S. Help keep Superconnect AI alive. Most people choose to contribute $20. It helps keep the lights on and the warm intros coming.

[Contribute Now - $20] [Other Amount] [No Thanks]

---
This is an automated follow-up email from Superconnect AI.
If you no longer wish to receive these emails, please reply with "UNSUBSCRIBE".
"""

async def simulate_email_send(to_email: str, subject: str, content: str) -> bool:
    """Simulate sending an email - in production, integrate with actual email service"""
    try:
        # Simulate email sending delay
        await asyncio.sleep(0.1)
        
        # Log the email (in production, you'd use a real email service like SendGrid, AWS SES, etc.)
        logger.info(f"SIMULATED EMAIL SENT:")
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Content: {content[:100]}...")
        
        # Simulate 95% success rate
        import random
        return random.random() < 0.95
        
    except Exception as e:
        logger.error(f"Error simulating email send: {str(e)}")
        return False

async def process_pending_follow_ups():
    """Background task to process pending follow-up emails"""
    try:
        from app.core.db import get_database
        db = get_database()
        pending_follow_ups = await get_pending_follow_ups(db)
        
        logger.info(f"Processing {len(pending_follow_ups)} pending follow-up emails")
        
        for follow_up in pending_follow_ups:
            success = await send_follow_up_email(db, follow_up["id"])
            if success:
                logger.info(f"Successfully sent follow-up email {follow_up['id']}")
            else:
                logger.error(f"Failed to send follow-up email {follow_up['id']}")
                
        return len(pending_follow_ups)
        
    except Exception as e:
        logger.error(f"Error processing pending follow-ups: {str(e)}")
        return 0

async def cancel_follow_up_email(db, follow_up_id: str) -> bool:
    """Cancel a scheduled follow-up email"""
    try:
        update = FollowUpEmailUpdate(status=FollowUpStatus.cancelled)
        
        result = await db.follow_up_emails.update_one(
            {"id": follow_up_id, "status": FollowUpStatus.scheduled.value},
            {"$set": update.model_dump(exclude_unset=True)}
        )
        
        if result.matched_count > 0:
            logger.info(f"Cancelled follow-up email {follow_up_id}")
            return True
        else:
            logger.warning(f"Follow-up email {follow_up_id} not found or already processed")
            return False
            
    except Exception as e:
        logger.error(f"Error cancelling follow-up email {follow_up_id}: {str(e)}")
        return False

async def get_follow_ups_by_warm_intro(db, warm_intro_request_id: str) -> List[dict]:
    """Get all follow-up emails for a specific warm intro request"""
    cursor = db.follow_up_emails.find({"warm_intro_request_id": warm_intro_request_id})
    return await cursor.to_list(length=None)

async def get_follow_up_stats(db) -> dict:
    """Get statistics about follow-up emails"""
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    
    cursor = db.follow_up_emails.aggregate(pipeline)
    stats = await cursor.to_list(length=None)
    
    # Convert to a more readable format
    stats_dict = {stat["_id"]: stat["count"] for stat in stats}
    
    return {
        "scheduled": stats_dict.get(FollowUpStatus.scheduled.value, 0),
        "sent": stats_dict.get(FollowUpStatus.sent.value, 0),
        "failed": stats_dict.get(FollowUpStatus.failed.value, 0),
        "cancelled": stats_dict.get(FollowUpStatus.cancelled.value, 0),
        "total": sum(stats_dict.values())
    }