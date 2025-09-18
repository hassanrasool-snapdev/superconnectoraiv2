from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class FollowUpStatus(str, Enum):
    scheduled = "scheduled"
    sent = "sent"
    failed = "failed"
    cancelled = "cancelled"

class FollowUpEmailBase(BaseModel):
    warm_intro_request_id: UUID
    requester_email: EmailStr
    requester_name: str
    connection_name: str
    facilitator_email: EmailStr
    scheduled_date: datetime
    follow_up_days: int = 14  # Default to 2 weeks

class FollowUpEmailCreate(FollowUpEmailBase):
    pass

class FollowUpEmailInDB(FollowUpEmailBase):
    id: UUID = Field(default_factory=uuid4)
    status: FollowUpStatus = FollowUpStatus.scheduled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

class FollowUpEmailPublic(FollowUpEmailBase):
    id: UUID
    status: FollowUpStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

class FollowUpEmailUpdate(BaseModel):
    status: FollowUpStatus
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None