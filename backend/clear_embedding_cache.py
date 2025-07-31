import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_embedding_cache():
    """
    Connects to the MongoDB database and clears the 'embedding_cache' collection.
    """
    logger.info("Connecting to MongoDB to clear embedding cache...")
    try:
        client = AsyncIOMotorClient(
            settings.DATABASE_URL,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        
        # The ismaster command is cheap and does not require auth.
        await client.admin.command('ismaster')
        logger.info("Successfully connected to MongoDB.")
        
        db = client[settings.DATABASE_NAME]
        cache_collection = db.embedding_cache
        
        logger.info(f"Found collection '{cache_collection.name}'.")
        
        # Get the count of documents before deletion
        count_before = await cache_collection.count_documents({})
        logger.info(f"Found {count_before} documents in embedding_cache.")
        
        if count_before > 0:
            # Delete all documents in the collection
            result = await cache_collection.delete_many({})
            logger.info(f"Successfully deleted {result.deleted_count} documents from embedding_cache.")
        else:
            logger.info("Embedding cache is already empty. No action needed.")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            logger.info("MongoDB connection closed.")

if __name__ == "__main__":
    asyncio.run(clear_embedding_cache())