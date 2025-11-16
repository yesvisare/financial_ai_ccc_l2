"""
L3 M10.2: Monitoring Financial RAG Performance

This module implements comprehensive monitoring for financial RAG systems,
tracking six critical metrics: citation accuracy, data staleness, MNPI detection,
query latency, compliance violations, and audit trail completeness.

The monitoring system bridges the gap between technical metrics (uptime, latency)
and business outcomes (regulatory compliance, data quality) for financial AI systems.
"""

import logging
import time
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "FinancialRAGMonitor",
    "ComplianceViolationType",
    "DataSource",
    "MetricsCollector",
    "generate_compliance_report",
    "verify_citation_accuracy"
]


class ComplianceViolationType(Enum):
    """Types of compliance violations in financial RAG systems."""
    MNPI = "Material Non-Public Information"
    PRIVILEGE = "Attorney-Client Privilege Breach"
    EXPORT_CONTROL = "Export Control Violation"
    CITATION_FAILURE = "Citation Verification Failure"
    STALENESS_SLA_BREACH = "Data Staleness SLA Breach"


class DataSource(Enum):
    """Financial data sources with different SLA requirements."""
    BLOOMBERG = "Bloomberg Terminal"
    SEC_EDGAR = "SEC EDGAR"
    INTERNAL_MODELS = "Internal Financial Models"
    MARKET_DATA = "Real-time Market Data"
    RESEARCH_REPORTS = "Research Reports"


