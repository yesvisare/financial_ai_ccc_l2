"""Tests for L3 M9.4: Human-in-the-Loop for High-Stakes Decisions"""

import pytest
from datetime import datetime, timedelta
from src.l3_m9_financial_compliance_risk import (
    RiskLevel,
    ReviewStatus,
    DecisionOutcome,
    classify_risk,
    route_to_reviewer,
    create_audit_entry,
    validate_approval_chain,
    check_sla_compliance,
    escalate_decision,
    verify_hash_chain,
    HumanInTheLoopWorkflow,
)


# ═══════════════════════════════════════════════════════════════════════════
# Risk Classification Tests
# ═══════════════════════════════════════════════════════════════════════════

def test_classify_risk_critical_mnpi():
    """Test CRITICAL risk classification for MNPI"""
    risk_level, reason = classify_risk(
        query_text="Approve Q4 earnings disclosure",
        contains_mnpi=True
    )
    assert risk_level == RiskLevel.CRITICAL
    assert "material non-public information" in reason.lower()


def test_classify_risk_critical_large_transaction():
    """Test CRITICAL risk for $10M+ transactions"""
    risk_level, reason = classify_risk(
        query_text="Approve $12M acquisition",
        transaction_amount=12_000_000,
        action_type="m_and_a_analysis"
    )
    assert risk_level == RiskLevel.CRITICAL
    assert "$10M" in reason


def test_classify_risk_high_large_transaction():
    """Test HIGH risk for $1M+ transactions"""
    risk_level, reason = classify_risk(
        query_text="Increase Tesla position",
        transaction_amount=8_000_000,
        action_type="investment_decision"
    )
    assert risk_level == RiskLevel.HIGH
    assert "$1M" in reason


def test_classify_risk_high_action_type():
    """Test HIGH risk for high-stakes action types"""
    risk_level, reason = classify_risk(
        query_text="Approve credit line",
        action_type="credit_approval"
    )
    assert risk_level == RiskLevel.HIGH
    assert "credit_approval" in reason or "mandatory review" in reason.lower()


def test_classify_risk_medium_low_confidence():
    """Test MEDIUM risk for low model confidence"""
    risk_level, reason = classify_risk(
        query_text="Analyze earnings",
        model_confidence=0.65
    )
    assert risk_level == RiskLevel.MEDIUM
    assert "confidence" in reason.lower()


def test_classify_risk_medium_moderate_transaction():
    """Test MEDIUM risk for $100K-1M transactions"""
    risk_level, reason = classify_risk(
        query_text="Execute trade",
        transaction_amount=500_000,
        action_type="investment_decision"
    )
    assert risk_level == RiskLevel.MEDIUM


def test_classify_risk_low_informational():
    """Test LOW risk for informational queries"""
    risk_level, reason = classify_risk(
        query_text="What is Tesla's market cap?",
        transaction_amount=0,
        action_type="informational"
    )
    assert risk_level == RiskLevel.LOW
    assert "informational" in reason.lower()


# ═══════════════════════════════════════════════════════════════════════════
# Routing Logic Tests
# ═══════════════════════════════════════════════════════════════════════════

def test_route_critical_risk():
    """Test routing for CRITICAL risk to CFO"""
    routing = route_to_reviewer(RiskLevel.CRITICAL)
    assert routing["reviewer_role"] == "CFO"
    assert routing["sla_hours"] == 2
    assert routing["requires_second_opinion"] is True
    assert routing["approval_committee_needed"] is True


def test_route_high_risk_large_transaction():
    """Test routing for HIGH risk $10M+ transaction"""
    routing = route_to_reviewer(RiskLevel.HIGH, transaction_amount=12_000_000)
    assert routing["reviewer_role"] == "Senior Analyst"
    assert routing["sla_hours"] == 4
    assert routing["requires_second_opinion"] is True


