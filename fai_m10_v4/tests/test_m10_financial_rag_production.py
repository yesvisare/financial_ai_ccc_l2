"""
Tests for L3 M10.4: Disaster Recovery & Business Continuity

Covers:
- ReplicationMonitor functionality
- DRVerifier health checks
- FailoverOrchestrator execution
- ComplianceReporter generation
- RTO/RPO validation
"""

import pytest
from datetime import datetime, timedelta
from src.l3_m10_financial_rag_production import (
    ReplicationMonitor,
    DRVerifier,
    FailoverOrchestrator,
    ComplianceReporter,
    ReplicationStatus,
    FailoverResult,
    verify_dr_readiness,
    execute_failover,
    generate_compliance_report
)


# Test Fixtures

@pytest.fixture
def mock_db_config():
    """Mock database configuration for testing."""
    return {
        "host": "test-db.example.com",
        "port": 5432,
        "database": "test_db",
        "user": "test_user",
        "password": "test_password"
    }


@pytest.fixture
def replication_monitor(mock_db_config):
    """Create ReplicationMonitor instance for testing."""
    return ReplicationMonitor(
        primary_config=mock_db_config,
        replica_config=mock_db_config
    )


@pytest.fixture
def dr_verifier(replication_monitor):
    """Create DRVerifier instance for testing."""
    return DRVerifier(replication_monitor)


@pytest.fixture
def failover_orchestrator(dr_verifier):
    """Create FailoverOrchestrator instance for testing."""
    return FailoverOrchestrator(dr_verifier)


@pytest.fixture
def compliance_reporter():
    """Create ComplianceReporter instance for testing."""
    return ComplianceReporter()


# ReplicationMonitor Tests

def test_replication_monitor_initialization(replication_monitor):
    """Test ReplicationMonitor initializes correctly."""
    assert replication_monitor is not None
    assert replication_monitor.primary_config is not None
    assert replication_monitor.replica_config is not None


def test_check_replication_lag(replication_monitor):
    """Test replication lag checking returns valid status."""
    status = replication_monitor.check_replication_lag()

    assert isinstance(status, ReplicationStatus)
    assert status.lag_seconds >= 0
    assert isinstance(status.is_connected, bool)
    assert isinstance(status.last_sync_time, datetime)
    assert 0 <= status.data_consistency_ratio <= 1.0
    assert isinstance(status.meets_rpo, bool)


def test_replication_lag_meets_rpo(replication_monitor):
    """Test that typical replication lag meets RPO (1 hour = 3600 seconds)."""
    status = replication_monitor.check_replication_lag()

    # Simulated lag should be small (< 10 seconds)
    assert status.lag_seconds < 3600, "Replication lag should meet RPO"
    assert status.meets_rpo is True


def test_data_consistency_check(replication_monitor):
    """Test data consistency ratio is within acceptable range."""
    consistency = replication_monitor._check_data_consistency()

    assert 0 <= consistency <= 1.0, "Consistency ratio must be between 0 and 1"
    assert consistency >= 0.99, "Consistency should be >= 99% for DR readiness"


def test_verify_dr_readiness_success(replication_monitor):
    """Test DR readiness verification when conditions are met."""
    is_ready, issues = replication_monitor.verify_dr_readiness()

    # With simulated good conditions, DR should be ready
    assert isinstance(is_ready, bool)
    assert isinstance(issues, list)

    if is_ready:
        assert len(issues) == 0, "Ready DR should have no issues"


# DRVerifier Tests

def test_dr_verifier_initialization(dr_verifier):
    """Test DRVerifier initializes correctly."""
    assert dr_verifier is not None
    assert dr_verifier.monitor is not None


