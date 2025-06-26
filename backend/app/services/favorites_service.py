from uuid import UUID
from typing import List, Optional
from app.models.favorite_connection import FavoriteConnectionInDB, FavoriteConnectionCreate

async def add_favorite_connection(db, user_id: UUID, connection_id: UUID) -> dict:
    """Add a connection to user's favorites"""
    # Check if already favorited
    existing = await db.favorite_connections.find_one({
        "user_id": str(user_id),
        "connection_id": str(connection_id)
    })
    
    if existing:
        return existing
    
    favorite = FavoriteConnectionInDB(
        connection_id=connection_id,
        user_id=user_id
    )
    
    # Convert to dict for MongoDB storage
    favorite_dict = favorite.model_dump(by_alias=True)
    favorite_dict["id"] = str(favorite_dict["id"])
    favorite_dict["user_id"] = str(favorite_dict["user_id"])
    favorite_dict["connection_id"] = str(favorite_dict["connection_id"])
    
    result = await db.favorite_connections.insert_one(favorite_dict)
    favorite_dict["_id"] = result.inserted_id
    
    return favorite_dict

async def remove_favorite_connection(db, user_id: UUID, connection_id: UUID) -> bool:
    """Remove a connection from user's favorites"""
    result = await db.favorite_connections.delete_one({
        "user_id": str(user_id),
        "connection_id": str(connection_id)
    })
    
    return result.deleted_count > 0

async def get_user_favorite_connections(db, user_id: UUID) -> List[dict]:
    """Get all favorite connections for a user with connection details"""
    # Get favorite connection IDs
    cursor = db.favorite_connections.find({"user_id": str(user_id)}).sort("created_at", -1)
    favorites = await cursor.to_list(length=None)
    
    if not favorites:
        return []
    
    # Get connection IDs
    connection_ids = [fav["connection_id"] for fav in favorites]
    
    # Get actual connection details
    connections_cursor = db.connections.find({
        "id": {"$in": connection_ids},
        "user_id": str(user_id)
    })
    connections = await connections_cursor.to_list(length=None)
    
    # Create a mapping for easier lookup
    connections_map = {conn["id"]: conn for conn in connections}
    
    # Combine favorites with connection details
    result = []
    for favorite in favorites:
        connection_id = favorite["connection_id"]
        if connection_id in connections_map:
            result.append({
                "favorite_id": favorite["id"],
                "favorited_at": favorite["created_at"],
                "connection": connections_map[connection_id]
            })
    
    return result

async def is_connection_favorited(db, user_id: UUID, connection_id: UUID) -> bool:
    """Check if a connection is favorited by user"""
    favorite = await db.favorite_connections.find_one({
        "user_id": str(user_id),
        "connection_id": str(connection_id)
    })
    
    return favorite is not None

async def get_user_favorites_count(db, user_id: UUID) -> int:
    """Get count of user's favorite connections"""
    count = await db.favorite_connections.count_documents({"user_id": str(user_id)})
    return count