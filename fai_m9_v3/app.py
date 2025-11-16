"""
FastAPI application for L3 M9.3: Regulatory Constraints in LLM Outputs

This API provides endpoints for:
- Filtering LLM outputs for MNPI violations
- Injecting regulatory disclaimers
- Enforcing information barriers
- Retrieving compliance audit logs
"""

import logging
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# Import from package
from src.l3_m9_financial_compliance_risk import (
    ComplianceFilter,
    MNPIDetector,
    DisclaimerManager,
    InformationBarrier,
    filter_llm_output
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M9.3: Regulatory Constraints API",
    description="Compliance filtering for financial LLM outputs (MNPI, disclaimers, Safe Harbor)",
    version="1.0.0"
)

# Global compliance filter instance
compliance_filter = ComplianceFilter()


# Request/Response Models
class Citation(BaseModel):
    """Citation metadata from M9.1"""
    source_id: str
    source_type: str
    document_url: Optional[str] = None
    filing_date: Optional[str] = None
    data_namespace: str = "public"


class PublicDisclosure(BaseModel):
    """Public disclosure record"""
    event_type: str
    date: str
    document_type: str
    ticker: Optional[str] = None


class FilterRequest(BaseModel):
    """Request model for compliance filtering"""
    llm_output: str = Field(..., description="Raw LLM response text")
    citations: List[Citation] = Field(default_factory=list, description="Citation metadata from M9.1")
    user_id: str = Field(default="anonymous", description="User identifier")
    risk_score: Optional[float] = Field(None, description="Risk score from M9.2 (0.0-1.0)")
    public_disclosures: Optional[List[PublicDisclosure]] = Field(None, description="Public disclosure records")


class FilterResponse(BaseModel):
    """Response model for compliance filtering"""
    allowed: bool
    filtered_text: Optional[str] = None
    blocked_reason: Optional[str] = None
    disclaimers_added: Optional[List[str]] = None
    mnpi_check: Optional[Dict[str, Any]] = None
    citations_filtered: int = 0
    audit_logged: bool = True


class MNPICheckRequest(BaseModel):
    """Request model for MNPI detection only"""
    text: str
    citations: List[Citation] = Field(default_factory=list)
    public_disclosures: Optional[List[PublicDisclosure]] = None


class DisclaimerRequest(BaseModel):
    """Request model for disclaimer injection"""
    text: str


class AuditLogQuery(BaseModel):
    """Query parameters for audit log retrieval"""
    user_id: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)


# Health Check
@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "L3_M9.3_Regulatory_Constraints",
        "version": "1.0.0",
        "services": {
            "mnpi_detector": "active",
            "disclaimer_manager": "active",
            "information_barrier": "active"
        }
    }


# Main Compliance Filter Endpoint
@app.post("/filter", response_model=FilterResponse)
def filter_compliance(request: FilterRequest):
    """
    Filter LLM output through complete compliance pipeline.

    This endpoint runs:
    1. Information barrier checks (Chinese Walls)
    2. MNPI detection (three-layer)
    3. Disclaimer injection (FINRA, Safe Harbor)
    4. Compliance audit logging

    Args:
        request: Filter request with LLM output and metadata

    Returns:
        Filtering result with compliance status
    """
    try:
        logger.info(f"Processing filter request for user={request.user_id}")

        # Convert Pydantic models to dicts
        citations_dict = [c.dict() for c in request.citations]
        disclosures_dict = [d.dict() for d in request.public_disclosures] if request.public_disclosures else None

        # Run compliance filter
        result = compliance_filter.filter_output(
            llm_output=request.llm_output,
            citations=citations_dict,
            user_id=request.user_id,
            risk_score=request.risk_score,
            public_disclosures=disclosures_dict
        )

        logger.info(f"Filter result: allowed={result['allowed']}")
        return FilterResponse(**result)

    except Exception as e:
        logger.error(f"Filter processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Compliance filtering failed: {str(e)}")


