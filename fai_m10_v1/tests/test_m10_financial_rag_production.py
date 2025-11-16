"""
Test suite for secure financial RAG deployment.

Tests cover:
- VPC isolation configuration
- Encryption at rest and in transit
- Secrets management setup
- IAM/RBAC configuration
- Audit logging with 7-year retention
- Security validation
- Production readiness checks
"""

import pytest
import json
from typing import Dict, Any

from src.l3_m10_financial_rag_production import (
    SecureDeploymentManager,
    validate_security_config,
    FinancialDataEncryption,
    SecretsManager,
    AuditLogger
)


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample security configuration for testing."""
    return {
        "vpc": {
            "cidr_block": "10.0.0.0/16",
            "public_subnet": "10.0.1.0/24",
            "private_subnets": ["10.0.10.0/24", "10.0.11.0/24"]
        },
        "encryption": {
            "enabled": True,
            "kms_key_id": "arn:aws:kms:us-east-1:123456789012:key/test-key",
            "tls_version": "1.3"
        },
        "secrets": {
            "manager": "AWS_SECRETS_MANAGER",
            "rotation_enabled": True,
            "rotation_days": 90
        },
        "iam": {
            "least_privilege": True,
            "rbac_enabled": True
        },
        "audit_logging": {
            "enabled": True,
            "retention_years": 7,
            "immutable_storage": True
        }
    }


@pytest.fixture
def deployment_manager(sample_config: Dict[str, Any]) -> SecureDeploymentManager:
    """Initialize SecureDeploymentManager for testing."""
    return SecureDeploymentManager(sample_config)


# ==================== Security Configuration Validation Tests ====================

def test_validate_security_config_valid(sample_config: Dict[str, Any]):
    """Test security configuration validation with valid config."""
    result = validate_security_config(sample_config)
    assert result is True


def test_validate_security_config_missing_vpc():
    """Test security configuration validation fails when VPC config missing."""
    invalid_config = {
        "encryption": {},
        "secrets": {},
        "iam": {},
        "audit_logging": {}
    }

    with pytest.raises(ValueError, match="Security configuration missing required key: vpc"):
        validate_security_config(invalid_config)


def test_validate_security_config_missing_encryption():
    """Test security configuration validation fails when encryption config missing."""
    invalid_config = {
        "vpc": {},
        "secrets": {},
        "iam": {},
        "audit_logging": {}
    }

    with pytest.raises(ValueError, match="Security configuration missing required key: encryption"):
        validate_security_config(invalid_config)


def test_validate_security_config_encryption_disabled():
    """Test security configuration validation fails when encryption disabled."""
    invalid_config = {
        "vpc": {},
        "encryption": {"enabled": False},
        "secrets": {},
        "iam": {},
        "audit_logging": {}
    }

    with pytest.raises(ValueError, match="Encryption must be enabled"):
        validate_security_config(invalid_config)


def test_validate_security_config_insufficient_retention():
    """Test security configuration validation fails when audit log retention < 7 years."""
    invalid_config = {
        "vpc": {},
        "encryption": {"enabled": True},
        "secrets": {},
        "iam": {},
        "audit_logging": {"retention_years": 5}
    }

    with pytest.raises(ValueError, match="Audit log retention must be >= 7 years"):
        validate_security_config(invalid_config)


# ==================== SecureDeploymentManager Tests ====================

def test_secure_deployment_manager_initialization(sample_config: Dict[str, Any]):
    """Test SecureDeploymentManager initialization."""
    manager = SecureDeploymentManager(sample_config)

    assert manager.config == sample_config
    assert manager.vpc_config == sample_config["vpc"]
    assert manager.encryption_config == sample_config["encryption"]
    assert manager.secrets_config == sample_config["secrets"]
    assert manager.iam_config == sample_config["iam"]
    assert manager.audit_config == sample_config["audit_logging"]


def test_setup_vpc_isolation(deployment_manager: SecureDeploymentManager):
    """Test VPC isolation setup."""
    result = deployment_manager.setup_vpc_isolation()

    # Verify VPC created
    assert "vpc_id" in result
    assert result["vpc_id"].startswith("vpc-")

    # Verify subnets created
    assert "public_subnet_id" in result
    assert "private_subnet_ids" in result
    assert isinstance(result["private_subnet_ids"], list)
    assert len(result["private_subnet_ids"]) == 2

    # Verify NAT Gateway created
    assert "nat_gateway_id" in result
    assert result["nat_gateway_id"].startswith("nat-")

    # Verify security groups created
    assert "security_group_ids" in result
    assert "alb_sg" in result["security_group_ids"]
    assert "rag_api_sg" in result["security_group_ids"]
    assert "vector_db_sg" in result["security_group_ids"]

    # Verify network isolation enabled
    assert result["network_isolation_enabled"] is True


def test_setup_vpc_isolation_missing_config():
    """Test VPC isolation fails with missing configuration."""
    manager = SecureDeploymentManager({"vpc": {}})

    with pytest.raises(ValueError, match="VPC configuration missing required field"):
        manager.setup_vpc_isolation()


def test_configure_encryption(deployment_manager: SecureDeploymentManager):
    """Test encryption configuration."""
    kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/test-key-123"
    result = deployment_manager.configure_encryption(kms_key_id)

    assert result["at_rest_enabled"] is True
    assert result["in_transit_enabled"] is True
    assert result["kms_key_id"] == kms_key_id
    assert result["tls_version"] == "1.3"
    assert result["fips_140_2_compliant"] is True
    assert result["automatic_key_rotation"] is True
    assert result["key_rotation_days"] == 365


def test_configure_encryption_no_kms_key():
    """Test encryption configuration handles missing KMS key gracefully."""
    manager = SecureDeploymentManager({
        "encryption": {"enabled": True}
    })

    result = manager.configure_encryption()

    assert result["at_rest_enabled"] is True
    assert result["in_transit_enabled"] is True
    assert result["kms_key_id"] == "NOT_CONFIGURED"


def test_setup_secrets_management(deployment_manager: SecureDeploymentManager):
    """Test secrets management setup."""
    result = deployment_manager.setup_secrets_management()

    assert result["secrets_manager_enabled"] is True
    assert result["rotation_enabled"] is True
    assert result["rotation_days"] == 90
    assert "openai_api_key" in result["supported_secret_types"]
    assert "pinecone_api_key" in result["supported_secret_types"]
    assert "database_credentials" in result["supported_secret_types"]
    assert result["encryption_at_rest"] is True
    assert result["version_management"] is True


def test_configure_iam_rbac(deployment_manager: SecureDeploymentManager):
    """Test IAM and RBAC configuration."""
    roles = ["analyst", "admin", "compliance"]
    result = deployment_manager.configure_iam_rbac(roles)

    assert len(result) == 3
    assert "analyst" in result
    assert "admin" in result
    assert "compliance" in result

    # Verify analyst permissions
    assert "read_documents" in result["analyst"]
    assert "query_rag" in result["analyst"]

    # Verify admin permissions (should have more than analyst)
    assert "manage_users" in result["admin"]
    assert "configure_system" in result["admin"]

    # Verify compliance permissions
    assert "read_audit_logs" in result["compliance"]
    assert "export_compliance_reports" in result["compliance"]


def test_configure_iam_rbac_unknown_role(deployment_manager: SecureDeploymentManager):
    """Test IAM/RBAC assigns minimal permissions to unknown roles."""
    roles = ["unknown_role"]
    result = deployment_manager.configure_iam_rbac(roles)

    assert "unknown_role" in result
    assert result["unknown_role"] == ["read_documents"]


def test_setup_audit_logging(deployment_manager: SecureDeploymentManager):
    """Test audit logging configuration."""
    result = deployment_manager.setup_audit_logging()

    assert result["cloudwatch_enabled"] is True
    assert result["cloudtrail_enabled"] is True
    assert result["retention_years"] == 7
    assert result["retention_days"] == 7 * 365
    assert result["immutable_storage"] is True
    assert result["s3_object_lock_enabled"] is True

    # Verify log types
    assert "api_calls" in result["log_types"]
    assert "authentication_events" in result["log_types"]
    assert "data_access_events" in result["log_types"]
    assert "configuration_changes" in result["log_types"]

    # Verify SOX compliance
    assert result["sox_section_404_compliant"] is True


def test_validate_production_readiness_pass(deployment_manager: SecureDeploymentManager):
    """Test production readiness validation passes with valid configuration."""
    result = deployment_manager.validate_production_readiness()

    assert result["ready"] is True
    assert len(result["checks_failed"]) == 0
    assert "SOC 2 Type II" in result["compliance_frameworks"]
    assert "SOX Section 404" in result["compliance_frameworks"]
    assert "GLBA Title V" in result["compliance_frameworks"]


def test_validate_production_readiness_fail():
    """Test production readiness validation fails with invalid configuration."""
    manager = SecureDeploymentManager({
        "vpc": {},
        "encryption": {"enabled": False},  # Encryption disabled
        "secrets": {},
        "iam": {},
        "audit_logging": {"enabled": False, "retention_years": 3}  # Insufficient retention
    })

    result = manager.validate_production_readiness()

    assert result["ready"] is False
    assert len(result["checks_failed"]) > 0
    assert len(result["compliance_frameworks"]) == 0


# ==================== FinancialDataEncryption Tests ====================

def test_financial_data_encryption_initialization():
    """Test FinancialDataEncryption initialization."""
    kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/test-key"
    encryption = FinancialDataEncryption(kms_key_id)

    assert encryption.kms_key_id == kms_key_id


def test_encrypt_sensitive_data():
    """Test encryption of sensitive financial data."""
    encryption = FinancialDataEncryption("test-kms-key")

    data = {
        "account_number": "1234567890",
        "balance": 50000,
        "ssn": "123-45-6789"
    }

    encryption_context = {
        "user_id": "analyst_123",
        "document_type": "portfolio"
    }

    ciphertext = encryption.encrypt_sensitive_data(data, encryption_context)

    assert isinstance(ciphertext, str)
    assert len(ciphertext) > 0


def test_decrypt_sensitive_data():
    """Test decryption of encrypted financial data."""
    encryption = FinancialDataEncryption("test-kms-key")

    original_data = {
        "account_number": "1234567890",
        "balance": 50000
    }

    # Encrypt
    ciphertext = encryption.encrypt_sensitive_data(original_data)

    # Decrypt
    decrypted_data = encryption.decrypt_sensitive_data(ciphertext)

    assert decrypted_data == original_data


# ==================== SecretsManager Tests ====================

def test_secrets_manager_initialization():
    """Test SecretsManager initialization."""
    secrets_manager = SecretsManager(region="us-east-1")

    assert secrets_manager.region == "us-east-1"


def test_get_secret_from_environment(monkeypatch):
    """Test secret retrieval from environment variable."""
    monkeypatch.setenv("FINANCIAL_RAG_OPENAI_API_KEY", "test-api-key-123")

    secrets_manager = SecretsManager()
    secret = secrets_manager.get_secret("financial-rag/openai-api-key")

    assert secret == "test-api-key-123"


def test_get_secret_not_found():
    """Test secret retrieval returns empty string when not found."""
    secrets_manager = SecretsManager()
    secret = secrets_manager.get_secret("non-existent-secret")

    assert secret == ""


def test_create_secret():
    """Test secret creation."""
    secrets_manager = SecretsManager(region="us-west-2")
    result = secrets_manager.create_secret("test-secret", "test-value")

    assert "arn" in result
    assert "version_id" in result
    assert "created_at" in result
    assert "us-west-2" in result["arn"]


# ==================== AuditLogger Tests ====================

def test_audit_logger_initialization():
    """Test AuditLogger initialization."""
    audit_logger = AuditLogger(log_group="/test/audit-logs")

    assert audit_logger.log_group == "/test/audit-logs"


def test_log_data_access(caplog):
    """Test audit logging of data access events."""
    audit_logger = AuditLogger()

    audit_logger.log_data_access(
        user_id="analyst_123",
        action="query_rag",
        resource="portfolio_10k_filings",
        result="success"
    )

    # Verify log entry created
    assert "AUDIT:" in caplog.text
    assert "analyst_123" in caplog.text
    assert "query_rag" in caplog.text
    assert "portfolio_10k_filings" in caplog.text


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_full_deployment_workflow(sample_config: Dict[str, Any]):
    """Test complete deployment workflow from start to finish."""
    # Validate configuration
    validate_security_config(sample_config)

    # Initialize deployment manager
    manager = SecureDeploymentManager(sample_config)

    # Execute deployment steps
    vpc_result = manager.setup_vpc_isolation()
    encryption_result = manager.configure_encryption()
    secrets_result = manager.setup_secrets_management()
    iam_result = manager.configure_iam_rbac(["analyst", "admin", "compliance"])
    audit_result = manager.setup_audit_logging()

    # Verify all steps completed successfully
    assert vpc_result is not None
    assert vpc_result["network_isolation_enabled"] is True

    assert encryption_result is not None
    assert encryption_result["at_rest_enabled"] is True
    assert encryption_result["in_transit_enabled"] is True

    assert secrets_result is not None
    assert secrets_result["secrets_manager_enabled"] is True

    assert iam_result is not None
    assert len(iam_result) > 0

    assert audit_result is not None
    assert audit_result["cloudwatch_enabled"] is True
    assert audit_result["sox_section_404_compliant"] is True

    # Validate production readiness
    readiness = manager.validate_production_readiness()
    assert readiness["ready"] is True
    assert len(readiness["compliance_frameworks"]) == 3


def test_sox_compliance_audit_log_retention(deployment_manager: SecureDeploymentManager):
    """Test that audit logging meets SOX Section 404 7-year retention requirement."""
    result = deployment_manager.setup_audit_logging()

    # SOX Section 404 requires 7+ years retention
    assert result["retention_years"] >= 7

    # Immutable storage required for SOX compliance
    assert result["immutable_storage"] is True
    assert result["s3_object_lock_enabled"] is True

    # Verify SOX compliance flag
    assert result["sox_section_404_compliant"] is True


def test_soc2_compliance_encryption_requirements(deployment_manager: SecureDeploymentManager):
    """Test that encryption meets SOC 2 Type II requirements."""
    result = deployment_manager.configure_encryption()

    # SOC 2 requires FIPS 140-2 Level 3 compliance
    assert result["fips_140_2_compliant"] is True

    # Verify encryption algorithms
    assert result["encryption_algorithms"]["at_rest"] == "AES-256-GCM"
    assert result["encryption_algorithms"]["in_transit"] == "TLS 1.3"

    # Verify automatic key rotation
    assert result["automatic_key_rotation"] is True
    assert result["key_rotation_days"] == 365


def test_glba_compliance_access_control(deployment_manager: SecureDeploymentManager):
    """Test that access control meets GLBA Title V requirements."""
    roles = ["analyst", "compliance"]
    result = deployment_manager.configure_iam_rbac(roles)

    # GLBA requires role-based access control
    assert len(result) > 0

    # Verify least privilege (analyst has limited permissions)
    assert "manage_users" not in result["analyst"]
    assert "configure_system" not in result["analyst"]

    # Verify compliance role has audit access
    assert "read_audit_logs" in result["compliance"]
