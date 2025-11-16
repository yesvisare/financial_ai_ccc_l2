"""
FastAPI application for L3 M9.2: Financial Compliance Risk - Risk Assessment in Retrieval

Provides REST API endpoints for financial query risk classification and
confidence scoring in RAG systems.

SERVICE: OFFLINE (local processing with optional semantic analysis)

Endpoints:
- GET  /              - Health check
- POST /classify      - Classify query risk level
- POST /confidence    - Compute retrieval confidence score
- POST /compliance    - Run compliance guardrail checks
- GET  /config        - View current configuration
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import os

from src.l3_m9_financial_compliance_risk import (
    classify_query_risk,
    compute_confidence_score,
    RiskLevel,
    SystemAction,
    ComplianceGuardrails
)
from config import get_config, SEMANTIC_ANALYSIS_ENABLED, LLM_CLIENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="L3 M9.2: Financial Compliance Risk API",
    description="Risk assessment and compliance guardrails for financial RAG systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ClassifyRequest(BaseModel):
    """Request model for query risk classification."""
    query: str = Field(..., description="The financial query to classify", min_length=1)
    user_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional user context (account_type, high_risk_query_count, etc.)",
        example={"account_type": "retail", "high_risk_query_count": 2}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Should I buy Tesla stock?",
                "user_context": {
                    "account_type": "retail",
                    "high_risk_query_count": 1
                }
            }
        }


class ClassifyResponse(BaseModel):
    """Response model for query risk classification."""
    risk_level: str
    confidence: float
    reasoning: str
    regulatory_concern: Optional[str]
    system_action: str
    pattern_matches: List[str]
    user_context_adjusted: bool


class ConfidenceRequest(BaseModel):
    """Request model for confidence scoring."""
    retrieval_results: List[Dict[str, Any]] = Field(
        ...,
        description="List of retrieved documents with scores and metadata",
        min_items=1
    )
    query: Optional[str] = Field(None, description="Optional query text for domain relevance")

    class Config:
        json_schema_extra = {
            "example": {
                "retrieval_results": [
                    {
                        "score": 0.92,
                        "source_type": "10-K",
                        "fiscal_period": "2024-Q4",
                        "numerical_claim": "94.9B"
                    },
                    {
                        "score": 0.89,
                        "source_type": "8-K",
                        "fiscal_period": "2024-Q4",
                        "numerical_claim": "94.9B"
                    }
                ],
                "query": "What was Apple's Q4 2024 revenue?"
            }
        }


class ConfidenceResponse(BaseModel):
    """Response model for confidence scoring."""
    overall_score: float
    retrieval_quality: float
    source_diversity: float
    temporal_consistency: float
    citation_agreement: float
    domain_relevance_bonus: float
    threshold_category: str


class ComplianceRequest(BaseModel):
    """Request model for compliance checks."""
    classification: Dict[str, Any] = Field(..., description="Risk classification result")
    documents: Optional[List[Dict[str, Any]]] = Field(None, description="Retrieved documents for MNPI check")


class ComplianceResponse(BaseModel):
    """Response model for compliance checks."""
    ria_compliance: Dict[str, Any]
    mnpi_compliance: Dict[str, Any]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint.

    Returns system status and configuration.
    """
    config = get_config()

    return {
        "status": "healthy",
        "module": "L3_M9_Financial_Compliance_Risk",
        "version": "1.0.0",
        "service": "OFFLINE (local processing)",
        "semantic_analysis_enabled": config["semantic_analysis_enabled"],
        "llm_client_available": config["llm_client_available"]
    }


@app.get("/config", tags=["Configuration"])
def view_config():
    """
    View current configuration.

    Returns detailed configuration status including semantic analysis availability.
    """
    return get_config()


