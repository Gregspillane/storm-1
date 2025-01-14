# System Patterns

## RAG Retrieval Patterns

### Hybrid Search Pattern
- Combines dense vector search with sparse keyword search
- Uses alpha parameter to control weighting between methods
- Automatically falls back to keyword search if vector search fails

### Rate Limiting Pattern
- Implements exponential backoff for rate limited requests
- Uses Retry-After header when available
- Logs retry attempts and wait times

### Fallback Pattern
- Attempts RAG retrieval first
- Falls back to web search if:
  - RAG results are below confidence threshold
  - RAG API returns no results
  - RAG API fails with error

### Information Conversion Pattern
- Converts raw API results to Information objects
- Preserves metadata and scores
- Handles both single and multiple queries

## Error Handling Patterns
- Graceful degradation when APIs fail
- Comprehensive logging of errors
- Automatic retries for transient failures
- Fallback to alternative retrieval methods

## Configuration Patterns
- Centralized configuration via environment variables
- Sensible defaults for all parameters
- Override options for specific use cases
- Validation of configuration values
