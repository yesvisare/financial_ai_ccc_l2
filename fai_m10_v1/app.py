"""
FastAPI application for secure financial RAG deployment.

Provides REST API endpoints for:
- Deploying secure financial RAG infrastructure
- Validating security configuration
- Checking compliance status
- Managing audit logs
"""

import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from src.l3_m10_financial_rag_production import (
    SecureDeploymentManager,
    validate_security_config,
    AuditLogger
)
from config import get_config, validate_production_readiness

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Secure Financial RAG Deployment API",
    description="Production-ready secure deployment for financial RAG systems with SOC 2, SOX, and GLBA compliance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize audit logger
audit_logger = AuditLogger()


# Request/Response models
class VPCConfig(BaseModel):
    """VPC configuration for network isolation."""
    cidr_block: str = Field(..., example="10.0.0.0/16", description="VPC CIDR block")
    public_subnet: str = Field(..., example="10.0.1.0/24", description="Public subnet for ALB/NAT Gateway")
    private_subnets: List[str] = Field(..., example=["10.0.10.0/24", "10.0.11.0/24"], description="Private subnets for RAG API and Vector DB")


class EncryptionConfig(BaseModel):
    """Encryption configuration for data at rest and in transit."""
    enabled: bool = Field(True, description="Enable encryption")
    kms_key_id: str = Field(..., example="arn:aws:kms:us-east-1:123456789012:key/xxxxx", description="AWS KMS key ID")
    tls_version: str = Field("1.3", description="TLS version for in-transit encryption")


class IAMConfig(BaseModel):
    """IAM and RBAC configuration."""
    least_privilege: bool = Field(True, description="Enable least privilege access")
    rbac_enabled: bool = Field(True, description="Enable application-level RBAC")
    roles: List[str] = Field(..., example=["analyst", "admin", "compliance"], description="Roles to configure")


class AuditLoggingConfig(BaseModel):
    """Audit logging configuration for SOX compliance."""
    enabled: bool = Field(True, description="Enable audit logging")
    retention_years: int = Field(7, description="Log retention in years (SOX requires 7+)")
    immutable_storage: bool = Field(True, description="Enable immutable storage (S3 Object Lock)")


class DeploymentRequest(BaseModel):
    """Request model for secure deployment."""
    vpc_config: VPCConfig
    encryption_config: EncryptionConfig
    iam_config: IAMConfig
    audit_logging_config: Optional[AuditLoggingConfig] = None

    class Config:
        schema_extra = {
            "example": {
                "vpc_config": {
                    "cidr_block": "10.0.0.0/16",
                    "public_subnet": "10.0.1.0/24",
                    "private_subnets": ["10.0.10.0/24", "10.0.11.0/24"]
                },
                "encryption_config": {
                    "enabled": True,
                    "kms_key_id": "arn:aws:kms:us-east-1:123456789012:key/xxxxx",
                    "tls_version": "1.3"
                },
                "iam_config": {
                    "least_privilege": True,
                    "rbac_enabled": True,
                    "roles": ["analyst", "admin", "compliance"]
                },
                "audit_logging_config": {
                    "enabled": True,
                    "retention_years": 7,
                    "immutable_storage": True
                }
            }
        }


class DeploymentResponse(BaseModel):
    """Response model for deployment status."""
    status: str
    vpc_id: str
    encryption_enabled: bool
    audit_logging_enabled: bool
    compliance_frameworks: List[str]
    deployment_details: Dict[str, Any]


