from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID

from app.services.auth_service import get_current_user
from app.services.retrieval_service import retrieval_service
from app.services import search_history_service
from app.models.search_history import SearchHistoryCreate
from app.core.db import get_database

router = APIRouter()

class RetrievalFilters(BaseModel):
    """Metadata filters for Pinecone query"""
    industry: Optional[str] = None
    size: Optional[str] = None
    city: Optional[str] = None
    followers: Optional[str] = None
    connected_on: Optional[str] = None

class RetrievalRequest(BaseModel):
    """Request model for retrieval and re-ranking"""
    query: str
    enable_query_rewrite: Optional[bool] = True
    filters: Optional[RetrievalFilters] = None

class RetrievalResult(BaseModel):
    """Response model for retrieval results"""
    profile: Dict[str, Any]
    score: int
    pro: str
    con: str

class RetrievalResponse(BaseModel):
    """Complete response model"""
    results: List[RetrievalResult]
    total_count: int
    query_used: str
    processing_info: Dict[str, Any]

@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_and_rerank_profiles(
    request: RetrievalRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Perform hybrid retrieval and re-ranking of profiles using Pinecone and OpenAI.
    
    This endpoint:
    1. Optionally rewrites the user query using gpt-4o-mini
    2. Generates embeddings for the query
    3. Performs hybrid search on Pinecone with specified parameters
    4. Fetches full profile data from the database
    5. Re-ranks results using gpt-4o with context budgeting
    6. Returns scored and annotated results
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )
    
    try:
        user_id = current_user["id"]
        
        # Convert filters to dictionary format for Pinecone
        filter_dict = None
        if request.filters:
            filter_dict = {}
            for field, value in request.filters.model_dump().items():
                if value is not None:
                    filter_dict[field] = value
        
        # Perform retrieval and re-ranking
        results = await retrieval_service.retrieve_and_rerank(
            user_query=request.query,
            user_id=user_id,
            enable_query_rewrite=request.enable_query_rewrite,
            filter_dict=filter_dict
        )
        
        # Save search to history
        try:
            history_entry = SearchHistoryCreate(
                query=request.query,
                filters=request.filters.model_dump() if request.filters else None,
                results_count=len(results)
            )
            await search_history_service.create_search_history_entry(db, UUID(user_id), history_entry)
        except Exception as history_error:
            print(f"Failed to save search history: {history_error}")
            # Don't fail the search if history saving fails
        
        # Format response
        formatted_results = []
        for result in results:
            formatted_results.append(RetrievalResult(
                profile=result["profile"],
                score=result["score"],
                pro=result["pro"],
                con=result["con"]
            ))
        
        return RetrievalResponse(
            results=formatted_results,
            total_count=len(formatted_results),
            query_used=request.query,  # Could be enhanced to show rewritten query
            processing_info={
                "query_rewrite_enabled": request.enable_query_rewrite,
                "filters_applied": filter_dict is not None,
                "pinecone_top_k": 600,
                "pinecone_alpha": 0.6
            }
        )
        
    except Exception as e:
        print(f"Retrieval router error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)}"
        )

@router.post("/retrieve/query-rewrite")
async def test_query_rewrite(
    query: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Test endpoint for query rewriting functionality.
    """
    if not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        rewritten_query = await retrieval_service.rewrite_query_with_llm(query, enable_rewrite=True)
        
        return {
            "original_query": query,
            "rewritten_query": rewritten_query,
            "rewrite_applied": query != rewritten_query
        }
        
    except Exception as e:
        print(f"Query rewrite error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query rewrite failed: {str(e)}"
        )

@router.get("/retrieve/health")
async def retrieval_health_check():
    """
    Health check endpoint for retrieval service components.
    """
    health_status = {
        "openai_client": retrieval_service.openai_client is not None,
        "pinecone_client": retrieval_service.pinecone_client is not None,
        "pinecone_index": retrieval_service.index is not None,
        "embeddings_service": True,  # Always available
        "status": "healthy"
    }
    
    # Check if critical components are missing
    if not health_status["openai_client"]:
        health_status["status"] = "degraded"
        health_status["warnings"] = health_status.get("warnings", []) + ["OpenAI client not initialized"]
    
    if not health_status["pinecone_index"]:
        health_status["status"] = "degraded" 
        health_status["warnings"] = health_status.get("warnings", []) + ["Pinecone index not available"]
    
    return health_status