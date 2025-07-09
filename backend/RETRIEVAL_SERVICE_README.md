# Retrieval Service Implementation

This document describes the implementation of the **Retrieval Service Refactor** that provides hybrid search and re-ranking capabilities using Pinecone and OpenAI.

## Overview

The Retrieval Service implements a sophisticated search pipeline that combines:
1. Optional LLM query rewriting using `gpt-4o-mini`
2. Hybrid Pinecone search with dense embeddings
3. Dynamic OpenAI re-ranking using `gpt-4o` with context budgeting
4. Service orchestration that ties all components together

## Architecture

### Components

1. **RetrievalService** (`app/services/retrieval_service.py`)
   - Main service class that orchestrates the entire retrieval pipeline
   - Handles OpenAI and Pinecone client initialization
   - Implements context budgeting for token management

2. **RetrievalRouter** (`app/routers/retrieval.py`)
   - FastAPI router that exposes retrieval endpoints
   - Handles request/response models and error handling
   - Integrates with authentication and search history

3. **Test Suite** (`test_retrieval.py`)
   - Comprehensive test script for all retrieval components
   - Tests query rewriting, embedding generation, and service health

## Key Features

### 1. Optional LLM Query Rewrite

**Function**: `rewrite_query_with_llm()`
- **Model**: `gpt-4o-mini`
- **Purpose**: Transform verbose user queries into concise search intent sentences
- **Toggle**: Can be enabled/disabled via `enable_rewrite` parameter
- **Fallback**: Returns original query if rewriting fails or is disabled

**Example**:
```python
original = "I'm looking for someone who has experience in machine learning and AI..."
rewritten = "Senior machine learning engineer with AI expertise"
```

### 2. Hybrid Pinecone Query

**Function**: `hybrid_pinecone_query()`
- **Parameters**:
  - `vector`: Dense embedding of search query (1536 dimensions)
  - `top_k`: 600 (as specified)
  - `alpha`: 0.6 (balance between dense and sparse results)
  - `filter`: Dictionary for metadata filtering
  - `namespace`: User ID for tenant isolation

**Features**:
- Serverless Pinecone index with automatic hybrid search
- Metadata filtering support
- Namespace isolation for multi-tenant architecture

### 3. Dynamic OpenAI Re-ranking

**Function**: `rerank_with_openai()`
- **Model**: `gpt-4o`
- **Context Budgeting**: Calculates optimal chunk size based on token limits
- **Formula**: `chunk_size = floor((128_000 - prompt_tokens) / avg_profile_tokens)`
- **Token Estimates**:
  - Total limit: 128,000 tokens
  - Prompt tokens: ~500 (conservative estimate)
  - Average profile tokens: ~200 (conservative estimate)

**System Prompt**:
```
You are a recruiting assistant. For each profile JSON, score 1-10 how well it matches the user query, then list a one-sentence pro and con.
```

**Response Format**:
```json
[
  {
    "profile_id": "profile_123",
    "score": 8,
    "pro": "Strong background in required technology with relevant industry experience.",
    "con": "Location might not be ideal for the role requirements."
  }
]
```

### 4. Service Orchestration

**Function**: `retrieve_and_rerank()`

**Pipeline Steps**:
1. **Query Rewrite** (optional): Transform verbose query using `gpt-4o-mini`
2. **Embedding Generation**: Create dense vector using `text-embedding-3-small`
3. **Hybrid Search**: Query Pinecone with specified parameters
4. **Data Fetching**: Retrieve full profile data from MongoDB
5. **Re-ranking**: Score and annotate results using `gpt-4o`
6. **Response**: Return sorted, annotated results

## API Endpoints

### POST `/api/v1/retrieve`

**Request**:
```json
{
  "query": "Senior software engineer with Python experience",
  "enable_query_rewrite": true,
  "filters": {
    "industry": "Technology",
    "city": "San Francisco"
  }
}
```

