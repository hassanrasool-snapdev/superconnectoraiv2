# Data & Embeddings Functionality

This document describes the implementation of the Data & Embeddings functionality for processing profile data, generating embeddings, and storing them in Pinecone.

## Overview

The embeddings system consists of:

1. **Profile Text Canonicalization**: Cleans and normalizes profile text
2. **Embedding Generation & Caching**: Uses OpenAI's text-embedding-3-small model with MongoDB caching
3. **Batch Upsert to Pinecone**: Stores vectors in Pinecone with tenant isolation
4. **CSV Data Processing**: Processes connection data from CSV files

## Components

### 1. EmbeddingsService (`app/services/embeddings_service.py`)

Main service class that handles all embeddings operations.

#### Key Methods:

- `canonicalize_profile_text()`: Cleans and normalizes profile text
- `generate_embedding()`: Generates embeddings using OpenAI
- `get_cached_embedding()` / `cache_embedding()`: Handles embedding caching
- `batch_upsert_to_pinecone()`: Performs batch upserts to Pinecone
- `process_profiles_and_upsert()`: End-to-end processing of CSV data

### 2. Embeddings Router (`app/routers/embeddings.py`)

FastAPI router exposing embeddings functionality via REST API.

#### Endpoints:

- `POST /api/v1/embeddings/canonicalize`: Canonicalize profile text
- `POST /api/v1/embeddings/generate`: Generate embeddings for profile text
- `GET /api/v1/embeddings/cached/{profile_id}`: Get cached embedding
- `POST /api/v1/embeddings/process-profiles`: Process CSV and upsert to Pinecone
- `POST /api/v1/embeddings/batch-upsert`: Custom batch upsert
- `GET /api/v1/embeddings/health`: Health check

## Configuration

Add these environment variables to your `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY="your_openai_api_key_here"

# Pinecone Configuration
PINECONE_API_KEY="your_pinecone_api_key_here"
PINECONE_INDEX_NAME="profile-embeddings"
PINECONE_ENVIRONMENT="us-east-1"
```

## Dependencies

The following packages were added to `requirements.txt`:

```
openai==1.54.4
pinecone-client==5.0.1
pandas==2.2.3
beautifulsoup4==4.12.3
emoji==2.14.0
```

## Profile Text Canonicalization

The `canonicalize_profile_text()` function processes profile fields as follows:

1. **Input Fields**: `name`, `headline`, `experience`, `skills`, `location`
2. **Processing Steps**:
   - Combines all fields into a single string
   - Removes HTML tags using BeautifulSoup
   - Removes emojis using the emoji library
   - Expands "Sr." to "Senior" (case-insensitive)
   - Normalizes whitespace (multiple spaces → single space)
   - Converts to lowercase and strips whitespace

**Example**:
```python
# Input
name = "John Doe Sr."
headline = "Senior Software Engineer"
experience = "Experienced developer with <strong>10+ years</strong> in Python 🐍"
skills = "Python, JavaScript, React"
location = "San Francisco, CA"

# Output
"john doe senior senior software engineer experienced developer with 10+ years in python python, javascript, react san francisco, ca"
```

## Embedding Generation & Caching

- **Model**: `text-embedding-3-small` (OpenAI)
- **Caching**: MongoDB collection `embedding_cache`
- **Cache Key**: `profile_id`
- **Cache Fields**: `profile_id`, `embedding`, `created_at`, `model`

The system first checks for cached embeddings before generating new ones to optimize API usage and performance.

## Pinecone Integration

### Batch Upsert Configuration:
- **Batch Size**: 500 vectors per batch
- **Namespace**: Uses `user_id` for tenant isolation
- **Vector Format**: `(id, vector, metadata)`

### Metadata Schema:
```json
{
  "industry": "...",
  "size": "...",
  "city": "...",
  "followers": "...",
  "connected_on": "...",
  "name": "...",
  "canonical_text": "..."
}
```

## CSV Data Processing

The system processes `Connections.csv` with the following mapping:

- **Name**: `FirstName` + `LastName`
- **Headline**: `Title`
- **Experience**: `Description/0`
- **Skills**: Not available in current CSV (empty string)
- **Location**: `City` + `State` + `Country`
- **Profile ID**: `LinkedinUrl` or fallback to `profile_{index}`

### Metadata Extraction:
- **industry**: `CompanyIndustry`
- **size**: `Company size`
- **city**: `City`
- **followers**: `Followers`
- **connected_on**: `Connected On`

## Usage Examples

### 1. Canonicalize Text
```bash
curl -X POST "http://localhost:8000/api/v1/embeddings/canonicalize" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe Sr.",
    "headline": "Senior Software Engineer",
    "experience": "Experienced developer",
    "skills": "Python, JavaScript",
    "location": "San Francisco, CA"
  }'
```

### 2. Generate Embedding
```bash
curl -X POST "http://localhost:8000/api/v1/embeddings/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "headline": "Software Engineer",
    "experience": "5 years experience",
    "skills": "Python",
    "location": "NYC"
  }'
```

### 3. Process CSV Data (Requires Authentication)
```bash
curl -X POST "http://localhost:8000/api/v1/embeddings/process-profiles" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"csv_path": "Connections.csv"}'
```

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_embeddings.py
```

The test script will:
- Test profile text canonicalization
- Test embedding generation (if OpenAI API key is set)
- Test CSV data loading

## Error Handling

The system includes comprehensive error handling:
- Invalid CSV data is skipped with logging
- OpenAI API errors are caught and re-raised
- Pinecone connection issues are handled gracefully
- Missing environment variables are validated

## Performance Considerations

- **Caching**: Embeddings are cached to avoid regenerating for the same profile
- **Batch Processing**: Pinecone upserts are batched (500 vectors per batch)
- **Async Operations**: All database and API operations are asynchronous
- **Error Recovery**: Individual profile processing errors don't stop the entire batch

## Security

- **Authentication**: Profile processing endpoints require JWT authentication
- **Tenant Isolation**: Pinecone namespaces use authenticated user IDs
- **API Key Management**: All API keys are stored as environment variables