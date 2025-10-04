from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import logging
from typing import Optional
from bson.codec_options import CodecOptions
from uuid import UUID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None

db = Database()

async def connect_to_mongo():
    """
    Establishes a connection to MongoDB with standard UUID representation.
    """
    logger.info("Connecting to MongoDB with standard UUID representation...")
    try:
        # Determine if TLS should be used based on the connection string
        # MongoDB Atlas and remote instances typically use mongodb+srv:// or require TLS
        # Local instances typically don't need TLS
        database_url = settings.DATABASE_URL or "mongodb://localhost:27017"
        use_tls = database_url.startswith("mongodb+srv://") or database_url.startswith("mongodb://") and "mongodb.net" in database_url
        
        logger.info(f"Connecting to MongoDB at: {database_url.split('@')[-1] if '@' in database_url else database_url}")
        logger.info(f"TLS enabled: {use_tls}")
        
        # Build connection parameters
        connection_params = {
            "uuidRepresentation": 'standard'  # Use 'standard' for cross-language compatibility
        }
        
        # Only add TLS parameters if connecting to a remote instance
        if use_tls:
            connection_params["tls"] = True
            connection_params["tlsAllowInvalidCertificates"] = True
        
        db.client = AsyncIOMotorClient(database_url, **connection_params)
        
        # The ismaster command is cheap and does not require auth.
        await db.client.admin.command('ismaster')
        
        # Log the configured UUID representation
        db_instance = get_database()
        logger.info(f"Successfully connected to MongoDB. UUID representation: {db_instance.codec_options.uuid_representation}")
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}", exc_info=True)
        raise

async def close_mongo_connection():
    """
    Closes the MongoDB connection.
    """
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
    logger.info("MongoDB connection closed.")

def get_database():
    """
    Returns the database instance, ensuring the client is initialized.
    """
    if db.client is None:
        raise Exception("Database client not initialized. Call connect_to_mongo first.")
    
    # Return the database with the correct codec options
    return db.client.get_database(settings.DATABASE_NAME)