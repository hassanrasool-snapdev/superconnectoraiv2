from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

class FavoriteConnectionBase(BaseModel):
    connection_id: str

class FavoriteConnectionCreate(FavoriteConnectionBase):
    pass

class FavoriteConnectionInDB(FavoriteConnectionBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    favorited_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)

class FavoriteConnectionPublic(BaseModel):
    favorite_id: str
    favorited_at: datetime
    connection: dict

    model_config = ConfigDict(from_attributes=True)