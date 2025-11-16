"""
Configuration for L3 M10.2: Monitoring Financial RAG Performance

This module manages environment configuration for monitoring infrastructure:
- Prometheus metrics export (optional)
- PagerDuty alerting (optional)
- AWS S3/Glacier audit storage (optional)
- Local monitoring (always available)
"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Monitoring service configuration (all optional for local development)
PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))

PAGERDUTY_ENABLED = os.getenv("PAGERDUTY_ENABLED", "false").lower() == "true"
PAGERDUTY_API_KEY = os.getenv("PAGERDUTY_API_KEY", "")
PAGERDUTY_INTEGRATION_KEY = os.getenv("PAGERDUTY_INTEGRATION_KEY", "")

AWS_S3_ENABLED = os.getenv("AWS_S3_ENABLED", "false").lower() == "true"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "financial-rag-audit-logs")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Monitoring configuration
CITATION_SAMPLE_RATE = float(os.getenv("CITATION_SAMPLE_RATE", "0.01"))  # 1% sampling
ALERT_ENABLED = os.getenv("ALERT_ENABLED", "false").lower() == "true"


def get_prometheus_client():
    """
    Initialize Prometheus metrics client (optional).

    Returns:
        Prometheus client if enabled, None otherwise
    """
    if not PROMETHEUS_ENABLED:
        logger.info("⚠️ Prometheus disabled - using local metrics only")
        return None

    try:
        from prometheus_client import start_http_server, Counter, Gauge, Histogram

        # Start Prometheus metrics server
        start_http_server(PROMETHEUS_PORT)

        logger.info(f"✓ Prometheus metrics server started on port {PROMETHEUS_PORT}")

        return {
            "Counter": Counter,
            "Gauge": Gauge,
            "Histogram": Histogram
        }

    except ImportError:
        logger.warning("⚠️ prometheus_client not installed - install with: pip install prometheus-client")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Prometheus client: {e}")
        return None


def get_pagerduty_client():
    """
    Initialize PagerDuty alert client (optional).

    Returns:
        PagerDuty client if enabled and configured, None otherwise
    """
    if not PAGERDUTY_ENABLED:
        logger.info("⚠️ PagerDuty disabled - alerts will be logged only")
        return None

    if not PAGERDUTY_API_KEY or not PAGERDUTY_INTEGRATION_KEY:
        logger.warning("⚠️ PagerDuty API keys not configured")
        return None

    try:
        import pypd

        pypd.api_key = PAGERDUTY_API_KEY

        logger.info("✓ PagerDuty client initialized")
        return pypd

    except ImportError:
        logger.warning("⚠️ pypd not installed - install with: pip install pypd")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize PagerDuty client: {e}")
        return None


def get_s3_client():
    """
    Initialize AWS S3 client for audit log storage (optional).

    Returns:
        Boto3 S3 client if enabled and configured, None otherwise
    """
    if not AWS_S3_ENABLED:
        logger.info("⚠️ AWS S3 disabled - audit logs stored locally only")
        return None

    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        logger.warning("⚠️ AWS credentials not configured")
        return None

    try:
        import boto3

        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

        logger.info(f"✓ AWS S3 client initialized (bucket: {AWS_S3_BUCKET})")
        return s3_client

    except ImportError:
        logger.warning("⚠️ boto3 not installed - install with: pip install boto3")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        return None


def get_monitor_config() -> dict:
    """
    Get complete monitoring configuration.

    Returns:
        Configuration dictionary for FinancialRAGMonitor
    """
    return {
        "citation_sample_rate": CITATION_SAMPLE_RATE,
        "prometheus_enabled": PROMETHEUS_ENABLED,
        "pagerduty_enabled": PAGERDUTY_ENABLED,
        "s3_enabled": AWS_S3_ENABLED,
        "alert_enabled": ALERT_ENABLED
    }


# Initialize clients on module import (only if enabled)
prometheus_client = get_prometheus_client()
pagerduty_client = get_pagerduty_client()
s3_client = get_s3_client()

# Log configuration status
logger.info("Configuration loaded:")
logger.info(f"  - Prometheus: {'enabled' if PROMETHEUS_ENABLED else 'disabled'}")
logger.info(f"  - PagerDuty: {'enabled' if PAGERDUTY_ENABLED else 'disabled'}")
logger.info(f"  - AWS S3: {'enabled' if AWS_S3_ENABLED else 'disabled'}")
logger.info(f"  - Citation sampling rate: {CITATION_SAMPLE_RATE * 100}%")