@app.post(
    "/classify",
    response_model=ClassifyResponse,
    tags=["Risk Classification"],
    status_code=status.HTTP_200_OK
)
def classify_query(request: ClassifyRequest):
    """
    Classify a financial query's risk level.

    Determines whether query is:
    - LOW: Educational/factual (e.g., "What is a 10-K filing?")
    - MEDIUM: Comparative analysis (e.g., "Compare Apple and Microsoft revenue")
    - HIGH: Investment advice (e.g., "Should I buy Tesla stock?") - requires RIA

    Returns risk level, confidence, and recommended system action.
    """
    try:
        # Use semantic analysis if available (not required)
        semantic_enabled = SEMANTIC_ANALYSIS_ENABLED and LLM_CLIENT is not None

        result = classify_query_risk(
            query=request.query,
            user_context=request.user_context,
            semantic_analysis=semantic_enabled
        )

        return ClassifyResponse(
            risk_level=result.risk_level.value,
            confidence=result.confidence,
            reasoning=result.reasoning,
            regulatory_concern=result.regulatory_concern,
            system_action=result.system_action.value,
            pattern_matches=result.pattern_matches,
            user_context_adjusted=result.user_context_adjusted
        )

    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification error: {str(e)}"
        )


@app.post(
    "/confidence",
    response_model=ConfidenceResponse,
    tags=["Confidence Scoring"],
    status_code=status.HTTP_200_OK
)
def score_confidence(request: ConfidenceRequest):
    """
    Compute multi-factor confidence score for retrieval results.

    Evaluates:
    - Retrieval quality (40%): Semantic similarity of top documents
    - Source diversity (25%): Variety of source types
    - Temporal consistency (20%): Sources from same fiscal period
    - Citation agreement (15%): Numerical claims match across sources
    - Domain relevance (bonus): Financial keyword matching

    Threshold categories:
    - HIGH (≥0.85): Answer with standard disclaimer
    - MEDIUM (0.70-0.84): Answer with "moderate confidence" warning
    - LOW (0.50-0.69): Warn "information may be incomplete"
    - VERY_LOW (<0.50): Refuse to answer, escalate
    """
    try:
        score = compute_confidence_score(
            retrieval_results=request.retrieval_results,
            query=request.query
        )

        return ConfidenceResponse(
            overall_score=score.overall_score,
            retrieval_quality=score.retrieval_quality,
            source_diversity=score.source_diversity,
            temporal_consistency=score.temporal_consistency,
            citation_agreement=score.citation_agreement,
            domain_relevance_bonus=score.domain_relevance_bonus,
            threshold_category=score.threshold_category
        )

    except Exception as e:
        logger.error(f"Confidence scoring failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confidence scoring error: {str(e)}"
        )


@app.post(
    "/compliance",
    response_model=ComplianceResponse,
    tags=["Compliance Guardrails"],
    status_code=status.HTTP_200_OK
)
def check_compliance(request: ComplianceRequest):
    """
    Run compliance guardrail checks.

    Validates:
    1. RIA Compliance: Blocks investment advice without license
    2. MNPI Compliance: Prevents material non-public information disclosure

    Returns compliance status and required actions.
    """
    try:
        guardrails = ComplianceGuardrails()

        # Reconstruct classification object
        from src.l3_m9_financial_compliance_risk import RiskClassificationResult
        classification = RiskClassificationResult(
            risk_level=RiskLevel(request.classification["risk_level"]),
            confidence=request.classification["confidence"],
            reasoning=request.classification["reasoning"],
            regulatory_concern=request.classification.get("regulatory_concern"),
            system_action=SystemAction(request.classification["system_action"]),
            pattern_matches=request.classification.get("pattern_matches", []),
            user_context_adjusted=request.classification.get("user_context_adjusted", False)
        )

        # Check RIA compliance
        ria_check = guardrails.check_ria_compliance(classification)

        # Check MNPI compliance (if documents provided)
        mnpi_check = {"compliant": True}
        if request.documents:
            mnpi_check = guardrails.check_mnpi_disclosure(request.documents)

        return ComplianceResponse(
            ria_compliance=ria_check,
            mnpi_compliance=mnpi_check
        )

    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance check error: {str(e)}"
        )


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    config = get_config()
    logger.info("=" * 70)
    logger.info("L3 M9.2: Financial Compliance Risk API - STARTED")
    logger.info("=" * 70)
    logger.info(f"Service: OFFLINE (local processing)")
    logger.info(f"Semantic Analysis: {config['semantic_analysis_enabled']}")
    if config['semantic_analysis_enabled']:
        logger.info(f"LLM Provider: {config['llm_provider']}")
        logger.info(f"LLM Client Available: {config['llm_client_available']}")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information."""
    logger.info("API shutting down...")
