"""
Configuration management for L3 M8.3: Financial Entity Recognition & Linking

This module is OFFLINE/LOCAL - no external API keys required for core functionality.

Services used:
- FinBERT: Local transformer model (Hugging Face)
- SEC EDGAR API: Free, no authentication
- Wikipedia API: Free Python library
- Redis/PostgreSQL: Optional caching (local or cloud)
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

# FinBERT Model Configuration
FINBERT_MODEL_PATH = os.getenv("FINBERT_MODEL_PATH", "ProsusAI/finbert")
FINBERT_CONFIDENCE_THRESHOLD = float(os.getenv("FINBERT_CONFIDENCE_THRESHOLD", "0.75"))

# Entity Linking Configuration
ENTITY_LINK_CONFIDENCE_THRESHOLD = float(os.getenv("ENTITY_LINK_CONFIDENCE_THRESHOLD", "0.85"))
SEC_EDGAR_USER_AGENT = os.getenv("SEC_EDGAR_USER_AGENT", "FinancialRAG contact@example.com")

# Caching Configuration (optional)
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))  # 24 hours

# Database Configuration (optional)
POSTGRES_ENABLED = os.getenv("POSTGRES_ENABLED", "false").lower() == "true"
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "financial_entities")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Metadata Enrichment Configuration
ENABLE_METADATA_ENRICHMENT = os.getenv("ENABLE_METADATA_ENRICHMENT", "true").lower() == "true"
YFINANCE_ENABLED = os.getenv("YFINANCE_ENABLED", "true").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# =============================================================================
# CONFIGURATION FUNCTIONS
# =============================================================================

def get_config() -> Dict[str, Any]:
    """
    Get application configuration.

    Returns:
        Dictionary containing all configuration settings
    """
    config = {
        # Model settings
        "finbert_model_path": FINBERT_MODEL_PATH,
        "finbert_confidence_threshold": FINBERT_CONFIDENCE_THRESHOLD,

        # Entity linking settings
        "entity_link_confidence_threshold": ENTITY_LINK_CONFIDENCE_THRESHOLD,
        "sec_edgar_user_agent": SEC_EDGAR_USER_AGENT,

        # Caching settings
        "redis_enabled": REDIS_ENABLED,
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT,
        "redis_db": REDIS_DB,
        "cache_ttl_seconds": CACHE_TTL_SECONDS,

        # Database settings
        "postgres_enabled": POSTGRES_ENABLED,
        "postgres_host": POSTGRES_HOST,
        "postgres_port": POSTGRES_PORT,
        "postgres_db": POSTGRES_DB,
        "postgres_user": POSTGRES_USER,

        # Enrichment settings
        "enable_metadata_enrichment": ENABLE_METADATA_ENRICHMENT,
        "yfinance_enabled": YFINANCE_ENABLED,

        # Logging
        "log_level": LOG_LEVEL
    }

    # Validate configuration
    _validate_config(config)

    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration settings and log warnings.

    Args:
        config: Configuration dictionary
    """
    # Check FinBERT model path
    if not config["finbert_model_path"]:
        logger.warning("⚠️ FinBERT model path not configured (will use default: ProsusAI/finbert)")

    # Check SEC EDGAR User-Agent
    if config["sec_edgar_user_agent"] == "FinancialRAG contact@example.com":
        logger.warning("⚠️ Using default SEC EDGAR User-Agent. Set SEC_EDGAR_USER_AGENT in .env for production")

    # Check Redis configuration
    if config["redis_enabled"]:
        try:
            import redis
            logger.info(f"✅ Redis enabled at {config['redis_host']}:{config['redis_port']}")
        except ImportError:
            logger.warning("⚠️ Redis enabled but redis library not installed. Install with: pip install redis")

    # Check PostgreSQL configuration
    if config["postgres_enabled"]:
        try:
            import psycopg2
            logger.info(f"✅ PostgreSQL enabled at {config['postgres_host']}:{config['postgres_port']}")
        except ImportError:
            logger.warning("⚠️ PostgreSQL enabled but psycopg2 library not installed. Install with: pip install psycopg2-binary")

    # Check yfinance for metadata enrichment
    if config["yfinance_enabled"]:
        try:
            import yfinance
            logger.info("✅ yfinance enabled for metadata enrichment")
        except ImportError:
            logger.warning("⚠️ yfinance enabled but not installed. Install with: pip install yfinance")


def get_redis_client() -> Optional[Any]:
    """
    Get configured Redis client (if enabled).

    Returns:
        Redis client instance or None if disabled/unavailable
    """
    if not REDIS_ENABLED:
        return None

    try:
        import redis

        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

        # Test connection
        client.ping()
        logger.info("✅ Connected to Redis")
        return client

    except ImportError:
        logger.error("⚠️ Redis library not installed")
        return None
    except Exception as e:
        logger.error(f"⚠️ Redis connection failed: {e}")
        return None


def get_postgres_connection() -> Optional[Any]:
    """
    Get configured PostgreSQL connection (if enabled).

    Returns:
        PostgreSQL connection or None if disabled/unavailable
    """
    if not POSTGRES_ENABLED:
        return None

    try:
        import psycopg2

        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )

        logger.info("✅ Connected to PostgreSQL")
        return conn

    except ImportError:
        logger.error("⚠️ psycopg2 library not installed")
        return None
    except Exception as e:
        logger.error(f"⚠️ PostgreSQL connection failed: {e}")
        return None


def setup_logging() -> None:
    """
    Configure logging based on environment settings.
    """
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info(f"Logging configured at {LOG_LEVEL} level")


# =============================================================================
# INITIALIZATION
# =============================================================================

# Setup logging on module import
setup_logging()

# Log startup configuration
logger.info("="*60)
logger.info("L3 M8.3: Financial Entity Recognition & Linking")
logger.info("="*60)
logger.info(f"FinBERT Model: {FINBERT_MODEL_PATH}")
logger.info(f"SEC EDGAR User-Agent: {SEC_EDGAR_USER_AGENT}")
logger.info(f"Redis Enabled: {REDIS_ENABLED}")
logger.info(f"PostgreSQL Enabled: {POSTGRES_ENABLED}")
logger.info(f"Metadata Enrichment: {ENABLE_METADATA_ENRICHMENT}")
logger.info("="*60)
