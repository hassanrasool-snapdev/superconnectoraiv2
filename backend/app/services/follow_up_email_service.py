from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
import logging
from uuid import UUID
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.models.follow_up_email import (
    FollowUpEmailCreate,
    FollowUpEmailInDB,
    FollowUpStatus,
    FollowUpEmailUpdate
)
from app.models.warm_intro_request import WarmIntroStatus, WarmIntroRequest
from app.models.user import UserInDB
from app.core.db import get_database
from app.core.config import settings
import time
import random

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

# New functions for automated follow-up emails based on warm intro requests

async def get_eligible_warm_intro_requests(db) -> List[dict]:
    """Get warm intro requests that are eligible for follow-up emails (older than 14 days, no follow-up sent yet)"""
    cutoff_date = datetime.utcnow() - timedelta(days=14)
    
    cursor = db.warm_intro_requests.find({
        "created_at": {"$lte": cutoff_date},
        "follow_up_sent_date": None,
        "status": WarmIntroStatus.pending.value
    })
    
    return await cursor.to_list(length=None)

async def send_automated_follow_up_email(db, warm_intro_request: dict) -> bool:
    """Send an automated follow-up email for a warm intro request"""
    try:
        # Get user email
        user = await db.users.find_one({"id": warm_intro_request["user_id"]})
        if not user:
            logger.error(f"User not found for warm intro request {warm_intro_request['id']}")
            return False
        
        user_email = user["email"]
        
        # Generate email content
        email_content = generate_automated_follow_up_content(
            warm_intro_request["requester_name"],
            warm_intro_request["connection_name"],
            warm_intro_request["id"]
        )
        
        # Send email
        success = await send_email_via_sendgrid(
            to_email=user_email,
            subject="Following up on your introduction request",
            html_content=email_content
        )
        
        if success:
            # Update the warm intro request with follow-up sent date
            await db.warm_intro_requests.update_one(
                {"id": warm_intro_request["id"]},
                {
                    "$set": {
                        "follow_up_sent_date": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Automated follow-up email sent for warm intro request {warm_intro_request['id']}")
            return True
        else:
            logger.error(f"Failed to send automated follow-up email for warm intro request {warm_intro_request['id']}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending automated follow-up email for warm intro request {warm_intro_request['id']}: {str(e)}")
        return False

def generate_automated_follow_up_content(requester_name: str, connection_name: str, request_id: str) -> str:
    """Generate the automated follow-up email content"""
    yes_link = f"{settings.FRONTEND_URL}/warm-intro-response?request_id={request_id}&response=yes"
    no_link = f"{settings.FRONTEND_URL}/warm-intro-response?request_id={request_id}&response=no"
    donate_link = f"{settings.FRONTEND_URL}/donate"
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">Following up on your introduction request</h2>
            
            <p>Hi there,</p>
            
            <p>Just checking in on your warm intro request to connect with <strong>{connection_name}</strong>. Were you able to connect?</p>
            
            <div style="margin: 30px 0; text-align: center;">
                <a href="{yes_link}" style="background-color: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-right: 10px; display: inline-block;">Yes, we connected</a>
                <a href="{no_link}" style="background-color: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">No, not yet</a>
            </div>
            
            <p>If you need any further support with your networking goals, please don't hesitate to reach out.</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 30px 0; text-align: center;">
                <p style="margin-bottom: 15px;"><strong>Help keep Superconnector AI alive!</strong></p>
                <p style="margin-bottom: 15px;">If you found this service helpful, please consider making a donation to support our work.</p>
                <a href="{donate_link}" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Make a Donation</a>
            </div>
            
            <p>Thanks,<br>
            The Superconnector Team</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="font-size: 12px; color: #666;">
                This is an automated follow-up email from Superconnector AI.<br>
                If you no longer wish to receive these emails, please contact support.
            </p>
        </div>
    </body>
    </html>
    """

async def send_email_via_sendgrid(to_email: str, subject: str, html_content: str, max_retries: int = 3) -> bool:
    """Send email using SendGrid API with retry logic"""
    
    if not settings.SENDGRID_API_KEY:
        logger.warning("SendGrid API key not configured, simulating email send")
        return await simulate_email_send(to_email, subject, html_content)
    
    for attempt in range(max_retries):
        try:
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            
            from_email = Email(settings.FROM_EMAIL, settings.FROM_NAME)
            to_email_obj = To(to_email)
            content = Content("text/html", html_content)
            
            mail = Mail(from_email, to_email_obj, subject, content)
            
            response = sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email} on attempt {attempt + 1}")
                return True
            elif response.status_code == 429:  # Rate limit
                wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                logger.warning(f"Rate limited sending email to {to_email}, waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}")
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.error(f"Failed to send email to {to_email}. Status code: {response.status_code}, Response: {response.body}")
                if attempt == max_retries - 1:  # Last attempt
                    return False
                await asyncio.sleep(1)  # Brief pause before retry
                
        except Exception as e:
            logger.error(f"Error sending email via SendGrid to {to_email} (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:  # Last attempt
                return False
            
            # Exponential backoff for retries
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(wait_time)
    
    return False

async def process_automated_follow_ups() -> int:
    """Process all eligible warm intro requests for automated follow-up emails"""
    try:
        db = get_database()
        eligible_requests = await get_eligible_warm_intro_requests(db)
        
        logger.info(f"Processing {len(eligible_requests)} eligible warm intro requests for follow-up")
        
        sent_count = 0
        failed_count = 0
        
        # Process requests in batches to avoid overwhelming the email service
        batch_size = 10
        for i in range(0, len(eligible_requests), batch_size):
            batch = eligible_requests[i:i + batch_size]
            
            # Process batch with some delay between emails
            for request in batch:
                try:
                    success = await send_automated_follow_up_email(db, request)
                    if success:
                        sent_count += 1
                        logger.info(f"Successfully sent follow-up email for request {request['id']}")
                    else:
                        failed_count += 1
                        logger.warning(f"Failed to send follow-up email for request {request['id']}")
                    
                    # Small delay between emails to be respectful to email service
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error processing follow-up for request {request['id']}: {str(e)}")
            
            # Longer delay between batches
            if i + batch_size < len(eligible_requests):
                logger.info(f"Processed batch {i//batch_size + 1}, waiting before next batch...")
                await asyncio.sleep(2)
        
        logger.info(f"Follow-up processing complete: {sent_count} sent, {failed_count} failed")
        return sent_count
        
    except Exception as e:
        logger.error(f"Error processing automated follow-ups: {str(e)}")
        return 0

async def record_user_response(db, request_id: str, connected: bool) -> dict:
    """Record user response to follow-up email with enhanced validation"""
    try:
        # First, check if the request exists and hasn't already been responded to
        existing_request = await db.warm_intro_requests.find_one({"id": request_id})
        
        if not existing_request:
            logger.warning(f"Warm intro request {request_id} not found")
            return {"success": False, "error": "request_not_found", "message": "Warm intro request not found"}
        
        # Check if user has already responded
        if existing_request.get("user_responded", False):
            logger.info(f"User has already responded to request {request_id}")
            return {
                "success": False,
                "error": "already_responded",
                "message": "You have already responded to this follow-up email",
                "previous_response": {
                    "connected": existing_request.get("status") == WarmIntroStatus.connected.value,
                    "response_date": existing_request.get("response_date")
                }
            }
        
        update_data = {
            "user_responded": True,
            "response_date": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if connected:
            update_data["status"] = WarmIntroStatus.connected.value
            update_data["connected_date"] = datetime.utcnow()
        else:
            # If they said no, we might want to keep status as pending
            # or create a new status for "no connection yet"
            pass
        
        result = await db.warm_intro_requests.update_one(
            {"id": request_id, "user_responded": {"$ne": True}},  # Only update if not already responded
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            logger.info(f"Recorded user response for warm intro request {request_id}: connected={connected}")
            
            # Log analytics data for tracking
            await log_follow_up_response(db, request_id, connected)
            
            return {"success": True, "message": "Response recorded successfully", "connected": connected}
        else:
            logger.warning(f"Warm intro request {request_id} not found or user already responded")
            return {"success": False, "error": "update_failed", "message": "Failed to update request - it may have been already responded to"}
            
    except Exception as e:
        logger.error(f"Error recording user response for request {request_id}: {str(e)}")
        return {"success": False, "error": "internal_error", "message": f"Internal server error: {str(e)}"}

async def log_follow_up_response(db, request_id: str, connected: bool):
    """Log follow-up response for analytics"""
    try:
        analytics_data = {
            "event_type": "follow_up_response",
            "request_id": request_id,
            "connected": connected,
            "timestamp": datetime.utcnow(),
            "source": "email_follow_up"
        }
        
        # Insert into analytics collection (create if doesn't exist)
        await db.follow_up_analytics.insert_one(analytics_data)
        logger.debug(f"Logged follow-up response analytics for request {request_id}")
        
    except Exception as e:
        logger.error(f"Error logging follow-up response analytics: {str(e)}")
        # Don't fail the main operation if analytics logging fails