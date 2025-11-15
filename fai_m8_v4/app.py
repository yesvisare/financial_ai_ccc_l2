"""
FastAPI application for L3 M8.4: Temporal Financial Information Handling

Production API for fiscal year-aware temporal retrieval of financial documents.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

from config import PINECONE_ENABLED, get_vector_client
from src.l3_m8_financial_domain_knowledge_injection import (
    FiscalCalendarManager,
    TemporalRetriever,
    TemporalValidator,
    fiscal_quarter_to_dates
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M8.4: Temporal Financial Information Handling API",
    description="Production API for fiscal year-aware temporal retrieval of financial documents. "
                "Converts fiscal periods to calendar dates and ensures temporal consistency.",
    version="1.0.0"
)

# Initialize components
fiscal_manager = FiscalCalendarManager()
vector_client = get_vector_client()
temporal_retriever = TemporalRetriever(fiscal_manager, vector_client)
temporal_validator = TemporalValidator(fiscal_manager)


# Request/Response Models

class FiscalPeriodRequest(BaseModel):
    """Request model for fiscal period conversion."""
    ticker: str = Field(..., description="Company ticker symbol (e.g., 'AAPL', 'MSFT')")
    fiscal_year: int = Field(..., description="Fiscal year (e.g., 2024)")
    quarter: str = Field(..., description="Quarter identifier (Q1, Q2, Q3, Q4)")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "fiscal_year": 2024,
                "quarter": "Q3"
            }
        }


class FiscalPeriodResponse(BaseModel):
    """Response model for fiscal period conversion."""
    ticker: str
    fiscal_period: str
    calendar_start: str
    calendar_end: str
    fiscal_year_end: str


class QueryRequest(BaseModel):
    """Request model for fiscal period query."""
    ticker: str = Field(..., description="Company ticker symbol")
    fiscal_year: int = Field(..., description="Fiscal year")
    quarter: str = Field(..., description="Quarter (Q1-Q4)")
    query_text: str = Field(..., description="Search query text")
    top_k: Optional[int] = Field(5, description="Number of results to return")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "fiscal_year": 2024,
                "quarter": "Q3",
                "query_text": "revenue growth",
                "top_k": 5
            }
        }


class PointInTimeRequest(BaseModel):
    """Request model for point-in-time query."""
    ticker: str = Field(..., description="Company ticker symbol")
    as_of_date: str = Field(..., description="Date in YYYY-MM-DD format")
    query_text: str = Field(..., description="Search query text")
    top_k: Optional[int] = Field(5, description="Number of results to return")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "as_of_date": "2023-03-15",
                "query_text": "What was Apple's revenue?",
                "top_k": 5
            }
        }


class ValidationRequest(BaseModel):
    """Request model for temporal consistency validation."""
    documents: List[Dict[str, Any]] = Field(..., description="Documents to validate")
    strict: Optional[bool] = Field(True, description="Strict validation mode")

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {"ticker": "AAPL", "filing_date": "2024-04-01", "fiscal_period": "Q3 FY2024"},
                    {"ticker": "AAPL", "filing_date": "2024-05-15", "fiscal_period": "Q3 FY2024"}
                ],
                "strict": True
            }
        }


class FiscalYearEndRequest(BaseModel):
    """Request model for fiscal year end lookup."""
    ticker: str = Field(..., description="Company ticker symbol")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL"
            }
        }


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "L3 M8.4: Temporal Financial Information Handling",
        "pinecone_enabled": PINECONE_ENABLED,
        "fiscal_companies": len(fiscal_manager.fiscal_year_ends)
    }


@app.post("/convert-fiscal-period", response_model=FiscalPeriodResponse)
async def convert_fiscal_period(request: FiscalPeriodRequest):
    """
    Convert fiscal quarter to calendar date range.

    Maps fiscal periods (e.g., "Q3 FY2024") to actual calendar dates.
    Example: Apple Q3 FY2024 → April 1 - June 30, 2024
    """
    try:
        date_range = fiscal_manager.fiscal_quarter_to_dates(
            request.ticker,
            request.fiscal_year,
            request.quarter
        )

        if not date_range:
            raise HTTPException(
                status_code=404,
                detail=f"Fiscal year data not found for ticker: {request.ticker}"
            )

        start_date, end_date = date_range

        company_data = fiscal_manager.get_fiscal_year_end(request.ticker)
        fy_end = company_data.get("fiscal_year_end") if company_data else "Unknown"

        return FiscalPeriodResponse(
            ticker=request.ticker.upper(),
            fiscal_period=f"{request.quarter} FY{request.fiscal_year}",
            calendar_start=start_date,
            calendar_end=end_date,
            fiscal_year_end=fy_end
        )

    except Exception as e:
        logger.error(f"Fiscal period conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query-fiscal-period")
async def query_fiscal_period(request: QueryRequest):
    """
    Query documents for a specific fiscal period.

    Converts fiscal period to calendar dates and filters vector database
    results to only include documents from that period.
    """
    if not PINECONE_ENABLED:
        logger.warning("Pinecone disabled. Returning simulation.")
        # Still return useful response without actual vector DB
        date_range = fiscal_manager.fiscal_quarter_to_dates(
            request.ticker,
            request.fiscal_year,
            request.quarter
        )

        if not date_range:
            raise HTTPException(
                status_code=404,
                detail=f"Fiscal year data not found for ticker: {request.ticker}"
            )

        return {
            "status": "simulation",
            "message": "Pinecone disabled. Set PINECONE_ENABLED=true in environment.",
            "ticker": request.ticker.upper(),
            "fiscal_period": f"{request.quarter} FY{request.fiscal_year}",
            "calendar_period": f"{date_range[0]} to {date_range[1]}",
            "query": request.query_text,
            "results": []
        }

    try:
        result = temporal_retriever.query_fiscal_period(
            request.ticker,
            request.fiscal_year,
            request.quarter,
            request.query_text,
            request.top_k
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))

        return result

    except Exception as e:
        logger.error(f"Fiscal period query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/point-in-time-query")
async def point_in_time_query_endpoint(request: PointInTimeRequest):
    """
    Execute point-in-time query.

    Retrieves documents filed before a specific date to reconstruct
    historical information state.

    Example: "What was Apple's revenue as of March 15, 2023?"
    → Returns only documents filed before 2023-03-15
    """
    if not PINECONE_ENABLED:
        logger.warning("Pinecone disabled. Returning simulation.")
        return {
            "status": "simulation",
            "message": "Pinecone disabled. Set PINECONE_ENABLED=true in environment.",
            "ticker": request.ticker.upper(),
            "as_of_date": request.as_of_date,
            "query": request.query_text,
            "results": []
        }

    try:
        result = temporal_retriever.point_in_time_query(
            request.ticker,
            request.as_of_date,
            request.query_text,
            request.top_k
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))

        return result

    except Exception as e:
        logger.error(f"Point-in-time query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-temporal-consistency")
async def validate_consistency(request: ValidationRequest):
    """
    Validate temporal consistency across documents.

    Detects issues like:
    - Mixing data from different fiscal periods
    - Comparing documents from different companies
    - Large date ranges indicating stale data
    """
    try:
        result = temporal_validator.validate_temporal_consistency(
            request.documents,
            request.strict
        )

        return result

    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fiscal-year-end")
async def get_fiscal_year_end(request: FiscalYearEndRequest):
    """
    Get fiscal year end information for a company.

    Returns fiscal year end date and metadata.
    """
    try:
        company_data = fiscal_manager.get_fiscal_year_end(request.ticker)

        if not company_data:
            raise HTTPException(
                status_code=404,
                detail=f"Fiscal year data not found for ticker: {request.ticker}"
            )

        return {
            "ticker": request.ticker.upper(),
            "fiscal_year_end": company_data.get("fiscal_year_end"),
            "company_name": company_data.get("company_name"),
            "source": company_data.get("source")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fiscal year end lookup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/companies")
async def list_companies():
    """
    List all companies in fiscal year database.

    Returns count and list of available ticker symbols.
    """
    tickers = list(fiscal_manager.fiscal_year_ends.keys())
    return {
        "count": len(tickers),
        "tickers": sorted(tickers)
    }


@app.get("/health")
async def health_check():
    """
    Extended health check with component status.
    """
    return {
        "status": "healthy",
        "components": {
            "fiscal_manager": {
                "status": "operational",
                "companies_loaded": len(fiscal_manager.fiscal_year_ends)
            },
            "pinecone": {
                "status": "enabled" if PINECONE_ENABLED else "disabled",
                "client_initialized": vector_client is not None
            }
        },
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
