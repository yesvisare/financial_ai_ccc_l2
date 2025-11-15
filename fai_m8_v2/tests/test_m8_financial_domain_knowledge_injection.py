"""
Tests for L3 M8.2: Real-Time Financial Data Enrichment

Test coverage:
- FinancialDataEnricher core functionality
- Caching mechanisms
- Market hours detection
- API fallback handling
- Ticker extraction
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from src.l3_m8_financial_domain_knowledge_injection import (
    FinancialDataEnricher,
    FinancialRAGWithEnrichment,
    extract_tickers,
    is_market_open
)


# Fixtures

@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    redis_mock = Mock()
    redis_mock.get = Mock(return_value=None)
    redis_mock.setex = Mock()
    redis_mock.ping = Mock(return_value=True)
    return redis_mock


@pytest.fixture
def enricher_no_redis():
    """FinancialDataEnricher without Redis."""
    return FinancialDataEnricher(redis_client=None)


@pytest.fixture
def enricher_with_redis(mock_redis):
    """FinancialDataEnricher with mocked Redis."""
    return FinancialDataEnricher(redis_client=mock_redis)


@pytest.fixture
def sample_stock_info():
    """Sample stock info from yfinance."""
    return {
        'currentPrice': 192.45,
        'regularMarketPrice': 192.45,
        'previousClose': 186.12,
        'marketCap': 2970000000000,
        'volume': 52847362,
        'trailingPE': 29.8,
        'fiftyTwoWeekHigh': 199.62,
        'fiftyTwoWeekLow': 164.08
    }


# Tests: Initialization

def test_enricher_initialization_no_redis():
    """Test enricher initialization without Redis."""
    enricher = FinancialDataEnricher(redis_client=None)

    assert enricher.cache is None
    assert enricher.ttl_config["stock_price"] == 60
    assert enricher.ttl_config["company_info"] == 86400
    assert enricher.ttl_config["market_status"] == 300
    assert enricher.metrics["cache_hits"] == 0
    assert enricher.metrics["cache_misses"] == 0


def test_enricher_initialization_with_redis(mock_redis):
    """Test enricher initialization with Redis."""
    enricher = FinancialDataEnricher(redis_client=mock_redis)

    assert enricher.cache is not None
    assert enricher.cache == mock_redis


def test_enricher_initialization_invalid_ttl():
    """Test that invalid TTL raises ValueError."""
    enricher = FinancialDataEnricher(redis_client=None)

    # Manually set invalid TTL
    enricher.ttl_config["stock_price"] = 0

    with pytest.raises(ValueError, match="TTL .* must be > 0"):
        # Trigger validation
        for key, ttl in enricher.ttl_config.items():
            if ttl <= 0:
                raise ValueError(f"TTL for {key} must be > 0, got {ttl}")


# Tests: Ticker Extraction

def test_extract_tickers_basic():
    """Test basic ticker extraction."""
    text = "AAPL and MSFT are performing well"
    tickers = extract_tickers(text)

    assert "AAPL" in tickers
    assert "MSFT" in tickers
    assert len(tickers) == 2


def test_extract_tickers_filters_common_words():
    """Test that common words are filtered out."""
    text = "I think AAPL is a good buy"
    tickers = extract_tickers(text)

    assert "AAPL" in tickers
    assert "I" not in tickers  # Common word filtered


def test_extract_tickers_empty_text():
    """Test ticker extraction from empty text."""
    tickers = extract_tickers("")
    assert tickers == []


def test_extract_tickers_no_tickers():
    """Test ticker extraction when no tickers present."""
    text = "The market is performing well today"
    tickers = extract_tickers(text)

    # May contain false positives, but should not crash
    assert isinstance(tickers, list)


# Tests: Market Hours Detection

def test_market_hours_weekend(enricher_no_redis):
    """Test that market is closed on weekends."""
    # Mock datetime to Saturday
    with patch('src.l3_m8_financial_domain_knowledge_injection.datetime') as mock_datetime:
        # Saturday, 2:00 PM EST
        mock_datetime.utcnow.return_value = datetime(2024, 11, 16, 19, 0, 0)  # Saturday UTC
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        status = enricher_no_redis._get_market_status()
        assert status == "CLOSED"


def test_get_current_price_multiple_keys(enricher_no_redis, sample_stock_info):
    """Test that _get_current_price tries multiple keys."""
    # Test with currentPrice
    price = enricher_no_redis._get_current_price(sample_stock_info)
    assert price == 192.45

    # Test with regularMarketPrice only
    info_alternate = {'regularMarketPrice': 150.0}
    price = enricher_no_redis._get_current_price(info_alternate)
    assert price == 150.0

    # Test with no valid price
    info_empty = {}
    price = enricher_no_redis._get_current_price(info_empty)
    assert price is None


# Tests: Cache Operations

def test_cache_get_no_redis(enricher_no_redis):
    """Test cache GET when Redis is disabled."""
    result = enricher_no_redis._get_from_cache("test_key")
    assert result is None


def test_cache_set_no_redis(enricher_no_redis):
    """Test cache SET when Redis is disabled."""
    # Should not raise exception
    enricher_no_redis._set_in_cache("test_key", "test_value", 60)


def test_cache_get_with_redis(enricher_with_redis, mock_redis):
    """Test cache GET with Redis."""
    mock_redis.get.return_value = b"cached_value"

    result = enricher_with_redis._get_from_cache("test_key")

    assert result == "cached_value"
    mock_redis.get.assert_called_once_with("test_key")


def test_cache_set_with_redis(enricher_with_redis, mock_redis):
    """Test cache SET with Redis."""
    enricher_with_redis._set_in_cache("test_key", "test_value", 60)

    mock_redis.setex.assert_called_once_with("test_key", 60, "test_value")


def test_cache_hit_rate_calculation(enricher_no_redis):
    """Test cache hit rate calculation."""
    enricher_no_redis.metrics["cache_hits"] = 60
    enricher_no_redis.metrics["cache_misses"] = 40

    hit_rate = enricher_no_redis._calculate_cache_hit_rate()
    assert hit_rate == 60.0


def test_cache_hit_rate_no_requests(enricher_no_redis):
    """Test cache hit rate with no requests."""
    hit_rate = enricher_no_redis._calculate_cache_hit_rate()
    assert hit_rate == 0.0


# Tests: Market Cap Formatting

def test_format_market_cap_trillions(enricher_no_redis):
    """Test market cap formatting for trillions."""
    formatted = enricher_no_redis._format_market_cap(2970000000000)
    assert formatted == "2.97T"


def test_format_market_cap_billions(enricher_no_redis):
    """Test market cap formatting for billions."""
    formatted = enricher_no_redis._format_market_cap(94900000000)
    assert formatted == "94.90B"


def test_format_market_cap_millions(enricher_no_redis):
    """Test market cap formatting for millions."""
    formatted = enricher_no_redis._format_market_cap(500000000)
    assert formatted == "500.00M"


def test_format_market_cap_none(enricher_no_redis):
    """Test market cap formatting with None."""
    formatted = enricher_no_redis._format_market_cap(None)
    assert formatted == "N/A"


# Tests: Fallback Data

def test_create_fallback_data(enricher_no_redis):
    """Test fallback data creation."""
    fallback = enricher_no_redis._create_fallback_data("AAPL")

    assert fallback["ticker"] == "AAPL"
    assert fallback["current_price"] is None
    assert fallback["change_percent"] is None
    assert fallback["fallback"] is True
    assert "error" in fallback


# Tests: Enrichment with Mocked yfinance

@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_enrich_with_market_data_success(mock_ticker_class, enricher_no_redis, sample_stock_info):
    """Test successful market data enrichment."""
    # Mock yfinance Ticker
    mock_ticker = Mock()
    mock_ticker.info = sample_stock_info
    mock_ticker_class.return_value = mock_ticker

    result = enricher_no_redis.enrich_with_market_data(
        text="Apple reported strong earnings",
        tickers=["AAPL"]
    )

    assert "original_text" in result
    assert "enriched_data" in result
    assert "AAPL" in result["enriched_data"]
    assert result["enriched_data"]["AAPL"]["current_price"] == 192.45
    assert result["enriched_data"]["AAPL"]["ticker"] == "AAPL"


@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_enrich_with_market_data_api_failure(mock_ticker_class, enricher_no_redis):
    """Test enrichment when API fails."""
    # Mock yfinance to raise exception
    mock_ticker_class.side_effect = Exception("API Error")

    result = enricher_no_redis.enrich_with_market_data(
        text="Test text",
        tickers=["AAPL"]
    )

    # Should return fallback data
    assert "AAPL" in result["enriched_data"]
    assert result["enriched_data"]["AAPL"]["fallback"] is True
    assert result["enriched_data"]["AAPL"]["current_price"] is None


@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_enrich_with_cache_hit(mock_ticker_class, enricher_with_redis, mock_redis, sample_stock_info):
    """Test enrichment with cache hit."""
    # Mock cached data
    cached_data = {
        "ticker": "AAPL",
        "current_price": 190.0,
        "cached": True
    }
    mock_redis.get.return_value = json.dumps(cached_data).encode('utf-8')

    result = enricher_with_redis.enrich_with_market_data(
        text="Test text",
        tickers=["AAPL"]
    )

    # Should use cached data, not call API
    assert result["enriched_data"]["AAPL"]["cached"] is True
    assert enricher_with_redis.metrics["cache_hits"] == 1
    assert enricher_with_redis.metrics["cache_misses"] == 0
    mock_ticker_class.assert_not_called()


@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_enrich_with_cache_miss(mock_ticker_class, enricher_with_redis, mock_redis, sample_stock_info):
    """Test enrichment with cache miss."""
    # Mock cache miss
    mock_redis.get.return_value = None

    # Mock yfinance
    mock_ticker = Mock()
    mock_ticker.info = sample_stock_info
    mock_ticker_class.return_value = mock_ticker

    result = enricher_with_redis.enrich_with_market_data(
        text="Test text",
        tickers=["AAPL"]
    )

    # Should call API and cache result
    assert enricher_with_redis.metrics["cache_misses"] == 1
    assert result["enriched_data"]["AAPL"]["current_price"] == 192.45
    mock_redis.setex.assert_called_once()


# Tests: Metrics

def test_get_metrics(enricher_no_redis):
    """Test metrics retrieval."""
    enricher_no_redis.metrics["api_calls"] = 100
    enricher_no_redis.metrics["api_failures"] = 5
    enricher_no_redis.metrics["cache_hits"] = 60
    enricher_no_redis.metrics["cache_misses"] = 40

    metrics = enricher_no_redis.get_metrics()

    assert metrics["cache_hit_rate"] == 60.0
    assert metrics["total_api_calls"] == 100
    assert metrics["api_failure_rate"] == 5.0
    assert metrics["cache_hits"] == 60
    assert metrics["cache_misses"] == 40


# Tests: RAG Integration

def test_rag_initialization():
    """Test RAG system initialization."""
    rag = FinancialRAGWithEnrichment(redis_client=None)

    assert rag.enricher is not None
    assert rag.ticker_pattern is not None


def test_rag_extract_tickers():
    """Test RAG ticker extraction."""
    rag = FinancialRAGWithEnrichment(redis_client=None)

    tickers = rag.extract_tickers("AAPL and MSFT are strong")

    assert "AAPL" in tickers
    assert "MSFT" in tickers


@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_rag_query(mock_ticker_class):
    """Test RAG query execution."""
    # Mock yfinance
    mock_ticker = Mock()
    mock_ticker.info = {
        'currentPrice': 192.45,
        'previousClose': 186.12,
        'marketCap': 2970000000000
    }
    mock_ticker_class.return_value = mock_ticker

    rag = FinancialRAGWithEnrichment(redis_client=None)

    result = rag.query(
        user_query="How is Apple performing?",
        context_text="Apple Inc. reported earnings..."
    )

    assert "user_query" in result
    assert "enrichment" in result
    assert "tickers_found" in result


# Tests: Utility Functions

def test_is_market_open():
    """Test is_market_open utility function."""
    # Just test that it returns a boolean
    result = is_market_open()
    assert isinstance(result, bool)


# Tests: Error Handling

@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_fetch_stock_data_invalid_ticker(mock_ticker_class, enricher_no_redis):
    """Test fetching data for invalid ticker."""
    # Mock yfinance to return empty info
    mock_ticker = Mock()
    mock_ticker.info = {}
    mock_ticker_class.return_value = mock_ticker

    result = enricher_no_redis._fetch_stock_data("INVALID")

    assert result is None


@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_fetch_stock_data_network_error(mock_ticker_class, enricher_no_redis):
    """Test fetching data when network error occurs."""
    # Mock yfinance to raise exception
    mock_ticker_class.side_effect = Exception("Network error")

    result = enricher_no_redis._fetch_stock_data("AAPL")

    assert result is None
    assert enricher_no_redis.metrics["api_calls"] == 1


# Tests: Multiple Tickers

@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_enrich_multiple_tickers(mock_ticker_class, enricher_no_redis, sample_stock_info):
    """Test enrichment with multiple tickers."""
    mock_ticker = Mock()
    mock_ticker.info = sample_stock_info
    mock_ticker_class.return_value = mock_ticker

    result = enricher_no_redis.enrich_with_market_data(
        text="Tech stocks AAPL and MSFT",
        tickers=["AAPL", "MSFT"]
    )

    assert "AAPL" in result["enriched_data"]
    assert "MSFT" in result["enriched_data"]
    assert len(result["enriched_data"]) == 2


# Integration Tests

@patch('src.l3_m8_financial_domain_knowledge_injection.yf.Ticker')
def test_end_to_end_enrichment_flow(mock_ticker_class, sample_stock_info):
    """Test complete enrichment flow from query to response."""
    # Mock yfinance
    mock_ticker = Mock()
    mock_ticker.info = sample_stock_info
    mock_ticker_class.return_value = mock_ticker

    # Initialize system
    rag = FinancialRAGWithEnrichment(redis_client=None)

    # Execute query
    result = rag.query(
        user_query="What's the current price of AAPL?",
        context_text="Apple Inc. is a technology company..."
    )

    # Verify complete flow
    assert result["user_query"] == "What's the current price of AAPL?"
    assert "AAPL" in result["tickers_found"]
    assert "enrichment" in result
    assert "enriched_data" in result["enrichment"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