def test_route_high_risk_standard():
    """Test routing for standard HIGH risk"""
    routing = route_to_reviewer(RiskLevel.HIGH, transaction_amount=5_000_000)
    assert routing["reviewer_role"] == "Senior Analyst"
    assert routing["sla_hours"] == 4
    assert routing["requires_second_opinion"] is False


def test_route_medium_risk():
    """Test routing for MEDIUM risk"""
    routing = route_to_reviewer(RiskLevel.MEDIUM)
    assert routing["reviewer_role"] == "Analyst"
    assert routing["sla_hours"] == 8


def test_route_low_risk():
    """Test routing for LOW risk"""
    routing = route_to_reviewer(RiskLevel.LOW)
    assert routing["reviewer_role"] == "Junior Analyst"
    assert routing["sla_hours"] == 24


# ═══════════════════════════════════════════════════════════════════════════
# Audit Trail Tests
# ═══════════════════════════════════════════════════════════════════════════

def test_create_audit_entry_basic():
    """Test basic audit entry creation"""
    entry = create_audit_entry(
        user_id="pm_001",
        query_text="Test query",
        rag_response={"result": "test"},
        risk_classification=RiskLevel.HIGH
    )

    assert "audit_id" in entry
    assert entry["user_id"] == "pm_001"
    assert entry["query_text"] == "Test query"
    assert entry["risk_classification"] == "HIGH"
    assert "current_hash" in entry
    assert "timestamp" in entry


def test_create_audit_entry_with_review():
    """Test audit entry with review data"""
    entry = create_audit_entry(
        user_id="pm_001",
        query_text="Test query",
        rag_response={},
        risk_classification=RiskLevel.HIGH,
        reviewer_id="analyst_42",
        decision_outcome=DecisionOutcome.APPROVED,
        supporting_evidence="Analysis complete"
    )

    assert entry["reviewer_id"] == "analyst_42"
    assert entry["decision_outcome"] == "approved"
    assert entry["supporting_evidence"] == "Analysis complete"


def test_create_audit_entry_hash_chain():
    """Test audit entry hash chain linkage"""
    entry1 = create_audit_entry(
        user_id="user1",
        query_text="Query 1",
        rag_response={},
        risk_classification=RiskLevel.LOW
    )

    entry2 = create_audit_entry(
        user_id="user2",
        query_text="Query 2",
        rag_response={},
        risk_classification=RiskLevel.HIGH,
        previous_hash=entry1["current_hash"]
    )

    assert entry2["previous_hash"] == entry1["current_hash"]
    assert entry1["current_hash"] != entry2["current_hash"]


def test_verify_hash_chain_valid():
    """Test hash chain verification with valid chain"""
    entries = []

    for i in range(3):
        prev_hash = entries[-1]["current_hash"] if entries else None
        entry = create_audit_entry(
            user_id=f"user_{i}",
            query_text=f"Query {i}",
            rag_response={},
            risk_classification=RiskLevel.LOW,
            previous_hash=prev_hash
        )
        entries.append(entry)

    is_valid, error = verify_hash_chain(entries)
    assert is_valid is True
    assert error is None


def test_verify_hash_chain_tampering():
    """Test hash chain detects tampering"""
    entries = []

    for i in range(3):
        prev_hash = entries[-1]["current_hash"] if entries else None
        entry = create_audit_entry(
            user_id=f"user_{i}",
            query_text=f"Query {i}",
            rag_response={},
            risk_classification=RiskLevel.LOW,
            previous_hash=prev_hash
        )
        entries.append(entry)

    # Tamper with middle entry
    entries[1]["query_text"] = "TAMPERED"

    is_valid, error = verify_hash_chain(entries)
    assert is_valid is False
    assert error is not None
    assert "Hash mismatch" in error


# ═══════════════════════════════════════════════════════════════════════════
# Approval Workflow Tests
# ═══════════════════════════════════════════════════════════════════════════

def test_validate_approval_chain_valid():
    """Test valid approval chain"""
    is_valid, reason = validate_approval_chain(
        decision_outcome=DecisionOutcome.APPROVED,
        reviewer_role="Senior Analyst",
        required_role="Senior Analyst"
    )
    assert is_valid is True


