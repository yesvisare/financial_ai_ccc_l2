"""
FastAPI application for L3 M7.1: Financial Document Types & Regulatory Context

Provides HTTP API endpoints for:
- Document classification
- Regulatory mapping
- Sensitivity classification
- PII detection and redaction
- Access control validation
- Retention policy queries
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

from src.l3_m7_financial_compliance_controls import (
    classify_document,
    DocumentType,
    SensitivityLevel,
    RegulatoryMapper,
    SensitivityClassifier,
    RetentionPolicyManager,
    PIIDetector,
    AccessController,
    MaterialEventDetector,
    check_access_control,
)
from config import EDGAR_ENABLED, get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M7.1: Financial Document Types & Regulatory Context",
    description="API for compliance-aware financial document classification and regulatory mapping",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Request/Response Models

class ClassifyRequest(BaseModel):
    """Request schema for document classification."""
    document_text: str = Field(..., description="Document content to classify")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata (filename, is_filed, etc.)")
    offline: bool = Field(default=False, description="Skip external API calls if True")


class RegulatoryMappingRequest(BaseModel):
    """Request schema for regulatory mapping."""
    document_type: str = Field(..., description="Document type (e.g., '10-K Annual Report')")


class SensitivityRequest(BaseModel):
    """Request schema for sensitivity classification."""
    document_type: str = Field(..., description="Document type")
    is_filed: bool = Field(default=False, description="Whether document has been publicly filed")


class PIIDetectionRequest(BaseModel):
    """Request schema for PII detection."""
    text: str = Field(..., description="Text to scan for PII")
    redact: bool = Field(default=False, description="Whether to redact detected PII")


class AccessControlRequest(BaseModel):
    """Request schema for access control check."""
    user_role: str = Field(..., description="User role (e.g., 'analyst', 'executive')")
    document_type: str = Field(..., description="Document type")
    is_filed: bool = Field(default=False, description="Whether document is filed")


class RetentionPolicyRequest(BaseModel):
    """Request schema for retention policy query."""
    document_type: str = Field(..., description="Document type")


class MaterialEventRequest(BaseModel):
    """Request schema for material event detection."""
    text: str = Field(..., description="Text to analyze for material events")


# Helper function to convert string to DocumentType enum
def str_to_document_type(doc_type_str: str) -> DocumentType:
    """Convert string to DocumentType enum."""
    for doc_type in DocumentType:
        if doc_type.value.lower() == doc_type_str.lower():
            return doc_type
    raise ValueError(f"Unknown document type: {doc_type_str}")


# API Endpoints

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns service status and configuration.
    """
    config = get_config()
    return {
        "status": "healthy",
        "module": "L3_M7_Financial_Compliance_Controls",
        "edgar_enabled": str(config["edgar_enabled"]),
        "version": "1.0.0",
        "endpoints": {
            "classify": "POST /classify",
            "regulatory_mapping": "POST /regulatory-mapping",
            "sensitivity": "POST /sensitivity",
            "pii_detection": "POST /pii-detection",
            "access_control": "POST /access-control",
            "retention_policy": "POST /retention-policy",
            "material_events": "POST /material-events",
            "config": "GET /config",
        }
    }


@app.get("/config")
async def get_configuration() -> Dict[str, Any]:
    """
    Get current application configuration.

    Returns all configuration values.
    """
    return get_config()


@app.post("/classify")
async def classify_document_endpoint(request: ClassifyRequest) -> Dict[str, Any]:
    """
    Classify a financial document.

    Performs complete analysis including:
    - Document type identification
    - Regulatory framework mapping
    - Sensitivity classification
    - PII detection
    - Material event detection
    - Retention policy
    """
    if not EDGAR_ENABLED and not request.offline:
        logger.warning("EDGAR not enabled - running in offline mode")
        request.offline = True

    try:
        result = classify_document(
            document_text=request.document_text,
            metadata=request.metadata,
            offline=request.offline
        )
        return result

    except Exception as e:
        logger.error(f"Error classifying document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regulatory-mapping")
async def regulatory_mapping_endpoint(request: RegulatoryMappingRequest) -> Dict[str, Any]:
    """
    Get regulatory framework mapping for a document type.

    Returns all applicable regulations and compliance requirements.
    """
    try:
        doc_type = str_to_document_type(request.document_type)
        mapper = RegulatoryMapper()
        summary = mapper.get_compliance_summary(doc_type)

        return summary

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error mapping regulations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sensitivity")
async def sensitivity_classification_endpoint(request: SensitivityRequest) -> Dict[str, Any]:
    """
    Classify document sensitivity level.

    Returns sensitivity classification (Public, MNPI, PII, etc.).
    """
    try:
        doc_type = str_to_document_type(request.document_type)
        classifier = SensitivityClassifier()
        sensitivity = classifier.classify_sensitivity(doc_type, request.is_filed)

        return {
            "document_type": doc_type.value,
            "is_filed": request.is_filed,
            "sensitivity_level": sensitivity.value,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error classifying sensitivity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pii-detection")
async def pii_detection_endpoint(request: PIIDetectionRequest) -> Dict[str, Any]:
    """
    Detect and optionally redact PII from text.

    Returns detected PII instances and optionally redacted text.
    """
    try:
        detector = PIIDetector()

        if request.redact:
            redacted_text, detections = detector.redact_pii(request.text)
            return {
                "pii_detected": len(detections) > 0,
                "pii_count": len(detections),
                "detections": detections,
                "redacted_text": redacted_text,
            }
        else:
            detections = detector.detect_pii(request.text)
            return {
                "pii_detected": len(detections) > 0,
                "pii_count": len(detections),
                "detections": detections,
            }

    except Exception as e:
        logger.error(f"Error detecting PII: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/access-control")
async def access_control_endpoint(request: AccessControlRequest) -> Dict[str, Any]:
    """
    Check access control for user role and document type.

    Returns whether access is allowed and accessible document types.
    """
    try:
        doc_type = str_to_document_type(request.document_type)
        access_allowed = check_access_control(request.user_role, doc_type, request.is_filed)

        controller = AccessController()
        accessible_types = controller.get_accessible_document_types(request.user_role)

        return {
            "user_role": request.user_role,
            "document_type": doc_type.value,
            "is_filed": request.is_filed,
            "access_allowed": access_allowed,
            "accessible_document_types": [dt.value for dt in accessible_types],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error checking access control: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retention-policy")
async def retention_policy_endpoint(request: RetentionPolicyRequest) -> Dict[str, Any]:
    """
    Get retention policy for a document type.

    Returns retention period and compliance requirements.
    """
    try:
        doc_type = str_to_document_type(request.document_type)
        manager = RetentionPolicyManager()
        period = manager.get_retention_period(doc_type)

        return {
            "document_type": doc_type.value,
            "retention_period_years": period if period else "Permanent",
            "compliance_note": "SOX 404 requires 7-year retention for most financial documents",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting retention policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/material-events")
async def material_events_endpoint(request: MaterialEventRequest) -> Dict[str, Any]:
    """
    Detect material events requiring Form 8-K filing.

    Returns detected material events and filing requirements.
    """
    try:
        detector = MaterialEventDetector()
        events = detector.detect_material_events(request.text)

        return {
            "material_events_detected": len(events) > 0,
            "event_count": len(events),
            "events": events,
            "requires_legal_review": len(events) > 0,
            "filing_deadline": "4 business days" if events else None,
        }

    except Exception as e:
        logger.error(f"Error detecting material events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {
        "error": "Endpoint not found",
        "message": "Use GET / to see available endpoints",
        "docs": "/docs for interactive API documentation"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
