"""
FastAPI application for M7.2: PII Detection & Financial Data Redaction

Provides REST API endpoints for financial document PII redaction with:
- Document redaction endpoint (/redact)
- Batch processing endpoint (/batch)
- Audit trail retrieval (/audit)
- Health check endpoint (/)

Usage:
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from src.l3_m7_financial_data_ingestion_compliance import (
    FinancialPIIRedactor,
    redact_document
)
from config import PRESIDIO_ENABLED, CONFIDENCE_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="M7.2: PII Detection & Financial Data Redaction",
    description="Production API for automated financial PII detection and redaction using Microsoft Presidio",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize global redactor instance
redactor = None
if PRESIDIO_ENABLED:
    try:
        redactor = FinancialPIIRedactor(confidence_threshold=CONFIDENCE_THRESHOLD)
        logger.info("✅ FinancialPIIRedactor initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize redactor: {e}")


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RedactRequest(BaseModel):
    """Request model for document redaction."""
    text: str = Field(..., description="Document text to redact", min_length=1)
    doc_id: str = Field(..., description="Unique document identifier")
    user_id: str = Field(default="system", description="User performing redaction")


class RedactResponse(BaseModel):
    """Response model for document redaction."""
    redacted_text: str
    entities_redacted: int
    entity_breakdown: Dict[str, int]
    audit_id: Optional[str]
    status: str


class BatchRedactRequest(BaseModel):
    """Request model for batch redaction."""
    documents: List[Dict[str, str]] = Field(
        ...,
        description="List of documents with 'text' and 'doc_id' fields"
    )
    user_id: str = Field(default="system", description="User performing redaction")


class BatchRedactResponse(BaseModel):
    """Response model for batch redaction."""
    results: List[RedactResponse]
    total_processed: int
    total_entities_redacted: int
    status: str


class HealthResponse(BaseModel):
    """Health check response."""
    message: str
    presidio_status: str
    confidence_threshold: float
    version: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint.

    Returns service status and configuration.
    """
    presidio_status = "enabled" if PRESIDIO_ENABLED else "disabled"

    if PRESIDIO_ENABLED and redactor is None:
        presidio_status = "enabled_but_failed"

    return HealthResponse(
        message="M7.2: PII Detection & Financial Data Redaction API",
        presidio_status=presidio_status,
        confidence_threshold=CONFIDENCE_THRESHOLD,
        version="1.0.0"
    )


@app.post("/redact", response_model=RedactResponse, status_code=status.HTTP_200_OK)
def redact_endpoint(request: RedactRequest):
    """
    Redact PII from a single financial document.

    **Detects and redacts:**
    - Social Security Numbers (SSN)
    - Tax IDs (EIN)
    - Routing Numbers (ABA)
    - Account Numbers
    - Credit Card Numbers
    - Phone Numbers, Email Addresses
    - Names and Addresses

    **Returns:**
    - Redacted document text
    - Count of entities redacted
    - Breakdown by entity type
    - Audit trail ID

    **Example:**
    ```json
    {
        "text": "SSN: 123-45-6789, Account: 98765432",
        "doc_id": "DOC001",
        "user_id": "analyst_01"
    }
    ```
    """
    if not PRESIDIO_ENABLED:
        logger.warning("⚠️ Presidio disabled - returning mock response")
        return RedactResponse(
            redacted_text=request.text,
            entities_redacted=0,
            entity_breakdown={},
            audit_id=None,
            status="skipped_presidio_disabled"
        )

    if redactor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Presidio redactor not initialized. Check server logs."
        )

    try:
        result = redactor.redact_document(
            text=request.text,
            doc_id=request.doc_id,
            user_id=request.user_id
        )

        return RedactResponse(
            redacted_text=result["redacted_text"],
            entities_redacted=result["entities_redacted"],
            entity_breakdown=result["entity_breakdown"],
            audit_id=result["audit_id"],
            status="success"
        )

    except Exception as e:
        logger.error(f"❌ Error redacting document {request.doc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redaction failed: {str(e)}"
        )


@app.post("/batch", response_model=BatchRedactResponse, status_code=status.HTTP_200_OK)
def batch_redact_endpoint(request: BatchRedactRequest):
    """
    Redact PII from multiple documents in batch.

    **Input:**
    ```json
    {
        "documents": [
            {"text": "SSN: 123-45-6789", "doc_id": "DOC001"},
            {"text": "Account: 98765432", "doc_id": "DOC002"}
        ],
        "user_id": "analyst_01"
    }
    ```

    **Returns:**
    - List of redaction results
    - Total documents processed
    - Total entities redacted across all documents
    """
    if not PRESIDIO_ENABLED:
        logger.warning("⚠️ Presidio disabled - returning mock response")
        return BatchRedactResponse(
            results=[],
            total_processed=0,
            total_entities_redacted=0,
            status="skipped_presidio_disabled"
        )

    if redactor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Presidio redactor not initialized. Check server logs."
        )

    results = []
    total_entities = 0

    for doc in request.documents:
        try:
            result = redactor.redact_document(
                text=doc.get("text", ""),
                doc_id=doc.get("doc_id", "UNKNOWN"),
                user_id=request.user_id
            )

            results.append(RedactResponse(
                redacted_text=result["redacted_text"],
                entities_redacted=result["entities_redacted"],
                entity_breakdown=result["entity_breakdown"],
                audit_id=result["audit_id"],
                status="success"
            ))

            total_entities += result["entities_redacted"]

        except Exception as e:
            logger.error(f"❌ Error processing document {doc.get('doc_id')}: {e}")
            results.append(RedactResponse(
                redacted_text=doc.get("text", ""),
                entities_redacted=0,
                entity_breakdown={},
                audit_id=None,
                status=f"error: {str(e)}"
            ))

    return BatchRedactResponse(
        results=results,
        total_processed=len(results),
        total_entities_redacted=total_entities,
        status="success"
    )


@app.get("/audit")
def get_audit_trail():
    """
    Retrieve complete audit trail.

    **Returns:**
    - List of all redaction operations
    - Timestamps, document hashes, entity counts
    - User IDs for compliance tracking

    **Use for:**
    - SOX Section 404 compliance (7-year retention)
    - GLBA audit requirements
    - GDPR data processing records
    """
    if not PRESIDIO_ENABLED or redactor is None:
        return JSONResponse(
            content={
                "audit_trail": [],
                "total_entries": 0,
                "status": "presidio_disabled"
            }
        )

    audit_trail = redactor.get_audit_trail()

    return JSONResponse(
        content={
            "audit_trail": audit_trail,
            "total_entries": len(audit_trail),
            "status": "success"
        }
    )


@app.get("/health")
def health():
    """Simple health check for load balancers."""
    return {"status": "healthy"}


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup configuration."""
    logger.info("=" * 60)
    logger.info("M7.2: PII Detection & Financial Data Redaction API")
    logger.info("=" * 60)
    logger.info(f"Presidio Status: {'Enabled' if PRESIDIO_ENABLED else 'Disabled'}")
    logger.info(f"Confidence Threshold: {CONFIDENCE_THRESHOLD}")

    if PRESIDIO_ENABLED:
        if redactor:
            logger.info("✅ Redactor initialized successfully")
        else:
            logger.error("❌ Redactor initialization failed")
    else:
        logger.warning("⚠️ Running in OFFLINE mode")
        logger.warning("⚠️ Set PRESIDIO_ENABLED=true in .env to enable redaction")

    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down PII Redaction API")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
