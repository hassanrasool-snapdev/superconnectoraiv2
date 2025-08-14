from uuid import UUID
from typing import List
from app.models.generated_email import GeneratedEmailBase, GeneratedEmailInDB
from app.services.ai_service import generate_email_content

async def create_email(db, user_id: UUID, email_data: GeneratedEmailBase) -> GeneratedEmailInDB:
    generated_content = await generate_email_content(email_data.reason_for_connecting)
    
    email = GeneratedEmailInDB(
        **email_data.model_dump(),
        user_id=user_id,
        generated_content=generated_content
    )
    await db.generated_emails.insert_one(email.model_dump(by_alias=True))
    return email

async def get_emails_by_user(db, user_id: UUID) -> List[GeneratedEmailInDB]:
    emails = await db.generated_emails.find({"user_id": str(user_id)}).to_list(length=100)
    return [GeneratedEmailInDB(**email) for email in emails]

async def get_email_by_id(db, user_id: UUID, email_id: UUID) -> GeneratedEmailInDB:
    email = await db.generated_emails.find_one({"id": str(email_id), "user_id": str(user_id)})
    if email:
        return GeneratedEmailInDB(**email)
    return None

async def update_email(db, user_id: UUID, email_id: UUID, email_data: GeneratedEmailBase) -> GeneratedEmailInDB:
    await db.generated_emails.update_one(
        {"id": str(email_id), "user_id": str(user_id)},
        {"$set": email_data.model_dump()}
    )
    return await get_email_by_id(db, user_id, email_id)

async def delete_email(db, user_id: UUID, email_id: UUID):
    await db.generated_emails.delete_one({"id": str(email_id), "user_id": str(user_id)})
    return