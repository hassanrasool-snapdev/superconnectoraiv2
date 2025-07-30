import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

# Get Pinecone configuration from environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

def get_all_namespaces():
    """
    Connects to Pinecone and retrieves all namespaces in the specified index.

    Returns:
        A list of namespace names.
    """
    if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
        print("Error: PINECONE_API_KEY and PINECONE_INDEX_NAME must be set in your environment variables.")
        return []

    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Get the index object
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Get index statistics, which include namespace information
        stats = index.describe_index_stats()
        
        # Extract namespaces from the stats object
        namespaces = list(stats.namespaces.keys())
        
        return namespaces

    except Exception as e:
        print(f"An error occurred while fetching namespaces: {e}")
        return []

def delete_namespace(namespace: str):
    """
    Deletes a namespace from the Pinecone index.
    """
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        index.delete(delete_all=True, namespace=namespace)
        print(f"Successfully deleted namespace: {namespace}")
    except Exception as e:
        print(f"An error occurred while deleting namespace {namespace}: {e}")


if __name__ == "__main__":
    print(f"Fetching namespaces for index '{PINECONE_INDEX_NAME}' to delete them...")
    
    namespaces = get_all_namespaces()
    
    if namespaces:
        print("\nFound namespaces to delete:")
        for ns in namespaces:
            print(f"- {ns}")
        
        # Confirm with the user before deleting
        confirm = input("\nAre you sure you want to delete all these namespaces? (yes/no): ")
        if confirm.lower() == 'yes':
            print("\nDeleting namespaces...")
            for ns in namespaces:
                delete_namespace(ns)
            print("\nAll namespaces have been deleted.")
        else:
            print("\nDeletion cancelled.")
    else:
        print("\nNo namespaces found to delete or an error occurred.")