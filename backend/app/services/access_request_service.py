from fastapi import HTTPException, status
from datetime import datetime
from uuid import UUID
from app.models.access_request import AccessRequestCreate, AccessRequestInDB, AccessRequestUpdate, AccessRequestStatus
from app.services.follow_up_email_service import send_email_via_sendgrid
import os

async def create_access_request(db, request_data: AccessRequestCreate):
    """Create a new access request"""
    # Check if there's already a pending request for this email
    existing_request = await db.access_requests.find_one({
        "email": request_data.email,
        "status": AccessRequestStatus.pending.value
    })
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending access request already exists for this email"
        )
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": request_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new access request
    access_request = AccessRequestInDB(**request_data.model_dump())
    request_dict = access_request.model_dump()
    request_dict["id"] = str(request_dict["id"])
    
    await db.access_requests.insert_one(request_dict)
    return request_dict

async def get_access_requests(db, status_filter: AccessRequestStatus = None):
    """Get all access requests, optionally filtered by status"""
    query = {}
    if status_filter:
        query["status"] = status_filter.value
    
    cursor = db.access_requests.find(query).sort("created_at", -1)
    requests = await cursor.to_list(length=None)
    return requests

async def get_access_request_by_id(db, request_id: str):
    """Get a specific access request by ID"""
    request = await db.access_requests.find_one({"id": request_id})
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found"
        )
    return request

async def update_access_request(db, request_id: str, update_data: AccessRequestUpdate, admin_id: str):
    """Update an access request (admin only)"""
    request = await get_access_request_by_id(db, request_id)
    
    update_dict = {}
    if update_data.status:
        update_dict["status"] = update_data.status.value
        update_dict["processed_at"] = datetime.utcnow()
        update_dict["processed_by"] = admin_id
    
    if update_data.admin_notes:
        update_dict["admin_notes"] = update_data.admin_notes
    
    await db.access_requests.update_one(
        {"id": request_id},
        {"$set": update_dict}
    )
    
    # Return updated request
    updated_request = await get_access_request_by_id(db, request_id)

    # Send email notification for rejected status
    if update_data.status == AccessRequestStatus.rejected:
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'access-denied.html')
        with open(template_path, 'r') as f:
            html_content = f.read()
        
        await send_email_via_sendgrid(
            to_email=updated_request["email"],
            subject="Update on your access request",
            html_content=html_content
        )

    return updated_request

async def approve_access_request_and_create_user(db, request_id: str, admin_id: str):
    """Approve an access request and automatically create user with OTP"""
    from app.services.auth_service import create_user_with_otp
    from app.models.user import AdminUserCreate
    
    # Get the access request
    request = await get_access_request_by_id(db, request_id)
    
    if request["status"] != AccessRequestStatus.pending.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending requests can be approved"
        )
    
    # Create user with OTP
    user_data = AdminUserCreate(email=request["email"])
    user_dict, temp_password = await create_user_with_otp(db, user_data)
    
    # Update access request status
    await update_access_request(
        db,
        request_id,
        AccessRequestUpdate(
            status=AccessRequestStatus.approved,
            admin_notes=f"User created successfully with temporary password"
        ),
        admin_id
    )
    
    # Send approval email
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'access-approved.html')
    with open(template_path, 'r') as f:
        html_content = f.read().replace("{{ temporary_password }}", temp_password)

    await send_email_via_sendgrid(
        to_email=request["email"],
        subject="Your access request has been approved!",
        html_content=html_content
    )
    
    return user_dict, temp_password