import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.db import connect_to_mongo, close_mongo_connection
from app.services.threading_service import threading_service
from app.routers import auth, connections, search, saved_searches, search_history, favorites, embeddings, pinecone_index, retrieval, generated_emails, tips, warm_intro_requests, health

# Get the logger used by Uvicorn
uvicorn_error_logger = logging.getLogger("uvicorn.error")
# Set the logger level to DEBUG
uvicorn_error_logger.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    await connect_to_mongo()
    threading_service.start()
    yield
    # on shutdown
    await close_mongo_connection()
    threading_service.stop()

app = FastAPI(lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins from all regions
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(connections.router, prefix="/api/v1", tags=["Connections"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(saved_searches.router, prefix="/api/v1", tags=["Saved Searches"])
app.include_router(search_history.router, prefix="/api/v1", tags=["Search History"])
app.include_router(favorites.router, prefix="/api/v1", tags=["Favorites"])
app.include_router(embeddings.router, prefix="/api/v1/embeddings", tags=["Embeddings"])
app.include_router(pinecone_index.router, prefix="/api/v1", tags=["Pinecone Index"])
app.include_router(retrieval.router, prefix="/api/v1", tags=["Retrieval"])
app.include_router(generated_emails.router, prefix="/api/v1", tags=["generated-emails"])
app.include_router(tips.router, prefix="/api/v1", tags=["Tipping"])
app.include_router(warm_intro_requests.router, prefix="/api/v1", tags=["Warm Intro Requests"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])