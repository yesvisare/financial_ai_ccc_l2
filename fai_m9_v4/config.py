"""Configuration and client setup for L3 M9.4: Human-in-the-Loop for High-Stakes Decisions"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# SERVICE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
# This module focuses on workflow orchestration and can operate independently
# of external AI services. OPENAI is optional for RAG response generation.

# Optional AI Service Configuration (for RAG response generation)
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Database Configuration (for audit trail persistence)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/financial_ai")

# Redis Configuration (for queue management)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Notification Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_ENABLED = os.getenv("SENDGRID_ENABLED", "false").lower() == "true"

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_ENABLED = os.getenv("SLACK_ENABLED", "false").lower() == "true"

# SLA Configuration
DEFAULT_SLA_HOURS = int(os.getenv("DEFAULT_SLA_HOURS", "24"))
SLA_WARNING_THRESHOLD = float(os.getenv("SLA_WARNING_THRESHOLD", "0.8"))  # Warn at 80% of SLA

# Workflow Configuration
ENABLE_AUTO_ESCALATION = os.getenv("ENABLE_AUTO_ESCALATION", "true").lower() == "true"
ESCALATION_THRESHOLD_HOURS = int(os.getenv("ESCALATION_THRESHOLD_HOURS", "2"))

# Security Configuration
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "2555"))  # 7 years for SOX compliance
HASH_ALGORITHM = os.getenv("HASH_ALGORITHM", "sha256")


def get_openai_client():
    """
    Initialize and return OpenAI client (optional for RAG integration).

    Returns:
        OpenAI client instance or None if service disabled
    """
    if not OPENAI_ENABLED:
        logger.info("ℹ️ OPENAI disabled. Workflow operates independently.")
        return None

    if not OPENAI_API_KEY:
        logger.warning("⚠️ OPENAI_API_KEY not set. RAG response generation unavailable.")
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OPENAI client initialized for RAG integration")
        return client
    except ImportError:
        logger.warning("⚠️ openai package not installed. Install with: pip install openai")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize OPENAI client: {e}")
        return None


def get_database_connection():
    """
    Initialize database connection for audit trail persistence.

    Returns:
        Database connection or None if unavailable
    """
    if not DATABASE_URL or DATABASE_URL == "postgresql://localhost/financial_ai":
        logger.warning("⚠️ DATABASE_URL not configured. Using in-memory storage.")
        return None

    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("✅ Database connection established")
        return conn
    except ImportError:
        logger.warning("⚠️ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        return None


def get_redis_connection():
    """
    Initialize Redis connection for queue management.

    Returns:
        Redis client or None if unavailable
    """
    if not REDIS_URL or REDIS_URL == "redis://localhost:6379/0":
        logger.warning("⚠️ REDIS_URL not configured. Queue management disabled.")
        return None

    try:
        import redis
        client = redis.from_url(REDIS_URL)
        client.ping()
        logger.info("✅ Redis connection established")
        return client
    except ImportError:
        logger.warning("⚠️ redis package not installed. Install with: pip install redis")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
        return None


# Module-specific configuration
MODULE_CONFIG = {
    "timeout": int(os.getenv("TIMEOUT", "30")),
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
    "enable_notifications": SENDGRID_ENABLED or SLACK_ENABLED,
    "enable_auto_escalation": ENABLE_AUTO_ESCALATION,
    "sla_warning_threshold": SLA_WARNING_THRESHOLD,
}


def validate_configuration() -> dict:
    """
    Validate configuration and return status report.

    Returns:
        Dictionary with configuration validation results
    """
    status = {
        "core_workflow": "✅ Ready",
        "openai_integration": "✅ Enabled" if OPENAI_ENABLED else "⚠️ Disabled",
        "database": "⚠️ Not configured (using in-memory storage)",
        "redis_queue": "⚠️ Not configured (queue management disabled)",
        "notifications": "⚠️ Disabled",
        "warnings": [],
    }

    # Check database
    if DATABASE_URL and DATABASE_URL != "postgresql://localhost/financial_ai":
        db_conn = get_database_connection()
        if db_conn:
            status["database"] = "✅ Connected"
            db_conn.close()
        else:
            status["database"] = "❌ Connection failed"

    # Check Redis
    if REDIS_URL and REDIS_URL != "redis://localhost:6379/0":
        redis_conn = get_redis_connection()
        if redis_conn:
            status["redis_queue"] = "✅ Connected"
        else:
            status["redis_queue"] = "❌ Connection failed"

    # Check notifications
    if SENDGRID_ENABLED or SLACK_ENABLED:
        status["notifications"] = "✅ Enabled"

    # Add warnings
    if not OPENAI_ENABLED:
        status["warnings"].append("OPENAI disabled - RAG response generation unavailable")

    if status["database"].startswith("⚠️"):
        status["warnings"].append("Database not configured - audit trail stored in memory only")

    if status["redis_queue"].startswith("⚠️"):
        status["warnings"].append("Redis not configured - queue management disabled")

    return status


if __name__ == "__main__":
    # Configuration validation for testing
    logging.basicConfig(level=logging.INFO)
    print("\n" + "=" * 60)
    print("L3 M9.4 Configuration Status")
    print("=" * 60)

    validation = validate_configuration()
    for key, value in validation.items():
        if key != "warnings":
            print(f"{key:20s}: {value}")

    if validation["warnings"]:
        print("\nWarnings:")
        for warning in validation["warnings"]:
            print(f"  ⚠️ {warning}")

    print("=" * 60 + "\n")
