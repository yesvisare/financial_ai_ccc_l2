"""
Configuration management for L3 M9.2: Financial Compliance Risk

Loads environment variables and initializes optional external service clients
for semantic analysis enhancement.

SERVICE DETECTION: OFFLINE (local processing)
- Core functionality: Pattern-based risk classification (no API required)
- Optional enhancement: Semantic analysis via OpenAI/Anthropic
"""

import os
import logging
from typing import Optional, Any, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

# Core configuration (always available)
OFFLINE = os.getenv("OFFLINE", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Optional semantic analysis enhancement
SEMANTIC_ANALYSIS_ENABLED = os.getenv("SEMANTIC_ANALYSIS_ENABLED", "false").lower() == "true"

# LLM provider for semantic analysis (if enabled)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # "openai" or "anthropic"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ============================================================================
# CLIENT INITIALIZATION
# ============================================================================

def init_llm_client() -> Optional[Any]:
    """
    Initialize LLM client for optional semantic analysis.

    The core risk classifier works WITHOUT this client (pattern-based only).
    Semantic analysis is an optional 40% enhancement to classification confidence.

    Returns:
        Initialized LLM client or None if disabled/unavailable
    """
    if not SEMANTIC_ANALYSIS_ENABLED:
        logger.info("✓ Running in LOCAL mode - pattern-based classification only")
        return None

    if OFFLINE:
        logger.warning("⚠️ OFFLINE mode enabled - skipping LLM client initialization")
        return None

    # Initialize based on provider
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            logger.warning("⚠️ SEMANTIC_ANALYSIS_ENABLED=true but OPENAI_API_KEY not found")
            return None

        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✓ OpenAI client initialized for semantic analysis")
            return client
        except ImportError:
            logger.error("❌ openai package not installed. Run: pip install openai")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            return None

    elif LLM_PROVIDER == "anthropic":
        if not ANTHROPIC_API_KEY:
            logger.warning("⚠️ SEMANTIC_ANALYSIS_ENABLED=true but ANTHROPIC_API_KEY not found")
            return None

        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            logger.info("✓ Anthropic client initialized for semantic analysis")
            return client
        except ImportError:
            logger.error("❌ anthropic package not installed. Run: pip install anthropic")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Anthropic client: {e}")
            return None

    else:
        logger.warning(f"⚠️ Unknown LLM_PROVIDER: {LLM_PROVIDER} (use 'openai' or 'anthropic')")
        return None


# ============================================================================
# GLOBAL CLIENTS
# ============================================================================

# LLM client for semantic analysis (optional)
LLM_CLIENT = init_llm_client()


def get_config() -> Dict[str, Any]:
    """
    Get current configuration summary.

    Returns:
        Dict containing configuration status
    """
    return {
        "offline_mode": OFFLINE,
        "semantic_analysis_enabled": SEMANTIC_ANALYSIS_ENABLED,
        "llm_provider": LLM_PROVIDER if SEMANTIC_ANALYSIS_ENABLED else None,
        "llm_client_available": LLM_CLIENT is not None,
        "log_level": LOG_LEVEL
    }
