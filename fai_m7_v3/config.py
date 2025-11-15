"""
Configuration management for L3 M7.3: Financial Document Parsing & Chunking
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SEC EDGAR API Configuration (Primary Service - Required)
EDGAR_ENABLED = os.getenv("EDGAR_ENABLED", "false").lower() == "true"
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "")

# Validate SEC User-Agent (required by SEC EDGAR API)
if EDGAR_ENABLED and not SEC_USER_AGENT:
    logger.warning("⚠️ SEC_USER_AGENT not set. EDGAR API requires company name and email.")
    logger.warning("⚠️ Example: 'CompanyName product-team@company.com'")
    EDGAR_ENABLED = False

if EDGAR_ENABLED and '@' not in SEC_USER_AGENT:
    logger.warning("⚠️ SEC_USER_AGENT must include email address (format: 'CompanyName email@company.com')")
    EDGAR_ENABLED = False

# Rate Limiting Configuration
SEC_RATE_LIMIT = int(os.getenv("SEC_RATE_LIMIT", "10"))  # 10 requests/second default (SEC maximum)

# Processing Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Optional: OpenAI API Configuration (for embeddings)
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if OPENAI_ENABLED and not OPENAI_API_KEY:
    logger.warning("⚠️ OPENAI_API_KEY not set. OpenAI features disabled.")
    OPENAI_ENABLED = False

# Optional: Pinecone Configuration (for vector database)
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "financial-filings")

if PINECONE_ENABLED and not PINECONE_API_KEY:
    logger.warning("⚠️ PINECONE_API_KEY not set. Pinecone features disabled.")
    PINECONE_ENABLED = False


def get_edgar_client() -> Optional[Dict[str, Any]]:
    """
    Get EDGAR API client configuration if enabled.

    Returns:
        Client configuration dict if enabled, None otherwise
    """
    if not EDGAR_ENABLED:
        logger.info("⚠️ EDGAR disabled - returning None")
        return None

    try:
        # Initialize EDGAR client configuration
        # Actual implementation would use requests with proper headers
        logger.info("✅ EDGAR client initialized")
        return {
            "base_url": "https://www.sec.gov",
            "user_agent": SEC_USER_AGENT,
            "rate_limit": SEC_RATE_LIMIT
        }
    except Exception as e:
        logger.error(f"Failed to initialize EDGAR client: {str(e)}")
        return None


def get_openai_client() -> Optional[Any]:
    """
    Get OpenAI client if enabled.

    Returns:
        OpenAI client instance if enabled, None otherwise
    """
    if not OPENAI_ENABLED:
        logger.info("⚠️ OpenAI disabled - vector embedding features unavailable")
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI client initialized")
        return client
    except ImportError:
        logger.error("OpenAI library not installed. Run: pip install openai")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        return None


def get_pinecone_client() -> Optional[Any]:
    """
    Get Pinecone client if enabled.

    Returns:
        Pinecone index instance if enabled, None otherwise
    """
    if not PINECONE_ENABLED:
        logger.info("⚠️ Pinecone disabled - vector database features unavailable")
        return None

    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        logger.info(f"✅ Pinecone client initialized (index: {PINECONE_INDEX_NAME})")
        return index
    except ImportError:
        logger.error("Pinecone library not installed. Run: pip install pinecone-client")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone client: {str(e)}")
        return None


def get_config() -> Dict[str, Any]:
    """
    Get complete configuration dictionary.

    Returns:
        Configuration dictionary with all settings
    """
    return {
        # Primary Service (Required)
        "edgar_enabled": EDGAR_ENABLED,
        "sec_user_agent": SEC_USER_AGENT,
        "sec_rate_limit": SEC_RATE_LIMIT,

        # Processing Settings
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,

        # Optional Services
        "openai_enabled": OPENAI_ENABLED,
        "pinecone_enabled": PINECONE_ENABLED,
        "pinecone_index": PINECONE_INDEX_NAME,
    }


# Log configuration on import
logger.info("=" * 60)
logger.info("L3 M7.3: Financial Document Parsing & Chunking")
logger.info("=" * 60)
logger.info(f"EDGAR enabled: {EDGAR_ENABLED}")
if EDGAR_ENABLED:
    logger.info(f"SEC rate limit: {SEC_RATE_LIMIT} req/sec")
else:
    logger.info("⚠️ Running in offline mode (EDGAR disabled)")
    logger.info("⚠️ To enable: Set EDGAR_ENABLED=true and SEC_USER_AGENT in .env")

logger.info(f"OpenAI enabled: {OPENAI_ENABLED}")
logger.info(f"Pinecone enabled: {PINECONE_ENABLED}")
logger.info("=" * 60)