**Response**:
```json
{
  "results": [
    {
      "profile": { /* full profile data */ },
      "score": 9,
      "pro": "Excellent Python skills with 8+ years experience",
      "con": "May be overqualified for junior positions"
    }
  ],
  "total_count": 25,
  "query_used": "Senior software engineer with Python experience",
  "processing_info": {
    "query_rewrite_enabled": true,
    "filters_applied": true,
    "pinecone_top_k": 600,
    "pinecone_alpha": 0.6
  }
}
```

### POST `/api/v1/retrieve/query-rewrite`

Test endpoint for query rewriting functionality.

### GET `/api/v1/retrieve/health`

Health check endpoint for service components.

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Pinecone Configuration  
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=profile-embeddings
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

### Token Budgeting Configuration

```python
TOTAL_TOKEN_LIMIT = 128000          # GPT-4o context limit
ESTIMATED_PROMPT_TOKENS = 500       # Conservative estimate
ESTIMATED_AVG_PROFILE_TOKENS = 200  # Conservative estimate
```

## Error Handling

### Graceful Degradation
- **OpenAI Unavailable**: Service continues with default scores
- **Pinecone Unavailable**: Raises appropriate error with clear message
- **JSON Parsing Errors**: Falls back to default scoring
- **Token Limit Exceeded**: Automatic chunking prevents issues

### Logging
- Comprehensive logging throughout the pipeline
- Performance metrics and processing counts
- Error details for debugging

## Testing

### Run Tests
```bash
cd backend
python test_retrieval.py
```

### Test Coverage
- Query rewriting functionality
- Embedding generation
- Chunk size calculation
- Service component health
- Hybrid query simulation

## Performance Considerations

### Context Budgeting
- Automatic calculation of optimal batch sizes
- Prevents token limit exceeded errors
- Balances throughput with API constraints

### Caching
- Leverages existing embedding cache from `EmbeddingsService`
- Reduces redundant API calls
- Improves response times

### Batch Processing
- Processes candidates in calculated chunks
- Parallel processing where possible
- Efficient memory usage

## Integration

### With Existing Services
- **EmbeddingsService**: Reuses embedding generation and caching
- **AuthService**: Integrated authentication
- **SearchHistoryService**: Automatic search logging
- **Database**: MongoDB integration for profile data

### Namespace Isolation
- Uses user ID as Pinecone namespace
- Ensures tenant data isolation
- Supports multi-user architecture

## Monitoring and Observability

### Health Checks
- Component availability status
- Configuration validation
- Service dependency checks

### Metrics
- Processing times per pipeline stage
- Token usage and chunk sizes
- Success/failure rates
- Result quality metrics

## Future Enhancements

### Potential Improvements
1. **Adaptive Token Estimation**: Dynamic token counting for better budgeting
2. **Result Caching**: Cache re-ranking results for similar queries
3. **A/B Testing**: Compare different alpha values and models
4. **Feedback Loop**: Learn from user interactions to improve ranking
5. **Semantic Filtering**: Enhanced metadata filtering with embeddings

### Scalability Considerations
1. **Async Processing**: Full async pipeline for better concurrency
2. **Result Streaming**: Stream results as they're processed
3. **Distributed Processing**: Scale re-ranking across multiple workers
4. **Advanced Caching**: Redis-based caching for high-traffic scenarios

## Troubleshooting

### Common Issues

1. **OpenAI Client Initialization Error**
   - Check `OPENAI_API_KEY` configuration
   - Verify API key permissions and quotas

2. **Pinecone Connection Issues**
   - Verify `PINECONE_API_KEY` and index configuration
   - Check index status and region settings

3. **Token Limit Errors**
   - Review chunk size calculation
   - Adjust token estimates if needed

4. **Empty Results**
   - Check if embeddings are properly indexed
   - Verify namespace configuration
   - Review filter parameters

### Debug Mode
Enable detailed logging by setting appropriate log levels in the application configuration.

## Conclusion

The Retrieval Service provides a robust, scalable solution for hybrid search and intelligent re-ranking. It combines the power of dense vector search with advanced language model capabilities to deliver highly relevant, scored, and annotated search results.