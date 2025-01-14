# System Patterns

## Core Architecture
- Modular design with separate components for:
  - Knowledge curation
  - Outline generation
  - Article generation
  - Article polishing
- Interface-driven development with clear module contracts

## STORM Architecture
1. Knowledge Curation Module
   - Collects broad coverage of information
   - Uses perspective-guided question asking
   - Simulates writer-expert conversations

2. Outline Generation Module
   - Organizes collected information hierarchically
   - Creates structured outline for article

3. Article Generation Module
   - Populates outline with collected information
   - Generates citations and references

4. Article Polishing Module
   - Refines article presentation
   - Adds summarization sections
   - Removes duplicate content

## Co-STORM Architecture
- Collaborative discourse protocol
- Turn management policy
- Dynamic mind map for shared conceptual space
- Multiple LLM agent types:
  - Co-STORM experts
  - Moderator
  - Human user

## RAG Architecture Pattern
- Hybrid retrieval combining:
  - Dense vector search for semantic similarity
  - Sparse vector (BM25) search for keyword matching
- Integration points:
  - Knowledge curation module
  - Existing search/retrieval infrastructure
  - Article generation pipeline
- Configuration requirements:
  - API key authentication
  - Search parameter tuning (alpha, topK, etc.)
  - Reranking options
- Error handling strategy:
  - Rate limit management
  - API error recovery
  - Fallback to standard retrieval

## Key Technical Decisions
- Use of DSPy framework for modularity
- Support for multiple language models
- Flexible search/retrieval module integration
- Separation of research and writing stages
- Human-in-the-loop capabilities in Co-STORM

