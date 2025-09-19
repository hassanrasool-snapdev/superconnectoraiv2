from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class AccessRequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class AccessRequestBase(BaseModel):
    email: EmailStr
    full_name: str
    reason: Optional[str] = None  # Why they need access
    organization: Optional[str] = None

class AccessRequestCreate(AccessRequestBase):
    pass

class AccessRequestInDB(AccessRequestBase):
    id: UUID = Field(default_factory=uuid4)
    status: AccessRequestStatus = AccessRequestStatus.pending
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    processed_by: Optional[UUID] = None  # Admin who processed the request
    admin_notes: Optional[str] = None

class AccessRequestPublic(AccessRequestBase):
    id: UUID
    status: AccessRequestStatus
    created_at: datetime
    processed_at: Optional[datetime] = None

class AccessRequestUpdate(BaseModel):
    status: Optional[AccessRequestStatus] = None
    admin_notes: Optional[str] = None