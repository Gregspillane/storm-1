import os
import time
import requests
import logging
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from knowledge_storm.interface import Retriever, Information

logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class SearchResult:
    id: str
    score: float
    content: str
    metadata: Dict[str, str]

class RAGRetriever:
    """Implementation of the Retriever interface using RAG API"""
    
    def __init__(self):
        self.api_key = os.getenv('RAG_API_KEY')
        self.base_url = os.getenv('RAG_API_URL')
        
        # Load configuration from secrets.toml
        self.similarity_top_k = int(os.getenv('RAG_RETRIEVER_SIMILARITY_TOP_K', 10))
        self.alpha = float(os.getenv('RAG_RETRIEVER_ALPHA', 0.75))
        self.reranking_enabled = os.getenv('RAG_RETRIEVER_RERANKING_ENABLED', 'true').lower() == 'true'
        self.reranking_top_n = int(os.getenv('RAG_RETRIEVER_RERANKING_TOP_N', 5))
        self.reranking_threshold = float(os.getenv('RAG_RETRIEVER_RERANKING_THRESHOLD', 0.7))
        self.max_retries = int(os.getenv('RAG_RETRIEVER_MAX_RETRIES', 3))
        self.base_delay = float(os.getenv('RAG_RETRIEVER_BASE_DELAY', 1.0))
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'ApiKey {self.api_key}',
            'Content-Type': 'application/json'
        })
        
    def retrieve(self, query: Union[str, List[str]], exclude_urls: List[str] = []) -> List[Information]:
        """Search for relevant documents using the RAG API.
        
        Args:
            query: A string or list of strings containing the search queries
            exclude_urls: A list of URLs to exclude from the search results
            
        Returns:
            A list of SearchResult objects containing the matched documents
        """
        queries = [query] if isinstance(query, str) else query
        all_results = []
        
        logger.info(f"RAG search initiated with {len(queries)} queries")
        logger.debug(f"Search configuration: alpha={self.alpha}, topK={self.similarity_top_k}, "
                    f"reranking={'enabled' if self.reranking_enabled else 'disabled'}")
        
        for q in queries:
            params = {
                'query': q,
                'options': {
                    'similarityTopK': self.similarity_top_k,
                    'alpha': self.alpha,
                    'rerankingEnabled': self.reranking_enabled,
                    'rerankingTopN': self.reranking_top_n,
                    'rerankingThreshold': self.reranking_threshold,
                    'excludeUrls': exclude_urls
                }
            }
            logger.debug(f"Executing RAG query: {q}")
        
            for attempt in range(self.max_retries):
                try:
                    response = self.session.post(
                        f'{self.base_url}/query',
                        json=params
                    )
                    
                    # Handle rate limits
                    if response.status_code == 429:
                        retry_after = float(response.headers.get('Retry-After', self.base_delay))
                        wait_time = retry_after * (2 ** attempt)
                        logger.warning(f"Rate limit hit, waiting {wait_time}s before retry (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                        
                    response.raise_for_status()
                    
                    response_data = response.json()
                    logger.debug(f"RAG API response received with {len(response_data.get('matches', []))} matches")
                    
                    results = []
                    for match in response_data.get('matches', []):
                        try:
                            content = match.get('text', '')
                            if not content:
                                continue
                                
                            info = Information(
                                url=match.get('id', ''),
                                description="",
                                snippets=[content],
                                title="",
                                meta={
                                    "score": match.get('score', 0),
                                    **match.get('metadata', {})
                                }
                            )
                            results.append(info)
                        except Exception as e:
                            logger.warning(f"Error processing match: {str(e)}")
                            continue
                        
                    return results
                    
                except requests.exceptions.RequestException as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"RAG API request failed after {self.max_retries} attempts: {str(e)}")
                        raise Exception(f'API request failed after {self.max_retries} attempts: {str(e)}')
                    logger.warning(f"RAG API request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                    time.sleep(self.base_delay * (2 ** attempt))
        
class PrimaryRAGRetriever(RAGRetriever):
    """Primary implementation combining RAG and web search retrievers"""
    
    def __init__(self, rag_retriever: RAGRetriever, web_retriever: Retriever):
        super().__init__()
        self.rag_retriever = rag_retriever
        self.web_retriever = web_retriever
        self.priority_threshold = float(os.getenv('RAG_RETRIEVER_PRIORITY_THRESHOLD', 0.8))
        self._usage_metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rate_limit_events': 0,
            'fallbacks': 0,
            'response_times': [],
            'result_scores': []
        }

    def collect_and_reset_rm_usage(self) -> Dict[str, int]:
        """Collect and reset usage metrics for the retriever.
        
        Returns:
            Dictionary mapping model names to query counts
        """
        metrics = {
            'rag_api': self._usage_metrics['total_calls'],
            'web_search': self._usage_metrics['fallbacks']
        }
        
        # Store performance metrics in logs
        logger.info(f"RAG API Performance Metrics:")
        logger.info(f"Total calls: {self._usage_metrics['total_calls']}")
        logger.info(f"Successful calls: {self._usage_metrics['successful_calls']}")
        logger.info(f"Failed calls: {self._usage_metrics['failed_calls']}")
        logger.info(f"Rate limit events: {self._usage_metrics['rate_limit_events']}")
        logger.info(f"Fallbacks: {self._usage_metrics['fallbacks']}")
        
        if self._usage_metrics['response_times']:
            avg_response_time = sum(self._usage_metrics['response_times']) / len(self._usage_metrics['response_times'])
            logger.info(f"Average response time: {avg_response_time:.4f}s")
            
        if self._usage_metrics['result_scores']:
            avg_result_score = sum(self._usage_metrics['result_scores']) / len(self._usage_metrics['result_scores'])
            logger.info(f"Average result score: {avg_result_score:.4f}")
        
        # Reset metrics
        self._usage_metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rate_limit_events': 0,
            'fallbacks': 0,
            'response_times': [],
            'result_scores': []
        }
        
        return metrics

    def retrieve(self, query: Union[str, List[str]], exclude_urls: List[str] = []) -> List[Information]:
        """Retrieve information using both RAG and web retrievers.
        
        Args:
            query: A string or list of strings containing the search queries
            exclude_urls: A list of URLs to exclude from the search results
            
        Returns:
            A list of Information objects containing the matched documents
        """
        self._usage_metrics['total_calls'] += 1
        start_time = time.time()
        logger.info("Starting hybrid retrieval with PrimaryRAGRetriever")
        logger.debug(f"Priority threshold: {self.priority_threshold}")
        
        # First try RAG retrieval
        try:
            logger.debug("Attempting RAG retrieval")
            results = self.rag_retriever.retrieve(query, exclude_urls=exclude_urls)
            
            if results:
                # Convert SearchResult to Information if needed
                if isinstance(results[0], SearchResult):
                    top_score = results[0].score
                    results = [Information(
                        url=r.id,
                        description="",
                        snippets=[r.content],
                        title="",
                        meta={"score": r.score, **r.metadata}
                    ) for r in results]
                else:
                    top_score = results[0].meta.get("score", 0)
                
                logger.info(f"RAG retrieval returned {len(results)} results with top score {top_score}")
                
                if top_score >= self.priority_threshold:
                    logger.info("Using RAG results (above threshold)")
                    self._usage_metrics['successful_calls'] += 1
                    self._usage_metrics['result_scores'].append(top_score)
                    self._usage_metrics['response_times'].append(time.time() - start_time)
                    return results
                
                logger.info(f"RAG results below threshold ({top_score} < {self.priority_threshold}), falling back to web search")
                self._usage_metrics['fallbacks'] += 1
            else:
                logger.info("RAG retrieval returned no results, falling back to web search")
                self._usage_metrics['fallbacks'] += 1
                
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {str(e)}, falling back to web search")
            self._usage_metrics['failed_calls'] += 1
            self._usage_metrics['fallbacks'] += 1
            
        # Fallback to web search if RAG fails or results are below threshold
        logger.debug("Executing web search fallback")
        web_results = self.web_retriever.retrieve(query, exclude_urls=exclude_urls)
        logger.info(f"Web search returned {len(web_results)} results")
        self._usage_metrics['response_times'].append(time.time() - start_time)
        return web_results
