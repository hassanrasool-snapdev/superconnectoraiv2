import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.services.follow_up_email_service import process_pending_follow_ups
from app.core.db import get_database

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.check_interval = 3600  # Check every hour (3600 seconds)
    
    async def start(self):
        """Start the scheduler service"""
        if self.running:
            logger.warning("Scheduler service is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._scheduler_loop())
        logger.info("Scheduler service started")
    
    async def stop(self):
        """Stop the scheduler service"""
        if not self.running:
            logger.warning("Scheduler service is not running")
            return
        
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Scheduler service stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop that runs background tasks"""
        logger.info(f"Scheduler loop started, checking every {self.check_interval} seconds")
        
        while self.running:
            try:
                # Process pending follow-up emails
                await self._process_follow_up_emails()
                
                # Wait for the next check interval
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                logger.info("Scheduler loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                # Wait a bit before retrying to avoid rapid error loops
                await asyncio.sleep(60)
    
    async def _process_follow_up_emails(self):
        """Process pending follow-up emails"""
        try:
            processed_count = await process_pending_follow_ups()
            if processed_count > 0:
                logger.info(f"Processed {processed_count} follow-up emails")
        except Exception as e:
            logger.error(f"Error processing follow-up emails: {str(e)}")
    
    def set_check_interval(self, seconds: int):
        """Set the check interval in seconds"""
        if seconds < 60:  # Minimum 1 minute
            raise ValueError("Check interval must be at least 60 seconds")
        
        self.check_interval = seconds
        logger.info(f"Check interval updated to {seconds} seconds")

# Global scheduler instance
scheduler_service = SchedulerService()

async def start_scheduler():
    """Start the global scheduler service"""
    await scheduler_service.start()

async def stop_scheduler():
    """Stop the global scheduler service"""
    await scheduler_service.stop()

async def get_scheduler_status():
    """Get the current status of the scheduler"""
    return {
        "running": scheduler_service.running,
        "check_interval": scheduler_service.check_interval,
        "next_check": datetime.utcnow() + timedelta(seconds=scheduler_service.check_interval) if scheduler_service.running else None
    }