"""
L3 M8.2: Real-Time Financial Data Enrichment

This module implements real-time financial data enrichment for RAG systems in production
financial applications. It integrates live market data APIs with intelligent caching
strategies to balance cost, latency, and data freshness.

Key Features:
- Live market data integration (yfinance, Alpha Vantage)
- Intelligent caching with differentiated TTLs
- Market hours awareness
- Graceful degradation for API failures
- Production-grade error handling

From: FinanceAI M8.2 - Real-Time Financial Data Enrichment
Script: https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_Finance_AI_M8_2_RealTime_Financial_Data_Enrichment (1).md
"""

import yfinance as yf
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

__all__ = [
    "FinancialDataEnricher",
    "FinancialRAGWithEnrichment",
    "extract_tickers",
    "is_market_open"
]


class FinancialDataEnricher:
    """
    Real-time financial data enrichment for RAG systems.

    Design Philosophy:
    - Cache-first: Check Redis before calling APIs (reduces costs)
    - Differentiated TTL: Different data types have different freshness needs
    - Graceful degradation: API failures don't crash the system
    - Market-hours aware: Don't show stale after-hours data as current
    """

    def __init__(self, redis_client: Optional[Any] = None):
        """
        Initialize the FinancialDataEnricher.

        Args:
            redis_client: Optional Redis client for caching. If None, caching is disabled.
        """
        self.cache = redis_client

        # Different TTL for different data types
        # Why these specific values?
        # - stock_price: 1 min = balance between freshness and cache hit rate
        # - company_info: 24 hours = company fundamentals change slowly
        # - market_status: 5 min = reasonable refresh for open/closed status
        self.ttl_config = {
            "stock_price": 60,      # 1 min (real-time trading needs)
            "company_info": 86400,   # 24 hours (changes slowly)
            "market_status": 300     # 5 min (open/closed status)
        }

        # Validate TTL configuration
        for key, ttl in self.ttl_config.items():
            if ttl <= 0:
                raise ValueError(f"TTL for {key} must be > 0, got {ttl}")

        # Track metrics for monitoring (Prometheus integration point)
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "api_calls": 0,
            "api_failures": 0
        }

    def enrich_with_market_data(self, text: str, tickers: List[str]) -> Dict[str, Any]:
        """
        Add real-time market data to retrieved RAG context.

        Args:
            text: Original document text from RAG retrieval
            tickers: List of stock tickers mentioned in the document (e.g., ['AAPL', 'MSFT'])

        Returns:
            Dictionary with original text + enriched market data

        Example:
            >>> enricher.enrich_with_market_data(
            ...     "Apple reported strong earnings...",
            ...     ["AAPL"]
            ... )
            {
                'original_text': 'Apple reported strong earnings...',
                'enriched_data': {
                    'AAPL': {
                        'current_price': 192.45,
                        'change_percent': 3.2,
                        'market_cap': '2.97T',
                        'data_timestamp': '2024-11-15 10:30:00',
                        'market_status': 'OPEN'
                    }
                }
            }
        """
        enriched_data = {}

        for ticker in tickers:
            # Check cache first (reduces API costs and latency)
            # Cache key format: "market:<ticker>:<data_type>"
            # Example: "market:AAPL:price" or "market:AAPL:info"
            cached = self._get_from_cache(f"market:{ticker}")

            if cached:
                # Cache hit - use cached data
                # This is the fast path (10ms vs 200ms for API call)
                enriched_data[ticker] = json.loads(cached)
                self.metrics["cache_hits"] += 1
                logger.info(f"Cache HIT for {ticker} - served in ~10ms")
                continue

            # Cache miss - fetch from API
            # This is the slow path but necessary for freshness
            self.metrics["cache_misses"] += 1
            logger.info(f"Cache MISS for {ticker} - fetching from API (~200ms)")

            try:
                # Fetch stock data from yfinance
                # Why yfinance? Free, reliable, 15-min delay acceptable for research
                stock_data = self._fetch_stock_data(ticker)

                if stock_data:
                    enriched_data[ticker] = stock_data

                    # Store in cache with TTL
                    # TTL ensures stale data automatically expires
                    self._set_in_cache(
                        f"market:{ticker}",
                        json.dumps(stock_data),
                        ttl=self.ttl_config["stock_price"]
                    )
                    logger.info(f"Cached {ticker} with {self.ttl_config['stock_price']}s TTL")
                else:
                    # API returned no data (invalid ticker, API down, etc.)
                    logger.warning(f"No data returned for {ticker}")
                    enriched_data[ticker] = self._create_fallback_data(ticker)

            except Exception as e:
                # API call failed completely - graceful degradation
                # Don't crash the entire RAG system because one stock lookup failed
                self.metrics["api_failures"] += 1
                logger.error(f"Failed to fetch {ticker}: {str(e)}")
                enriched_data[ticker] = self._create_fallback_data(ticker)

        return {
            "original_text": text,
            "enriched_data": enriched_data,
            "enrichment_timestamp": datetime.utcnow().isoformat(),
            "cache_hit_rate": self._calculate_cache_hit_rate()
        }

    def _fetch_stock_data(self, ticker: str) -> Optional[Dict]:
        """
        Fetch stock data from yfinance API.

        Why yfinance specifically?
        - Free (no API key needed)
        - Reliable (widely used in fintech)
        - 15-min delay acceptable for research use cases
        - Good coverage of global stocks

        Production consideration:
        - Add retry logic for transient failures (network blips)
        - Implement rate limiting to avoid hitting yfinance's informal limits
        - Consider fallback to Alpha Vantage if yfinance fails
        """
        self.metrics["api_calls"] += 1

        try:
            # Create yfinance Ticker object
            # This is a lazy-loaded object - no API call yet
            stock = yf.Ticker(ticker)

            # Fetch current info
            # This triggers the actual API call
            info = stock.info

            # Get current price and daily change
            # Use robust key extraction with fallbacks (API schema changes over time)
            current_price = self._get_current_price(info)
            previous_close = info.get('previousClose')

            if not current_price or not previous_close:
                # Invalid ticker or API didn't return price data
                logger.warning(f"Missing price data for {ticker}")
                return None

            # Calculate percentage change
            # Formula: ((current - previous) / previous) * 100
            change_percent = ((current_price - previous_close) / previous_close) * 100

            # Determine market status
            # This prevents showing stale after-hours data as current
            market_status = self._get_market_status()

            return {
                "ticker": ticker,
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "change_percent": round(change_percent, 2),
                "change_dollars": round(current_price - previous_close, 2),
                "market_cap": self._format_market_cap(info.get('marketCap')),
                "volume": info.get('volume'),
                "pe_ratio": info.get('trailingPE'),
                "52_week_high": info.get('fiftyTwoWeekHigh'),
                "52_week_low": info.get('fiftyTwoWeekLow'),
                "data_timestamp": datetime.utcnow().isoformat(),
                "market_status": market_status,
                "data_source": "yfinance (15-min delay)"
            }

        except Exception as e:
            # yfinance can throw various exceptions:
            # - Invalid ticker (AAPL123 doesn't exist)
            # - Rate limit hit (too many requests)
            # - Network timeout
            # Log the error but don't crash - graceful degradation
            logger.error(f"yfinance API error for {ticker}: {str(e)}")
            return None

    def _get_current_price(self, info: Dict) -> Optional[float]:
        """
        Robust price extraction with fallbacks for API schema changes.

        Args:
            info: Stock info dictionary from yfinance

        Returns:
            Current price or None if not found
        """
        # Try multiple keys (API schema changes over time)
        price_keys = ['currentPrice', 'regularMarketPrice', 'price']

        for key in price_keys:
            price = info.get(key)
            if price and price > 0:
                return price

        # No valid price found
        return None

    def _get_market_status(self) -> str:
        """
        Determine if market is open, closed, or in pre/post-market.

        Why this matters:
        - Showing 4 PM data at 10 AM next day as "current" is misleading
        - After-hours prices are less reliable (lower volume)
        - Different exchanges have different hours (NYSE vs TSE vs LSE)

        Production enhancement:
        - Support multiple exchanges (US, Europe, Asia)
        - Account for market holidays
        - Use market calendar APIs for accuracy
        """
        # Cache market status for 5 minutes
        # No need to check every query - status doesn't change that fast
        cached_status = self._get_from_cache("market:status")
        if cached_status:
            return cached_status

        # Simple US market hours check (9:30 AM - 4:00 PM ET)
        # This is simplified - production should use exchange-specific calendars
        now = datetime.utcnow()
        us_time = now - timedelta(hours=5)  # Convert to EST (approximate)

        hour = us_time.hour
        minute = us_time.minute
        weekday = us_time.weekday()

        # Weekend = market closed
        if weekday >= 5:  # Saturday (5) or Sunday (6)
            status = "CLOSED"
        # Check regular trading hours (9:30 AM - 4:00 PM)
        elif (hour == 9 and minute >= 30) or (9 < hour < 16):
            status = "OPEN"
        # Pre-market (4:00 AM - 9:30 AM)
        elif 4 <= hour < 9 or (hour == 9 and minute < 30):
            status = "PRE_MARKET"
        # After-hours (4:00 PM - 8:00 PM)
        elif 16 <= hour < 20:
            status = "AFTER_HOURS"
        else:
            status = "CLOSED"

        # Cache for 5 minutes
        self._set_in_cache("market:status", status, ttl=self.ttl_config["market_status"])

        return status

    def _format_market_cap(self, market_cap: Optional[float]) -> str:
        """
        Format market cap in human-readable form.

        Example:
            2_970_000_000_000 -> "2.97T"
            94_900_000_000 -> "94.9B"
        """
        if not market_cap:
            return "N/A"

        if market_cap >= 1e12:  # Trillions
            return f"{market_cap / 1e12:.2f}T"
        elif market_cap >= 1e9:  # Billions
            return f"{market_cap / 1e9:.2f}B"
        elif market_cap >= 1e6:  # Millions
            return f"{market_cap / 1e6:.2f}M"
        else:
            return f"{market_cap:.2f}"

    def _create_fallback_data(self, ticker: str) -> Dict:
        """
        Create fallback data when API fails.

        Philosophy: Better to show "data unavailable" than crash the system.
        This maintains RAG system availability even if market data APIs are down.
        """
        return {
            "ticker": ticker,
            "current_price": None,
            "change_percent": None,
            "data_timestamp": datetime.utcnow().isoformat(),
            "market_status": "UNKNOWN",
            "error": "Market data temporarily unavailable",
            "fallback": True
        }

    def _get_from_cache(self, key: str) -> Optional[str]:
        """
        Retrieve value from Redis cache.

        Redis operations:
        - GET: O(1) time complexity - very fast
        - Returns None if key doesn't exist or has expired (TTL)
        """
        if not self.cache:
            # Caching disabled
            return None

        try:
            value = self.cache.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            # Redis connection failure - log but don't crash
            logger.error(f"Cache GET error for {key}: {str(e)}")
            return None

    def _set_in_cache(self, key: str, value: str, ttl: int):
        """
        Store value in Redis cache with TTL (Time To Live).

        TTL mechanism:
        - Redis automatically deletes key after TTL seconds
        - No need for manual cleanup
        - Ensures stale data doesn't persist

        Example:
            _set_in_cache("market:AAPL", data, ttl=60)
            After 60 seconds, Redis automatically deletes the key
        """
        if not self.cache:
            # Caching disabled
            return

        try:
            # SETEX = SET with EXpiration
            # Atomic operation - no race condition between SET and EXPIRE
            self.cache.setex(key, ttl, value)
        except Exception as e:
            # Redis connection failure - log but don't crash
            # System continues without caching (slower but functional)
            logger.error(f"Cache SET error for {key}: {str(e)}")

    def _calculate_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate for monitoring.

        Target: 60%+ hit rate
        - Above 60%: Good cost optimization
        - Below 40%: Consider increasing TTLs or pre-fetching popular stocks
        """
        total_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total_requests == 0:
            return 0.0
        return (self.metrics["cache_hits"] / total_requests) * 100

    def get_metrics(self) -> Dict:
        """
        Export metrics for Prometheus monitoring.

        Metrics to track:
        - cache_hit_rate: Measure caching effectiveness
        - api_failure_rate: Detect API reliability issues
        - enrichment_latency: Track performance
        """
        return {
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "total_api_calls": self.metrics["api_calls"],
            "api_failure_rate": (self.metrics["api_failures"] / max(self.metrics["api_calls"], 1)) * 100,
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"]
        }


class FinancialRAGWithEnrichment:
    """
    RAG system with real-time financial data enrichment.

    Workflow:
    1. Query arrives: "How is Apple performing?"
    2. Retrieve relevant documents from vector DB (historical context)
    3. Extract financial entities (Apple -> AAPL ticker)
    4. Enrich with real-time market data
    5. Combine historical + current context
    6. Generate response with LLM

    Note: This is a simplified version. Full implementation requires
    OpenAI and Pinecone credentials configured via environment variables.
    """

    def __init__(self, redis_client: Optional[Any] = None):
        """
        Initialize the RAG system with enrichment.

        Args:
            redis_client: Optional Redis client for caching
        """
        self.enricher = FinancialDataEnricher(redis_client)

        # Ticker symbol regex pattern
        # Matches: AAPL, MSFT, GOOGL (1-5 uppercase letters)
        self.ticker_pattern = re.compile(r'\b[A-Z]{1,5}\b')

    def extract_tickers(self, text: str) -> List[str]:
        """
        Extract ticker symbols from text.

        Args:
            text: Text to extract tickers from

        Returns:
            List of potential ticker symbols

        Example:
            >>> extract_tickers("AAPL and MSFT are performing well")
            ['AAPL', 'MSFT']
        """
        matches = self.ticker_pattern.findall(text)
        # Filter out common false positives (e.g., "I", "A", "US")
        common_words = {'I', 'A', 'US', 'IT', 'IS', 'AT', 'TO', 'OR', 'AND', 'THE'}
        return [m for m in matches if m not in common_words]

    def query(self, user_query: str, context_text: str = "") -> Dict[str, Any]:
        """
        Execute query with financial data enrichment.

        Args:
            user_query: User's natural language query
            context_text: Retrieved document text from RAG system

        Returns:
            Dictionary with enriched context

        Example:
            >>> rag.query(
            ...     "How is Apple performing?",
            ...     "Apple reported strong Q1 2024 earnings..."
            ... )
        """
        # Extract tickers from both query and context
        query_tickers = self.extract_tickers(user_query)
        context_tickers = self.extract_tickers(context_text)
        all_tickers = list(set(query_tickers + context_tickers))

        logger.info(f"Extracted tickers: {all_tickers}")

        # Enrich with real-time market data
        enrichment_result = self.enricher.enrich_with_market_data(
            text=context_text,
            tickers=all_tickers
        )

        return {
            "user_query": user_query,
            "context": context_text,
            "enrichment": enrichment_result,
            "tickers_found": all_tickers
        }


# Utility functions

def extract_tickers(text: str) -> List[str]:
    """
    Extract ticker symbols from text.

    Args:
        text: Text to extract tickers from

    Returns:
        List of potential ticker symbols

    Example:
        >>> extract_tickers("AAPL and MSFT are performing well")
        ['AAPL', 'MSFT']
    """
    ticker_pattern = re.compile(r'\b[A-Z]{1,5}\b')
    matches = ticker_pattern.findall(text)
    # Filter out common false positives
    common_words = {'I', 'A', 'US', 'IT', 'IS', 'AT', 'TO', 'OR', 'AND', 'THE'}
    return [m for m in matches if m not in common_words]


def is_market_open() -> bool:
    """
    Check if US stock market is currently open.

    Returns:
        True if market is open, False otherwise

    Example:
        >>> is_market_open()
        True  # If called during market hours
    """
    enricher = FinancialDataEnricher(redis_client=None)
    status = enricher._get_market_status()
    return status == "OPEN"