def test_validate_approval_chain_insufficient_role():
    """Test insufficient reviewer role"""
    is_valid, reason = validate_approval_chain(
        decision_outcome=DecisionOutcome.APPROVED,
        reviewer_role="Analyst",
        required_role="Senior Analyst"
    )
    assert is_valid is False
    assert "insufficient" in reason.lower()


def test_validate_approval_chain_missing_second_opinion():
    """Test missing required second opinion"""
    is_valid, reason = validate_approval_chain(
        decision_outcome=DecisionOutcome.APPROVED,
        reviewer_role="Senior Analyst",
        required_role="Senior Analyst",
        requires_second_opinion=True,
        second_reviewer_role=None
    )
    assert is_valid is False
    assert "second opinion" in reason.lower()


def test_validate_approval_chain_with_second_opinion():
    """Test valid second opinion"""
    is_valid, reason = validate_approval_chain(
        decision_outcome=DecisionOutcome.APPROVED,
        reviewer_role="Senior Analyst",
        required_role="Senior Analyst",
        requires_second_opinion=True,
        second_reviewer_role="Senior Analyst"
    )
    assert is_valid is True


# ═══════════════════════════════════════════════════════════════════════════
# SLA Compliance Tests
# ═══════════════════════════════════════════════════════════════════════════

def test_sla_compliance_within_limit():
    """Test SLA compliance when within time limit"""
    submission_time = datetime.utcnow() - timedelta(hours=2)
    review_time = datetime.utcnow()

    result = check_sla_compliance(
        submission_time=submission_time,
        review_time=review_time,
        sla_hours=4
    )

    assert result["is_compliant"] is True
    assert result["elapsed_hours"] < 4


def test_sla_compliance_breach():
    """Test SLA compliance when breached"""
    submission_time = datetime.utcnow() - timedelta(hours=6)
    review_time = datetime.utcnow()

    result = check_sla_compliance(
        submission_time=submission_time,
        review_time=review_time,
        sla_hours=4
    )

    assert result["is_compliant"] is False
    assert result["elapsed_hours"] > 4


def test_sla_compliance_pending():
    """Test SLA compliance for pending review"""
    submission_time = datetime.utcnow() - timedelta(hours=1)

    result = check_sla_compliance(
        submission_time=submission_time,
        review_time=None,
        sla_hours=4
    )

    assert result["remaining_hours"] > 0
    assert "⏳" in result["status"]


def test_sla_compliance_pending_overdue():
    """Test SLA compliance for overdue pending review"""
    submission_time = datetime.utcnow() - timedelta(hours=6)

    result = check_sla_compliance(
        submission_time=submission_time,
        review_time=None,
        sla_hours=4
    )

    assert result["remaining_hours"] < 0
    assert "⚠️" in result["status"]


# ═══════════════════════════════════════════════════════════════════════════
# Escalation Tests
# ═══════════════════════════════════════════════════════════════════════════

def test_escalate_to_next_level():
    """Test escalation to next level in hierarchy"""
    escalation_path = ["Analyst", "Senior Analyst", "Head of Trading", "CFO"]

    result = escalate_decision(
        current_reviewer_role="Analyst",
        escalation_path=escalation_path,
        reason="SLA breach"
    )

    assert result["next_reviewer_role"] == "Senior Analyst"
    assert result["priority"] == "HIGH"


def test_escalate_at_highest_level():
    """Test escalation when already at highest level"""
    escalation_path = ["Senior Analyst", "CFO"]

    result = escalate_decision(
        current_reviewer_role="CFO",
        escalation_path=escalation_path,
        reason="Complex decision"
    )

    assert result["next_reviewer_role"] == "CFO"
    assert result["requires_committee"] is True
    assert result["priority"] == "CRITICAL"


