import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# Load environment variables from .env file
load_dotenv()

# Get MongoDB configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "superconnector")

def format_size(size_bytes):
    """Converts bytes to a human-readable format (KB, MB, GB)."""
    if size_bytes is None:
        return "N/A"
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size_bytes >= power and n < len(power_labels) -1 :
        size_bytes /= power
        n += 1
    return f"{size_bytes:.2f} {power_labels[n]}B"

def get_mongo_stats():
    """
    Connects to MongoDB and retrieves database and collection statistics.
    """
    if not DATABASE_URL:
        print("Error: DATABASE_URL must be set in your environment variables.")
        return

    try:
        client = MongoClient(DATABASE_URL, tlsCAFile=certifi.where())
        db = client[DATABASE_NAME]

        # Get database stats
        db_stats = db.command('dbStats')
        
        print(f"\n--- Database Statistics for '{DATABASE_NAME}' ---")
        print(f"  - Total Size: {format_size(db_stats.get('storageSize'))}")
        print(f"  - Index Size: {format_size(db_stats.get('indexSize'))}")
        print(f"  - Number of Collections: {db_stats.get('collections')}")
        print(f"  - Number of Objects: {db_stats.get('objects')}")

        # Get stats for each collection
        print("\n--- Collection Statistics ---")
        collections = db.list_collection_names()
        for collection_name in collections:
            coll_stats = db.command('collStats', collection_name)
            print(f"\n  Collection: '{collection_name}'")
            print(f"    - Document Count: {coll_stats.get('count')}")
            print(f"    - Average Object Size: {format_size(coll_stats.get('avgObjSize'))}")
            print(f"    - Total Size: {format_size(coll_stats.get('size'))}")
            print(f"    - Total Index Size: {format_size(coll_stats.get('totalIndexSize'))}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    get_mongo_stats()