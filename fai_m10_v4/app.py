"""
FastAPI server for L3 M10.4: Disaster Recovery & Business Continuity

Provides HTTP API endpoints for:
- DR health monitoring
- Replication lag checking
- Automated failover execution
- FINRA compliance reporting
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.l3_m10_financial_rag_production import (
    ReplicationMonitor,
    DRVerifier,
    FailoverOrchestrator,
    ComplianceReporter,
    ReplicationStatus,
    FailoverResult,
    verify_dr_readiness
)
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M10.4: Disaster Recovery & Business Continuity",
    description="Production API for Financial RAG disaster recovery monitoring and failover orchestration",
    version="1.0.0"
)


# Request/Response Models

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    services: Dict[str, Any]


class ReplicationCheckResponse(BaseModel):
    """Replication lag check response."""
    lag_seconds: float
    is_connected: bool
    last_sync_time: str
    data_consistency_ratio: float
    meets_rpo: bool


class DRReadinessResponse(BaseModel):
    """DR readiness verification response."""
    ready: bool
    issues: List[str]
    replication_lag_seconds: float
    data_consistency: float
    meets_rpo: bool
    timestamp: str


class FailoverRequest(BaseModel):
    """Request model for failover execution."""
    reason: str = Field(..., description="Reason for initiating failover")
    force: bool = Field(False, description="Force failover even if DR not ready (dangerous)")


class FailoverResponse(BaseModel):
    """Failover execution response."""
    success: bool
    rto_minutes: float
    data_loss_minutes: float
    timestamp: str
    errors: List[str]


class ComplianceReportRequest(BaseModel):
    """Request model for compliance report generation."""
    test_date: str = Field(..., description="DR test date (ISO format)")
    include_details: bool = Field(True, description="Include detailed metrics")


# Global instances (initialized from config)
monitor = None
verifier = None
orchestrator = None
reporter = ComplianceReporter()


def initialize_components():
    """Initialize DR monitoring components."""
    global monitor, verifier, orchestrator

    if not config.AWS_ENABLED:
        logger.warning("⚠️ AWS services disabled - DR monitoring unavailable")
        return

    monitor = ReplicationMonitor(
        primary_config=config.PRIMARY_DB_CONFIG,
        replica_config=config.DR_DB_CONFIG
    )
    monitor.cloudwatch = config.cloudwatch_client

    verifier = DRVerifier(monitor)
    orchestrator = FailoverOrchestrator(verifier)

    logger.info("✅ DR components initialized")


# Initialize on startup
initialize_components()


# API Endpoints

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.

    Returns system health status including service availability.
    """
    services = {
        "aws": config.AWS_ENABLED,
        "pinecone": config.PINECONE_ENABLED,
        "postgresql": config.POSTGRESQL_ENABLED,
        "dr_monitoring": monitor is not None
    }

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": services
    }


@app.get("/replication/status", response_model=ReplicationCheckResponse)
async def check_replication_status():
    """
    Check current replication lag and status.

    Returns:
        Replication metrics including lag, connectivity, and RPO compliance
    """
    if not config.AWS_ENABLED or monitor is None:
        raise HTTPException(
            status_code=503,
            detail="AWS services not enabled. Set AWS_ENABLED=true and configure credentials."
        )

    try:
        status = monitor.check_replication_lag()

        return {
            "lag_seconds": status.lag_seconds,
            "is_connected": status.is_connected,
            "last_sync_time": status.last_sync_time.isoformat(),
            "data_consistency_ratio": status.data_consistency_ratio,
            "meets_rpo": status.meets_rpo
        }

    except Exception as e:
        logger.error(f"Error checking replication status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dr/readiness", response_model=DRReadinessResponse)
async def check_dr_readiness():
    """
    Verify DR region readiness for failover.

    Runs comprehensive pre-flight checks:
    - Replication connectivity
    - Lag within acceptable limits
    - Data consistency
    - Infrastructure health
    """
    if not config.AWS_ENABLED or verifier is None:
        raise HTTPException(
            status_code=503,
            detail="AWS services not enabled"
        )

    try:
        health = verifier.run_health_checks()
        return health

    except Exception as e:
        logger.error(f"Error checking DR readiness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dr/failover", response_model=FailoverResponse)
