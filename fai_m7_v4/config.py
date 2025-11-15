"""
Configuration management for L3 M7.4: Audit Trail & Document Provenance
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Database Configuration (PostgreSQL for audit trail)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/audit_db"
)

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def get_database_url() -> str:
    """
    Get PostgreSQL database URL.

    Returns:
        Database connection string

    Raises:
        ValueError: If DATABASE_URL is invalid
    """
    if not DATABASE_URL.startswith("postgresql://"):
        raise ValueError("DATABASE_URL must be a valid PostgreSQL connection string")

    logger.info("Database URL configured")
    return DATABASE_URL


def validate_config() -> bool:
    """
    Validate configuration on startup.

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If configuration is invalid
    """
    try:
        get_database_url()
        logger.info("✅ Configuration validated successfully")
        logger.info(f"Log Level: {LOG_LEVEL}")
        logger.info(f"Debug Mode: {DEBUG}")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {str(e)}")
        raise
