from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.services.auth_service import get_current_user
from app.services import generated_emails_service
from app.models.generated_email import GeneratedEmailPublic, GeneratedEmailBase
from app.core.db import get_database

router = APIRouter()

@router.post("/generated-emails", response_model=GeneratedEmailPublic, status_code=status.HTTP_201_CREATED)
async def create_generated_email(
    email_data: GeneratedEmailBase,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    user_id = UUID(current_user["id"])
    return await generated_emails_service.create_email(db, user_id, email_data)

@router.get("/generated-emails", response_model=List[GeneratedEmailPublic])
async def get_generated_emails(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    user_id = UUID(current_user["id"])
    return await generated_emails_service.get_emails_by_user(db, user_id)

@router.get("/generated-emails/{email_id}", response_model=GeneratedEmailPublic)
async def get_generated_email(
    email_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    user_id = UUID(current_user["id"])
    email = await generated_emails_service.get_email_by_id(db, user_id, email_id)
    if not email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    return email

@router.put("/generated-emails/{email_id}", response_model=GeneratedEmailPublic)
async def update_generated_email(
    email_id: UUID,
    email_data: GeneratedEmailBase,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    user_id = UUID(current_user["id"])
    return await generated_emails_service.update_email(db, user_id, email_id, email_data)

@router.delete("/generated-emails/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_generated_email(
    email_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    user_id = UUID(current_user["id"])
    await generated_emails_service.delete_email(db, user_id, email_id)
    return