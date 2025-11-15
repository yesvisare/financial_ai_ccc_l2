"""
Configuration management for L3 M8.1: Financial Terminology & Concept Embeddings

Loads environment variables and initializes external service clients.
Primary SERVICE: PINECONE (vector database)
Secondary: SENTENCE_TRANSFORMERS (local embeddings - no API key needed)
"""

import os
import logging
from typing import Optional, Any, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Service configuration
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "financial-knowledge")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def init_clients() -> Dict[str, Any]:
    """
    Initialize external service clients based on environment config.

    Returns:
        Dict containing initialized clients or empty dict if disabled
    """
    clients = {}

    if not PINECONE_ENABLED:
        logger.warning("⚠️ PINECONE disabled - vector search unavailable")
        logger.info("   → Set PINECONE_ENABLED=true in .env to enable")
        return clients

    if not PINECONE_API_KEY:
        logger.warning("⚠️ PINECONE_API_KEY not found - clients unavailable")
        logger.info("   → Add PINECONE_API_KEY to .env file")
        return clients

    try:
        # Initialize Pinecone client
        from pinecone import Pinecone

        pc = Pinecone(api_key=PINECONE_API_KEY)
        clients["pinecone"] = pc

        # Check if index exists
        try:
            index_list = pc.list_indexes()
            index_names = [idx.name for idx in index_list.indexes]

            if PINECONE_INDEX_NAME in index_names:
                logger.info(f"✓ Connected to existing Pinecone index: {PINECONE_INDEX_NAME}")
                clients["pinecone_index"] = pc.Index(PINECONE_INDEX_NAME)
            else:
                logger.warning(f"⚠️ Pinecone index '{PINECONE_INDEX_NAME}' not found")
                logger.info(f"   → Available indexes: {index_names}")
                logger.info("   → Create index or update PINECONE_INDEX_NAME in .env")

        except Exception as e:
            logger.warning(f"⚠️ Could not verify Pinecone index: {e}")

        logger.info("✓ Pinecone client initialized")

    except ImportError:
        logger.error("⚠️ pinecone-client library not installed")
        logger.info("   → Run: pip install pinecone-client")
        return clients

    except Exception as e:
        logger.error(f"⚠️ Pinecone initialization failed: {e}")
        return clients

    return clients


def init_embedding_model() -> Optional[Any]:
    """
    Initialize sentence-transformers model (local, no API key needed).

    Returns:
        SentenceTransformer model or None if unavailable
    """
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✓ Loaded sentence-transformers model: all-MiniLM-L6-v2 (384 dims)")
        return model

    except ImportError:
        logger.warning("⚠️ sentence-transformers not installed")
        logger.info("   → Run: pip install sentence-transformers")
        return None

    except Exception as e:
        logger.error(f"⚠️ Model loading failed: {e}")
        return None


# Global clients dictionary
CLIENTS = init_clients()

# Global embedding model
EMBEDDING_MODEL = init_embedding_model()
