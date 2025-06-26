from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.db import connect_to_mongo, close_mongo_connection
from app.routers import auth, connections, search, saved_searches, search_history, favorites

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    await connect_to_mongo()
    yield
    # on shutdown
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(connections.router, prefix="/api/v1", tags=["Connections"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(saved_searches.router, prefix="/api/v1", tags=["Saved Searches"])
app.include_router(search_history.router, prefix="/api/v1", tags=["Search History"])
app.include_router(favorites.router, prefix="/api/v1", tags=["Favorites"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}