# MNPI Detection Only
@app.post("/mnpi/detect")
def detect_mnpi(request: MNPICheckRequest):
    """
    Detect MNPI violations only (without full compliance pipeline).

    Useful for testing or pre-screening content before full filtering.

    Args:
        request: MNPI check request

    Returns:
        MNPI detection results
    """
    try:
        logger.info("Processing MNPI detection request")

        citations_dict = [c.dict() for c in request.citations]
        disclosures_dict = [d.dict() for d in request.public_disclosures] if request.public_disclosures else None

        mnpi_detector = MNPIDetector()
        result = mnpi_detector.detect(
            text=request.text,
            citations=citations_dict,
            public_disclosures=disclosures_dict
        )

        return {
            "success": True,
            "mnpi_detection": result
        }

    except Exception as e:
        logger.error(f"MNPI detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Disclaimer Injection Only
@app.post("/disclaimers/inject")
def inject_disclaimers(request: DisclaimerRequest):
    """
    Inject required disclaimers into text (without MNPI checks).

    Adds FINRA Rule 2210 and Safe Harbor disclaimers as needed.

    Args:
        request: Text to process

    Returns:
        Text with disclaimers added
    """
    try:
        logger.info("Processing disclaimer injection request")

        disclaimer_manager = DisclaimerManager()
        filtered_text, added_disclaimers = disclaimer_manager.add_disclaimers(request.text)

        return {
            "success": True,
            "original_text": request.text,
            "filtered_text": filtered_text,
            "disclaimers_added": added_disclaimers
        }

    except Exception as e:
        logger.error(f"Disclaimer injection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Information Barrier Check
@app.post("/barriers/check")
def check_information_barrier(
    user_id: str,
    data_namespace: str,
    user_permissions: Optional[Dict[str, List[str]]] = None
):
    """
    Check if user has access to data namespace (Chinese Wall enforcement).

    Args:
        user_id: User identifier
        data_namespace: Data classification level
        user_permissions: Optional permission mappings

    Returns:
        Access decision
    """
    try:
        logger.info(f"Checking information barrier: user={user_id}, namespace={data_namespace}")

        barrier = InformationBarrier(user_permissions=user_permissions)
        has_access = barrier.check_access(user_id, data_namespace)

        return {
            "success": True,
            "user_id": user_id,
            "data_namespace": data_namespace,
            "access_granted": has_access
        }

    except Exception as e:
        logger.error(f"Information barrier check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Audit Log Retrieval
@app.post("/audit/logs")
def get_audit_logs(query: AuditLogQuery):
    """
    Retrieve compliance audit logs.

    Logs include all detected violations, blocked responses, and compliance actions.
    Critical for SEC investigations and regulatory audits.

    Args:
        query: Audit log query parameters

    Returns:
        Audit log records
    """
    try:
        logger.info(f"Retrieving audit logs: user_id={query.user_id}, limit={query.limit}")

        logs = compliance_filter.get_audit_log(user_id=query.user_id)

        # Apply limit
        limited_logs = logs[-query.limit:] if len(logs) > query.limit else logs

        return {
            "success": True,
            "total_records": len(logs),
            "returned_records": len(limited_logs),
            "logs": limited_logs
        }

    except Exception as e:
        logger.error(f"Audit log retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch Processing
@app.post("/filter/batch")
def filter_batch(requests: List[FilterRequest]):
    """
    Process multiple compliance filtering requests in batch.

    Useful for bulk content validation or historical data review.

    Args:
        requests: List of filter requests

    Returns:
        Batch processing results
    """
    try:
        logger.info(f"Processing batch filter request: {len(requests)} items")

        results = []
        for idx, req in enumerate(requests):
            try:
                citations_dict = [c.dict() for c in req.citations]
                disclosures_dict = [d.dict() for d in req.public_disclosures] if req.public_disclosures else None

                result = compliance_filter.filter_output(
                    llm_output=req.llm_output,
                    citations=citations_dict,
                    user_id=req.user_id,
                    risk_score=req.risk_score,
                    public_disclosures=disclosures_dict
                )

                results.append({
                    "index": idx,
                    "success": True,
                    "result": result
                })

            except Exception as item_error:
                logger.error(f"Batch item {idx} failed: {item_error}")
                results.append({
                    "index": idx,
                    "success": False,
                    "error": str(item_error)
                })

        successful = sum(1 for r in results if r["success"])

        return {
            "total_items": len(requests),
            "successful": successful,
            "failed": len(requests) - successful,
            "results": results
        }

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
