from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from app.models.access_request import (
    AccessRequestCreate, 
    AccessRequestPublic, 
    AccessRequestUpdate,
    AccessRequestStatus
)
from app.models.user import UserWithOTP
from app.core.db import get_database
from app.services import access_request_service, auth_service

router = APIRouter()

@router.post("/access-requests", response_model=AccessRequestPublic, status_code=status.HTTP_201_CREATED)
async def submit_access_request(request_data: AccessRequestCreate, db=Depends(get_database)):
    """Public endpoint for users to request access to the system"""
    request_dict = await access_request_service.create_access_request(db, request_data)
    return AccessRequestPublic(**request_dict)

@router.get("/admin/access-requests", response_model=List[AccessRequestPublic])
async def get_access_requests(
    status_filter: Optional[AccessRequestStatus] = Query(None, description="Filter by status"),
    db=Depends(get_database),
    current_admin: dict = Depends(auth_service.get_current_admin_user)
):
    """Admin endpoint to view all access requests"""
    requests = await access_request_service.get_access_requests(db, status_filter)
    return [AccessRequestPublic(**req) for req in requests]

@router.get("/admin/access-requests/{request_id}", response_model=AccessRequestPublic)
async def get_access_request(
    request_id: str,
    db=Depends(get_database),
    current_admin: dict = Depends(auth_service.get_current_admin_user)
):
    """Admin endpoint to view a specific access request"""
    request = await access_request_service.get_access_request_by_id(db, request_id)
    return AccessRequestPublic(**request)

@router.patch("/admin/access-requests/{request_id}", response_model=AccessRequestPublic)
async def update_access_request(
    request_id: str,
    update_data: AccessRequestUpdate,
    db=Depends(get_database),
    current_admin: dict = Depends(auth_service.get_current_admin_user)
):
    """Admin endpoint to update an access request"""
    updated_request = await access_request_service.update_access_request(
        db, request_id, update_data, current_admin["id"]
    )
    return AccessRequestPublic(**updated_request)

@router.post("/admin/access-requests/{request_id}/approve", response_model=UserWithOTP)
async def approve_access_request(
    request_id: str,
    db=Depends(get_database),
    current_admin: dict = Depends(auth_service.get_current_admin_user)
):
    """Admin endpoint to approve an access request and create user with OTP"""
    user_dict, temp_password = await access_request_service.approve_access_request_and_create_user(
        db, request_id, current_admin["id"]
    )
    
    # Convert user_dict to UserPublic format and add OTP
    from app.models.user import UserPublic
    user_public = UserPublic(
        id=user_dict["id"],
        email=user_dict["email"],
        role=user_dict["role"],
        status=user_dict["status"],
        is_premium=user_dict["is_premium"],
        must_change_password=user_dict["must_change_password"],
        created_at=user_dict["created_at"],
        last_login=user_dict.get("last_login")
    )
    
    return UserWithOTP(**user_public.model_dump(), otp=temp_password)