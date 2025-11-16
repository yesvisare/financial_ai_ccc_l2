"""FastAPI application for L3 M9.4: Human-in-the-Loop for High-Stakes Decisions"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from src.l3_m9_financial_compliance_risk import (
    RiskLevel,
    DecisionOutcome,
    classify_risk,
    route_to_reviewer,
    create_audit_entry,
    check_sla_compliance,
    escalate_decision,
    HumanInTheLoopWorkflow,
)
from config import (
    OPENAI_ENABLED,
    validate_configuration,
    MODULE_CONFIG,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M9.4: Human-in-the-Loop for High-Stakes Decisions",
    description="Production API for financial AI workflow orchestration with human oversight",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Global workflow instance (in production, use database persistence)
workflow = HumanInTheLoopWorkflow()


# ═══════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    """Request model for submitting a query for review"""
    user_id: str = Field(..., description="ID of user submitting query")
    query_text: str = Field(..., description="Financial query text")
    transaction_amount: Optional[float] = Field(None, description="Transaction dollar amount")
    action_type: Optional[str] = Field(None, description="Type of action (e.g., 'investment_decision')")
    rag_response: Optional[Dict[str, Any]] = Field(None, description="AI-generated RAG response")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "pm_001",
                "query_text": "Approve $8M increase in Tesla position based on Q3 earnings",
                "transaction_amount": 8000000,
                "action_type": "investment_decision",
                "rag_response": {
                    "recommendation": "Increase position by $8M",
                    "confidence": 0.85
                }
            }
        }


class ReviewSubmission(BaseModel):
    """Request model for submitting a human review"""
    audit_id: str = Field(..., description="Audit entry ID being reviewed")
    reviewer_id: str = Field(..., description="ID of reviewer")
    reviewer_role: str = Field(..., description="Role of reviewer")
    decision_outcome: DecisionOutcome = Field(..., description="Decision outcome")
    supporting_evidence: str = Field(..., description="Analyst's reasoning and evidence")

    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "a1b2c3d4e5f6",
                "reviewer_id": "analyst_senior_42",
                "reviewer_role": "Senior Analyst",
                "decision_outcome": "rejected",
                "supporting_evidence": "Q3 earnings beat driven by $200M one-time tax benefit. Excluding one-time gain, Tesla missed estimates. Proposed trade breaches 5% concentration limit. Recommend modified $4M increase instead."
            }
        }


class RiskClassificationRequest(BaseModel):
    """Request model for risk classification only"""
    query_text: str
    transaction_amount: Optional[float] = None
    action_type: Optional[str] = None
    contains_mnpi: bool = False
    model_confidence: Optional[float] = None


class QueryResponse(BaseModel):
    """Response model for query submission"""
    audit_id: str
    risk_level: str
    risk_reason: str
    routing: Dict[str, Any]
    sla_compliance: Dict[str, Any]
    status: str
    message: str


class ReviewResponse(BaseModel):
    """Response model for review submission"""
    status: str
    audit_id: str
    decision_outcome: str
    message: str


class RiskClassificationResponse(BaseModel):
    """Response model for risk classification"""
    risk_level: str
    reasoning: str


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    service: str
    configuration: Dict[str, str]
    timestamp: str


# ═══════════════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", response_model=HealthResponse)
async def root():
    """
    Health check endpoint with configuration status.

    Returns system status and configuration validation results.
    """
    config_status = validate_configuration()

    return HealthResponse(
        status="online",
        service="L3 M9.4: Human-in-the-Loop for High-Stakes Decisions",
        configuration=config_status,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/submit-query", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
async def submit_query(request: QueryRequest):
    """
    Submit a financial query for human review.

    This endpoint:
    1. Classifies risk level based on transaction size and action type
    2. Routes to appropriate reviewer based on risk
    3. Creates tamper-proof audit trail entry
    4. Calculates SLA requirements
    5. Returns routing information and audit ID

    Args:
        request: Query submission with user_id, query_text, transaction details

    Returns:
        Query response with audit_id, routing, and SLA information
    """
    try:
        logger.info(f"Received query from user {request.user_id}")

        result = workflow.process_query(
            user_id=request.user_id,
            query_text=request.query_text,
            transaction_amount=request.transaction_amount,
            action_type=request.action_type,
            rag_response=request.rag_response
        )

        logger.info(f"Query processed: audit_id={result['audit_id']}, risk={result['risk_level']}")

        return QueryResponse(**result)

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@app.post("/submit-review", response_model=ReviewResponse)
async def submit_review(request: ReviewSubmission):
    """
    Submit a human review decision for a query.

    This endpoint:
    1. Validates reviewer authority for the decision
    2. Updates audit trail with review decision
    3. Recalculates hash chain for tamper detection
    4. Returns confirmation of review submission

    Args:
        request: Review submission with audit_id, reviewer details, and decision

    Returns:
        Review response with confirmation
    """
    try:
        logger.info(f"Received review from {request.reviewer_id} for audit {request.audit_id}")

        result = workflow.submit_review(
            audit_id=request.audit_id,
            reviewer_id=request.reviewer_id,
            reviewer_role=request.reviewer_role,
            decision_outcome=request.decision_outcome,
            supporting_evidence=request.supporting_evidence
        )

        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )

        logger.info(f"Review submitted: {result['decision_outcome']}")

        return ReviewResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit review: {str(e)}"
        )


@app.post("/classify-risk", response_model=RiskClassificationResponse)
async def classify_risk_endpoint(request: RiskClassificationRequest):
    """
    Classify risk level for a query without submitting for review.

    Useful for pre-flight checks and UI risk indicators.

    Args:
        request: Risk classification request with query details

    Returns:
        Risk level and reasoning
    """
    try:
        risk_level, reasoning = classify_risk(
            query_text=request.query_text,
            transaction_amount=request.transaction_amount,
            action_type=request.action_type,
            contains_mnpi=request.contains_mnpi,
            model_confidence=request.model_confidence
        )

        return RiskClassificationResponse(
            risk_level=risk_level.value,
            reasoning=reasoning
        )

    except Exception as e:
        logger.error(f"Error classifying risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify risk: {str(e)}"
        )


@app.get("/audit-trail")
async def get_audit_trail():
    """
    Retrieve complete audit trail with hash chain verification.

    Returns all audit entries with cryptographic verification for
    SOX compliance and regulatory audits.

    Returns:
        Complete audit trail with validation status
    """
    try:
        audit_data = workflow.get_audit_trail()

        logger.info(f"Retrieved audit trail: {audit_data['total_entries']} entries, "
                   f"valid={audit_data['hash_chain_valid']}")

        return audit_data

    except Exception as e:
        logger.error(f"Error retrieving audit trail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit trail: {str(e)}"
        )


@app.get("/audit-entry/{audit_id}")
async def get_audit_entry(audit_id: str):
    """
    Retrieve a specific audit entry by ID.

    Args:
        audit_id: Audit entry identifier

    Returns:
        Complete audit entry details
    """
    try:
        audit_trail_data = workflow.get_audit_trail()
        audit_entry = next(
            (entry for entry in audit_trail_data["audit_trail"] if entry["audit_id"] == audit_id),
            None
        )

        if not audit_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit entry {audit_id} not found"
            )

        return audit_entry

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit entry: {str(e)}"
        )


@app.get("/pending-reviews")
async def get_pending_reviews(reviewer_role: Optional[str] = None):
    """
    Get all pending reviews, optionally filtered by reviewer role.

    Args:
        reviewer_role: Optional role filter (e.g., 'Senior Analyst')

    Returns:
        List of pending review items with SLA status
    """
    try:
        audit_trail_data = workflow.get_audit_trail()
        pending_reviews = []

        for entry in audit_trail_data["audit_trail"]:
            if not entry.get("reviewer_id"):  # No review submitted yet
                # Get routing info to check role
                risk_level = RiskLevel(entry["risk_classification"])
                routing = route_to_reviewer(risk_level=risk_level)

                # Filter by role if specified
                if reviewer_role and routing["reviewer_role"] != reviewer_role:
                    continue

                # Calculate SLA status
                submission_time = datetime.fromisoformat(entry["timestamp"])
                sla_check = check_sla_compliance(
                    submission_time=submission_time,
                    review_time=None,
                    sla_hours=routing["sla_hours"]
                )

                pending_reviews.append({
                    "audit_id": entry["audit_id"],
                    "query_text": entry["query_text"][:100] + "..." if len(entry["query_text"]) > 100 else entry["query_text"],
                    "risk_level": entry["risk_classification"],
                    "assigned_to": routing["reviewer_role"],
                    "sla_status": sla_check,
                    "submitted_at": entry["timestamp"],
                })

        logger.info(f"Retrieved {len(pending_reviews)} pending reviews")

        return {
            "total_pending": len(pending_reviews),
            "reviews": pending_reviews
        }

    except Exception as e:
        logger.error(f"Error retrieving pending reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pending reviews: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """
    Detailed health check for monitoring and alerting.

    Returns:
        System health metrics and component status
    """
    config_status = validate_configuration()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": config_status,
        "metrics": {
            "total_queries_processed": len(workflow.audit_trail),
            "pending_reviews": len([e for e in workflow.audit_trail if not e.get("reviewer_id")]),
            "completed_reviews": len([e for e in workflow.audit_trail if e.get("reviewer_id")]),
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# Startup/Shutdown Events
# ═══════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 60)
    logger.info("L3 M9.4: Human-in-the-Loop for High-Stakes Decisions")
    logger.info("=" * 60)
    logger.info(f"OPENAI Integration: {'Enabled' if OPENAI_ENABLED else 'Disabled'}")
    logger.info(f"Auto-escalation: {'Enabled' if MODULE_CONFIG['enable_auto_escalation'] else 'Disabled'}")
    logger.info(f"Notifications: {'Enabled' if MODULE_CONFIG['enable_notifications'] else 'Disabled'}")
    logger.info("API documentation: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("Shutting down HITL workflow API...")
    logger.info(f"Total queries processed: {len(workflow.audit_trail)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
