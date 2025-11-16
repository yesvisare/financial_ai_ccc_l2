"""
Configuration and client initialization for L3 M10.4: Disaster Recovery & Business Continuity

Manages:
- Environment variables for AWS, Pinecone, PostgreSQL
- AWS boto3 client initialization (CloudWatch, Route53, RDS)
- Database connection configurations
- Service availability flags
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ============================================================================
# Environment Variables
# ============================================================================

# AWS Configuration
AWS_ENABLED = os.getenv("AWS_ENABLED", "false").lower() == "true"
AWS_REGION_PRIMARY = os.getenv("AWS_REGION_PRIMARY", "us-east-1")
AWS_REGION_DR = os.getenv("AWS_REGION_DR", "us-west-2")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

# Pinecone Configuration
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
PINECONE_INDEX_PRIMARY = os.getenv("PINECONE_INDEX_PRIMARY", "financial-rag-primary")
PINECONE_INDEX_DR = os.getenv("PINECONE_INDEX_DR", "financial-rag-dr")

# PostgreSQL Configuration
POSTGRESQL_ENABLED = os.getenv("POSTGRESQL_ENABLED", "false").lower() == "true"

# Primary Database (US-EAST-1)
POSTGRES_PRIMARY_HOST = os.getenv("POSTGRES_PRIMARY_HOST", "")
POSTGRES_PRIMARY_PORT = int(os.getenv("POSTGRES_PRIMARY_PORT", "5432"))
POSTGRES_PRIMARY_DB = os.getenv("POSTGRES_PRIMARY_DB", "financial_rag")
POSTGRES_PRIMARY_USER = os.getenv("POSTGRES_PRIMARY_USER", "")
POSTGRES_PRIMARY_PASSWORD = os.getenv("POSTGRES_PRIMARY_PASSWORD", "")

# DR Database (US-WEST-2)
POSTGRES_DR_HOST = os.getenv("POSTGRES_DR_HOST", "")
POSTGRES_DR_PORT = int(os.getenv("POSTGRES_DR_PORT", "5432"))
POSTGRES_DR_DB = os.getenv("POSTGRES_DR_DB", "financial_rag")
POSTGRES_DR_USER = os.getenv("POSTGRES_DR_USER", "")
POSTGRES_DR_PASSWORD = os.getenv("POSTGRES_DR_PASSWORD", "")

# Route 53 Configuration
ROUTE53_HOSTED_ZONE_ID = os.getenv("ROUTE53_HOSTED_ZONE_ID", "")
ROUTE53_DOMAIN = os.getenv("ROUTE53_DOMAIN", "rag.yourcompany.com")

# Monitoring Configuration
PAGERDUTY_ENABLED = os.getenv("PAGERDUTY_ENABLED", "false").lower() == "true"
PAGERDUTY_INTEGRATION_KEY = os.getenv("PAGERDUTY_INTEGRATION_KEY", "")

# ============================================================================
# Database Connection Configurations
# ============================================================================

PRIMARY_DB_CONFIG: Dict[str, Any] = {
    "host": POSTGRES_PRIMARY_HOST,
    "port": POSTGRES_PRIMARY_PORT,
    "database": POSTGRES_PRIMARY_DB,
    "user": POSTGRES_PRIMARY_USER,
    "password": POSTGRES_PRIMARY_PASSWORD
}

DR_DB_CONFIG: Dict[str, Any] = {
    "host": POSTGRES_DR_HOST,
    "port": POSTGRES_DR_PORT,
    "database": POSTGRES_DR_DB,
    "user": POSTGRES_DR_USER,
    "password": POSTGRES_DR_PASSWORD
}

# ============================================================================
# AWS Client Initialization
# ============================================================================

cloudwatch_client: Optional[Any] = None
route53_client: Optional[Any] = None
rds_client: Optional[Any] = None

if AWS_ENABLED:
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        logger.warning("⚠️ AWS_ENABLED=true but AWS credentials not set")
        logger.warning("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    else:
        try:
            import boto3

            # Initialize CloudWatch client (for metrics and alarms)
            cloudwatch_client = boto3.client(
                'cloudwatch',
                region_name=AWS_REGION_PRIMARY,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            logger.info(f"✅ CloudWatch client initialized (region: {AWS_REGION_PRIMARY})")

            # Initialize Route 53 client (for DNS failover)
            route53_client = boto3.client(
                'route53',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            logger.info("✅ Route 53 client initialized")

            # Initialize RDS client (for database management)
            rds_client = boto3.client(
                'rds',
                region_name=AWS_REGION_PRIMARY,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            logger.info(f"✅ RDS client initialized (region: {AWS_REGION_PRIMARY})")

        except ImportError:
            logger.error("❌ boto3 package not installed. Run: pip install boto3")
            AWS_ENABLED = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS clients: {e}")
            AWS_ENABLED = False
else:
    logger.info("ℹ️ AWS disabled (set AWS_ENABLED=true to enable)")

# ============================================================================
# Pinecone Client Initialization
# ============================================================================

pinecone_client: Optional[Any] = None

if PINECONE_ENABLED:
    if not PINECONE_API_KEY:
        logger.warning("⚠️ PINECONE_ENABLED=true but PINECONE_API_KEY not set")
    else:
        try:
            import pinecone

            # Initialize Pinecone
            pinecone.init(
                api_key=PINECONE_API_KEY,
                environment=PINECONE_ENVIRONMENT
            )

            pinecone_client = pinecone
            logger.info(f"✅ Pinecone client initialized (environment: {PINECONE_ENVIRONMENT})")

        except ImportError:
            logger.error("❌ pinecone-client package not installed. Run: pip install pinecone-client[grpc]")
            PINECONE_ENABLED = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone: {e}")
            PINECONE_ENABLED = False
else:
    logger.info("ℹ️ Pinecone disabled (set PINECONE_ENABLED=true to enable)")

# ============================================================================
# PostgreSQL Client Validation
# ============================================================================

if POSTGRESQL_ENABLED:
    if not POSTGRES_PRIMARY_HOST or not POSTGRES_DR_HOST:
        logger.warning("⚠️ POSTGRESQL_ENABLED=true but database hosts not configured")
        logger.warning("   Set POSTGRES_PRIMARY_HOST and POSTGRES_DR_HOST")
    else:
        try:
            import psycopg2
            logger.info("✅ psycopg2 package available for PostgreSQL connections")
        except ImportError:
            logger.error("❌ psycopg2 package not installed. Run: pip install psycopg2-binary")
            POSTGRESQL_ENABLED = False
else:
    logger.info("ℹ️ PostgreSQL disabled (set POSTGRESQL_ENABLED=true to enable)")

# ============================================================================
# Configuration Summary
# ============================================================================

def print_config_summary():
    """Print configuration summary for debugging."""
    logger.info("=" * 60)
    logger.info("L3 M10.4: Disaster Recovery Configuration")
    logger.info("=" * 60)
    logger.info(f"AWS Enabled:        {AWS_ENABLED}")
    logger.info(f"  Primary Region:   {AWS_REGION_PRIMARY}")
    logger.info(f"  DR Region:        {AWS_REGION_DR}")
    logger.info(f"  CloudWatch:       {'✅' if cloudwatch_client else '❌'}")
    logger.info(f"  Route 53:         {'✅' if route53_client else '❌'}")
    logger.info(f"  RDS Client:       {'✅' if rds_client else '❌'}")
    logger.info(f"Pinecone Enabled:   {PINECONE_ENABLED}")
    logger.info(f"  Environment:      {PINECONE_ENVIRONMENT if PINECONE_ENABLED else 'N/A'}")
    logger.info(f"PostgreSQL Enabled: {POSTGRESQL_ENABLED}")
    logger.info(f"  Primary Host:     {POSTGRES_PRIMARY_HOST if POSTGRES_PRIMARY_HOST else 'Not configured'}")
    logger.info(f"  DR Host:          {POSTGRES_DR_HOST if POSTGRES_DR_HOST else 'Not configured'}")
    logger.info(f"PagerDuty Enabled:  {PAGERDUTY_ENABLED}")
    logger.info("=" * 60)


# Export all configuration
__all__ = [
    # Flags
    "AWS_ENABLED",
    "PINECONE_ENABLED",
    "POSTGRESQL_ENABLED",
    "PAGERDUTY_ENABLED",

    # AWS Config
    "AWS_REGION_PRIMARY",
    "AWS_REGION_DR",
    "ROUTE53_HOSTED_ZONE_ID",
    "ROUTE53_DOMAIN",

    # Database Configs
    "PRIMARY_DB_CONFIG",
    "DR_DB_CONFIG",

    # Clients
    "cloudwatch_client",
    "route53_client",
    "rds_client",
    "pinecone_client",

    # Utilities
    "print_config_summary"
]
