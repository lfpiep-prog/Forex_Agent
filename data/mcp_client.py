import os
import requests
import logging
from textblob import TextBlob
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load .env explicitly
load_dotenv()

logger = logging.getLogger("MCPClient")

class SentimentType:
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class MCPDataClient:
    
    SENTIMENT_THRESHOLD_BULLISH = 0.15
    SENTIMENT_THRESHOLD_BEARISH = -0.15
    BRAVE_NEWS_URL = "https://api.search.brave.com/res/v1/news/search"

    def __init__(self, server_name: str = "financial-analysis"):
        self.server_name = server_name
        self.api_key = os.environ.get("BRAVE_API_KEY")
        
        if not self.api_key:
            logger.warning("BRAVE_API_KEY not found! Sentiment analysis will assume NEUTRAL.")
        else:
            logger.info(f"Initialized MCP Client using Brave Search.")

    def connect(self) -> bool:
        """Mock connection verify for interface consistency."""
        return True

    def get_sentiment(self, symbol: str) -> str:
        """
        Fetches news for the symbol and calculates sentiment.
        Returns: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        if not self.api_key:
            return SentimentType.NEUTRAL
            
        try:
            results = self._fetch_news(symbol)
            if not results:
                logger.debug(f"[Sentiment] No news found for {symbol}")
                return SentimentType.NEUTRAL
            
            avg_polarity = self._analyze_polarity(results, symbol)
            logger.info(f"[Sentiment] {symbol} Polarity: {avg_polarity:.4f}")
            
            if avg_polarity > self.SENTIMENT_THRESHOLD_BULLISH:
                return SentimentType.BULLISH
            elif avg_polarity < self.SENTIMENT_THRESHOLD_BEARISH:
                return SentimentType.BEARISH
            else:
                return SentimentType.NEUTRAL

        except Exception as e:
            logger.error(f"[Sentiment] Error for {symbol}: {e}")
            return SentimentType.NEUTRAL

    def _fetch_news(self, symbol: str) -> List[Dict[str, Any]]:
        query = f"{symbol} forex news analysis outlook"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {"q": query, "count": 10}
        
        try:
            response = requests.get(self.BRAVE_NEWS_URL, headers=headers, params=params)
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"[Sentiment] API Request Failed: {e}")
            return []

    def _analyze_polarity(self, results: List[Dict[str, Any]], symbol: str) -> float:
        total_polarity = 0.0
        count = 0
        
        for item in results:
            # Combine title and description for better context
            text = f"{item.get('title', '')} {item.get('description', '')}"
            if not text.strip(): 
                continue
                
            blob = TextBlob(text)
            total_polarity += blob.sentiment.polarity
            count += 1
            
        if count == 0: 
            return 0.0
        return total_polarity / count

    def get_macro_data(self) -> Dict[str, Any]:
        """Fetch high-level macro data (Placeholder)."""
        return {}
