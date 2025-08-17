from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class WarmIntroStatus(str, Enum):
    pending = "pending"
    connected = "connected"
    declined = "declined"

class WarmIntroRequestBase(BaseModel):
    requester_name: str
    connection_name: str
    requester_first_name: Optional[str] = None
    requester_last_name: Optional[str] = None
    connection_first_name: Optional[str] = None
    connection_last_name: Optional[str] = None
    status: WarmIntroStatus = WarmIntroStatus.pending

class WarmIntroRequest(WarmIntroRequestBase):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    connected_date: Optional[datetime] = None
    declined_date: Optional[datetime] = None

    class Config:
        # Allow the model to be serialized with aliases
        populate_by_name = True
        # Use enum values when serializing
        use_enum_values = True

class WarmIntroRequestPublic(WarmIntroRequestBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    connected_date: Optional[datetime] = None
    declined_date: Optional[datetime] = None

class WarmIntroRequestCreate(BaseModel):
    requester_name: str
    connection_name: str
    requester_first_name: Optional[str] = None
    requester_last_name: Optional[str] = None
    connection_first_name: Optional[str] = None
    connection_last_name: Optional[str] = None
    status: WarmIntroStatus = WarmIntroStatus.pending

class WarmIntroRequestUpdate(BaseModel):
    status: WarmIntroStatus
    connected_date: Optional[datetime] = None
    declined_date: Optional[datetime] = None