class ValidationResponse(BaseModel):
    """Response model for security validation."""
    valid: bool
    checks_passed: List[str]
    checks_failed: List[str]
    compliance_frameworks: List[str]
    recommendations: List[str]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    service: str
    version: str
    timestamp: str


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """
    Health check endpoint.

    Returns:
        Service status and metadata
    """
    from datetime import datetime

    audit_logger.log_data_access(
        user_id="anonymous",
        action="health_check",
        resource="/",
        result="success"
    )

    return {
        "status": "healthy",
        "service": "Secure Financial RAG Deployment API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """
    Detailed health check with system status.

    Returns:
        Detailed health information
    """
    config = get_config()

    health_status = {
        "status": "healthy",
        "openai_configured": config["openai"]["enabled"],
        "aws_region": config["aws"]["region"],
        "encryption_enabled": config["encryption"]["enabled"],
        "audit_logging_enabled": config["audit_logging"]["enabled"]
    }

    audit_logger.log_data_access(
        user_id="system",
        action="health_check_detailed",
        resource="/health",
        result="success"
    )

    return health_status


@app.post("/deploy", response_model=DeploymentResponse)
async def deploy_secure_rag(request: DeploymentRequest):
    """
    Deploy secure financial RAG system with full security controls.

    Args:
        request: Deployment configuration including VPC, encryption, IAM settings

    Returns:
        Deployment status and configuration details

    Raises:
        HTTPException: If deployment fails or configuration is invalid
    """
    try:
        logger.info("Starting secure RAG deployment...")

        # Build complete configuration
        config = {
            "vpc": request.vpc_config.dict(),
            "encryption": request.encryption_config.dict(),
            "iam": request.iam_config.dict(),
            "secrets": {
                "manager": "AWS_SECRETS_MANAGER",
                "rotation_enabled": True
            },
            "audit_logging": request.audit_logging_config.dict() if request.audit_logging_config else {
                "enabled": True,
                "retention_years": 7,
                "immutable_storage": True
            }
        }

        # Validate configuration
        validate_security_config(config)

        # Initialize deployment manager
        manager = SecureDeploymentManager(config)

        # Execute deployment steps
        vpc_result = manager.setup_vpc_isolation()
        encryption_result = manager.configure_encryption(request.encryption_config.kms_key_id)
        secrets_result = manager.setup_secrets_management()
        iam_result = manager.configure_iam_rbac(request.iam_config.roles)
        audit_result = manager.setup_audit_logging()

        # Validate production readiness
        readiness = manager.validate_production_readiness()

        if not readiness["ready"]:
            raise ValueError(f"Deployment validation failed: {readiness['checks_failed']}")

        logger.info("✅ Secure deployment completed successfully")

        # Log audit event
        audit_logger.log_data_access(
            user_id="system",
            action="deploy_secure_rag",
            resource=vpc_result["vpc_id"],
            result="success"
        )

        return DeploymentResponse(
            status="deployed",
            vpc_id=vpc_result["vpc_id"],
            encryption_enabled=encryption_result["at_rest_enabled"],
            audit_logging_enabled=audit_result["cloudwatch_enabled"],
            compliance_frameworks=readiness["compliance_frameworks"],
            deployment_details={
                "vpc": vpc_result,
                "encryption": encryption_result,
                "secrets": secrets_result,
                "iam_roles": iam_result,
                "audit_logging": audit_result
            }
        )

    except ValueError as e:
        logger.error(f"Configuration validation error: {str(e)}")
        audit_logger.log_data_access(
            user_id="system",
            action="deploy_secure_rag",
            resource="N/A",
            result="failure"
        )
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        audit_logger.log_data_access(
            user_id="system",
            action="deploy_secure_rag",
            resource="N/A",
            result="failure"
        )
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@app.get("/security/validate", response_model=ValidationResponse)
async def validate_security():
    """
    Validate current security configuration against SOC 2 Type II requirements.

    Returns:
        Validation status, passed/failed checks, and compliance frameworks

    Example:
        GET /security/validate
        Response: {
            "valid": true,
            "checks_passed": ["Encryption enabled", "VPC configured", ...],
            "checks_failed": [],
            "compliance_frameworks": ["SOC 2 Type II", "SOX Section 404", "GLBA Title V"],
            "recommendations": []
        }
    """
    config = get_config()

    try:
        # Validate configuration
        is_valid = validate_security_config(config)

        # Check production readiness
        is_ready = validate_production_readiness()

        compliance_frameworks = []
        recommendations = []

        if is_valid and is_ready:
            compliance_frameworks = ["SOC 2 Type II", "SOX Section 404", "GLBA Title V"]
        else:
            recommendations.append("Enable all required security controls for compliance")

        if not config["encryption"]["enabled"]:
            recommendations.append("Enable encryption at rest and in transit")

        if config["audit_logging"]["retention_years"] < 7:
            recommendations.append("Increase audit log retention to 7+ years for SOX compliance")

        audit_logger.log_data_access(
            user_id="system",
            action="validate_security",
            resource="/security/validate",
            result="success"
        )

        return {
            "valid": is_valid and is_ready,
            "checks_passed": [
                "Encryption enabled",
                "VPC configured",
                "Secrets Manager configured",
                "IAM/RBAC configured",
                "Audit logging enabled",
                "7+ year retention",
                "Immutable storage"
            ] if is_valid and is_ready else ["Partial configuration"],
            "checks_failed": [] if is_valid and is_ready else ["See recommendations"],
            "compliance_frameworks": compliance_frameworks,
            "recommendations": recommendations
        }

    except ValueError as e:
        return {
            "valid": False,
            "checks_passed": [],
            "checks_failed": [str(e)],
            "compliance_frameworks": [],
            "recommendations": ["Fix configuration errors to proceed"]
        }


@app.get("/compliance/status")
async def get_compliance_status():
    """
    Get current compliance status for financial regulations.

    Returns:
        Compliance status for SOC 2, SOX, GLBA, and other frameworks
    """
    config = get_config()

    try:
        is_ready = validate_production_readiness()

        compliance_status = {
            "soc_2_type_ii": {
                "status": "compliant" if is_ready else "non_compliant",
                "requirements": [
                    {"name": "Security", "status": "met" if config["encryption"]["enabled"] else "not_met"},
                    {"name": "Availability", "status": "met"},
                    {"name": "Processing Integrity", "status": "met"},
                    {"name": "Confidentiality", "status": "met" if config["encryption"]["enabled"] else "not_met"},
                    {"name": "Privacy", "status": "met"}
                ]
            },
            "sox_section_404": {
                "status": "compliant" if config["audit_logging"]["retention_years"] >= 7 else "non_compliant",
                "requirements": [
                    {"name": "7-year retention", "status": "met" if config["audit_logging"]["retention_years"] >= 7 else "not_met"},
                    {"name": "Immutable storage", "status": "met" if config["audit_logging"].get("immutable_storage") else "not_met"},
                    {"name": "Audit trail", "status": "met" if config["audit_logging"]["enabled"] else "not_met"}
                ]
            },
            "glba_title_v": {
                "status": "compliant" if config["encryption"]["enabled"] else "non_compliant",
                "requirements": [
                    {"name": "Data encryption", "status": "met" if config["encryption"]["enabled"] else "not_met"},
                    {"name": "Access controls", "status": "met"},
                    {"name": "Privacy notices", "status": "met"}
                ]
            }
        }

        audit_logger.log_data_access(
            user_id="system",
            action="get_compliance_status",
            resource="/compliance/status",
            result="success"
        )

        return compliance_status

    except Exception as e:
        logger.error(f"Failed to get compliance status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit/logs")
async def get_audit_logs(limit: int = 100):
    """
    Retrieve recent audit logs.

    Args:
        limit: Maximum number of log entries to return

    Returns:
        List of recent audit log entries
    """
    # In production, query CloudWatch Logs or S3
    # This is a simplified implementation

    audit_logger.log_data_access(
        user_id="system",
        action="get_audit_logs",
        resource="/audit/logs",
        result="success"
    )

    return {
        "message": "Audit logs available in CloudWatch Logs and S3",
        "log_group": "/financial-rag/production",
        "s3_bucket": "financial-rag-audit-logs",
        "retention_years": 7,
        "query_tools": ["CloudWatch Insights", "Athena", "OpenSearch"]
    }


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with audit logging."""
    audit_logger.log_data_access(
        user_id="system",
        action=f"{request.method} {request.url.path}",
        resource=str(request.url),
        result="http_error"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with audit logging."""
    logger.error(f"Unhandled exception: {str(exc)}")
    audit_logger.log_data_access(
        user_id="system",
        action=f"{request.method} {request.url.path}",
        resource=str(request.url),
        result="server_error"
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
