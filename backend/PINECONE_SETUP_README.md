# Pinecone Index Setup Guide

This guide explains how to set up and configure the Pinecone index for storing profile embeddings in the SuperConnector AI application.

## Overview

The Pinecone index is configured as a serverless vector database that stores 1536-dimensional embeddings generated from LinkedIn profile data using OpenAI's `text-embedding-3-small` model. The index supports:

- **Hybrid Search**: Dense + sparse vector search capabilities
- **Metadata Filtering**: Filter by industry, company size, city, followers, and connection date
- **Namespace Isolation**: Multi-tenant support using user IDs as namespaces
- **Cosine Similarity**: Optimized for semantic similarity search

## Index Configuration

- **Dimension**: 1536 (matches `text-embedding-3-small` model)
- **Metric**: Cosine similarity
- **Cloud**: AWS (configurable)
- **Region**: us-west-2 (configurable)
- **Type**: Serverless (auto-scaling, pay-per-use)

## Prerequisites

1. **Pinecone Account**: Sign up at [pinecone.io](https://pinecone.io)
2. **API Key**: Get your API key from the Pinecone console
3. **Environment Variables**: Configure the required environment variables

## Environment Configuration

Add the following variables to your `.env` file:

```bash
# Pinecone Configuration
PINECONE_API_KEY="your_pinecone_api_key_here"
PINECONE_INDEX_NAME="profile-embeddings"
PINECONE_CLOUD="aws"
PINECONE_REGION="us-west-2"
```

### Configuration Options

- `PINECONE_API_KEY`: Your Pinecone API key (required)
- `PINECONE_INDEX_NAME`: Name of the index (default: "profile-embeddings")
- `PINECONE_CLOUD`: Cloud provider (default: "aws", options: "aws", "gcp", "azure")
- `PINECONE_REGION`: Cloud region (default: "us-west-2")

## Setup Methods

### Method 1: Command Line Script (Recommended)

Run the standalone setup script:

```bash
cd backend
python setup_pinecone_index.py
```

This script will:
- Validate your configuration
- Create the index if it doesn't exist
- Display setup results and index information
- Provide next steps

### Method 2: API Endpoints

Use the REST API endpoints to manage the index:

#### Create/Setup Index
```bash
curl -X POST http://localhost:8000/api/v1/pinecone/index/setup
```

#### Check Index Status
```bash
curl http://localhost:8000/api/v1/pinecone/index/info
```

#### Check if Index Exists
```bash
curl http://localhost:8000/api/v1/pinecone/index/exists
```

#### Delete Index (Use with caution!)
```bash
curl -X DELETE http://localhost:8000/api/v1/pinecone/index
```

### Method 3: Python Code

```python
from app.services.pinecone_index_service import pinecone_index_service

# Setup the index
result = pinecone_index_service.setup_index()
print(result)

# Check if index exists
exists = pinecone_index_service.index_exists()
print(f"Index exists: {exists}")

# Get index information
info = pinecone_index_service.get_index_info()
print(info)
```

## Index Features

### 1. Hybrid Search Support
The index automatically supports hybrid search combining:
- **Dense vectors**: Semantic embeddings from OpenAI
- **Sparse vectors**: Keyword-based search (can be added later)

### 2. Metadata Filtering
Filter search results by metadata fields:
- `industry`: Company industry
- `size`: Company size
- `city`: Location city
- `followers`: Number of followers
- `connected_on`: Connection date
- `name`: Profile name
- `canonical_text`: Processed profile text

Example metadata structure:
```json
{
  "industry": "Technology",
  "size": "1001-5000 employees",
  "city": "San Francisco",
  "followers": "500+",
  "connected_on": "2024-01-15",
  "name": "John Doe",
  "canonical_text": "john doe senior software engineer..."
}
```

### 3. Namespace Isolation
Each user's data is stored in a separate namespace using their user ID:
- Namespace: `user_123` contains all embeddings for user 123
- Provides data isolation and multi-tenancy
- Enables user-specific searches and data management

## Usage Examples

### 1. Process and Store Profiles
```python
from app.services.embeddings_service import embeddings_service

# Process CSV and store embeddings
result = await embeddings_service.process_profiles_and_upsert(
    csv_path="Connections.csv",
    user_id="user_123"
)
```

### 2. Search Similar Profiles
```python
# Generate query embedding
query_text = "senior software engineer python machine learning"
query_embedding = await embeddings_service.generate_embedding(query_text)

# Search in Pinecone (using the index directly)
from app.services.embeddings_service import embeddings_service
index = embeddings_service.index

results = index.query(
    vector=query_embedding,
    top_k=10,
    namespace="user_123",
    filter={"industry": "Technology"},
    include_metadata=True
)
```

## Troubleshooting

### Common Issues

1. **"PINECONE_API_KEY is not set"**
   - Ensure your API key is in the `.env` file
   - Restart your application after adding the key

2. **"Index creation failed"**
   - Check your Pinecone account limits
   - Verify the region is supported
   - Ensure you have sufficient quota

3. **"Index not ready"**
   - Serverless indexes take time to initialize
   - The script waits up to 5 minutes for readiness
   - Check Pinecone console for status

4. **"Connection timeout"**
   - Check your internet connection
   - Verify the API key is correct
   - Try a different region if needed

### Verification Steps

1. **Check Configuration**:
   ```bash
   python -c "from app.core.config import settings; print(f'API Key: {settings.PINECONE_API_KEY[:8]}...')"
   ```

2. **Test Connection**:
   ```bash
   python -c "from app.services.pinecone_index_service import pinecone_index_service; print(pinecone_index_service.index_exists())"
   ```

3. **View Index Stats**:
   ```bash
   python -c "from app.services.pinecone_index_service import pinecone_index_service; print(pinecone_index_service.get_index_info())"
   ```

## Best Practices

1. **Index Naming**: Use descriptive names like `profile-embeddings-prod`
2. **Namespace Strategy**: Use consistent user ID format for namespaces
3. **Metadata Design**: Keep metadata fields consistent and indexed
4. **Batch Operations**: Use batch upserts for better performance
5. **Error Handling**: Always handle Pinecone API errors gracefully
6. **Monitoring**: Monitor index usage and performance in Pinecone console

## Security Considerations

1. **API Key Protection**: Never commit API keys to version control
2. **Environment Isolation**: Use different indexes for dev/staging/prod
3. **Access Control**: Implement proper authentication before index operations
4. **Data Privacy**: Ensure compliance with data protection regulations
5. **Namespace Isolation**: Always use proper namespace isolation for multi-tenant data

## Next Steps

After setting up the index:

1. **Test the Setup**: Run the embeddings processing pipeline
2. **Load Data**: Process your LinkedIn connections CSV file
3. **Implement Search**: Build search functionality using the embeddings
4. **Monitor Performance**: Track search latency and accuracy
5. **Scale as Needed**: Adjust configuration based on usage patterns

## Support

For issues related to:
- **Pinecone Service**: Check [Pinecone Documentation](https://docs.pinecone.io/)
- **Application Integration**: Review the embeddings service code
- **Configuration**: Verify environment variables and settings