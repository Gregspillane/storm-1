# Quick Start Guide

## 1. Environment Setup
1. Install Python 3.11+
2. Create virtual environment:
   ```shell
   conda create -n storm python=3.11
   conda activate storm
   ```
3. Install requirements:
   ```shell
   pip install -r requirements.txt
   ```

## 2. API Key Setup
1. Create secrets.toml file in project root
2. Add required API keys:
   ```toml
   # For OpenAI
   OPENAI_API_KEY="your_openai_api_key"
   
   # For Bing search
   BING_SEARCH_API_KEY="your_bing_api_key"
   
   # Encoder configuration
   ENCODER_API_TYPE="openai"
   ```

## 3. Running STORM
1. Run basic STORM example with Bing search:
   ```shell
   python examples/storm_examples/run_storm_wiki_gpt.py \
       --output-dir output \
       --retriever bing \
       --do-research \
       --do-generate-outline \
       --do-generate-article \
       --do-polish-article
   ```

2. Run Co-STORM example:
   ```shell
   python examples/costorm_examples/run_costorm_gpt.py \
       --output-dir output \
       --retriever bing
   ```

## 4. Testing Different Configurations
- Modify run_storm_wiki_gpt.py to:
  - Change language models
  - Adjust search parameters
  - Modify output formats

## Troubleshooting
- If you encounter API key errors:
  - Verify keys in secrets.toml
  - Check environment variables
- If you get module not found errors:
  - Verify virtual environment activation
  - Reinstall requirements
