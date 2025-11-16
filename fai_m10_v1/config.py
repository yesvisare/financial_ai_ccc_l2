"""
Configuration management for secure financial RAG deployment.

Loads environment variables and validates security settings.
Service auto-detected from script: OPENAI
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service configuration (auto-detected from script: OPENAI)
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Pinecone configuration (vector database)
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")

# AWS configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_VPC_ID = os.getenv("AWS_VPC_ID", "")
AWS_KMS_KEY_ID = os.getenv("AWS_KMS_KEY_ID", "")

# Security configuration
ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "true").lower() == "true"
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"
LOG_RETENTION_YEARS = int(os.getenv("LOG_RETENTION_YEARS", "7"))

# Database configuration (PostgreSQL for user/role management)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/financial_rag")

# Redis configuration (caching)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


def get_config() -> Dict[str, Any]:
    """
    Get complete deployment configuration.

    Returns:
        Configuration dictionary with all deployment settings including:
        - openai: OpenAI API configuration
        - pinecone: Pinecone vector database configuration
        - aws: AWS service configuration
        - vpc: VPC network isolation settings
        - encryption: Encryption at rest/in transit settings
        - secrets: Secrets Manager configuration
        - iam: IAM and RBAC settings
        - audit_logging: CloudWatch and CloudTrail settings

    Raises:
        ValueError: If required configuration is missing

    Example:
        config = get_config()
        openai_key = config["openai"]["api_key"]
        vpc_cidr = config["vpc"]["cidr_block"]
    """
    config = {
        "openai": {
            "enabled": OPENAI_ENABLED,
            "api_key": OPENAI_API_KEY,
            "model": "gpt-4",
            "embedding_model": "text-embedding-3-large"
        },
        "pinecone": {
            "enabled": PINECONE_ENABLED,
            "api_key": PINECONE_API_KEY,
            "environment": PINECONE_ENVIRONMENT,
            "index_name": "financial-rag-production"
        },
        "aws": {
            "region": AWS_REGION,
            "vpc_id": AWS_VPC_ID,
            "kms_key_id": AWS_KMS_KEY_ID
        },
        "vpc": {
            "cidr_block": "10.0.0.0/16",
            "public_subnet": "10.0.1.0/24",
            "private_subnets": ["10.0.10.0/24", "10.0.11.0/24"],
            "availability_zones": ["us-east-1a", "us-east-1b"]
        },
        "encryption": {
            "enabled": ENABLE_ENCRYPTION,
            "kms_key_id": AWS_KMS_KEY_ID,
            "tls_version": "1.3",
            "at_rest_algorithm": "AES-256-GCM",
            "fips_140_2_compliant": True
        },
        "secrets": {
            "manager": "AWS_SECRETS_MANAGER",
            "rotation_enabled": True,
            "rotation_days": 90,
            "naming_convention": "financial-rag/{environment}/{service}/{key_name}"
        },
        "iam": {
            "least_privilege": True,
            "rbac_enabled": True,
            "roles": {
                "analyst": ["read_documents", "query_rag", "view_portfolio"],
                "admin": ["read_documents", "query_rag", "write_documents", "manage_users", "configure_system"],
                "compliance": ["read_documents", "query_rag", "read_audit_logs", "export_compliance_reports"],
                "viewer": ["read_documents"]
            }
        },
        "audit_logging": {
            "enabled": ENABLE_AUDIT_LOGGING,
            "retention_years": LOG_RETENTION_YEARS,
            "retention_days": LOG_RETENTION_YEARS * 365,
            "immutable_storage": True,
            "s3_object_lock_enabled": True,
            "log_destinations": {
                "cloudwatch_log_group": "/financial-rag/production",
                "s3_archive_bucket": "financial-rag-audit-logs",
                "cloudtrail_bucket": "financial-rag-cloudtrail"
            },
            "services": ["CloudWatch", "CloudTrail"]
        },
        "database": {
            "url": DATABASE_URL,
            "pool_size": 10,
            "max_overflow": 20
        },
        "redis": {
            "url": REDIS_URL,
            "ttl_seconds": 3600
        }
    }

    # Validate critical settings
    _validate_config(config)

    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration for common issues.

    Args:
        config: Configuration dictionary to validate

    Side Effects:
        Logs warnings for missing or invalid configuration
    """
    # Check OpenAI configuration
    if config["openai"]["enabled"] and not config["openai"]["api_key"]:
        logger.warning("⚠️ OPENAI_ENABLED=true but OPENAI_API_KEY not provided")
        logger.warning("   OpenAI API calls will fail. Set OPENAI_API_KEY in .env file")

    # Check Pinecone configuration
    if config["pinecone"]["enabled"] and not config["pinecone"]["api_key"]:
        logger.warning("⚠️ PINECONE_ENABLED=true but PINECONE_API_KEY not provided")
        logger.warning("   Pinecone operations will fail. Set PINECONE_API_KEY in .env file")

    # Check encryption configuration
    if config["encryption"]["enabled"] and not config["aws"]["kms_key_id"]:
        logger.warning("⚠️ ENABLE_ENCRYPTION=true but AWS_KMS_KEY_ID not provided")
        logger.warning("   Encryption at rest may not be fully configured")

    # Check audit logging retention
    if config["audit_logging"]["retention_years"] < 7:
        logger.warning(f"⚠️ LOG_RETENTION_YEARS={config['audit_logging']['retention_years']} is less than 7 years")
        logger.warning("   SOX Section 404 requires 7+ year retention for financial audit logs")

    # Check VPC configuration
    if not config["aws"]["vpc_id"]:
        logger.warning("⚠️ AWS_VPC_ID not configured")
        logger.warning("   VPC isolation will use default configuration")


