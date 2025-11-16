"""
FastAPI wrapper for L3_M10.3: Managing Financial Knowledge Base Drift
Provides REST API endpoints for all operations from script

Services: OpenAI (Embeddings) + Pinecone (Vector DB)
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

# CRITICAL: Import from src package
from src.l3_m10_financial_rag_in_production import (
    FinancialKBDriftDetector,
    KnowledgeBaseVersionManager,
    RegulatoryMonitor,
    SelectiveRetrainingPipeline,
    AuditTrailManager,
    detect_drift,
    create_version,
    monitor_regulatory_updates
)

import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="L3_M10.3: Managing Financial Knowledge Base Drift",
    description="Production API for drift detection and knowledge base versioning in financial RAG systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global service instances
openai_client = None
pinecone_index = None
drift_detector = None
version_manager = None
regulatory_monitor = None
retraining_pipeline = None
audit_manager = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global openai_client, pinecone_index, drift_detector, version_manager
    global regulatory_monitor, retraining_pipeline, audit_manager

    logger.info("Starting L3_M10.3 Drift Detection API")

    # Validate configuration
    if not config.validate_config():
        logger.warning("Configuration validation failed - some features may be disabled")

    # Initialize OpenAI client
    openai_client = config.get_openai_client()

    # Initialize Pinecone index
    pinecone_index = config.get_pinecone_index()

    # Initialize service instances
    drift_detector = FinancialKBDriftDetector(
        threshold=config.DRIFT_THRESHOLD,
        openai_client=openai_client,
        pinecone_index=pinecone_index
    )
    version_manager = KnowledgeBaseVersionManager()
    regulatory_monitor = RegulatoryMonitor()
    retraining_pipeline = SelectiveRetrainingPipeline(
        openai_client=openai_client,
        pinecone_index=pinecone_index
    )
    audit_manager = AuditTrailManager()

    logger.info("Services initialized successfully")


# Request/Response Models

class BaselineRequest(BaseModel):
    """Request model for establishing baseline."""
    financial_concepts: Dict[str, str] = Field(
        ...,
        description="Dict mapping concept names to definitions",
        example={
            "Lease Accounting": "ASC 842 requires lessees to recognize...",
            "Revenue Recognition": "ASC 606 establishes five-step model..."
        }
    )


class DriftDetectionRequest(BaseModel):
    """Request model for drift detection."""
    current_concepts: Dict[str, str] = Field(
        ...,
        description="Current concept definitions to check for drift"
    )


class VersionCreateRequest(BaseModel):
    """Request model for version creation."""
    standard_name: str = Field(..., example="ASC 842")
    effective_from: str = Field(..., example="2019-01-01")
    effective_until: Optional[str] = Field(None, example="2024-12-31")
    concept_definitions: Optional[Dict[str, str]] = None


class VersionQueryRequest(BaseModel):
    """Request model for version query."""
    query_date: str = Field(..., example="2023-06-15")
    standard_name: str = Field(..., example="ASC 842")


class RetrainingRequest(BaseModel):
    """Request model for retraining pipeline."""
    drift_concepts: List[str] = Field(
        ...,
        description="Concepts that experienced drift",
        example=["Lease Accounting", "Right-of-Use Asset"]
    )
    document_corpus: List[Dict[str, Any]] = Field(
        ...,
        description="Document corpus with content and metadata"
    )
    batch_size: int = Field(50, description="Batch size for processing")


class RegressionTestRequest(BaseModel):
    """Request model for regression testing."""
    test_queries: List[Dict[str, Any]] = Field(
        ...,
        description="Test queries with metadata"
    )
    expected_results: List[Dict[str, Any]] = Field(
        ...,
        description="Expected results for validation"
    )


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "M10.3 Financial Knowledge Base Drift Detection",
        "version": "1.0.0"
    }


@app.get("/status")
async def get_status():
    """Get system status and service availability."""
    return config.get_service_status()


@app.post("/baseline/establish")
async def establish_baseline(request: BaselineRequest):
    """
    Establish baseline embeddings for financial concepts.

    Creates baseline embeddings that will be used for drift detection.
    Should be run once when initializing the system or after major updates.
    """
    try:
        logger.info(f"Establishing baseline for {len(request.financial_concepts)} concepts")

        result = drift_detector.establish_baseline(request.financial_concepts)

        # Log to audit trail
        audit_manager.log_drift_detection(
            drift_results={"action": "baseline_establishment", "result": result},
            approver="system"
        )

        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Baseline establishment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/drift/detect")
async def detect_drift_endpoint(request: DriftDetectionRequest):
    """
    Detect drift by comparing current concepts to baseline.

    Analyzes semantic changes in concept definitions using embedding similarity.
    Returns severity-classified drift report (HIGH/MEDIUM/LOW).
    """
    try:
        logger.info(f"Detecting drift for {len(request.current_concepts)} concepts")

        drift_results = drift_detector.detect_drift(request.current_concepts)

        # Log to audit trail
        audit_manager.log_drift_detection(
            drift_results=drift_results,
            approver=None  # Set approver in production
        )

        return {
            "status": "success",
            "drift_report": drift_results
        }
    except Exception as e:
        logger.error(f"Drift detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/version/create")
async def create_version_endpoint(request: VersionCreateRequest):
    """
    Create new knowledge base version with effective dates.

    Implements version control for regulatory standards with temporal query routing.
    Supports multiple concurrent standards (e.g., ASC 840 and ASC 842).
    """
    try:
        logger.info(f"Creating version: {request.standard_name}")

        version = version_manager.create_version(
            standard_name=request.standard_name,
            effective_from=request.effective_from,
            effective_until=request.effective_until,
            concept_definitions=request.concept_definitions
        )

        # Log to audit trail
        audit_manager.log_version_creation(
            version_metadata=version,
            approver="system"  # Set actual approver in production
        )

        return {
            "status": "success",
            "version": version
        }
    except Exception as e:
        logger.error(f"Version creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/version/query")
async def query_version(request: VersionQueryRequest):
    """
    Get appropriate knowledge base version for a given date.

    Implements temporal query routing based on transaction dates.
    Returns the version of standards effective on the specified date.
    """
    try:
        logger.info(f"Querying version for {request.standard_name} on {request.query_date}")

        version = version_manager.get_version_for_date(
            query_date=request.query_date,
            standard_name=request.standard_name
        )

        if not version:
            raise HTTPException(
                status_code=404,
                detail=f"No version found for {request.standard_name} on {request.query_date}"
            )

        return {
            "status": "success",
            "version": version
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Version query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/version/list")
async def list_versions():
    """
    List all knowledge base versions.

    Returns all versions with their effective date ranges and metadata.
    """
    try:
        versions = version_manager.list_versions()
        return {
            "status": "success",
            "versions": versions,
            "count": len(versions)
        }
    except Exception as e:
        logger.error(f"Version listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regulatory/check")
async def check_regulatory_updates():
    """
    Check FASB, SEC, and AICPA sources for regulatory updates.

    Automated monitoring of regulatory websites for new standards,
    amendments, and effective date announcements.
    """
    try:
        logger.info("Checking regulatory sources for updates")

        updates = regulatory_monitor.check_for_updates()

        return {
            "status": "success",
            "updates": updates
        }
    except Exception as e:
        logger.error(f"Regulatory check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrain/execute")
async def execute_retraining(request: RetrainingRequest, background_tasks: BackgroundTasks):
    """
    Execute selective retraining pipeline for affected documents.

    Identifies and re-embeds only documents affected by drifted concepts.
    Processes in batches for efficiency (default: 50 documents/batch).
    """
    try:
        logger.info(f"Starting retraining for {len(request.drift_concepts)} drifted concepts")

        # Identify affected documents
        affected_docs = retraining_pipeline.identify_affected_documents(
            drift_concepts=request.drift_concepts,
            document_corpus=request.document_corpus
        )

        # Execute retraining (can be run in background for large batches)
        result = retraining_pipeline.retrain_documents(
            documents=affected_docs,
            batch_size=request.batch_size
        )

        return {
            "status": "success",
            "affected_documents": len(affected_docs),
            "retraining_result": result
        }
    except Exception as e:
        logger.error(f"Retraining failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regression/validate")
async def validate_regression(request: RegressionTestRequest):
    """
    Run regression tests to validate updates don't break existing queries.

    Tests historical queries against expected results after knowledge base updates.
    Ensures zero historical query breakage for SOX compliance.
    """
    try:
        logger.info(f"Running regression tests for {len(request.test_queries)} queries")

        from src.l3_m10_financial_rag_in_production import validate_regression

        results = validate_regression(
            test_queries=request.test_queries,
            expected_results=request.expected_results
        )

        return {
            "status": "success",
            "test_results": results
        }
    except Exception as e:
        logger.error(f"Regression validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit/trail")
async def get_audit_trail(event_type: Optional[str] = None):
    """
    Retrieve audit trail entries.

    Returns immutable audit records with cryptographic hashing for SOX compliance.
    Supports filtering by event type (drift_detection, version_creation).
    """
    try:
        logger.info(f"Retrieving audit trail (filter: {event_type})")

        trail = audit_manager.get_audit_trail(event_type=event_type)

        return {
            "status": "success",
            "audit_trail": trail,
            "count": len(trail)
        }
    except Exception as e:
        logger.error(f"Audit trail retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """
    Get current configuration settings.

    Returns drift threshold, batch size, and other operational parameters.
    """
    return {
        "drift_threshold": config.DRIFT_THRESHOLD,
        "retraining_batch_size": config.RETRAINING_BATCH_SIZE,
        "log_level": config.LOG_LEVEL,
        "openai_enabled": config.OPENAI_ENABLED,
        "pinecone_enabled": config.PINECONE_ENABLED
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
