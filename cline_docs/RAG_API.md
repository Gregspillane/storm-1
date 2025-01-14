# Query API Documentation

## Overview
The Query API endpoint provides direct access to CloudIndex-AI's hybrid search capabilities. It combines dense vector search with sparse vector (BM25) search for optimal document retrieval, with optional reranking support.

## Endpoint
```
POST /public/v1/query
```

## Authentication
- Requires API key authentication
- Include API key in request header:
  ```
  Authorization: ApiKey YOUR_API_KEY
  ```
- API key must have access to the target project

## Request Format
```typescript
{
  query: string;              // The search query text
  options?: {
    similarityTopK?: number;  // Number of results to return (default based on project settings)
    alpha?: number;           // Weight between dense (1.0) and sparse (0.0) vectors (default: 0.75)
    rerankingEnabled?: boolean;  // Whether to apply reranking (default from project settings)
    rerankingTopN?: number;      // Number of results to rerank (default from project settings)
    rerankingThreshold?: number; // Minimum score for reranked results (default from project settings)
  }
}
```

### Parameter Details

#### Required Parameters
- `query`: The search query text to find relevant documents

#### Optional Parameters
- `similarityTopK`: Number of results to return
  - Type: number
  - Default: Project configuration value
  - Minimum: 1
  - Maximum: 100

- `alpha`: Weight between dense and sparse vectors
  - Type: number
  - Default: 0.75
  - Range: 0.0 to 1.0
  - 1.0 = pure dense vector search
  - 0.0 = pure sparse vector (BM25) search

- `rerankingEnabled`: Enable/disable reranking
  - Type: boolean
  - Default: Project configuration value

- `rerankingTopN`: Number of results to rerank
  - Type: number
  - Default: Project configuration value
  - Must be ≤ similarityTopK
  - Only used if rerankingEnabled is true

- `rerankingThreshold`: Minimum score threshold for reranked results
  - Type: number
  - Default: Project configuration value
  - Range: 0.0 to 1.0
  - Only used if rerankingEnabled is true

## Response Format
```typescript
{
  matches: Array<{
    id: string;           // Document chunk ID
    score: number;        // Relevance score (0.0 to 1.0)
    content: string;      // Document chunk content
    metadata: {           // Document metadata
      source: string;     // Source document identifier
      type: string;       // Document type
      [key: string]: any; // Additional metadata fields
    };
  }>;
  namespace: string;      // Project namespace
  total: number;         // Total number of matches found
}
```

## Error Responses

### 400 Bad Request
Invalid request parameters or format
```json
{
  "error": "Invalid request parameters",
  "code": "invalid_request",
  "details": {
    "field": "Description of the validation error"
  }
}
```

### 401 Unauthorized
Invalid or missing API key
```json
{
  "error": "Invalid API key",
  "code": "unauthorized"
}
```

### 403 Forbidden
API key lacks access to the project
```json
{
  "error": "Access denied",
  "code": "forbidden"
}
```

### 429 Too Many Requests
Rate limit exceeded
```json
{
  "error": "Rate limit exceeded",
  "code": "rate_limit_exceeded",
  "details": {
    "retryAfter": 60
  }
}
```

### 500 Internal Server Error
Server-side error
```json
{
  "error": "Internal server error",
  "code": "internal_error"
}
```

## Example Usage

### Basic Query
```bash
curl -X POST https://api.cloudindex.ai/public/v1/query \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the capital of France?"
  }'
```

### Advanced Query with Options
```bash
curl -X POST https://api.cloudindex.ai/public/v1/query \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the capital of France?",
    "options": {
      "similarityTopK": 10,
      "alpha": 0.8,
      "rerankingEnabled": true,
      "rerankingTopN": 5,
      "rerankingThreshold": 0.7
    }
  }'
```

## Rate Limiting
- Rate limits are applied per API key
- Limits vary by tier
- Rate limit headers included in responses:
  ```
  X-RateLimit-Limit: requests per window
  X-RateLimit-Remaining: remaining requests
  X-RateLimit-Reset: UTC timestamp when limit resets
  ```

## Best Practices
1. Start with default parameters and adjust based on results
2. Use higher alpha (0.7-0.9) for semantic search
3. Use lower alpha (0.3-0.5) for keyword-focused search
4. Enable reranking for higher precision but slower response
5. Adjust similarityTopK based on your use case:
   - 3-5 for featured snippets
   - 10-20 for search results pages
   - 50+ for comprehensive research
6. Handle rate limits gracefully with exponential backoff
