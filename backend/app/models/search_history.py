from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class SearchHistoryBase(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    results_count: int

class SearchHistoryCreate(SearchHistoryBase):
    pass

class SearchHistoryInDB(SearchHistoryBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    searched_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)

class SearchHistoryPublic(SearchHistoryBase):
    id: str
    searched_at: datetime

    model_config = ConfigDict(from_attributes=True)