def test_run_health_checks(dr_verifier):
    """Test comprehensive DR health checks."""
    health = dr_verifier.run_health_checks()

    assert "ready" in health
    assert "issues" in health
    assert "replication_lag_seconds" in health
    assert "data_consistency" in health
    assert "meets_rpo" in health
    assert "timestamp" in health

    assert isinstance(health["ready"], bool)
    assert isinstance(health["issues"], list)
    assert health["replication_lag_seconds"] >= 0
    assert 0 <= health["data_consistency"] <= 1.0


# FailoverOrchestrator Tests

def test_failover_orchestrator_initialization(failover_orchestrator):
    """Test FailoverOrchestrator initializes correctly."""
    assert failover_orchestrator is not None
    assert failover_orchestrator.verifier is not None


def test_execute_failover(failover_orchestrator):
    """Test failover execution returns valid result."""
    result = failover_orchestrator.execute_failover("Test failover")

    assert isinstance(result, FailoverResult)
    assert isinstance(result.success, bool)
    assert result.rto_minutes >= 0
    assert result.data_loss_minutes >= 0
    assert isinstance(result.timestamp, datetime)
    assert isinstance(result.errors, list)


def test_failover_rto_within_target(failover_orchestrator):
    """Test that failover RTO is within 15-minute target."""
    result = failover_orchestrator.execute_failover("RTO test")

    # Simulated failover should complete quickly
    assert result.rto_minutes < 15, "RTO should be within 15-minute target"


def test_failover_data_loss_within_rpo(failover_orchestrator):
    """Test that failover data loss is within RPO (60 minutes)."""
    result = failover_orchestrator.execute_failover("RPO test")

    # Data loss should be minimal with good replication
    assert result.data_loss_minutes < 60, "Data loss should be within 1-hour RPO"


# ComplianceReporter Tests

def test_compliance_reporter_initialization(compliance_reporter):
    """Test ComplianceReporter initializes correctly."""
    assert compliance_reporter is not None


def test_generate_quarterly_report(compliance_reporter):
    """Test quarterly compliance report generation."""
    test_date = datetime(2024, 12, 15, 14, 0, 0)

    mock_failover = FailoverResult(
        success=True,
        rto_minutes=8.5,
        data_loss_minutes=5.0,
        timestamp=test_date,
        errors=[]
    )

    mock_replication = ReplicationStatus(
        lag_seconds=5.2,
        is_connected=True,
        last_sync_time=test_date,
        data_consistency_ratio=0.998,
        meets_rpo=True
    )

    report = compliance_reporter.generate_quarterly_report(
        test_date,
        mock_failover,
        mock_replication
    )

    assert "report_type" in report
    assert "test_date" in report
    assert "quarter" in report
    assert "rto_analysis" in report
    assert "rpo_analysis" in report
    assert "data_consistency" in report
    assert "overall_result" in report
    assert "compliance_statement" in report


def test_compliance_report_rto_evaluation(compliance_reporter):
    """Test RTO evaluation in compliance report."""
    test_date = datetime(2024, 12, 15, 14, 0, 0)

    # Test passing RTO (< 15 minutes)
    passing_failover = FailoverResult(
        success=True,
        rto_minutes=8.5,
        data_loss_minutes=5.0,
        timestamp=test_date,
        errors=[]
    )

    mock_replication = ReplicationStatus(
        lag_seconds=5.2,
        is_connected=True,
        last_sync_time=test_date,
        data_consistency_ratio=0.998,
        meets_rpo=True
    )

    report = compliance_reporter.generate_quarterly_report(
        test_date,
        passing_failover,
        mock_replication
    )

    assert report["rto_analysis"]["pass"] is True
    assert report["rto_analysis"]["measured_minutes"] < 15