def test_escalate_unknown_role():
    """Test fail-safe escalation for unknown role"""
    escalation_path = ["Analyst", "Senior Analyst", "CFO"]

    result = escalate_decision(
        current_reviewer_role="Unknown Role",
        escalation_path=escalation_path,
        reason="Unknown role handling"
    )

    assert result["next_reviewer_role"] == "CFO"  # Escalate to highest
    assert result["priority"] == "CRITICAL"


# ═══════════════════════════════════════════════════════════════════════════
# Workflow Integration Tests
# ═══════════════════════════════════════════════════════════════════════════

def test_workflow_process_query():
    """Test complete workflow query processing"""
    workflow = HumanInTheLoopWorkflow()

    result = workflow.process_query(
        user_id="pm_001",
        query_text="Approve $8M Tesla position increase",
        transaction_amount=8_000_000,
        action_type="investment_decision"
    )

    assert "audit_id" in result
    assert result["risk_level"] == "HIGH"
    assert result["routing"]["reviewer_role"] == "Senior Analyst"
    assert result["status"] == "pending"


def test_workflow_submit_review():
    """Test workflow review submission"""
    workflow = HumanInTheLoopWorkflow()

    # Submit query
    query_result = workflow.process_query(
        user_id="pm_001",
        query_text="Test query",
        transaction_amount=5_000_000,
        action_type="investment_decision"
    )

    audit_id = query_result["audit_id"]

    # Submit review
    review_result = workflow.submit_review(
        audit_id=audit_id,
        reviewer_id="analyst_42",
        reviewer_role="Senior Analyst",
        decision_outcome=DecisionOutcome.APPROVED,
        supporting_evidence="Analysis complete, approved"
    )

    assert review_result["status"] == "success"
    assert review_result["decision_outcome"] == "approved"


def test_workflow_get_audit_trail():
    """Test workflow audit trail retrieval"""
    workflow = HumanInTheLoopWorkflow()

    # Submit multiple queries
    for i in range(3):
        workflow.process_query(
            user_id=f"user_{i}",
            query_text=f"Query {i}",
            transaction_amount=1_000_000,
            action_type="investment_decision"
        )

    audit_data = workflow.get_audit_trail()

    assert audit_data["total_entries"] == 3
    assert audit_data["hash_chain_valid"] is True
    assert len(audit_data["audit_trail"]) == 3


def test_workflow_review_not_found():
    """Test review submission for non-existent audit entry"""
    workflow = HumanInTheLoopWorkflow()

    result = workflow.submit_review(
        audit_id="nonexistent_id",
        reviewer_id="analyst_42",
        reviewer_role="Senior Analyst",
        decision_outcome=DecisionOutcome.APPROVED,
        supporting_evidence="Test"
    )

    assert result["status"] == "error"
    assert "not found" in result["message"].lower()


# ═══════════════════════════════════════════════════════════════════════════
# Edge Cases and Error Handling
# ═══════════════════════════════════════════════════════════════════════════

def test_empty_query_text():
    """Test handling of empty query text"""
    risk_level, reason = classify_risk(
        query_text="",
        transaction_amount=0
    )
    assert risk_level == RiskLevel.LOW


def test_negative_transaction_amount():
    """Test handling of negative transaction amounts"""
    risk_level, reason = classify_risk(
        query_text="Test",
        transaction_amount=-1000
    )
    assert risk_level == RiskLevel.LOW


def test_verify_empty_hash_chain():
    """Test hash chain verification with empty list"""
    is_valid, error = verify_hash_chain([])
    assert is_valid is True
    assert error is None


# ═══════════════════════════════════════════════════════════════════════════
# Integration Test Configuration
# ═══════════════════════════════════════════════════════════════════════════

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring external services"
    )


@pytest.mark.integration
def test_with_external_services():
    """Integration test requiring external services (database, Redis, etc.)"""
    # This test would require actual database and Redis setup
    # Skip by default unless --run-integration flag is set
    pytest.skip("Integration tests require external services")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
