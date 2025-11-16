"""Configuration management for L3 M9.1: Explainability & Citation Tracking"""

import os
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Service Configuration (Multi-service setup)
# Primary: ANTHROPIC (Claude API for LLM generation)
# Secondary: OPENAI (for text embeddings)
# Tertiary: PINECONE (for vector database)

ANTHROPIC_ENABLED = os.getenv("ANTHROPIC_ENABLED", "false").lower() == "true"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "sec-filings")

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def get_anthropic_client() -> Optional[Any]:
    """
    Get configured Anthropic client for Claude API.

    Returns:
        Anthropic client instance or None if disabled/not configured
    """
    if not ANTHROPIC_ENABLED:
        logger.warning("⚠️ ANTHROPIC is disabled - LLM generation unavailable")
        return None

    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set but service enabled")
        raise ValueError("ANTHROPIC_API_KEY required when ANTHROPIC_ENABLED=true")

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info("✅ ANTHROPIC client initialized successfully")
        return client
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize ANTHROPIC client: {str(e)}")
        return None


def get_openai_embeddings() -> Optional[Any]:
    """
    Get configured OpenAI embeddings model.

    Returns:
        OpenAI embeddings instance or None if disabled/not configured
    """
    if not OPENAI_ENABLED:
        logger.warning("⚠️ OPENAI is disabled - embeddings unavailable")
        return None

    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set but service enabled")
        raise ValueError("OPENAI_API_KEY required when OPENAI_ENABLED=true")

    try:
        from langchain.embeddings import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        )
        logger.info("✅ OPENAI embeddings initialized successfully")
        return embeddings
    except ImportError:
        logger.error("langchain/openai packages not installed. Run: pip install langchain openai")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OPENAI embeddings: {str(e)}")
        return None


def get_pinecone_vectorstore(namespace: str = "sec-filings") -> Optional[Any]:
    """
    Get configured Pinecone vector store.

    Args:
        namespace: Pinecone namespace for document storage

    Returns:
        Pinecone vector store instance or None if disabled/not configured
    """
    if not PINECONE_ENABLED:
        logger.warning("⚠️ PINECONE is disabled - vector search unavailable")
        return None

    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not set but service enabled")
        raise ValueError("PINECONE_API_KEY required when PINECONE_ENABLED=true")

    try:
        import pinecone
        from langchain.vectorstores import Pinecone

        # Initialize Pinecone
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT
        )

        # Get embeddings
        embeddings = get_openai_embeddings()
        if embeddings is None:
            logger.error("Cannot create vectorstore without embeddings")
            return None

        # Create vectorstore
        vectorstore = Pinecone.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings,
            namespace=namespace
        )

        logger.info(f"✅ PINECONE vectorstore initialized: {PINECONE_INDEX_NAME}/{namespace}")
        return vectorstore
    except ImportError:
        logger.error("pinecone-client/langchain packages not installed. Run: pip install pinecone-client langchain")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize PINECONE vectorstore: {str(e)}")
        return None


def validate_config() -> bool:
    """
    Validate configuration and return status.

    Returns:
        True if configuration is valid, False otherwise
    """
    valid = True

    # Check ANTHROPIC configuration
    if ANTHROPIC_ENABLED and not ANTHROPIC_API_KEY:
        logger.error("Invalid config: ANTHROPIC enabled but no API key")
        valid = False

    # Check OPENAI configuration
    if OPENAI_ENABLED and not OPENAI_API_KEY:
        logger.error("Invalid config: OPENAI enabled but no API key")
        valid = False

    # Check PINECONE configuration
    if PINECONE_ENABLED:
        if not PINECONE_API_KEY:
            logger.error("Invalid config: PINECONE enabled but no API key")
            valid = False
        if not PINECONE_ENVIRONMENT:
            logger.error("Invalid config: PINECONE enabled but no environment")
            valid = False

    if valid:
        logger.info("✅ Configuration validated successfully")
    else:
        logger.warning("⚠️ Configuration validation failed - some features will not work")

    # Log service status
    logger.info(f"Service status: ANTHROPIC={ANTHROPIC_ENABLED}, OPENAI={OPENAI_ENABLED}, PINECONE={PINECONE_ENABLED}")

    return valid


def get_service_status() -> dict:
    """
    Get current status of all services.

    Returns:
        Dictionary with service availability status
    """
    return {
        "anthropic_enabled": ANTHROPIC_ENABLED,
        "anthropic_configured": ANTHROPIC_ENABLED and bool(ANTHROPIC_API_KEY),
        "openai_enabled": OPENAI_ENABLED,
        "openai_configured": OPENAI_ENABLED and bool(OPENAI_API_KEY),
        "pinecone_enabled": PINECONE_ENABLED,
        "pinecone_configured": PINECONE_ENABLED and bool(PINECONE_API_KEY) and bool(PINECONE_ENVIRONMENT),
        "environment": ENVIRONMENT
    }
