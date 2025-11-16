"""
FastAPI wrapper for L3 M10.2: Monitoring Financial RAG Performance

This API provides endpoints for:
- Query tracking and monitoring
- Data staleness checks
- Compliance report generation
- Metrics export (Prometheus-compatible)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from src.l3_m10_financial_rag_in_production import (
    FinancialRAGMonitor,
    DataSource,
    generate_compliance_report
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M10.2: Financial RAG Monitoring",
    description="Monitoring API for Financial RAG systems with compliance tracking",
    version="1.0.0"
)

# Initialize global monitor instance
monitor = FinancialRAGMonitor()


class Citation(BaseModel):
    """Citation model for validation."""
    source: str = Field(..., description="Document source identifier")
    page: int = Field(..., description="Page number")
    quote: str = Field(..., description="Quoted text")
    confidence: Optional[float] = Field(None, description="Citation confidence score")


class QueryTrackRequest(BaseModel):
    """Request model for tracking RAG queries."""
    query: str = Field(..., description="User query string")
    response: str = Field(..., description="RAG system response")
    citations: List[Citation] = Field(..., description="List of citations")
    data_sources: List[str] = Field(
        ...,
        description="Data sources used (Bloomberg, SEC_EDGAR, INTERNAL_MODELS, etc.)"
    )


class StalenessCheckRequest(BaseModel):
    """Request model for checking data staleness."""
    source: str = Field(
        ...,
        description="Data source to check (BLOOMBERG, SEC_EDGAR, INTERNAL_MODELS, etc.)"
    )


class ComplianceReportRequest(BaseModel):
    """Request model for generating compliance reports."""
    start_date: Optional[str] = Field(None, description="Start date (ISO format)")
    end_date: Optional[str] = Field(None, description="End date (ISO format)")


@app.get("/")
def root():
    """API health check."""
    return {
        "status": "running",
        "module": "L3_M10.2: Monitoring Financial RAG Performance",
        "version": "1.0.0",
        "monitoring_active": True
    }


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    metrics = monitor.metrics_collector.get_metrics_summary()
    return {
        "status": "healthy",
        "uptime": "running",
        "metrics_summary": metrics
    }


@app.post("/track_query")
def track_query(request: QueryTrackRequest) -> Dict[str, Any]:
    """
    Track a RAG query with comprehensive monitoring.

    This endpoint:
    1. Measures query latency
    2. Checks for compliance violations (MNPI, privilege, export control)
    3. Verifies citations (1% sampling)
    4. Updates data staleness metrics
    5. Creates SOX 404 audit trail entry

    Returns monitoring results including compliance status and metrics.
    """
    try:
        # Convert source strings to DataSource enums
        data_sources = []
        for source_str in request.data_sources:
            try:
                source = DataSource[source_str.upper().replace(" ", "_")]
                data_sources.append(source)
            except KeyError:
                logger.warning(f"Unknown data source: {source_str}, skipping")

        # Convert Pydantic models to dicts
        citations_dict = [c.dict() for c in request.citations]

        result = monitor.track_query(
            query=request.query,
            response=request.response,
            citations=citations_dict,
            data_sources=data_sources
        )

        return result

    except Exception as e:
        logger.error(f"Error tracking query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check_staleness")
def check_staleness(request: StalenessCheckRequest) -> Dict[str, Any]:
    """
    Check data staleness for a specific source against SLA thresholds.

    SLA Thresholds:
    - Bloomberg: <5 minutes
    - SEC EDGAR: <24 hours
    - Internal Models: <1 hour
    - Market Data: <5 minutes
    - Research Reports: <24 hours
    """
    try:
        # Convert string to DataSource enum
        source = DataSource[request.source.upper().replace(" ", "_")]
        result = monitor.check_data_staleness(source)
        return result

    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data source: {request.source}. "
                   f"Valid sources: {[s.name for s in DataSource]}"
        )
    except Exception as e:
        logger.error(f"Error checking staleness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance_report")
def compliance_report(request: ComplianceReportRequest) -> Dict[str, Any]:
    """
    Generate SOX 404 compliance report.

    The report includes:
    - All six critical metrics (citation accuracy, staleness, MNPI, latency, violations, audit trail)
    - SLA compliance status
    - Audit trail completeness (100% required)
    - 7-year retention status
    """
    try:
        start_date = None
        end_date = None

        if request.start_date:
            start_date = datetime.fromisoformat(request.start_date)
        if request.end_date:
            end_date = datetime.fromisoformat(request.end_date)

        report = generate_compliance_report(monitor, start_date, end_date)
        return report

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def get_metrics() -> Dict[str, Any]:
    """
    Get current metrics summary (Prometheus-compatible format).

    Returns all six critical financial metrics:
    1. Citation Accuracy
    2. Data Staleness (by source)
    3. MNPI Detection Counts
    4. Query Latency (p95)
    5. Compliance Violation Count
    6. Audit Trail Completeness
    """
    try:
        metrics = monitor.metrics_collector.get_metrics_summary()
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit_logs")
def get_audit_logs(limit: int = 100) -> Dict[str, Any]:
    """
    Retrieve recent audit logs (SOX 404 compliance).

    Args:
        limit: Maximum number of logs to return (default: 100)

    Returns:
        List of audit log entries
    """
    try:
        logs = monitor.metrics_collector.metrics["audit_logs"][-limit:]
        return {
            "status": "success",
            "count": len(logs),
            "logs": logs
        }

    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data_sources")
def list_data_sources() -> Dict[str, Any]:
    """
    List all supported data sources with their SLA thresholds.
    """
    sources = {
        "BLOOMBERG": {"name": "Bloomberg Terminal", "sla_hours": 5/60},
        "SEC_EDGAR": {"name": "SEC EDGAR", "sla_hours": 24},
        "INTERNAL_MODELS": {"name": "Internal Financial Models", "sla_hours": 1},
        "MARKET_DATA": {"name": "Real-time Market Data", "sla_hours": 5/60},
        "RESEARCH_REPORTS": {"name": "Research Reports", "sla_hours": 24}
    }

    return {
        "status": "success",
        "sources": sources
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
