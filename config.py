"""
Configuration and client initialization for L3 M7.1: Financial Document Types & Regulatory Context

Manages environment variables, EDGAR client initialization, and application configuration.
"""

import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Load environment variables
EDGAR_ENABLED = os.getenv("EDGAR_ENABLED", "false").lower() == "true"
EDGAR_USER_AGENT = os.getenv("EDGAR_USER_AGENT", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
OFFLINE = os.getenv("OFFLINE", "false").lower() == "true"

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize EDGAR client
edgar_client: Optional[Any] = None

if EDGAR_ENABLED:
    try:
        # EDGAR client initialization
        # Note: Using sec-edgar-downloader or direct SEC API
        # For demonstration, we'll use a placeholder
        # In production, initialize actual EDGAR client:
        # from sec_edgar_downloader import Downloader
        # company_name, email = EDGAR_USER_AGENT.split()
        # edgar_client = Downloader(company_name, email)

        logger.info("✓ EDGAR client initialized")
        logger.info(f"  User Agent: {EDGAR_USER_AGENT}")

        # Placeholder client for offline mode
        class EDGARClientPlaceholder:
            """Placeholder EDGAR client for demonstration."""
            def __init__(self, user_agent: str):
                self.user_agent = user_agent
                logger.info(f"EDGAR client placeholder created with user agent: {user_agent}")

            def get_filing(self, ticker: str, form_type: str):
                """Placeholder method for getting filings."""
                logger.warning("⚠️ EDGAR client not fully configured - using placeholder")
                return {"status": "placeholder", "message": "Set up actual EDGAR client for production use"}

        if EDGAR_USER_AGENT:
            edgar_client = EDGARClientPlaceholder(EDGAR_USER_AGENT)
        else:
            logger.warning("⚠️ EDGAR_USER_AGENT not set - client not initialized")
            edgar_client = None

    except Exception as e:
        logger.error(f"Failed to initialize EDGAR client: {e}")
        logger.error("  → Check EDGAR_USER_AGENT format: 'CompanyName email@example.com'")
        edgar_client = None
else:
    logger.info("⚠️ EDGAR service disabled - running in offline mode")
    logger.info("  → Set EDGAR_ENABLED=true in .env to enable")


def get_edgar_client():
    """
    Get EDGAR client instance.

    Returns:
        EDGAR client if available, None otherwise
    """
    if not EDGAR_ENABLED or edgar_client is None:
        logger.warning("EDGAR client not available")
        logger.warning("  → Enable with EDGAR_ENABLED=true in .env")
        return None
    return edgar_client


def get_config() -> dict:
    """
    Get current application configuration.

    Returns:
        Dict with configuration values
    """
    return {
        "edgar_enabled": EDGAR_ENABLED,
        "edgar_user_agent": EDGAR_USER_AGENT if EDGAR_USER_AGENT else "Not configured",
        "log_level": LOG_LEVEL,
        "offline": OFFLINE,
        "edgar_client_available": edgar_client is not None,
    }


# Export configuration
__all__ = [
    "EDGAR_ENABLED",
    "EDGAR_USER_AGENT",
    "LOG_LEVEL",
    "OFFLINE",
    "edgar_client",
    "get_edgar_client",
    "get_config",
]
