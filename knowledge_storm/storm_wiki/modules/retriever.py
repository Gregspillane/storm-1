from typing import Union, List, Dict, Optional
from urllib.parse import urlparse
import time
import requests
import dspy

from ...interface import Retriever, Information
from ...utils import ArticleTextProcessing

# Internet source restrictions according to Wikipedia standard:
# https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources
GENERALLY_UNRELIABLE = {
    "112_Ukraine",
    "Ad_Fontes_Media",
    "AlterNet",
    "Amazon",
    "Anadolu_Agency_(controversial_topics)",
    "Ancestry.com",
    "Answers.com",
    "Antiwar.com",
    "Anti-Defamation_League",
    "arXiv",
    "Atlas_Obscura_places",
    "Bild",
    "Blaze_Media",
    "Blogger",
    "BroadwayWorld",
    "California_Globe",
    "The_Canary",
    "CelebrityNetWorth",
    "CESNUR",
    "ChatGPT",
    "CNET_(November_2022\u2013present)",
    "CoinDesk",
    "Consortium_News",
    "CounterPunch",
    "Correo_del_Orinoco",
    "Cracked.com",
    "Daily_Express",
    "Daily_Kos",
    "Daily_Sabah",
    "The_Daily_Wire",
    "Discogs",
    "Distractify",
    "The_Electronic_Intifada",
    "Encyclopaedia_Metallum",
    "Ethnicity_of_Celebs",
    "Facebook",
    "FamilySearch",
    "Fandom",
    "The_Federalist",
    "Find_a_Grave",
    "Findmypast",
    "Flags_of_the_World",
    "Flickr",
    "Forbes.com_contributors",
    "Fox_News_(politics_and_science)",
    "Fox_News_(talk_shows)",
    "Gawker",
    "GB_News",
    "Geni.com",
    "gnis-class",
    "gns-class",
    "GlobalSecurity.org",
    "Goodreads",
    "Guido_Fawkes",
    "Heat_Street",
    "History",
    "HuffPost_contributors",
    "IMDb",
    "Independent_Media_Center",
    "Inquisitr",
    "International_Business_Times",
    "Investopedia",
    "Jewish_Virtual_Library",
    "Joshua_Project",
    "Know_Your_Meme",
    "Land_Transport_Guru",
    "LinkedIn",
    "LiveJournal",
    "Marquis_Who's_Who",
    "Mashable_sponsored_content",
    "MEAWW",
    "Media_Bias/Fact_Check",
    "Media_Research_Center",
    "Medium",
    "metal-experience",
    "Metro",
    "The_New_American",
    "New_York_Post",
    "NGO_Monitor",
    "The_Onion",
    "Our_Campaigns",
    "PanAm_Post",
    "Patheos",
    "An_Phoblacht",
    "The_Post_Millennial",
    "arXiv",
    "bioRxiv",
    "medRxiv",
    "PeerJ Preprints",
    "Preprints.org",
    "SSRN",
    "PR_Newswire",
    "Quadrant",
    "Quillette",
    "Quora",
    "Raw_Story",
    "Reddit",
    "RedState",
    "ResearchGate",
    "Rolling_Stone_(politics_and_society,_2011\u2013present)",
    "Rolling_Stone_(Culture_Council)",
    "Scribd",
    "Scriptural_texts",
    "Simple_Flying",
    "Sixth_Tone_(politics)",
    "The_Skwawkbox",
    "SourceWatch",
    "Spirit_of_Metal",
    "Sportskeeda",
    "Stack_Exchange",
    "Stack_Overflow",
    "MathOverflow",
    "Ask_Ubuntu",
    "starsunfolded.com",
    "Statista",
    "TASS",
    "The_Truth_About_Guns",
    "TV.com",
    "TV_Tropes",
    "Twitter",
    "X.com",
    "Urban_Dictionary",
    "Venezuelanalysis",
    "VGChartz",
    "VoC",
    "Washington_Free_Beacon",
    "Weather2Travel",
    "The_Western_Journal",
    "We_Got_This_Covered",
    "WhatCulture",
    "Who's_Who_(UK)",
    "WhoSampled",
    "Wikidata",
    "WikiLeaks",
    "Wikinews",
    "Wikipedia",
    "WordPress.com",
    "Worldometer",
    "YouTube",
    "ZDNet",
}
DEPRECATED = {
    "Al_Mayadeen",
    "ANNA_News",
    "Baidu_Baike",
    "China_Global_Television_Network",
    "The_Cradle",
    "Crunchbase",
    "The_Daily_Caller",
    "Daily_Mail",
    "Daily_Star",
    "The_Epoch_Times",
    "FrontPage_Magazine",
    "The_Gateway_Pundit",
    "Global_Times",
    "The_Grayzone",
    "HispanTV",
    "Jihad_Watch",
    "Last.fm",
    "LifeSiteNews",
    "The_Mail_on_Sunday",
    "MintPress_News",
    "National_Enquirer",
    "New_Eastern_Outlook",
    "News_Break",
    "NewsBlaze",
    "News_of_the_World",
    "Newsmax",
    "NNDB",
    "Occupy_Democrats",
    "Office_of_Cuba_Broadcasting",
    "One_America_News_Network",
    "Peerage_websites",
    "Press_TV",
    "Project_Veritas",
    "Rate_Your_Music",
    "Republic_TV",
    "Royal_Central",
    "RT",
    "Sputnik",
    "The_Sun",
    "Taki's_Magazine",
    "Tasnim_News_Agency",
    "Telesur",
    "The_Unz_Review",
    "VDARE",
    "Voltaire_Network",
    "WorldNetDaily",
    "Zero_Hedge",
}
BLACKLISTED = {
    "Advameg",
    "bestgore.com",
    "Breitbart_News",
    "Centre_for_Research_on_Globalization",
    "Examiner.com",
    "Famous_Birthdays",
    "Healthline",
    "InfoWars",
    "Lenta.ru",
    "LiveLeak",
    "Lulu.com",
    "MyLife",
    "Natural_News",
    "OpIndia",
    "The_Points_Guy",
    "The_Points_Guy_(sponsored_content)",
    "Swarajya",
    "Veterans_Today",
    "ZoomInfo",
}


