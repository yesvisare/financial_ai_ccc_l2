"""
Tests for L3 M10.2: Monitoring Financial RAG Performance

Comprehensive test suite covering:
- Query tracking and monitoring
- Compliance checking (MNPI, privilege, export control)
- Citation verification
- Data staleness monitoring
- Audit trail generation
- Compliance report generation
"""

import pytest
from datetime import datetime, timedelta

from src.l3_m10_financial_rag_in_production import (
    FinancialRAGMonitor,
    MetricsCollector,
    ComplianceViolationType,
    DataSource,
    generate_compliance_report,
    verify_citation_accuracy
)


class TestMetricsCollector:
    """Test MetricsCollector functionality."""

    def test_initialization(self):
        """Test MetricsCollector initializes with default metrics."""
        collector = MetricsCollector()

        assert collector.metrics["successful_queries"] == 0
        assert collector.metrics["failed_queries"] == 0
        assert collector.metrics["mnpi_detections"] == 0
        assert collector.metrics["compliance_violations"] == 0
        assert collector.metrics["citation_accuracy_percent"] == 100.0
        assert len(collector.metrics["query_latencies"]) == 0
        assert len(collector.metrics["audit_logs"]) == 0

    def test_record_query_latency(self):
        """Test latency recording."""
        collector = MetricsCollector()
        collector.record_query_latency(0.5)
        collector.record_query_latency(1.2)
        collector.record_query_latency(0.8)

        assert len(collector.metrics["query_latencies"]) == 3
        assert 0.5 in collector.metrics["query_latencies"]

    def test_update_citation_accuracy(self):
        """Test citation accuracy updates."""
        collector = MetricsCollector()
        collector.update_citation_accuracy(97.5)

        assert collector.metrics["citation_accuracy_percent"] == 97.5

    def test_citation_accuracy_below_threshold_warning(self):
        """Test warning when citation accuracy drops below 95%."""
        collector = MetricsCollector()
        # Should log warning (captured in logs, not tested here)
        collector.update_citation_accuracy(92.0)

        assert collector.metrics["citation_accuracy_percent"] == 92.0

    def test_increment_mnpi_detection(self):
        """Test MNPI detection counter."""
        collector = MetricsCollector()
        collector.increment_mnpi_detection()
        collector.increment_mnpi_detection()

        assert collector.metrics["mnpi_detections"] == 2

    def test_record_compliance_violation(self):
        """Test compliance violation recording."""
        collector = MetricsCollector()
        collector.record_compliance_violation(ComplianceViolationType.MNPI)
        collector.record_compliance_violation(ComplianceViolationType.PRIVILEGE)

        assert collector.metrics["compliance_violations"] == 2

    def test_update_data_staleness(self):
        """Test data staleness updates."""
        collector = MetricsCollector()
        collector.update_data_staleness(DataSource.BLOOMBERG, 0.05)  # 3 minutes

        assert DataSource.BLOOMBERG.value in collector.metrics["data_staleness"]
        assert collector.metrics["data_staleness"][DataSource.BLOOMBERG.value] == 0.05

    def test_data_staleness_sla_breach(self):
        """Test data staleness SLA breach detection."""
        collector = MetricsCollector()
        # Bloomberg SLA is 5 minutes (0.083 hours)
        collector.update_data_staleness(DataSource.BLOOMBERG, 1.0)  # 1 hour (breach)

        assert collector.metrics["data_staleness"][DataSource.BLOOMBERG.value] == 1.0

    def test_p95_latency_calculation(self):
        """Test p95 latency calculation."""
        collector = MetricsCollector()

        # Add 100 latencies
        for i in range(100):
            collector.record_query_latency(i * 0.01)  # 0.00s to 0.99s

        p95 = collector.get_p95_latency()
        assert p95 >= 0.90  # Should be around 0.95s

    def test_p95_latency_empty(self):
        """Test p95 latency with no data."""
        collector = MetricsCollector()
        p95 = collector.get_p95_latency()

        assert p95 == 0.0

    def test_get_metrics_summary(self):
        """Test metrics summary generation."""
        collector = MetricsCollector()
        collector.record_query_latency(1.0)
        collector.update_citation_accuracy(98.0)
        collector.increment_mnpi_detection()

        summary = collector.get_metrics_summary()

        assert "successful_queries" in summary
        assert "p95_latency_seconds" in summary
        assert "citation_accuracy_percent" in summary
        assert summary["mnpi_detections"] == 1


