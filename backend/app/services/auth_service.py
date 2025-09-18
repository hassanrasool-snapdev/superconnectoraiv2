from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from datetime import datetime
from app.core.db import get_database
from app.core.config import settings
from app.core import security
from app.models.user import UserCreate, UserInDB, TokenData, UserRole, UserStatus
from app.services import invitation_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_user_by_email(db, email: str):
    return await db.users.find_one({"email": email})

async def create_user(db, user: UserCreate):
    # Validate invitation if provided
    invitation_id = None
    if user.invitation_code:
        invitation = await invitation_service.get_invitation_by_code(db, user.invitation_code)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid invitation code"
            )
        
        if invitation["email"] != user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation email does not match registration email"
            )
        
        # Accept the invitation
        await invitation_service.accept_invitation(db, user.invitation_code)
        invitation_id = invitation["id"]
    else:
        # Check if user is authorized without invitation (for admin bootstrap)
        is_authorized = await invitation_service.is_user_authorized(db, user.email)
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Registration requires a valid invitation"
            )
    
    hashed_password = security.get_password_hash(user.password)
    user_in_db = UserInDB(
        email=user.email,
        hashed_password=hashed_password,
        invitation_id=invitation_id
    )
    
    # Pydantic models must be converted to dicts to be stored in MongoDB
    user_dict = user_in_db.model_dump()
    # Convert UUID to string for MongoDB compatibility
    user_dict["id"] = str(user_dict["id"])
    if user_dict["invitation_id"]:
        user_dict["invitation_id"] = str(user_dict["invitation_id"])
    
    await db.users.insert_one(user_dict)
    return user_dict

async def authenticate_user(db, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not security.verify_password(password, user["hashed_password"]):
        return None
    
    # Check if user is still authorized
    if user.get("status") != UserStatus.active.value:
        return None
    
    # Update last login
    await db.users.update_one(
        {"email": email},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user