"""
Configuration for L3 M8.2: Real-Time Financial Data Enrichment

This module manages environment variables and client initialization for:
- Redis (caching layer)
- OpenAI (for RAG embeddings and chat - optional)
- Pinecone (for vector storage - optional)

All external services are optional and can be disabled via environment variables.
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Environment variables - Redis Configuration
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_URL = os.getenv("REDIS_URL", "")  # Full connection string (overrides individual params)

# OpenAI Configuration (optional - for RAG integration)
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Pinecone Configuration (optional - for vector storage)
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "financial-rag")

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class Config:
    """
    Application configuration manager.

    Validates environment variables and provides configuration objects
    for external services.
    """

    def __init__(self):
        """Initialize configuration and validate settings."""
        # Redis configuration
        self.redis_enabled = REDIS_ENABLED
        self.redis_host = REDIS_HOST
        self.redis_port = REDIS_PORT
        self.redis_password = REDIS_PASSWORD
        self.redis_db = REDIS_DB
        self.redis_url = REDIS_URL

        # OpenAI configuration
        self.openai_enabled = OPENAI_ENABLED
        self.openai_api_key = OPENAI_API_KEY

        # Pinecone configuration
        self.pinecone_enabled = PINECONE_ENABLED
        self.pinecone_api_key = PINECONE_API_KEY
        self.pinecone_environment = PINECONE_ENVIRONMENT
        self.pinecone_index_name = PINECONE_INDEX_NAME

        # Log level
        self.log_level = LOG_LEVEL

        # Validate configuration
        self._validate()

    def _validate(self):
        """Validate configuration and warn about missing credentials."""
        # Validate Redis
        if self.redis_enabled:
            if not self.redis_url and not self.redis_host:
                logger.warning("⚠️ REDIS_ENABLED=true but no REDIS_HOST or REDIS_URL provided")

        # Validate OpenAI
        if self.openai_enabled and not self.openai_api_key:
            logger.warning("⚠️ OPENAI_ENABLED=true but no OPENAI_API_KEY provided")

        # Validate Pinecone
        if self.pinecone_enabled:
            if not self.pinecone_api_key:
                logger.warning("⚠️ PINECONE_ENABLED=true but no PINECONE_API_KEY provided")
            if not self.pinecone_environment:
                logger.warning("⚠️ PINECONE_ENABLED=true but no PINECONE_ENVIRONMENT provided")

    def is_redis_ready(self) -> bool:
        """Check if Redis configuration is valid."""
        if not self.redis_enabled:
            return False
        return bool(self.redis_url or self.redis_host)

    def is_openai_ready(self) -> bool:
        """Check if OpenAI configuration is valid."""
        if not self.openai_enabled:
            return False
        return bool(self.openai_api_key)

    def is_pinecone_ready(self) -> bool:
        """Check if Pinecone configuration is valid."""
        if not self.pinecone_enabled:
            return False
        return bool(self.pinecone_api_key and self.pinecone_environment)

    def get_redis_connection_string(self) -> str:
        """
        Get Redis connection string.

        Returns:
            Redis URL in format: redis://[:password@]host:port/db
        """
        if self.redis_url:
            return self.redis_url

        # Build connection string from individual parameters
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global config instance
config = Config()


# Client initialization functions

def get_redis_client():
    """
    Get Redis client if enabled and configured.

    Returns:
        Redis client instance or None if disabled/not configured

    Example:
        >>> redis_client = get_redis_client()
        >>> if redis_client:
        ...     redis_client.ping()
    """
    if not config.is_redis_ready():
        logger.info("⚠️ Redis disabled or not configured - caching unavailable")
        return None

    try:
        import redis
        redis_url = config.get_redis_connection_string()
        logger.info(f"Connecting to Redis at {redis_url}")

        client = redis.from_url(
            redis_url,
            decode_responses=False,  # We handle decoding manually
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test connection
        client.ping()
        logger.info("✅ Redis connection successful")
        return client

    except ImportError:
        logger.error("❌ Redis library not installed. Install with: pip install redis")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
        logger.info("⚠️ Continuing without caching - performance will be degraded")
        return None


def get_openai_client():
    """
    Get OpenAI client if enabled and configured.

    Returns:
        OpenAI client instance or None if disabled/not configured

    Note:
        Requires OPENAI_ENABLED=true and OPENAI_API_KEY to be set
    """
    if not config.is_openai_ready():
        logger.info("⚠️ OpenAI disabled or not configured - full RAG features unavailable")
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=config.openai_api_key)
        logger.info("✅ OpenAI client initialized")
        return client

    except ImportError:
        logger.error("❌ OpenAI library not installed. Install with: pip install openai")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        return None


def get_pinecone_client():
    """
    Get Pinecone client if enabled and configured.

    Returns:
        Pinecone client instance or None if disabled/not configured

    Note:
        Requires PINECONE_ENABLED=true, PINECONE_API_KEY, and PINECONE_ENVIRONMENT
    """
    if not config.is_pinecone_ready():
        logger.info("⚠️ Pinecone disabled or not configured - vector storage unavailable")
        return None

    try:
        import pinecone

        pinecone.init(
            api_key=config.pinecone_api_key,
            environment=config.pinecone_environment
        )

        logger.info(f"✅ Pinecone initialized (environment: {config.pinecone_environment})")
        return pinecone

    except ImportError:
        logger.error("❌ Pinecone library not installed. Install with: pip install pinecone-client")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Pinecone: {e}")
        return None


# Initialize logging based on config
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Configuration summary (logged at startup)
def log_configuration_summary():
    """Log configuration summary for debugging."""
    logger.info("=" * 60)
    logger.info("L3 M8.2: Real-Time Financial Data Enrichment - Configuration")
    logger.info("=" * 60)
    logger.info(f"Redis: {'✅ Enabled' if config.redis_enabled else '❌ Disabled'}")
    if config.redis_enabled:
        logger.info(f"  Host: {config.redis_host}:{config.redis_port}")
        logger.info(f"  Database: {config.redis_db}")

    logger.info(f"OpenAI: {'✅ Enabled' if config.openai_enabled else '❌ Disabled'}")
    if config.openai_enabled:
        api_key_preview = config.openai_api_key[:8] + "..." if config.openai_api_key else "Not set"
        logger.info(f"  API Key: {api_key_preview}")

    logger.info(f"Pinecone: {'✅ Enabled' if config.pinecone_enabled else '❌ Disabled'}")
    if config.pinecone_enabled:
        logger.info(f"  Environment: {config.pinecone_environment}")
        logger.info(f"  Index: {config.pinecone_index_name}")

    logger.info("=" * 60)


# Log configuration on import (only if running directly)
if __name__ != "__main__":
    log_configuration_summary()
