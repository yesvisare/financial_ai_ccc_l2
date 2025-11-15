"""
FastAPI application for L3 M7.4: Audit Trail & Document Provenance

This API provides SOX-compliant audit trail endpoints for financial RAG systems.
All business logic is implemented in the src.l3_m7_financial_data_ingestion_compliance package.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

from src.l3_m7_financial_data_ingestion_compliance import FinancialAuditTrail
from config import get_database_url, validate_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration on startup
try:
    validate_config()
    DATABASE_URL = get_database_url()
except Exception as e:
    logger.error(f"Configuration validation failed: {str(e)}")
    raise

# Initialize audit trail
audit_trail = FinancialAuditTrail(DATABASE_URL)

app = FastAPI(
    title="L3 M7.4: Audit Trail & Document Provenance",
    description="SOX-compliant audit trail API for financial RAG systems",
    version="1.0.0"
)


# Request/Response Models
class LogEventRequest(BaseModel):
    """Generic event logging request."""
    event_type: str = Field(..., description="Type of event (e.g., 'document_ingested')")
    event_data: Dict[str, Any] = Field(..., description="Event-specific data")
    user_id: Optional[str] = Field(None, description="User identifier")


class DocumentIngestedRequest(BaseModel):
    """Request for logging document ingestion."""
    document_id: str
    source_url: str
    filing_date: str
    document_type: str
    user_id: Optional[str] = None


class DocumentProcessedRequest(BaseModel):
    """Request for logging document processing completion."""
    document_id: str
    chunks_created: int
    embeddings_created: int
    processing_time_seconds: float
    user_id: Optional[str] = None


class QueryRequest(BaseModel):
    """Request for logging a RAG query."""
    query_text: str
    query_id: str
    user_id: str


class RetrievalRequest(BaseModel):
    """Request for logging retrieval results."""
    query_id: str
    chunks_retrieved: List[Dict[str, Any]]
    user_id: str


class GenerationRequest(BaseModel):
    """Request for logging answer generation."""
    query_id: str
    answer: str
    citations: List[str]
    model_used: str
    user_id: str


class ComplianceReportRequest(BaseModel):
    """Request for generating compliance report."""
    start_date: str  # ISO format datetime
    end_date: str    # ISO format datetime


# API Endpoints
@app.get("/")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Status information and total event count
    """
    try:
        event_count = audit_trail.get_event_count()
        return {
            "status": "healthy",
            "module": "L3 M7.4: Audit Trail & Document Provenance",
            "database": "connected",
            "total_events": event_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Database connection failed")


@app.post("/log_event")
async def log_event(request: LogEventRequest):
    """
    Log a generic audit event.

    Example:
        POST /log_event
        {
            "event_type": "custom_event",
            "event_data": {"key": "value"},
            "user_id": "user@company.com"
        }
    """
    try:
        event_hash = audit_trail.log_event(
            request.event_type,
            request.event_data,
            request.user_id
        )
        return {
            "status": "logged",
            "event_hash": event_hash,
            "event_type": request.event_type
        }
    except Exception as e:
        logger.error(f"Failed to log event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/log_document_ingested")
async def log_document_ingested(request: DocumentIngestedRequest):
    """
    Log when a financial document is ingested into the system.

    Example:
        POST /log_document_ingested
        {
            "document_id": "aapl_10k_2024",
            "source_url": "https://sec.gov/...",
            "filing_date": "2024-03-15",
            "document_type": "10-K",
            "user_id": "pipeline@company.com"
        }
    """
    try:
        event_hash = audit_trail.log_document_ingested(
            request.document_id,
            request.source_url,
            request.filing_date,
            request.document_type,
            request.user_id
        )
        return {
            "status": "logged",
            "event_hash": event_hash,
            "event_type": "document_ingested",
            "document_id": request.document_id
        }
    except Exception as e:
        logger.error(f"Failed to log document ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/log_document_processed")
async def log_document_processed(request: DocumentProcessedRequest):
    """
    Log when document processing completes.

    Example:
        POST /log_document_processed
        {
            "document_id": "aapl_10k_2024",
            "chunks_created": 487,
            "embeddings_created": 487,
            "processing_time_seconds": 12.5,
            "user_id": "pipeline@company.com"
        }
    """
    try:
        event_hash = audit_trail.log_document_processed(
            request.document_id,
            request.chunks_created,
            request.embeddings_created,
            request.processing_time_seconds,
            request.user_id
        )
        return {
            "status": "logged",
            "event_hash": event_hash,
            "event_type": "document_processed",
            "document_id": request.document_id
        }
    except Exception as e:
        logger.error(f"Failed to log document processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/log_query")
async def log_query(request: QueryRequest):
    """
    Log a user query.

    Example:
        POST /log_query
        {
            "query_text": "What was Apple's revenue in Q4 2024?",
            "query_id": "q_20241115_001",
            "user_id": "analyst@company.com"
        }
    """
    try:
        event_hash = audit_trail.log_query(
            request.query_text,
            request.query_id,
            request.user_id
        )
        return {
            "status": "logged",
            "event_hash": event_hash,
            "event_type": "query_executed",
            "query_id": request.query_id
        }
    except Exception as e:
        logger.error(f"Failed to log query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/log_retrieval")
async def log_retrieval(request: RetrievalRequest):
    """
    Log retrieval results (provenance tracking).

    Example:
        POST /log_retrieval
        {
            "query_id": "q_20241115_001",
            "chunks_retrieved": [
                {
                    "chunk_id": "aapl_10k_2024#chunk_127",
                    "page_num": 28,
                    "score": 0.87,
                    "text_preview": "Revenue for Q4 2024..."
                }
            ],
            "user_id": "analyst@company.com"
        }
    """
    try:
        event_hash = audit_trail.log_retrieval(
            request.query_id,
            request.chunks_retrieved,
            request.user_id
        )
        return {
            "status": "logged",
            "event_hash": event_hash,
            "event_type": "retrieval_completed",
            "query_id": request.query_id,
            "chunks_count": len(request.chunks_retrieved)
        }
    except Exception as e:
        logger.error(f"Failed to log retrieval: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/log_generation")
async def log_generation(request: GenerationRequest):
    """
    Log answer generation with citations.

    Example:
        POST /log_generation
        {
            "query_id": "q_20241115_001",
            "answer": "According to the 10-K filing...",
            "citations": ["[1] AAPL 10-K FY2024, p.28"],
            "model_used": "gpt-4",
            "user_id": "analyst@company.com"
        }
    """
    try:
        event_hash = audit_trail.log_generation(
            request.query_id,
            request.answer,
            request.citations,
            request.model_used,
            request.user_id
        )
        return {
            "status": "logged",
            "event_hash": event_hash,
            "event_type": "generation_completed",
            "query_id": request.query_id
        }
    except Exception as e:
        logger.error(f"Failed to log generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/verify_integrity")
async def verify_integrity():
    """
    Verify the integrity of the entire audit trail.

    Returns:
        Verification results with any broken chain links
    """
    try:
        is_valid, broken_events = audit_trail.verify_integrity()
        return {
            "status": "verified" if is_valid else "compromised",
            "chain_valid": is_valid,
            "broken_events": broken_events,
            "total_events": audit_trail.get_event_count()
        }
    except Exception as e:
        logger.error(f"Integrity verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance_report")
async def compliance_report(request: ComplianceReportRequest):
    """
    Generate a compliance audit report for a date range.

    Example:
        POST /compliance_report
        {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-12-31T23:59:59Z"
        }
    """
    try:
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))

        report = audit_trail.generate_compliance_report(start_date, end_date)
        return report
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