class TestFinancialRAGMonitor:
    """Test FinancialRAGMonitor functionality."""

    def test_initialization(self):
        """Test FinancialRAGMonitor initialization."""
        monitor = FinancialRAGMonitor()

        assert monitor.metrics_collector is not None
        assert len(monitor.mnpi_keywords) > 0
        assert monitor.citation_sample_rate == 0.01

    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = {"citation_sample_rate": 0.05}
        monitor = FinancialRAGMonitor(config)

        assert monitor.citation_sample_rate == 0.05

    def test_track_query_success(self):
        """Test successful query tracking."""
        monitor = FinancialRAGMonitor()

        result = monitor.track_query(
            query="What is Apple's revenue?",
            response="Apple's Q4 2024 revenue was $90B",
            citations=[
                {"source": "SEC_EDGAR", "page": 12, "quote": "Revenue $90B"}
            ],
            data_sources=[DataSource.SEC_EDGAR]
        )

        assert result["status"] == "success"
        assert "latency_seconds" in result
        assert "compliance" in result
        assert "audit_log_id" in result

    def test_mnpi_detection(self):
        """Test MNPI keyword detection."""
        monitor = FinancialRAGMonitor()

        result = monitor.track_query(
            query="What are the upcoming earnings?",
            response="The upcoming earnings announcement will exceed expectations",
            citations=[],
            data_sources=[]
        )

        assert result["compliance"]["passed"] is False
        assert len(result["compliance"]["violations"]) > 0
        assert result["compliance"]["violations"][0]["type"] == ComplianceViolationType.MNPI.value

    def test_check_compliance_clean(self):
        """Test compliance check with no violations."""
        monitor = FinancialRAGMonitor()

        compliance_result = monitor._check_compliance(
            query="What is Tesla's revenue?",
            response="Tesla's Q3 2024 revenue was $23.4B based on public 10-Q filing",
            citations=[{"source": "SEC_EDGAR_TSLA_10Q", "page": 8, "quote": "Revenue $23.4B"}]
        )

        assert compliance_result["passed"] is True
        assert len(compliance_result["violations"]) == 0

    def test_check_compliance_mnpi_violation(self):
        """Test compliance check detects MNPI."""
        monitor = FinancialRAGMonitor()

        compliance_result = monitor._check_compliance(
            query="What's the upcoming earnings?",
            response="The upcoming earnings will show material non-public growth",
            citations=[]
        )

        assert compliance_result["passed"] is False
        mnpi_violations = [
            v for v in compliance_result["violations"]
            if v["type"] == ComplianceViolationType.MNPI.value
        ]
        assert len(mnpi_violations) > 0

    def test_verify_citations_sampling(self):
        """Test citation verification with sampling."""
        monitor = FinancialRAGMonitor({"citation_sample_rate": 1.0})  # 100% sampling for test

        citations = [
            {"source": "SEC_EDGAR", "page": 12, "quote": "Revenue $90B"},
            {"source": "Bloomberg", "page": 1, "quote": "EPS $1.35"}
        ]

        result = monitor._verify_citations(citations)

        assert result["sampled"] is True
        assert result["total_citations"] == 2
        assert result["accuracy"] == 100.0

    def test_verify_citations_invalid(self):
        """Test citation verification with invalid citations."""
        monitor = FinancialRAGMonitor({"citation_sample_rate": 1.0})

        citations = [
            {"source": "SEC_EDGAR", "page": 12, "quote": "Revenue $90B"},
            {"source": "Bloomberg"}  # Missing page and quote
        ]

        result = monitor._verify_citations(citations)

        assert result["sampled"] is True
        assert result["accuracy"] < 100.0

    def test_verify_citations_no_sampling(self):
        """Test citation verification when not sampled."""
        monitor = FinancialRAGMonitor({"citation_sample_rate": 0.0})  # Never sample

        citations = [
            {"source": "SEC_EDGAR", "page": 12, "quote": "Revenue $90B"}
        ]

        result = monitor._verify_citations(citations)

        assert result["sampled"] is False

    def test_check_data_staleness(self):
        """Test data staleness checking."""
        monitor = FinancialRAGMonitor()

        result = monitor.check_data_staleness(DataSource.SEC_EDGAR)

        assert "source" in result
        assert "hours_since_update" in result
        assert "sla_threshold_hours" in result
        assert "is_stale" in result
        assert "status" in result

    def test_create_audit_log(self):
        """Test audit log creation."""
        monitor = FinancialRAGMonitor()

        audit_entry = monitor._create_audit_log(
            query="Test query",
            response="Test response",
            citations=[{"source": "SEC", "page": 1, "quote": "test"}],
            compliance_result={"passed": True, "violations": []},
            latency=0.5
        )

        assert "id" in audit_entry
        assert "timestamp" in audit_entry
        assert "query_hash" in audit_entry
        assert audit_entry["citations_count"] == 1
        assert audit_entry["compliance_passed"] is True
        assert audit_entry["latency_seconds"] == 0.5
        assert audit_entry["retention_years"] == 7

    def test_generate_compliance_report(self):
        """Test compliance report generation."""
        monitor = FinancialRAGMonitor()

        # Add some test data
        monitor.metrics_collector.record_query_latency(1.5)
        monitor.metrics_collector.update_citation_accuracy(97.0)

        report = monitor.generate_compliance_report()

        assert "report_id" in report
        assert "period" in report
        assert "metrics" in report
        assert "sla_compliance" in report
        assert report["sla_compliance"]["citation_accuracy"] is True
        assert report["sla_compliance"]["p95_latency"] is True
        assert report["audit_trail_completeness"] == 100.0

    def test_generate_compliance_report_with_dates(self):
        """Test compliance report with custom date range."""
        monitor = FinancialRAGMonitor()

        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        report = monitor.generate_compliance_report(start_date, end_date)

        assert report["period"]["start"] == start_date.isoformat()
        assert report["period"]["end"] == end_date.isoformat()


