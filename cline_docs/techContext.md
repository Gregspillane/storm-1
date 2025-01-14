# Technical Context

## RAG Integration Details

### Configuration Parameters
- RAG_API_KEY: API key for RAG service
- RAG_API_URL: Base URL for RAG API
- RAG_RETRIEVER_SIMILARITY_TOP_K: Number of top results to return
- RAG_RETRIEVER_ALPHA: Weighting between dense/sparse search
- RAG_RETRIEVER_RERANKING_ENABLED: Enable/disable reranking
- RAG_RETRIEVER_RERANKING_TOP_N: Number of results to rerank
- RAG_RETRIEVER_RERANKING_THRESHOLD: Reranking confidence threshold
- RAG_RETRIEVER_MAX_RETRIES: Maximum retry attempts
- RAG_RETRIEVER_BASE_DELAY: Base delay between retries
- RAG_RETRIEVER_PRIORITY_THRESHOLD: Confidence threshold for RAG results

### Implementation Details
- Uses requests.Session for connection pooling
- Implements exponential backoff for rate limiting
- Converts raw API results to Information objects
- Handles both single and multiple queries
- Supports URL exclusion
- Provides comprehensive logging

### Error Handling
- Handles rate limits with exponential backoff
- Falls back to web search on RAG failure
- Logs all errors with context
- Validates API responses
- Implements timeout handling

### Performance Considerations
- Connection pooling for API calls
- Batch processing of multiple queries
- Caching of frequent queries
- Asynchronous processing where possible
- Monitoring of API response times