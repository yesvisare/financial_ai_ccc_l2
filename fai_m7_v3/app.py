"""
FastAPI server for L3 M7.3: Financial Document Parsing & Chunking
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

from src.l3_m7_financial_data_ingestion_compliance import (
    FinancialDocumentChunker,
    chunk_filing,
    extract_sections,
    parse_xbrl_data
)
from config import (
    EDGAR_ENABLED,
    SEC_USER_AGENT,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    OPENAI_ENABLED,
    PINECONE_ENABLED,
    get_config
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M7.3: Financial Document Parsing & Chunking",
    description="Production API for compliance-aware financial document parsing and chunking",
    version="1.0.0"
)


class ChunkRequest(BaseModel):
    """Request model for chunking endpoint."""
    ticker: str = Field(..., description="Stock ticker (e.g., 'MSFT', 'AAPL')")
    filing_type: str = Field(default='10-K', description="Filing type: '10-K', '10-Q', or '8-K'")
    fiscal_year: Optional[int] = Field(None, description="Optional fiscal year filter")
    chunk_size: Optional[int] = Field(None, description="Override default chunk size")
    chunk_overlap: Optional[int] = Field(None, description="Override default chunk overlap")


class ChunkResponse(BaseModel):
    """Response model for chunking endpoint."""
    status: str
    message: str
    num_chunks: int
    chunks: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class SectionRequest(BaseModel):
    """Request model for section extraction."""
    html_content: str = Field(..., description="Raw HTML from SEC filing")
    filing_type: str = Field(default='10-K', description="Filing type")


class SectionResponse(BaseModel):
    """Response model for section extraction."""
    status: str
    sections: Dict[str, str]
    metadata: Dict[str, Any]


@app.get("/")
async def root():
    """Health check endpoint."""
    config = get_config()
    return {
        "status": "online",
        "service": "L3 M7.3: Financial Document Parsing & Chunking",
        "edgar_enabled": EDGAR_ENABLED,
        "openai_enabled": OPENAI_ENABLED,
        "pinecone_enabled": PINECONE_ENABLED,
        "config": config
    }


@app.post("/chunk", response_model=ChunkResponse)
async def chunk_filing_endpoint(request: ChunkRequest):
    """
    Download and chunk SEC filing with compliance-aware boundaries.

    This endpoint:
    1. Downloads SEC filing from EDGAR API (if enabled)
    2. Extracts regulatory sections (Item 1, 1A, 7, 8)
    3. Parses XBRL financial data
    4. Creates compliance-aware chunks with metadata

    Returns chunks with complete metadata for audit trails and temporal queries.
    """
    try:
        logger.info(f"Received chunk request: {request.ticker} - {request.filing_type}")

        # Check if EDGAR service is enabled
        if not EDGAR_ENABLED:
            logger.warning("⚠️ EDGAR service is disabled - using mock data")
            user_agent = None
        else:
            user_agent = SEC_USER_AGENT

        # Use custom chunk size if provided, otherwise use config defaults
        chunk_size = request.chunk_size or CHUNK_SIZE
        chunk_overlap = request.chunk_overlap or CHUNK_OVERLAP

        # Create chunker
        chunker = FinancialDocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Chunk filing
        chunks = chunker.chunk_filing(
            ticker=request.ticker,
            filing_type=request.filing_type,
            fiscal_year=request.fiscal_year,
            user_agent=user_agent
        )

        # Prepare response
        return ChunkResponse(
            status="success",
            message=f"Successfully chunked {request.filing_type} for {request.ticker}",
            num_chunks=len(chunks),
            chunks=chunks[:10],  # Return first 10 chunks in response (full list can be large)
            metadata={
                "ticker": request.ticker,
                "filing_type": request.filing_type,
                "fiscal_year": request.fiscal_year,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "edgar_enabled": EDGAR_ENABLED,
                "total_chunks": len(chunks)
            }
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing chunk request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract-sections", response_model=SectionResponse)
async def extract_sections_endpoint(request: SectionRequest):
    """
    Extract regulatory sections from SEC filing HTML.

    This endpoint extracts sections while preserving regulatory boundaries:
    - Item 1: Business
    - Item 1A: Risk Factors
    - Item 7: MD&A
    - Item 8: Financial Statements

    Preserves SOX Section 404 compliance by maintaining section integrity.
    """
    try:
        logger.info(f"Received section extraction request for {request.filing_type}")

        # Extract sections
        sections = extract_sections(request.html_content, request.filing_type)

        return SectionResponse(
            status="success",
            sections=sections,
            metadata={
                "filing_type": request.filing_type,
                "num_sections": len(sections),
                "section_names": list(sections.keys())
            }
        )

    except Exception as e:
        logger.error(f"Error extracting sections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint.

    Returns configuration status and service availability.
    """
    config = get_config()

    health_status = {
        "status": "healthy",
        "services": {
            "edgar": {
                "enabled": EDGAR_ENABLED,
                "status": "available" if EDGAR_ENABLED else "disabled",
                "user_agent_configured": bool(SEC_USER_AGENT)
            },
            "openai": {
                "enabled": OPENAI_ENABLED,
                "status": "available" if OPENAI_ENABLED else "disabled"
            },
            "pinecone": {
                "enabled": PINECONE_ENABLED,
                "status": "available" if PINECONE_ENABLED else "disabled"
            }
        },
        "config": config
    }

    # Determine overall health
    if not EDGAR_ENABLED:
        health_status["status"] = "degraded"
        health_status["warning"] = "EDGAR service disabled - core functionality limited to mock data"

    return health_status


@app.get("/capabilities")
async def get_capabilities():
    """
    Get API capabilities based on enabled services.

    Returns list of available operations.
    """
    capabilities = {
        "core": [
            "extract_sections",
            "parse_xbrl",
            "chunk_filing"
        ],
        "edgar": [],
        "vector_db": []
    }

    if EDGAR_ENABLED:
        capabilities["edgar"] = [
            "download_real_filings",
            "rate_limited_access"
        ]

    if OPENAI_ENABLED and PINECONE_ENABLED:
        capabilities["vector_db"] = [
            "generate_embeddings",
            "store_in_pinecone",
            "semantic_search"
        ]

    return {
        "capabilities": capabilities,
        "services": {
            "edgar": EDGAR_ENABLED,
            "openai": OPENAI_ENABLED,
            "pinecone": PINECONE_ENABLED
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