def is_valid_wikipedia_source(url):
    parsed_url = urlparse(url)
    # Check if the URL is from a reliable domain
    combined_set = GENERALLY_UNRELIABLE | DEPRECATED | BLACKLISTED
    for domain in combined_set:
        if domain in parsed_url.netloc:
            return False

    return True


class RAGRetriever(Retriever):
    """Retriever implementation using RAG API for hybrid search"""
    
    def __init__(self):
        self.base_url = "https://api.cloudindex.ai/public/v1"
        self.session = requests.Session()
        self.last_request_time = 0
        self.retry_delay = 1  # initial retry delay in seconds
        
        # Load configuration from secrets.toml
        try:
            import toml
            with open("secrets.toml") as f:
                secrets = toml.load(f)
                self.api_key = secrets["rag"]["api_key"]
        except Exception as e:
            raise RuntimeError("Failed to load RAG API configuration") from e
            
    def _handle_rate_limit(self, response: requests.Response):
        """Handle rate limiting based on API response headers"""
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", self.retry_delay))
            time.sleep(retry_after)
            return True
        return False
        
    def _make_request(self, query: str, options: dict = None):
        """Make API request with error handling"""
        url = f"{self.base_url}/query"
        headers = {
            "Authorization": f"ApiKey {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "options": options or {}
        }
        
        for attempt in range(3):
            try:
                response = self.session.post(url, headers=headers, json=payload)
                
                # Handle rate limiting
                if self._handle_rate_limit(response):
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == 2:  # Last attempt
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                        
                    raise RuntimeError(
                        f"RAG API request failed: {str(e)}. "
                        f"Error details: {error_data.get('error', 'Unknown error')}"
                    )
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

    def retrieve(self, query: str, top_k: int = 10, alpha: float = 0.75) -> List[Information]:
        """Retrieve relevant information using RAG API"""
        options = {
            "similarityTopK": top_k,
            "alpha": alpha,
            "rerankingEnabled": True,
            "rerankingTopN": min(top_k, 5),
            "rerankingThreshold": 0.7
        }
        
        try:
            # Make API request
            response = self._make_request(query, options)
            
            # Process results into STORM format
            results = []
            for match in response.get("matches", []):
                if not self._validate_result(match):
                    continue
                    
                info = Information(
                    content=match["content"],
                    metadata={
                        "source": match["metadata"]["source"],
                        "score": match["score"],
                        "type": match["metadata"]["type"]
                    }
                )
                results.append(info)
                
            return results
            
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve information: {str(e)}")
            
    def _validate_result(self, result: Dict) -> bool:
        """Validate that a result meets STORM's requirements"""
        required_fields = ["content", "metadata", "score"]
        required_metadata = ["source", "type"]
        
        # Check required fields exist
        if not all(field in result for field in required_fields):
            return False
            
        # Check required metadata exists
        if not all(field in result["metadata"] for field in required_metadata):
            return False
            
        # Validate content length
        if len(result["content"]) < 50 or len(result["content"]) > 10000:
            return False
            
        return True
