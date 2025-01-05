# Technical Context

## Core Technologies
- Python 3.11
- DSPy framework
- Various language models:
  - OpenAI (GPT-3.5, GPT-4)
  - Claude
  - Google
  - DeepSeek
  - Groq
  - Ollama
- Search/Retrieval modules:
  - You.com
  - Bing
  - Serper
  - Brave
  - DuckDuckGo
  - Tavily
  - Azure AI Search

## Development Setup
1. Python environment:
   ```shell
   conda create -n storm python=3.11
   conda activate storm
   pip install -r requirements.txt
   ```

2. Configuration:
   - API keys and settings are stored in secrets.toml
   - Required configurations:
     * OPENAI_API_KEY
     * OPENAI_API_TYPE
     * OPENAI_API_VERSION
     * SERPER_API_KEY
   - The system loads configurations directly from secrets.toml

## Technical Constraints
- Requires API keys for chosen language models and search engines
- Python 3.11+ required
- Specific hardware requirements may vary based on chosen language models
- Internet connection required for search/retrieval modules

## Installation Options
1. Via pip:
   ```shell
   pip install knowledge-storm
   ```

2. From source:
   ```shell
   git clone https://github.com/stanford-oval/storm.git
   cd storm
   pip install -r requirements.txt
   ```

## Questions for User:
1. Are there any specific hardware constraints we should document?
2. Are there any additional technical requirements or constraints we should be aware of?
