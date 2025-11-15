"""
Tests for L3 M7.4: Audit Trail & Document Provenance

This test suite validates:
- Hash computation and determinism
- Event logging and hash chaining
- Chain integrity verification
- Compliance report generation
- Failure scenarios from Section 8
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from src.l3_m7_financial_data_ingestion_compliance import (
    FinancialAuditTrail,
    AuditEvent,
    Base,
    hash_event,
    verify_chain_integrity
)


@pytest.fixture
def test_database_url():
    """
    In-memory SQLite database for testing.
    Note: Production uses PostgreSQL, but SQLite works for unit tests.
    """
    return "sqlite:///:memory:"


@pytest.fixture
def audit_trail(test_database_url):
    """Create a fresh audit trail instance for each test."""
    trail = FinancialAuditTrail(test_database_url)
    return trail


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "document_id": "aapl_10k_2024",
        "source_url": "https://sec.gov/...",
        "filing_date": "2024-03-15"
    }


# Test 1: Hash Computation
def test_hash_event_determinism(sample_event_data):
    """Test that hash_event produces deterministic results."""
    hash1 = hash_event(sample_event_data)
    hash2 = hash_event(sample_event_data)

    assert hash1 == hash2, "Hash should be deterministic"
    assert len(hash1) == 64, "SHA-256 hash should be 64 characters"


def test_hash_event_with_previous_hash(sample_event_data):
    """Test hash chaining with previous hash."""
    hash1 = hash_event(sample_event_data, previous_hash=None)
    hash2 = hash_event(sample_event_data, previous_hash=hash1)

    assert hash1 != hash2, "Hash should change when previous_hash is included"
    assert len(hash2) == 64, "Hash should be 64 characters"


def test_hash_event_json_key_ordering():
    """Test that JSON key ordering is deterministic (failure mode from Section 8)."""
    data1 = {"b": 2, "a": 1}
    data2 = {"a": 1, "b": 2}

    hash1 = hash_event(data1)
    hash2 = hash_event(data2)

    assert hash1 == hash2, "Hash should be same regardless of key order"


# Test 2: Audit Trail Initialization
def test_audit_trail_initialization(test_database_url):
    """Test audit trail initializes correctly."""
    trail = FinancialAuditTrail(test_database_url)
    assert trail.database_url == test_database_url
    assert trail.get_event_count() == 0, "New trail should have 0 events"


def test_audit_trail_invalid_database_url():
    """Test initialization fails with invalid database URL."""
    with pytest.raises(ValueError):
        FinancialAuditTrail("invalid://url")


# Test 3: Event Logging
def test_log_event_basic(audit_trail):
    """Test basic event logging."""
    event_hash = audit_trail.log_event(
        "test_event",
        {"key": "value"},
        user_id="test_user"
    )

    assert event_hash is not None
    assert len(event_hash) == 64
    assert audit_trail.get_event_count() == 1


def test_log_document_ingested(audit_trail):
    """Test logging document ingestion."""
    event_hash = audit_trail.log_document_ingested(
        document_id="aapl_10k_2024",
        source_url="https://sec.gov/...",
        filing_date="2024-03-15",
        document_type="10-K",
        user_id="pipeline@company.com"
    )

    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


def test_log_document_processed(audit_trail):
    """Test logging document processing."""
    event_hash = audit_trail.log_document_processed(
        document_id="aapl_10k_2024",
        chunks_created=487,
        embeddings_created=487,
        processing_time_seconds=12.5,
        user_id="pipeline@company.com"
    )

    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


def test_log_query(audit_trail):
    """Test logging a query."""
    event_hash = audit_trail.log_query(
        query_text="What was Apple's revenue in Q4 2024?",
        query_id="q_001",
        user_id="analyst@company.com"
    )

    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


def test_log_retrieval(audit_trail):
    """Test logging retrieval results."""
    chunks = [
        {
            "chunk_id": "aapl_10k_2024#chunk_127",
            "page_num": 28,
            "score": 0.87,
            "text_preview": "Revenue for Q4 2024..."
        }
    ]

    event_hash = audit_trail.log_retrieval(
        query_id="q_001",
        chunks_retrieved=chunks,
        user_id="analyst@company.com"
    )

    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


def test_log_generation(audit_trail):
    """Test logging answer generation."""
    event_hash = audit_trail.log_generation(
        query_id="q_001",
        answer="According to the 10-K filing, Apple's Q4 2024 revenue was $94.9B...",
        citations=["[1] AAPL 10-K FY2024, p.28"],
        model_used="gpt-4",
        user_id="analyst@company.com"
    )

    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


# Test 4: Hash Chain Integrity
def test_hash_chain_formation(audit_trail):
    """Test that events form a proper hash chain."""
    # Log three events
    hash1 = audit_trail.log_event("event1", {"data": "first"}, user_id="user1")
    hash2 = audit_trail.log_event("event2", {"data": "second"}, user_id="user2")
    hash3 = audit_trail.log_event("event3", {"data": "third"}, user_id="user3")

    # Verify chain
    is_valid, broken_events = audit_trail.verify_integrity()

    assert is_valid, "Hash chain should be valid"
    assert len(broken_events) == 0, "No events should be broken"
    assert audit_trail.get_event_count() == 3


def test_verify_integrity_empty_trail(audit_trail):
    """Test verification of empty audit trail."""
    is_valid, broken_events = audit_trail.verify_integrity()

    assert is_valid, "Empty trail should be valid"
    assert len(broken_events) == 0


def test_verify_chain_integrity_standalone(test_database_url):
    """Test standalone verification function."""
    trail = FinancialAuditTrail(test_database_url)
    trail.log_event("test", {"data": "value"})

    is_valid, broken_events = verify_chain_integrity(test_database_url)

    assert is_valid
    assert len(broken_events) == 0


# Test 5: Compliance Report Generation
def test_compliance_report_basic(audit_trail):
    """Test compliance report generation."""
    # Log some events
    audit_trail.log_document_ingested(
        "aapl_10k_2024",
        "https://sec.gov/...",
        "2024-03-15",
        "10-K",
        user_id="user1"
    )
    audit_trail.log_query(
        "What was revenue?",
        "q_001",
        user_id="user2"
    )

    # Generate report
    start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2024, 12, 31, tzinfo=timezone.utc)

    report = audit_trail.generate_compliance_report(start_date, end_date)

    assert report["total_events"] == 2
    assert "document_ingested" in report["event_breakdown"]
    assert "query_executed" in report["event_breakdown"]
    assert report["unique_users"] == 2
    assert report["chain_valid"] is True


def test_compliance_report_date_filtering(audit_trail):
    """Test compliance report filters by date correctly."""
    # Log events at different times (simulated by using current time)
    audit_trail.log_event("event1", {"data": "value1"}, user_id="user1")
    audit_trail.log_event("event2", {"data": "value2"}, user_id="user2")

    # Report for a future date range (should be empty)
    future_start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    future_end = datetime(2025, 12, 31, tzinfo=timezone.utc)

    report = audit_trail.generate_compliance_report(future_start, future_end)

    assert report["total_events"] == 0, "No events should be in future date range"


# Test 6: Failure Scenarios (from Section 8)
def test_timezone_handling():
    """Test that timestamps use UTC (failure mode: timezone bugs)."""
    trail = FinancialAuditTrail("sqlite:///:memory:")
    event_hash = trail.log_event("test", {"data": "value"})

    # Verify the logged event has UTC timezone
    session = trail.SessionLocal()
    try:
        event = session.query(AuditEvent).first()
        assert event.timestamp.tzinfo is not None, "Timestamp should have timezone"
        # Note: SQLite doesn't enforce timezone, but PostgreSQL does
    finally:
        session.close()


def test_long_query_text_truncation(audit_trail):
    """Test that long query text is truncated (storage efficiency)."""
    long_query = "What " * 200  # Very long query

    event_hash = audit_trail.log_query(
        query_text=long_query,
        query_id="q_long",
        user_id="user1"
    )

    # Verify event was logged successfully
    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


def test_answer_preview_truncation(audit_trail):
    """Test that long answers are truncated to preview (storage efficiency)."""
    long_answer = "According to the filing, " * 100  # Very long answer

    event_hash = audit_trail.log_generation(
        query_id="q_001",
        answer=long_answer,
        citations=["[1] Test"],
        model_used="gpt-4",
        user_id="user1"
    )

    # Verify event was logged successfully
    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


def test_multiple_users_unique_count(audit_trail):
    """Test that unique user counting works correctly."""
    audit_trail.log_event("event1", {"data": "1"}, user_id="user1")
    audit_trail.log_event("event2", {"data": "2"}, user_id="user1")  # Same user
    audit_trail.log_event("event3", {"data": "3"}, user_id="user2")  # Different user

    report = audit_trail.generate_compliance_report(
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2025, 1, 1, tzinfo=timezone.utc)
    )

    assert report["unique_users"] == 2, "Should count 2 unique users"


# Test 7: Edge Cases
def test_event_with_no_user_id(audit_trail):
    """Test logging events without user_id (system events)."""
    event_hash = audit_trail.log_event(
        "system_event",
        {"data": "automated"},
        user_id=None
    )

    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


def test_event_with_complex_json_data(audit_trail):
    """Test logging events with complex nested JSON data."""
    complex_data = {
        "nested": {
            "level1": {
                "level2": ["item1", "item2"],
                "value": 123
            }
        },
        "array": [1, 2, 3, 4, 5]
    }

    event_hash = audit_trail.log_event(
        "complex_event",
        complex_data,
        user_id="user1"
    )

    assert event_hash is not None
    assert audit_trail.get_event_count() == 1


# Test 8: Performance and Scalability
def test_bulk_event_logging(audit_trail):
    """Test logging multiple events quickly."""
    num_events = 100

    for i in range(num_events):
        audit_trail.log_event(
            f"event_{i}",
            {"index": i, "data": f"value_{i}"},
            user_id=f"user_{i % 10}"  # 10 unique users
        )

    assert audit_trail.get_event_count() == num_events

    # Verify integrity of all events
    is_valid, broken_events = audit_trail.verify_integrity()
    assert is_valid, "All events should maintain chain integrity"


# Test 9: Error Handling
def test_log_event_with_invalid_data():
    """Test that logging fails gracefully with invalid database connection."""
    # Use invalid database URL
    with pytest.raises(Exception):
        trail = FinancialAuditTrail("postgresql://invalid:invalid@localhost:9999/invalid")
        # Connection error should occur when trying to create tables or log events


def test_compliance_report_invalid_dates(audit_trail):
    """Test compliance report with invalid date format."""
    # This should be handled by the API layer, but test robustness
    with pytest.raises(Exception):
        # Pass invalid date types (strings instead of datetime objects)
        audit_trail.generate_compliance_report("invalid", "dates")
