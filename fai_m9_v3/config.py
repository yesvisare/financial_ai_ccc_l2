"""
Configuration management for L3 M9.3: Regulatory Constraints in LLM Outputs
Handles environment variables, database connections, and service initialization
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ============================================================================
# SERVICE CONFIGURATION (Auto-detected: ANTHROPIC)
# ============================================================================
# This module integrates with M9.1 Citation Tracker which uses Anthropic.
# The compliance filter primarily operates on LLM outputs rather than
# generating them directly. Anthropic API is used for upstream modules.
# ============================================================================

ANTHROPIC_ENABLED = os.getenv("ANTHROPIC_ENABLED", "false").lower() == "true"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Database Configuration (PostgreSQL for compliance tracking)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "financial_compliance")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Redis Configuration (for caching and session management)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Compliance Configuration
MNPI_DETECTION_THRESHOLD = float(os.getenv("MNPI_DETECTION_THRESHOLD", "0.85"))
ENABLE_AUTO_DISCLAIMERS = os.getenv("ENABLE_AUTO_DISCLAIMERS", "true").lower() == "true"
ESCALATE_INVESTMENT_ADVICE = os.getenv("ESCALATE_INVESTMENT_ADVICE", "true").lower() == "true"

# Application Settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_anthropic_client():
    """
    Initialize and return Anthropic client for M9.1 integration.

    Note: This module primarily filters outputs from M9.1/M9.2.
    Direct Anthropic calls are minimal and inherited from upstream modules.

    Returns:
        Configured Anthropic client instance or None if disabled
    """
    if not ANTHROPIC_ENABLED:
        logger.warning("⚠️ ANTHROPIC service is disabled. Set ANTHROPIC_ENABLED=true to enable.")
        logger.info("ℹ️  Note: This module can operate as a filter without direct LLM calls")
        return None

    if not ANTHROPIC_API_KEY:
        logger.error("❌ ANTHROPIC_API_KEY not found in environment")
        logger.info("ℹ️  To enable: Add ANTHROPIC_API_KEY to .env file")
        return None

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info("✅ Anthropic client initialized successfully")
        return client
    except ImportError:
        logger.error("❌ anthropic package not installed. Run: pip install anthropic")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Anthropic client: {e}")
        return None


def get_postgres_connection():
    """
    Initialize PostgreSQL connection for compliance database.

    Returns:
        Database connection or None if unavailable
    """
    if not POSTGRES_PASSWORD:
        logger.warning("⚠️ PostgreSQL not configured (no password set)")
        logger.info("ℹ️  Set POSTGRES_PASSWORD in .env to enable database features")
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
        logger.info(f"✅ PostgreSQL connected: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
        return conn
    except ImportError:
        logger.error("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        return None
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.info("ℹ️  Verify POSTGRES_* environment variables are correct")
        return None


def get_redis_client():
    """
    Initialize Redis client for caching.

    Returns:
        Redis client or None if unavailable
    """
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
        logger.info(f"✅ Redis connected: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        return client
    except ImportError:
        logger.warning("⚠️ redis package not installed. Run: pip install redis")
        return None
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        logger.info("ℹ️  Module can operate without Redis (caching disabled)")
        return None


def get_spacy_model():
    """
    Load spaCy NLP model for linguistic analysis.

    Returns:
        spaCy language model or None if unavailable
    """
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded: en_core_web_sm")
            return nlp
        except OSError:
            logger.error("❌ spaCy model 'en_core_web_sm' not found")
            logger.info("ℹ️  Run: python -m spacy download en_core_web_sm")
            return None
    except ImportError:
        logger.error("❌ spaCy not installed. Run: pip install spacy")
        return None


def verify_configuration() -> Dict[str, Any]:
    """
    Verify all configuration settings and service availability.

    Returns:
        Configuration status report
    """
    logger.info("=" * 60)
    logger.info("L3 M9.3: Configuration Verification")
    logger.info("=" * 60)

    status = {
        "anthropic": ANTHROPIC_ENABLED and bool(ANTHROPIC_API_KEY),
        "postgres": bool(POSTGRES_PASSWORD),
        "redis": False,
        "spacy": False
    }

    # Test Anthropic
    if status["anthropic"]:
        client = get_anthropic_client()
        status["anthropic"] = client is not None
    else:
        logger.info("⚠️  Anthropic: Disabled (module can run as standalone filter)")

    # Test PostgreSQL
    if status["postgres"]:
        conn = get_postgres_connection()
        if conn:
            conn.close()
        else:
            status["postgres"] = False
    else:
        logger.warning("⚠️  PostgreSQL: Not configured")

    # Test Redis
    redis_client = get_redis_client()
    status["redis"] = redis_client is not None

    # Test spaCy
    nlp = get_spacy_model()
    status["spacy"] = nlp is not None

    logger.info("=" * 60)
    logger.info("Configuration Summary:")
    logger.info(f"  Anthropic (M9.1 Integration): {'✅' if status['anthropic'] else '⚠️  Optional'}")
    logger.info(f"  PostgreSQL (Compliance DB):   {'✅' if status['postgres'] else '❌ Required'}")
    logger.info(f"  Redis (Caching):              {'✅' if status['redis'] else '⚠️  Optional'}")
    logger.info(f"  spaCy (NLP):                  {'✅' if status['spacy'] else '❌ Required'}")
    logger.info(f"  MNPI Threshold:               {MNPI_DETECTION_THRESHOLD}")
    logger.info(f"  Auto Disclaimers:             {'Enabled' if ENABLE_AUTO_DISCLAIMERS else 'Disabled'}")
    logger.info("=" * 60)

    # Determine overall readiness
    required_services = ["postgres", "spacy"]
    all_required_ready = all(status[svc] for svc in required_services)

    if all_required_ready:
        logger.info("✅ All required services ready")
    else:
        missing = [svc for svc in required_services if not status[svc]]
        logger.error(f"❌ Missing required services: {', '.join(missing)}")

    return {
        "ready": all_required_ready,
        "services": status,
        "config": {
            "mnpi_threshold": MNPI_DETECTION_THRESHOLD,
            "auto_disclaimers": ENABLE_AUTO_DISCLAIMERS,
            "escalate_investment_advice": ESCALATE_INVESTMENT_ADVICE,
            "debug": DEBUG
        }
    }


if __name__ == "__main__":
    # Run configuration verification
    result = verify_configuration()

    if result["ready"]:
        print("\n✅ Configuration valid - Ready to start")
    else:
        print("\n❌ Configuration incomplete - Check logs above")
        print("\nTo fix:")
        print("  1. Copy .env.example to .env")
        print("  2. Set POSTGRES_PASSWORD")
        print("  3. Install spaCy model: python -m spacy download en_core_web_sm")
        print("  4. Optionally set ANTHROPIC_API_KEY for M9.1 integration")
