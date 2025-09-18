from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class InvitationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    revoked = "revoked"

class InvitationBase(BaseModel):
    email: EmailStr
    invited_by: str  # Email of the person who sent the invitation
    message: Optional[str] = None
    expires_at: datetime

class InvitationCreate(InvitationBase):
    pass

class InvitationInDB(InvitationBase):
    id: UUID = Field(default_factory=uuid4)
    status: InvitationStatus = InvitationStatus.pending
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None

class InvitationPublic(InvitationBase):
    id: UUID
    status: InvitationStatus
    created_at: datetime
    accepted_at: Optional[datetime] = None

class InvitationUpdate(BaseModel):
    status: InvitationStatus
    accepted_at: Optional[datetime] = None