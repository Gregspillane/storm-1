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

## Key Technical Decisions
- Use of DSPy framework for modularity
- Support for multiple language models
- Flexible search/retrieval module integration
- Separation of research and writing stages
- Human-in-the-loop capabilities in Co-STORM

