from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class GeneratedEmailBase(BaseModel):
    connection_id: UUID
    reason_for_connecting: str
    generated_content: str

class GeneratedEmailInDB(GeneratedEmailBase):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GeneratedEmailPublic(GeneratedEmailBase):
    id: UUID
    created_at: datetime