"""
Configuration and environment management for L3_M10.3
Handles API keys, service initialization, and environment variables

Services detected from script Section 4:
- OpenAI (primary): Embeddings API for drift detection
- Pinecone (secondary): Vector database for knowledge storage
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Service configuration - auto-detected from script Section 4
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "financial-kb-drift")

# Application settings
DRIFT_THRESHOLD = float(os.getenv("DRIFT_THRESHOLD", "0.85"))
RETRAINING_BATCH_SIZE = int(os.getenv("RETRAINING_BATCH_SIZE", "50"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# PostgreSQL configuration for audit trails
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "financial_kb_drift")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")


def get_openai_client():
    """
    Get OpenAI client if enabled.

    Returns:
        OpenAI client or None if disabled/missing keys
    """
    if not OPENAI_ENABLED:
        logger.warning("⚠️ OPENAI disabled in environment")
        return None

    if not OPENAI_API_KEY:
        logger.warning("⚠️ OPENAI_API_KEY not set")
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI client initialized")
        return client
    except ImportError:
        logger.error("OpenAI library not installed. Install with: pip install openai")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI: {e}")
        return None


def get_pinecone_index():
    """
    Get Pinecone index if enabled.

    Returns:
        Pinecone index or None if disabled/missing keys
    """
    if not PINECONE_ENABLED:
        logger.warning("⚠️ PINECONE disabled in environment")
        return None

    if not PINECONE_API_KEY or not PINECONE_ENVIRONMENT:
        logger.warning("⚠️ PINECONE_API_KEY or PINECONE_ENVIRONMENT not set")
        return None

    try:
        import pinecone

        # Initialize Pinecone
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT
        )

        # Get or create index
        if PINECONE_INDEX_NAME not in pinecone.list_indexes():
            logger.info(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
            pinecone.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=1536,  # text-embedding-3-small dimensions
                metric="cosine"
            )

        index = pinecone.Index(PINECONE_INDEX_NAME)
        logger.info(f"✅ Pinecone index '{PINECONE_INDEX_NAME}' initialized")
        return index
    except ImportError:
        logger.error("Pinecone library not installed. Install with: pip install pinecone-client")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {e}")
        return None


def get_postgres_connection():
    """
    Get PostgreSQL connection for audit trails.

    Returns:
        PostgreSQL connection or None if disabled/missing config
    """
    if not POSTGRES_USER or not POSTGRES_PASSWORD:
        logger.warning("⚠️ PostgreSQL credentials not set")
        return None

    try:
        import psycopg2

        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        logger.info("✅ PostgreSQL connection established")
        return conn
    except ImportError:
        logger.error("psycopg2 library not installed. Install with: pip install psycopg2-binary")
        return None
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        return None


def validate_config() -> bool:
    """
    Validate configuration before running.

    Returns:
        True if config is valid, False otherwise
    """
    errors = []

    # Check OpenAI configuration
    if OPENAI_ENABLED and not OPENAI_API_KEY:
        errors.append("OPENAI enabled but no API key provided")

    # Check Pinecone configuration
    if PINECONE_ENABLED:
        if not PINECONE_API_KEY:
            errors.append("PINECONE enabled but no API key provided")
        if not PINECONE_ENVIRONMENT:
            errors.append("PINECONE enabled but no environment provided")

    # Check drift threshold
    if not (0.0 <= DRIFT_THRESHOLD <= 1.0):
        errors.append(f"DRIFT_THRESHOLD must be between 0 and 1, got {DRIFT_THRESHOLD}")

    # Check batch size
    if RETRAINING_BATCH_SIZE <= 0:
        errors.append(f"RETRAINING_BATCH_SIZE must be positive, got {RETRAINING_BATCH_SIZE}")

    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        return False

    logger.info("Configuration validated successfully")
    return True


def get_service_status() -> dict:
    """
    Get status of all configured services.

    Returns:
        Dict with service availability status
    """
    status = {
        "openai": {
            "enabled": OPENAI_ENABLED,
            "configured": bool(OPENAI_API_KEY),
            "available": get_openai_client() is not None
        },
        "pinecone": {
            "enabled": PINECONE_ENABLED,
            "configured": bool(PINECONE_API_KEY and PINECONE_ENVIRONMENT),
            "available": False  # Checked separately to avoid initialization
        },
        "postgres": {
            "enabled": bool(POSTGRES_USER and POSTGRES_PASSWORD),
            "configured": bool(POSTGRES_USER and POSTGRES_PASSWORD),
            "available": False  # Checked separately to avoid connection
        },
        "settings": {
            "drift_threshold": DRIFT_THRESHOLD,
            "retraining_batch_size": RETRAINING_BATCH_SIZE,
            "log_level": LOG_LEVEL
        }
    }

    return status