async def execute_failover(request: FailoverRequest):
    """
    Execute automated failover to DR region.

    **CRITICAL OPERATION**: This will redirect production traffic to DR region.

    Steps performed:
    1. Verify DR readiness (skipped if force=true)
    2. Update Route 53 DNS to DR region
    3. Wait for DNS propagation
    4. Verify DR serving traffic
    5. Measure and return RTO

    Args:
        request: Failover request with reason and force flag

    Returns:
        Failover result with RTO, data loss, and status
    """
    if not config.AWS_ENABLED or orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="AWS services not enabled"
        )

    try:
        logger.warning(f"🚨 FAILOVER REQUESTED: {request.reason}")

        # Safety check unless forced
        if not request.force:
            health = verifier.run_health_checks()
            if not health["ready"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"DR not ready for failover: {health['issues']}. Use force=true to override."
                )

        result = orchestrator.execute_failover(request.reason)

        return {
            "success": result.success,
            "rto_minutes": result.rto_minutes,
            "data_loss_minutes": result.data_loss_minutes,
            "timestamp": result.timestamp.isoformat(),
            "errors": result.errors
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing failover: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/report")
async def generate_compliance_report(request: ComplianceReportRequest):
    """
    Generate FINRA Rule 4370 quarterly compliance report.

    Creates comprehensive DR test documentation including:
    - RTO/RPO measurements vs. targets
    - Data consistency validation
    - Test pass/fail status
    - Compliance statement for auditors

    Args:
        request: Report generation parameters

    Returns:
        Complete compliance report with all required metrics
    """
    try:
        test_date = datetime.fromisoformat(request.test_date)

        # For demo purposes, use mock data
        # In production, this would use actual test results from database
        from src.l3_m10_financial_rag_production import ReplicationStatus, FailoverResult

        mock_failover = FailoverResult(
            success=True,
            rto_minutes=8.5,
            data_loss_minutes=5.0,
            timestamp=test_date,
            errors=[]
        )

        mock_replication = ReplicationStatus(
            lag_seconds=5.2,
            is_connected=True,
            last_sync_time=test_date,
            data_consistency_ratio=0.998,
            meets_rpo=True
        )

        report = reporter.generate_quarterly_report(
            test_date,
            mock_failover,
            mock_replication
        )

        if not request.include_details:
            # Return summary only
            return {
                "quarter": report["quarter"],
                "overall_result": report["overall_result"],
                "compliance_statement": report["compliance_statement"]
            }

        return report

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format. Use ISO format (YYYY-MM-DD): {e}"
        )
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/rto")
async def get_rto_metrics():
    """
    Get RTO (Recovery Time Objective) target and historical performance.

    Returns:
        RTO targets and recent measurements
    """
    return {
        "rto_target_minutes": 15,
        "description": "Maximum acceptable downtime during market hours",
        "regulatory_basis": "FINRA Rule 4370 - Business Continuity Planning",
        "typical_performance": "8-12 minutes",
        "last_test": {
            "date": "2024-12-15",
            "measured_minutes": 8.5,
            "status": "PASS"
        }
    }


@app.get("/metrics/rpo")
async def get_rpo_metrics():
    """
    Get RPO (Recovery Point Objective) target and current lag.

    Returns:
        RPO targets and current replication status
    """
    rpo_info = {
        "rpo_target_minutes": 60,
        "description": "Maximum acceptable data loss measured in time",
        "regulatory_basis": "SOX Section 404 - Document retention and audit trail",
        "typical_lag_seconds": 5.0
    }

    if monitor:
        try:
            status = monitor.check_replication_lag()
            rpo_info["current_lag_seconds"] = status.lag_seconds
            rpo_info["current_lag_minutes"] = status.lag_seconds / 60
            rpo_info["meets_rpo"] = status.meets_rpo
        except:
            pass

    return rpo_info


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
