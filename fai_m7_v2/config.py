"""
Configuration management for M7.2: PII Detection & Financial Data Redaction
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Presidio Configuration (Self-Hosted)
PRESIDIO_ENABLED = os.getenv("PRESIDIO_ENABLED", "false").lower() == "true"
SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_lg")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

# Audit Trail Configuration
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "2555"))  # 7 years
ENABLE_HASH_CHAIN = os.getenv("ENABLE_HASH_CHAIN", "true").lower() == "true"

# Initialize Presidio components
presidio_analyzer = None
presidio_anonymizer = None

if PRESIDIO_ENABLED:
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        import spacy

        # Load spaCy model
        try:
            nlp = spacy.load(SPACY_MODEL)
            logger.info(f"✅ Loaded spaCy model: {SPACY_MODEL}")
        except OSError:
            logger.warning(f"⚠️ spaCy model '{SPACY_MODEL}' not found. Run: python -m spacy download {SPACY_MODEL}")
            nlp = None

        # Initialize Presidio engines
        presidio_analyzer = AnalyzerEngine()
        presidio_anonymizer = AnonymizerEngine()
        logger.info("✅ Presidio engines initialized")

    except ImportError as e:
        logger.error(f"❌ Failed to import Presidio: {e}")
        logger.error("Install with: pip install presidio-analyzer presidio-anonymizer")
        presidio_analyzer = None
        presidio_anonymizer = None
else:
    logger.info("ℹ️ Presidio disabled (set PRESIDIO_ENABLED=true to enable)")
    logger.info("ℹ️ Running in OFFLINE mode - API will return mock responses")