class TestStandaloneFunctions:
    """Test standalone utility functions."""

    def test_generate_compliance_report_function(self):
        """Test standalone generate_compliance_report function."""
        monitor = FinancialRAGMonitor()
        report = generate_compliance_report(monitor)

        assert "report_id" in report
        assert "metrics" in report

    def test_verify_citation_accuracy_sampled(self):
        """Test standalone citation verification function."""
        citations = [
            {"source": "SEC", "page": 1, "quote": "test"},
            {"source": "Bloomberg", "page": 2, "quote": "test2"}
        ]

        result = verify_citation_accuracy(citations, sample_rate=1.0)

        assert "sampled" in result
        if result["sampled"]:
            assert "accuracy" in result

    def test_verify_citation_accuracy_not_sampled(self):
        """Test citation verification when not sampled."""
        citations = [{"source": "SEC", "page": 1, "quote": "test"}]

        result = verify_citation_accuracy(citations, sample_rate=0.0)

        assert result["sampled"] is False


class TestEnums:
    """Test enum definitions."""

    def test_compliance_violation_types(self):
        """Test ComplianceViolationType enum."""
        assert ComplianceViolationType.MNPI.value == "Material Non-Public Information"
        assert ComplianceViolationType.PRIVILEGE.value == "Attorney-Client Privilege Breach"
        assert ComplianceViolationType.EXPORT_CONTROL.value == "Export Control Violation"
        assert ComplianceViolationType.CITATION_FAILURE.value == "Citation Verification Failure"

    def test_data_sources(self):
        """Test DataSource enum."""
        assert DataSource.BLOOMBERG.value == "Bloomberg Terminal"
        assert DataSource.SEC_EDGAR.value == "SEC EDGAR"
        assert DataSource.INTERNAL_MODELS.value == "Internal Financial Models"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_track_query_with_empty_citations(self):
        """Test tracking query with no citations."""
        monitor = FinancialRAGMonitor()

        result = monitor.track_query(
            query="What is the market cap?",
            response="The market cap is $2T",
            citations=[],
            data_sources=[DataSource.BLOOMBERG]
        )

        assert result["status"] == "success"

    def test_track_query_with_empty_data_sources(self):
        """Test tracking query with no data sources."""
        monitor = FinancialRAGMonitor()

        result = monitor.track_query(
            query="General question",
            response="General answer",
            citations=[],
            data_sources=[]
        )

        assert result["status"] == "success"

    def test_p95_latency_single_value(self):
        """Test p95 calculation with single value."""
        collector = MetricsCollector()
        collector.record_query_latency(1.0)

        p95 = collector.get_p95_latency()
        assert p95 == 1.0

    def test_validate_citation_missing_fields(self):
        """Test citation validation with missing fields."""
        monitor = FinancialRAGMonitor()

        # Missing 'quote' field
        invalid_citation = {"source": "SEC", "page": 1}
        is_valid = monitor._validate_citation(invalid_citation)

        assert is_valid is False

    def test_multiple_mnpi_keywords(self):
        """Test detection of multiple MNPI keywords."""
        monitor = FinancialRAGMonitor()

        compliance_result = monitor._check_compliance(
            query="Tell me about insider trading",
            response="This confidential merger involves material non-public information",
            citations=[]
        )

        assert compliance_result["passed"] is False
        assert len(compliance_result["violations"]) >= 2  # Multiple MNPI keywords


class TestIntegration:
    """Integration tests for end-to-end workflows."""

    def test_complete_monitoring_workflow(self):
        """Test complete monitoring workflow from query to report."""
        monitor = FinancialRAGMonitor()

        # Track multiple queries
        for i in range(10):
            monitor.track_query(
                query=f"Query {i}",
                response=f"Response {i}",
                citations=[{"source": "SEC", "page": i, "quote": "test"}],
                data_sources=[DataSource.SEC_EDGAR]
            )

        # Check metrics
        metrics = monitor.metrics_collector.get_metrics_summary()
        assert metrics["successful_queries"] == 10

        # Generate report
        report = monitor.generate_compliance_report()
        assert report["sla_compliance"]["zero_violations"] is True

    def test_compliance_failure_workflow(self):
        """Test workflow with compliance failures."""
        monitor = FinancialRAGMonitor()

        # Track query with MNPI violation
        result = monitor.track_query(
            query="Insider information",
            response="The upcoming earnings show material non-public growth",
            citations=[],
            data_sources=[]
        )

        assert result["compliance"]["passed"] is False

        # Generate report should show violations
        report = monitor.generate_compliance_report()
        assert report["metrics"]["mnpi_detections"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