def test_compliance_report_rpo_evaluation(compliance_reporter):
    """Test RPO evaluation in compliance report."""
    test_date = datetime(2024, 12, 15, 14, 0, 0)

    # Test passing RPO (< 60 minutes)
    mock_failover = FailoverResult(
        success=True,
        rto_minutes=8.5,
        data_loss_minutes=5.0,
        timestamp=test_date,
        errors=[]
    )

    passing_replication = ReplicationStatus(
        lag_seconds=5.2,
        is_connected=True,
        last_sync_time=test_date,
        data_consistency_ratio=0.998,
        meets_rpo=True
    )

    report = compliance_reporter.generate_quarterly_report(
        test_date,
        mock_failover,
        passing_replication
    )

    assert report["rpo_analysis"]["pass"] is True
    assert report["rpo_analysis"]["measured_minutes"] < 60


def test_compliance_report_overall_pass(compliance_reporter):
    """Test overall compliance report pass status."""
    test_date = datetime(2024, 12, 15, 14, 0, 0)

    passing_failover = FailoverResult(
        success=True,
        rto_minutes=8.5,
        data_loss_minutes=5.0,
        timestamp=test_date,
        errors=[]
    )

    passing_replication = ReplicationStatus(
        lag_seconds=5.2,
        is_connected=True,
        last_sync_time=test_date,
        data_consistency_ratio=0.998,
        meets_rpo=True
    )

    report = compliance_reporter.generate_quarterly_report(
        test_date,
        passing_failover,
        passing_replication
    )

    assert report["overall_result"]["pass"] is True
    assert "TEST PASSED" in report["overall_result"]["status"]


# Convenience Function Tests

def test_verify_dr_readiness_convenience_function(mock_db_config):
    """Test verify_dr_readiness convenience function."""
    is_ready, issues = verify_dr_readiness(mock_db_config, mock_db_config)

    assert isinstance(is_ready, bool)
    assert isinstance(issues, list)


def test_execute_failover_convenience_function(mock_db_config):
    """Test execute_failover convenience function."""
    result = execute_failover(mock_db_config, mock_db_config, "Test failover")

    assert isinstance(result, FailoverResult)
    assert isinstance(result.success, bool)


def test_generate_compliance_report_convenience_function():
    """Test generate_compliance_report convenience function."""
    test_date = datetime(2024, 12, 15, 14, 0, 0)

    mock_failover = FailoverResult(
        success=True,
        rto_minutes=8.5,
        data_loss_minutes=5.0,
        timestamp=test_date,
        errors=[]
    )

    mock_replication = ReplicationStatus(
        lag_seconds=5.2,
        is_connected=True,
        last_sync_time=test_date,
        data_consistency_ratio=0.998,
        meets_rpo=True
    )

    report = generate_compliance_report(test_date, mock_failover, mock_replication)

    assert "overall_result" in report
    assert isinstance(report, dict)


# Edge Cases and Error Handling

def test_replication_status_dataclass():
    """Test ReplicationStatus dataclass creation."""
    status = ReplicationStatus(
        lag_seconds=5.2,
        is_connected=True,
        last_sync_time=datetime.utcnow(),
        data_consistency_ratio=0.998,
        meets_rpo=True
    )

    assert status.lag_seconds == 5.2
    assert status.is_connected is True
    assert status.data_consistency_ratio == 0.998
    assert status.meets_rpo is True


def test_failover_result_dataclass():
    """Test FailoverResult dataclass creation."""
    timestamp = datetime.utcnow()
    result = FailoverResult(
        success=True,
        rto_minutes=8.5,
        data_loss_minutes=5.0,
        timestamp=timestamp,
        errors=[]
    )

    assert result.success is True
    assert result.rto_minutes == 8.5
    assert result.data_loss_minutes == 5.0
    assert result.timestamp == timestamp
    assert result.errors == []


def test_failover_with_errors():
    """Test failover result with errors."""
    timestamp = datetime.utcnow()
    errors = ["DR region not responding", "Health check failed"]

    result = FailoverResult(
        success=False,
        rto_minutes=0,
        data_loss_minutes=0,
        timestamp=timestamp,
        errors=errors
    )

    assert result.success is False
    assert len(result.errors) == 2
    assert "DR region not responding" in result.errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
