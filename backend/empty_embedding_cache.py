import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# Load environment variables from .env file
load_dotenv()

# Get MongoDB configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "superconnector")
COLLECTION_NAME = "embedding_cache"

def empty_collection():
    """
    Connects to MongoDB and deletes all documents from the specified collection.
    """
    if not DATABASE_URL:
        print("Error: DATABASE_URL must be set in your environment variables.")
        return

    client = None  # Initialize client to None
    try:
        client = MongoClient(DATABASE_URL, tlsCAFile=certifi.where())
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        print(f"Connecting to database '{DATABASE_NAME}' and collection '{COLLECTION_NAME}'...")

        # Get the count of documents before deleting
        count = collection.count_documents({})
        
        if count == 0:
            print(f"The collection '{COLLECTION_NAME}' is already empty.")
            return

        print(f"Found {count} documents in the collection.")
        
        # Confirm with the user before deleting
        confirm = input(f"Are you sure you want to delete all {count} documents from '{COLLECTION_NAME}'? (yes/no): ")
        if confirm.lower() == 'yes':
            print("\nDeleting documents...")
            result = collection.delete_many({})
            print(f"Successfully deleted {result.deleted_count} documents.")
        else:
            print("\nDeletion cancelled.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    empty_collection()