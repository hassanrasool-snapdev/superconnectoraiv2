from fastapi import APIRouter, HTTPException
from app.core.db import db
from app.services.pinecone_index_service import pinecone_index_service

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """
    Enhanced health check endpoint that verifies connectivity to critical services.
    """
    mongo_status = "ok"
    pinecone_status = "ok"
    mongo_error = None
    pinecone_error = None

    # Check MongoDB connection
    try:
        await db.client.admin.command('ismaster')
    except Exception as e:
        mongo_status = "error"
        mongo_error = str(e)

    # Check Pinecone index status
    try:
        index_info = pinecone_index_service.get_index_info()
        if not index_info or not index_info.get("status", {}).get("ready"):
            pinecone_status = "error"
            pinecone_error = "Pinecone index is not ready or does not exist."
    except Exception as e:
        pinecone_status = "error"
        pinecone_error = str(e)

    health_status = {
        "status": "ok" if mongo_status == "ok" and pinecone_status == "ok" else "error",
        "services": {
            "mongodb": {
                "status": mongo_status,
                "error": mongo_error
            },
            "pinecone": {
                "status": pinecone_status,
                "error": pinecone_error
            }
        }
    }

    if health_status["status"] == "error":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status