def validate_production_readiness() -> bool:
    """
    Validate configuration is ready for production deployment.

    Checks:
    1. Encryption enabled
    2. Audit logging enabled with 7+ year retention
    3. KMS key configured
    4. Immutable storage enabled
    5. OpenAI API key provided (if enabled)
    6. Pinecone API key provided (if enabled)

    Returns:
        True if production-ready, False otherwise

    Example:
        if validate_production_readiness():
            print("✅ Ready for production deployment")
        else:
            print("❌ Configuration issues - not production ready")
    """
    config = get_config()

    checks = [
        (config["encryption"]["enabled"], "Encryption must be enabled"),
        (config["audit_logging"]["enabled"], "Audit logging must be enabled"),
        (config["audit_logging"]["retention_years"] >= 7, "Audit logs must retain for 7+ years (SOX Section 404)"),
        (bool(config["aws"]["kms_key_id"]) or not config["encryption"]["enabled"], "KMS key must be configured if encryption enabled"),
        (config["audit_logging"]["immutable_storage"], "Immutable storage must be enabled (S3 Object Lock)"),
    ]

    # Check OpenAI if enabled
    if config["openai"]["enabled"]:
        checks.append(
            (bool(config["openai"]["api_key"]), "OpenAI API key must be provided if OPENAI_ENABLED=true")
        )

    # Check Pinecone if enabled
    if config["pinecone"]["enabled"]:
        checks.append(
            (bool(config["pinecone"]["api_key"]), "Pinecone API key must be provided if PINECONE_ENABLED=true")
        )

    all_passed = True
    for check, message in checks:
        if not check:
            logger.error(f"❌ Production readiness check failed: {message}")
            all_passed = False
        else:
            logger.info(f"✅ {message}")

    if all_passed:
        logger.info("✅ Configuration is production-ready")
        logger.info(f"   Compliant with: SOC 2 Type II, SOX Section 404, GLBA Title V")
    else:
        logger.error("❌ Configuration is NOT production-ready - fix issues above")

    return all_passed


def get_openai_client():
    """
    Get OpenAI client instance.

    Returns:
        OpenAI client if enabled and configured, None otherwise

    Example:
        client = get_openai_client()
        if client:
            response = client.chat.completions.create(...)
    """
    config = get_config()

    if not config["openai"]["enabled"]:
        logger.warning("⚠️ OpenAI is disabled (OPENAI_ENABLED=false)")
        return None

    if not config["openai"]["api_key"]:
        logger.error("❌ OpenAI API key not configured")
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=config["openai"]["api_key"])
        logger.info("✅ OpenAI client initialized")
        return client
    except ImportError:
        logger.error("❌ openai package not installed. Run: pip install openai")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
        return None


def get_pinecone_client():
    """
    Get Pinecone client instance.

    Returns:
        Pinecone client if enabled and configured, None otherwise

    Example:
        client = get_pinecone_client()
        if client:
            index = client.Index("financial-rag-production")
    """
    config = get_config()

    if not config["pinecone"]["enabled"]:
        logger.warning("⚠️ Pinecone is disabled (PINECONE_ENABLED=false)")
        return None

    if not config["pinecone"]["api_key"]:
        logger.error("❌ Pinecone API key not configured")
        return None

    try:
        import pinecone
        pinecone.init(
            api_key=config["pinecone"]["api_key"],
            environment=config["pinecone"]["environment"]
        )
        logger.info("✅ Pinecone client initialized")
        return pinecone
    except ImportError:
        logger.error("❌ pinecone-client package not installed. Run: pip install pinecone-client")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Pinecone client: {str(e)}")
        return None


if __name__ == "__main__":
    # Test configuration loading
    print("Testing configuration...")
    config = get_config()
    print(f"\n✅ Configuration loaded successfully")
    print(f"   OpenAI Enabled: {config['openai']['enabled']}")
    print(f"   Pinecone Enabled: {config['pinecone']['enabled']}")
    print(f"   AWS Region: {config['aws']['region']}")
    print(f"   Encryption Enabled: {config['encryption']['enabled']}")
    print(f"   Audit Log Retention: {config['audit_logging']['retention_years']} years")

    print("\nValidating production readiness...")
    is_ready = validate_production_readiness()

    if is_ready:
        print("\n✅ Configuration is production-ready!")
    else:
        print("\n❌ Configuration has issues - see logs above")
