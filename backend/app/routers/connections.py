from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from typing import List, Dict
from uuid import UUID

from app.services.auth_service import get_current_user
from app.services import connections_service
from app.models.connection import ConnectionPublic
from app.core.db import get_database

router = APIRouter()

@router.post("/connections/upload", status_code=status.HTTP_201_CREATED)
async def upload_connections(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")
    
    user_id = UUID(current_user["id"])
    count = await connections_service.process_csv_upload(db, file, user_id)
    return {"message": f"Successfully uploaded and processed {count} connections."}

@router.get("/connections", response_model=List[ConnectionPublic])
async def get_connections(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000)
):
    user_id = UUID(current_user["id"])
    connections = await connections_service.get_user_connections(db, user_id, page, limit)
    return connections

@router.get("/connections/count")
async def get_connections_count(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    user_id = UUID(current_user["id"])
    count = await connections_service.get_user_connections_count(db, user_id)
    return {"count": count}

@router.delete("/connections", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connections(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    user_id = UUID(current_user["id"])
    await connections_service.delete_user_connections(db, user_id)
    return