from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    invitation_code: Optional[str] = None  # Required for registration

class UserInDB(UserBase):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    role: UserRole = UserRole.user
    status: UserStatus = UserStatus.active
    is_premium: bool = False  # Premium membership status
    invitation_id: Optional[UUID] = None  # Link to the invitation used
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class UserPublic(UserBase):
    id: UUID
    role: UserRole
    status: UserStatus
    is_premium: bool = False  # Premium membership status
    created_at: datetime
    last_login: Optional[datetime] = None

class UserUpdate(BaseModel):
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_premium: Optional[bool] = None  # Allow updating premium status
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None