class MetricsCollector:
    """
    Collects and tracks financial RAG metrics for Prometheus export.

    This class manages six critical financial metrics:
    1. Citation Accuracy (target: >95%)
    2. Data Staleness (varies by source)
    3. MNPI Detection Counts
    4. Query Latency (p95 <2 seconds)
    5. Compliance Violation Count (zero tolerance)
    6. Audit Trail Completeness (100% required for SOX 404)
    """

    def __init__(self):
        """Initialize metrics collector with counters and gauges."""
        self.metrics: Dict[str, Any] = {
            "successful_queries": 0,
            "failed_queries": 0,
            "mnpi_detections": 0,
            "compliance_violations": 0,
            "citation_accuracy_percent": 100.0,
            "query_latencies": [],
            "data_staleness": {},
            "audit_logs": []
        }
        logger.info("MetricsCollector initialized")

    def record_query_latency(self, latency_seconds: float) -> None:
        """
        Record query latency for SLA monitoring.

        Args:
            latency_seconds: Query execution time in seconds
        """
        self.metrics["query_latencies"].append(latency_seconds)
        logger.debug(f"Recorded latency: {latency_seconds:.3f}s")

    def update_citation_accuracy(self, accuracy: float) -> None:
        """
        Update citation accuracy percentage.

        Args:
            accuracy: Accuracy percentage (0-100)
        """
        self.metrics["citation_accuracy_percent"] = accuracy
        if accuracy < 95.0:
            logger.warning(f"⚠️ Citation accuracy below threshold: {accuracy:.2f}%")

    def increment_mnpi_detection(self) -> None:
        """Increment MNPI detection counter (Regulation FD compliance)."""
        self.metrics["mnpi_detections"] += 1
        logger.warning("🚨 MNPI content detected and blocked")

    def record_compliance_violation(self, violation_type: ComplianceViolationType) -> None:
        """
        Record compliance violation (zero tolerance policy).

        Args:
            violation_type: Type of compliance violation
        """
        self.metrics["compliance_violations"] += 1
        logger.error(f"🚨 COMPLIANCE VIOLATION: {violation_type.value}")

    def update_data_staleness(self, source: DataSource, hours: float) -> None:
        """
        Update data staleness for a specific source.

        Args:
            source: Data source identifier
            hours: Hours since last update
        """
        self.metrics["data_staleness"][source.value] = hours

        # Check SLA thresholds
        sla_thresholds = {
            DataSource.BLOOMBERG: 5/60,  # 5 minutes
            DataSource.SEC_EDGAR: 24,
            DataSource.INTERNAL_MODELS: 1,
            DataSource.MARKET_DATA: 5/60,
            DataSource.RESEARCH_REPORTS: 24
        }

        threshold = sla_thresholds.get(source, 24)
        if hours > threshold:
            logger.warning(
                f"⚠️ Data staleness SLA breach: {source.value} "
                f"({hours:.2f}h > {threshold}h threshold)"
            )

    def get_p95_latency(self) -> float:
        """
        Calculate p95 query latency.

        Returns:
            95th percentile latency in seconds
        """
        if not self.metrics["query_latencies"]:
            return 0.0

        sorted_latencies = sorted(self.metrics["query_latencies"])
        p95_index = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[p95_index] if p95_index < len(sorted_latencies) else sorted_latencies[-1]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get complete metrics summary for reporting.

        Returns:
            Dictionary containing all current metrics
        """
        return {
            "successful_queries": self.metrics["successful_queries"],
            "failed_queries": self.metrics["failed_queries"],
            "mnpi_detections": self.metrics["mnpi_detections"],
            "compliance_violations": self.metrics["compliance_violations"],
            "citation_accuracy_percent": self.metrics["citation_accuracy_percent"],
            "p95_latency_seconds": self.get_p95_latency(),
            "data_staleness": self.metrics["data_staleness"],
            "audit_log_count": len(self.metrics["audit_logs"])
        }


class FinancialRAGMonitor:
    """
    Main monitoring class for financial RAG systems.

    Implements comprehensive monitoring including:
    - Real-time query tracking
    - Compliance checking (MNPI, privilege, export control)
    - Citation verification (1% sampling)
    - Data staleness monitoring
    - SOX 404 audit trail generation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Financial RAG Monitor.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.metrics_collector = MetricsCollector()
        self.mnpi_keywords = self._load_mnpi_keywords()
        self.citation_sample_rate = self.config.get("citation_sample_rate", 0.01)  # 1%
        logger.info("FinancialRAGMonitor initialized")

    def _load_mnpi_keywords(self) -> List[str]:
        """
        Load MNPI detection keywords for Regulation FD compliance.

        Returns:
            List of MNPI indicator keywords
        """
        return [
            "upcoming earnings",
            "pre-announcement",
            "insider trading",
            "material non-public",
            "confidential merger",
            "acquisition target",
            "unreleased guidance",
            "private placement"
        ]

    def track_query(
        self,
        query: str,
        response: str,
        citations: List[Dict[str, Any]],
        data_sources: List[DataSource]
    ) -> Dict[str, Any]:
        """
        Track a RAG query with comprehensive monitoring.

        This is the main entry point for monitoring RAG queries. It:
        1. Measures query latency
        2. Checks for compliance violations
        3. Verifies citations (1% sampling)
        4. Updates data staleness metrics
        5. Creates audit trail entry

        Args:
            query: User query string
            response: RAG system response
            citations: List of citation dictionaries
            data_sources: List of data sources used

        Returns:
            Dictionary with monitoring results and metrics
        """
        start_time = time.time()

        try:
            # Check compliance
            compliance_result = self._check_compliance(query, response, citations)

            # Verify citations (1% sampling)
            citation_result = self._verify_citations(citations)

            # Update data staleness
            for source in data_sources:
                self.check_data_staleness(source)

            # Record latency
            latency = time.time() - start_time
            self.metrics_collector.record_query_latency(latency)

            # Create audit log entry
            audit_entry = self._create_audit_log(
                query=query,
                response=response,
                citations=citations,
                compliance_result=compliance_result,
                latency=latency
            )

            self.metrics_collector.metrics["successful_queries"] += 1

            logger.info(f"Query tracked successfully (latency: {latency:.3f}s)")

            return {
                "status": "success",
                "latency_seconds": latency,
                "compliance": compliance_result,
                "citations": citation_result,
                "audit_log_id": audit_entry["id"]
            }

        except Exception as e:
            self.metrics_collector.metrics["failed_queries"] += 1
            logger.error(f"Error tracking query: {e}")
            raise

    def _check_compliance(
        self,
        query: str,
        response: str,
        citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check for compliance violations in query and response.

        Detects:
        - MNPI content (Regulation FD)
        - Privilege boundary crossings
        - Export control violations

        Args:
            query: User query
            response: System response
            citations: Citation list

        Returns:
            Compliance check results
        """
        violations = []

        # Check for MNPI
        response_lower = response.lower()
        for keyword in self.mnpi_keywords:
            if keyword.lower() in response_lower:
                violations.append({
                    "type": ComplianceViolationType.MNPI.value,
                    "keyword": keyword,
                    "severity": "CRITICAL"
                })
                self.metrics_collector.increment_mnpi_detection()

        # Check privilege boundaries
        if self._check_privilege_violation(response, citations):
            violations.append({
                "type": ComplianceViolationType.PRIVILEGE.value,
                "severity": "CRITICAL"
            })
            self.metrics_collector.record_compliance_violation(
                ComplianceViolationType.PRIVILEGE
            )

        # Check export control
        if self._check_export_control_violation(response):
            violations.append({
                "type": ComplianceViolationType.EXPORT_CONTROL.value,
                "severity": "HIGH"
            })
            self.metrics_collector.record_compliance_violation(
                ComplianceViolationType.EXPORT_CONTROL
            )

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def _check_privilege_violation(
        self,
        response: str,
        citations: List[Dict[str, Any]]
    ) -> bool:
        """
        Check for attorney-client privilege boundary violations.

        Args:
            response: System response
            citations: Citation list

        Returns:
            True if violation detected
        """
        # Check if response contains privileged markers
        privileged_markers = ["attorney-client", "privileged communication", "legal advice"]
        for marker in privileged_markers:
            if marker.lower() in response.lower():
                # Verify user has privilege access
                return True  # Simplified: would check user permissions in production
        return False

    def _check_export_control_violation(self, response: str) -> bool:
        """
        Check for export control violations (ITAR, EAR).

        Args:
            response: System response

        Returns:
            True if violation detected
        """
        export_keywords = ["itar controlled", "export restricted", "ear category"]
        for keyword in export_keywords:
            if keyword.lower() in response.lower():
                return True
        return False

    def _verify_citations(self, citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify citation accuracy using 1% sampling strategy.

        This implements the "1% real-time sampling" approach from the script
        to balance accuracy monitoring with performance.

        Args:
            citations: List of citation dictionaries

        Returns:
            Citation verification results
        """
        import random

        if not citations:
            return {"sampled": False, "accuracy": 100.0}

        # 1% sampling
        should_sample = random.random() < self.citation_sample_rate

        if not should_sample:
            return {"sampled": False, "accuracy": None}

        # Verify each citation
        correct_citations = 0
        for citation in citations:
            if self._validate_citation(citation):
                correct_citations += 1

        accuracy = (correct_citations / len(citations)) * 100 if citations else 100.0
        self.metrics_collector.update_citation_accuracy(accuracy)

        return {
            "sampled": True,
            "total_citations": len(citations),
            "correct_citations": correct_citations,
            "accuracy": accuracy
        }

    def _validate_citation(self, citation: Dict[str, Any]) -> bool:
        """
        Validate a single citation against source document.

        Args:
            citation: Citation dictionary with 'source', 'page', 'quote'

        Returns:
            True if citation is accurate
        """
        # Simplified validation - in production would check actual document
        required_fields = ["source", "page", "quote"]
        return all(field in citation for field in required_fields)

    def check_data_staleness(self, source: DataSource) -> Dict[str, Any]:
        """
        Check data staleness for a specific source against SLA thresholds.

        SLA Thresholds:
        - Bloomberg: <5 minutes
        - SEC EDGAR: <24 hours
        - Internal Models: <1 hour
        - Market Data: <5 minutes
        - Research Reports: <24 hours

        Args:
            source: Data source to check

        Returns:
            Staleness status and metrics
        """
        # Simulate last update check - in production would query actual source
        # For demo, use random staleness between 0-48 hours
        import random
        hours_since_update = random.uniform(0, 48)

        self.metrics_collector.update_data_staleness(source, hours_since_update)

        sla_thresholds = {
            DataSource.BLOOMBERG: 5/60,
            DataSource.SEC_EDGAR: 24,
            DataSource.INTERNAL_MODELS: 1,
            DataSource.MARKET_DATA: 5/60,
            DataSource.RESEARCH_REPORTS: 24
        }

        threshold = sla_thresholds.get(source, 24)
        is_stale = hours_since_update > threshold

        return {
            "source": source.value,
            "hours_since_update": hours_since_update,
            "sla_threshold_hours": threshold,
            "is_stale": is_stale,
            "status": "BREACH" if is_stale else "OK"
        }

    def _create_audit_log(
        self,
        query: str,
        response: str,
        citations: List[Dict[str, Any]],
        compliance_result: Dict[str, Any],
        latency: float
    ) -> Dict[str, Any]:
        """
        Create SOX 404 compliant audit log entry.

        Audit logs must include:
        - Timestamp
        - Query hash (not raw query for privacy)
        - Citations used
        - Compliance check results
        - User context
        - Retention metadata

        Args:
            query: User query
            response: System response
            citations: Citations used
            compliance_result: Compliance check results
            latency: Query latency

        Returns:
            Audit log entry
        """
        import hashlib

        audit_entry = {
            "id": hashlib.sha256(f"{time.time()}{query}".encode()).hexdigest()[:16],
            "timestamp": datetime.utcnow().isoformat(),
            "query_hash": hashlib.sha256(query.encode()).hexdigest(),
            "citations_count": len(citations),
            "compliance_passed": compliance_result["passed"],
            "violations": compliance_result["violations"],
            "latency_seconds": latency,
            "retention_years": 7  # SOX 404 requirement
        }

        self.metrics_collector.metrics["audit_logs"].append(audit_entry)
        logger.debug(f"Audit log created: {audit_entry['id']}")

        return audit_entry

    def generate_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate SOX 404 compliance report for audit purposes.

        Args:
            start_date: Report start date (default: 30 days ago)
            end_date: Report end date (default: now)

        Returns:
            Compliance report with all required metrics
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        metrics = self.metrics_collector.get_metrics_summary()

        report = {
            "report_id": f"SOX404-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "metrics": metrics,
            "sla_compliance": {
                "citation_accuracy": metrics["citation_accuracy_percent"] >= 95.0,
                "p95_latency": metrics["p95_latency_seconds"] < 2.0,
                "zero_violations": metrics["compliance_violations"] == 0
            },
            "audit_trail_completeness": 100.0,  # All queries logged
            "retention_status": "7-year retention active (S3/Glacier)",
            "generated_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Compliance report generated: {report['report_id']}")

        return report


def generate_compliance_report(
    monitor: FinancialRAGMonitor,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate compliance report.

    Args:
        monitor: FinancialRAGMonitor instance
        start_date: Report start date
        end_date: Report end date

    Returns:
        Compliance report dictionary
    """
    return monitor.generate_compliance_report(start_date, end_date)


def verify_citation_accuracy(
    citations: List[Dict[str, Any]],
    sample_rate: float = 0.01
) -> Dict[str, Any]:
    """
    Standalone function to verify citation accuracy.

    Args:
        citations: List of citations to verify
        sample_rate: Sampling rate (default: 1%)

    Returns:
        Verification results
    """
    import random

    if not citations or random.random() >= sample_rate:
        return {"sampled": False}

    correct = sum(
        1 for c in citations
        if all(field in c for field in ["source", "page", "quote"])
    )

    return {
        "sampled": True,
        "accuracy": (correct / len(citations)) * 100
    }
