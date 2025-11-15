"""
FastAPI service for L3 M8.2: Real-Time Financial Data Enrichment

This API provides endpoints for enriching financial queries with real-time market data.
Supports integration with RAG systems for production financial applications.

Author: TechVoyageHub
License: MIT
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging

from src.l3_m8_financial_domain_knowledge_injection import (
    FinancialDataEnricher,
    FinancialRAGWithEnrichment,
    extract_tickers,
    is_market_open
)
from config import get_redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M8.2: Real-Time Financial Data Enrichment",
    description="Production API for enriching RAG systems with real-time financial market data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Request/Response Models

class EnrichmentRequest(BaseModel):
    """Request model for enrichment endpoint."""
    text: str = Field(..., description="Document text to enrich", min_length=1)
    tickers: List[str] = Field(..., description="List of stock tickers (e.g., ['AAPL', 'MSFT'])")

    class Config:
        schema_extra = {
            "example": {
                "text": "Apple reported strong Q1 2024 earnings with revenue of $94.9B",
                "tickers": ["AAPL"]
            }
        }


class EnrichmentResponse(BaseModel):
    """Response model for enrichment endpoint."""
    original_text: str
    enriched_data: Dict[str, Any]
    enrichment_timestamp: str
    cache_hit_rate: float


class QueryRequest(BaseModel):
    """Request model for RAG query endpoint."""
    query: str = Field(..., description="User's natural language query", min_length=1)
    context: Optional[str] = Field(default="", description="Retrieved RAG document context")

    class Config:
        schema_extra = {
            "example": {
                "query": "How is Apple performing today?",
                "context": "Apple Inc. is a technology company..."
            }
        }


class QueryResponse(BaseModel):
    """Response model for RAG query endpoint."""
    user_query: str
    context: str
    enrichment: Dict[str, Any]
    tickers_found: List[str]


class TickerExtractionRequest(BaseModel):
    """Request model for ticker extraction endpoint."""
    text: str = Field(..., description="Text to extract tickers from", min_length=1)

    class Config:
        schema_extra = {
            "example": {
                "text": "AAPL and MSFT are performing well in the tech sector"
            }
        }


class TickerExtractionResponse(BaseModel):
    """Response model for ticker extraction endpoint."""
    text: str
    tickers: List[str]


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""
    cache_hit_rate: float
    total_api_calls: int
    api_failure_rate: float
    cache_hits: int
    cache_misses: int


class MarketStatusResponse(BaseModel):
    """Response model for market status endpoint."""
    is_open: bool
    status: str
    timestamp: str


# Initialize services
redis_client = get_redis_client()
enricher = FinancialDataEnricher(redis_client)
rag_system = FinancialRAGWithEnrichment(redis_client)


# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "L3 M8.2: Real-Time Financial Data Enrichment",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "enrich": "/enrich",
            "query": "/query",
            "extract_tickers": "/extract-tickers",
            "market_status": "/market-status",
            "metrics": "/metrics"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring systems.

    Returns:
        Health status of the service
    """
    try:
        # Check Redis connection if enabled
        if redis_client:
            redis_client.ping()
            redis_status = "connected"
        else:
            redis_status = "disabled"

        return {
            "status": "healthy",
            "service": "financial_data_enrichment",
            "redis": redis_status,
            "timestamp": FinancialDataEnricher(None)._get_market_status()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/enrich", response_model=EnrichmentResponse, tags=["Enrichment"])
async def enrich_data(request: EnrichmentRequest):
    """
    Enrich document text with real-time market data for specified tickers.

    This endpoint fetches current stock prices, market caps, and other financial
    metrics for the specified tickers and enriches the provided text.

    Args:
        request: EnrichmentRequest containing text and tickers

    Returns:
        EnrichmentResponse with enriched data

    Example:
        ```bash
        curl -X POST http://localhost:8000/enrich \\
          -H "Content-Type: application/json" \\
          -d '{
            "text": "Apple reported strong earnings",
            "tickers": ["AAPL"]
          }'
        ```
    """
    try:
        logger.info(f"Enrichment request for tickers: {request.tickers}")
        result = enricher.enrich_with_market_data(request.text, request.tickers)
        return EnrichmentResponse(**result)
    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def rag_query(request: QueryRequest):
    """
    Execute RAG query with automatic ticker extraction and enrichment.

    This endpoint:
    1. Extracts tickers from the query and context
    2. Fetches real-time market data for those tickers
    3. Enriches the context with current data
    4. Returns the enriched context ready for LLM processing

    Args:
        request: QueryRequest containing user query and context

    Returns:
        QueryResponse with enriched context

    Example:
        ```bash
        curl -X POST http://localhost:8000/query \\
          -H "Content-Type: application/json" \\
          -d '{
            "query": "How is Apple performing?",
            "context": "Apple Inc. is a tech company..."
          }'
        ```
    """
    try:
        logger.info(f"RAG query: {request.query[:50]}...")
        result = rag_system.query(request.query, request.context)
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/extract-tickers", response_model=TickerExtractionResponse, tags=["Utilities"])
async def extract_tickers_endpoint(request: TickerExtractionRequest):
    """
    Extract stock ticker symbols from text.

    Uses regex pattern matching to identify potential ticker symbols (1-5 uppercase letters)
    and filters out common false positives.

    Args:
        request: TickerExtractionRequest containing text

    Returns:
        TickerExtractionResponse with extracted tickers

    Example:
        ```bash
        curl -X POST http://localhost:8000/extract-tickers \\
          -H "Content-Type: application/json" \\
          -d '{
            "text": "AAPL and MSFT are strong performers"
          }'
        ```
    """
    try:
        tickers = extract_tickers(request.text)
        logger.info(f"Extracted tickers: {tickers}")
        return TickerExtractionResponse(text=request.text, tickers=tickers)
    except Exception as e:
        logger.error(f"Ticker extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.get("/market-status", response_model=MarketStatusResponse, tags=["Utilities"])
async def get_market_status():
    """
    Get current US stock market status (OPEN, CLOSED, PRE_MARKET, AFTER_HOURS).

    This endpoint checks the current time against US market hours (9:30 AM - 4:00 PM ET)
    and returns the market status.

    Returns:
        MarketStatusResponse with market status

    Example:
        ```bash
        curl http://localhost:8000/market-status
        ```
    """
    try:
        is_open_now = is_market_open()
        # Get detailed status
        temp_enricher = FinancialDataEnricher(None)
        status = temp_enricher._get_market_status()

        from datetime import datetime
        return MarketStatusResponse(
            is_open=is_open_now,
            status=status,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Market status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """
    Get enrichment service metrics for monitoring and optimization.

    Metrics include:
    - cache_hit_rate: Percentage of requests served from cache (target: 60%+)
    - total_api_calls: Total number of external API calls made
    - api_failure_rate: Percentage of API calls that failed
    - cache_hits: Number of cache hits
    - cache_misses: Number of cache misses

    Returns:
        MetricsResponse with service metrics

    Example:
        ```bash
        curl http://localhost:8000/metrics
        ```
    """
    try:
        metrics = enricher.get_metrics()
        return MetricsResponse(**metrics)
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics failed: {str(e)}")


@app.get("/ticker/{ticker}", tags=["Data"])
async def get_ticker_data(ticker: str):
    """
    Get real-time data for a specific ticker symbol.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)

    Returns:
        Current market data for the ticker

    Example:
        ```bash
        curl http://localhost:8000/ticker/AAPL
        ```
    """
    try:
        ticker = ticker.upper()
        logger.info(f"Fetching data for ticker: {ticker}")
        result = enricher.enrich_with_market_data("", [ticker])

        if ticker not in result["enriched_data"]:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")

        return result["enriched_data"][ticker]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ticker data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Data retrieval failed: {str(e)}")


# Exception handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
