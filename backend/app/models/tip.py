from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class TipBase(BaseModel):
    connection_id: str
    amount: float
    message: Optional[str] = None

class TipCreate(TipBase):
    pass

class TipInDB(TipBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    transaction_id: Optional[str] = None # For Venmo transaction ID

    model_config = ConfigDict(populate_by_name=True)

class TipPublic(TipBase):
    id: str
    created_at: datetime
    transaction_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)