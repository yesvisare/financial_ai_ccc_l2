"""
Configuration and environment setup for L3 M8.4: Temporal Financial Information Handling

Manages environment variables and initializes external service clients:
- Pinecone (vector database with temporal metadata filtering)
- Anthropic Claude (LLM for response generation)
- Redis (optional caching for fiscal year ends)
"""

import os
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Environment Variables
# ============================================================================

# Pinecone Configuration (Primary Service - Required for vector queries)
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "financial-documents")

# Anthropic Configuration (Secondary Service - Optional for LLM generation)
ANTHROPIC_ENABLED = os.getenv("ANTHROPIC_ENABLED", "false").lower() == "true"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Redis Configuration (Optional - Caching fiscal year ends)
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# Pinecone Client Initialization
# ============================================================================

def get_vector_client() -> Optional[Any]:
    """
    Initialize and return Pinecone client if enabled.

    Returns:
        Pinecone client instance or None if disabled/unavailable
    """
    if not PINECONE_ENABLED:
        logger.info("⚠️ Pinecone disabled. Set PINECONE_ENABLED=true to enable vector queries.")
        return None

    if not PINECONE_API_KEY:
        logger.error("❌ PINECONE_API_KEY not set. Vector queries will fail.")
        return None

    if not PINECONE_ENVIRONMENT:
        logger.error("❌ PINECONE_ENVIRONMENT not set. Required for Pinecone initialization.")
        return None

    try:
        # Import Pinecone only if needed
        import pinecone

        # Initialize Pinecone
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT
        )

        # Get or create index
        if PINECONE_INDEX_NAME not in pinecone.list_indexes():
            logger.warning(f"⚠️ Index '{PINECONE_INDEX_NAME}' not found in Pinecone environment.")
            logger.warning("   Create index with: pinecone.create_index(name, dimension, metric)")
            return None

        index = pinecone.Index(PINECONE_INDEX_NAME)
        logger.info(f"✅ Pinecone client initialized (index: {PINECONE_INDEX_NAME})")
        return index

    except ImportError:
        logger.error("❌ Pinecone library not installed. Run: pip install pinecone-client")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Pinecone: {str(e)}")
        return None


# ============================================================================
# Anthropic Client Initialization
# ============================================================================

def get_anthropic_client() -> Optional[Any]:
    """
    Initialize and return Anthropic client if enabled.

    Returns:
        Anthropic client instance or None if disabled/unavailable
    """
    if not ANTHROPIC_ENABLED:
        logger.info("⚠️ Anthropic disabled. Set ANTHROPIC_ENABLED=true to enable LLM generation.")
        return None

    if not ANTHROPIC_API_KEY:
        logger.error("❌ ANTHROPIC_API_KEY not set. LLM generation will fail.")
        return None

    try:
        # Import Anthropic only if needed
        from anthropic import Anthropic

        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info("✅ Anthropic client initialized")
        return client

    except ImportError:
        logger.error("❌ Anthropic library not installed. Run: pip install anthropic")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Anthropic: {str(e)}")
        return None


# ============================================================================
# Redis Client Initialization
# ============================================================================

def get_redis_client() -> Optional[Any]:
    """
    Initialize and return Redis client if enabled.

    Returns:
        Redis client instance or None if disabled/unavailable
    """
    if not REDIS_ENABLED:
        logger.info("⚠️ Redis disabled. Fiscal year ends will not be cached.")
        return None

    try:
        # Import Redis only if needed
        import redis

        client = redis.from_url(REDIS_URL)
        # Test connection
        client.ping()
        logger.info(f"✅ Redis client initialized (url: {REDIS_URL})")
        return client

    except ImportError:
        logger.error("❌ Redis library not installed. Run: pip install redis")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis: {str(e)}")
        return None


# ============================================================================
# Initialize Clients on Module Load
# ============================================================================

# Initialize vector client (Pinecone)
vector_client = get_vector_client()

# Initialize LLM client (Anthropic) - optional
anthropic_client = get_anthropic_client()

# Initialize cache client (Redis) - optional
redis_client = get_redis_client()


# ============================================================================
# Configuration Summary
# ============================================================================

def print_config_summary():
    """Print configuration summary for debugging."""
    print("\n" + "="*60)
    print("L3 M8.4: Temporal Financial Information Handling - Configuration")
    print("="*60)
    print(f"Pinecone:   {'✅ Enabled' if PINECONE_ENABLED else '❌ Disabled'}")
    if PINECONE_ENABLED:
        print(f"  - API Key:     {'✅ Set' if PINECONE_API_KEY else '❌ Not Set'}")
        print(f"  - Environment: {PINECONE_ENVIRONMENT or '❌ Not Set'}")
        print(f"  - Index:       {PINECONE_INDEX_NAME}")
        print(f"  - Client:      {'✅ Initialized' if vector_client else '❌ Failed'}")

    print(f"\nAnthropic:  {'✅ Enabled' if ANTHROPIC_ENABLED else '❌ Disabled (Optional)'}")
    if ANTHROPIC_ENABLED:
        print(f"  - API Key:     {'✅ Set' if ANTHROPIC_API_KEY else '❌ Not Set'}")
        print(f"  - Client:      {'✅ Initialized' if anthropic_client else '❌ Failed'}")

    print(f"\nRedis:      {'✅ Enabled' if REDIS_ENABLED else '❌ Disabled (Optional)'}")
    if REDIS_ENABLED:
        print(f"  - URL:         {REDIS_URL}")
        print(f"  - Client:      {'✅ Initialized' if redis_client else '❌ Failed'}")

    print("\nLog Level:  " + LOG_LEVEL)
    print("="*60 + "\n")


# Print summary if running as main module
if __name__ == "__main__":
    print_config_summary()
