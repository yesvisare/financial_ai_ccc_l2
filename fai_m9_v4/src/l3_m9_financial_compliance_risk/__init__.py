"""
L3 M9.4: Human-in-the-Loop for High-Stakes Decisions

This module implements a risk-based human review workflow for financial AI systems,
ensuring high-stakes decisions receive appropriate expert oversight before execution.
Supports regulatory compliance (SOX, FINRA, ECOA) with tamper-proof audit trails.
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "RiskLevel",
    "ReviewStatus",
    "DecisionOutcome",
    "classify_risk",
    "route_to_reviewer",
    "create_audit_entry",
    "validate_approval_chain",
    "check_sla_compliance",
    "escalate_decision",
    "verify_hash_chain",
    "HumanInTheLoopWorkflow",
]


# ═══════════════════════════════════════════════════════════════════════════
# Enumerations
# ═══════════════════════════════════════════════════════════════════════════

class RiskLevel(str, Enum):
    """Risk classification levels for financial decisions"""
    CRITICAL = "CRITICAL"  # MNPI, regulatory violations
    HIGH = "HIGH"          # >$1M investment decisions
    MEDIUM = "MEDIUM"      # Conditional review needed
    LOW = "LOW"            # Informational only


class ReviewStatus(str, Enum):
    """Status of human review process"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"


class DecisionOutcome(str, Enum):
    """Final decision outcomes"""
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    ESCALATED = "escalated"


# ═══════════════════════════════════════════════════════════════════════════
# Risk Classification
# ═══════════════════════════════════════════════════════════════════════════

def classify_risk(
    query_text: str,
    transaction_amount: Optional[float] = None,
    action_type: Optional[str] = None,
    contains_mnpi: bool = False,
    model_confidence: Optional[float] = None
) -> Tuple[RiskLevel, str]:
    """
    Classify financial query risk level based on multiple factors.

    Implements risk-proportional review principle: matches scrutiny depth
    to financial risk using transaction size, action type, MNPI presence,
    and model confidence thresholds.

    Args:
        query_text: The financial query or request text
        transaction_amount: Dollar amount involved (if applicable)
        action_type: Type of action (e.g., 'investment_decision', 'portfolio_rebalancing')
        contains_mnpi: Whether query involves material non-public information
        model_confidence: AI model confidence score (0-1)

    Returns:
        Tuple of (RiskLevel, reasoning string)

    Examples:
        >>> classify_risk("What is Tesla's market cap?", 0, "informational")
        (RiskLevel.LOW, "Informational query with no financial impact")

        >>> classify_risk("Approve $8M Tesla position increase", 8_000_000, "investment_decision")
        (RiskLevel.HIGH, "Investment decision exceeds $1M threshold")
    """
    logger.info(f"Classifying risk for query: {query_text[:100]}...")

    reasons = []

    # CRITICAL: MNPI always requires highest scrutiny
    if contains_mnpi:
        reasons.append("Contains material non-public information (MNPI)")
        logger.warning("CRITICAL risk: MNPI detected")
        return RiskLevel.CRITICAL, "; ".join(reasons)

    # HIGH: Large financial impact
    if transaction_amount and transaction_amount >= 1_000_000:
        reasons.append(f"Transaction amount ${transaction_amount:,.0f} exceeds $1M threshold")

        # CRITICAL: Very large transactions require committee approval
        if transaction_amount >= 10_000_000:
            reasons.append("Transaction exceeds $10M requiring CFO review")
            logger.warning(f"CRITICAL risk: ${transaction_amount:,.0f} transaction")
            return RiskLevel.CRITICAL, "; ".join(reasons)

        logger.info(f"HIGH risk: ${transaction_amount:,.0f} transaction")
        return RiskLevel.HIGH, "; ".join(reasons)

    # HIGH: Action types requiring mandatory review
    high_risk_actions = {
        "investment_decision",
        "portfolio_rebalancing",
        "credit_approval",
        "m_and_a_analysis",
    }

    if action_type and action_type.lower().replace(" ", "_") in high_risk_actions:
        reasons.append(f"Action type '{action_type}' requires mandatory review")
        logger.info(f"HIGH risk: {action_type} detected")
        return RiskLevel.HIGH, "; ".join(reasons)

    # MEDIUM: Low model confidence
    if model_confidence is not None and model_confidence < 0.70:
        reasons.append(f"Model confidence {model_confidence:.1%} below 70% threshold")
        logger.info(f"MEDIUM risk: Low confidence ({model_confidence:.1%})")
        return RiskLevel.MEDIUM, "; ".join(reasons)

    # MEDIUM: Moderate financial impact
    if transaction_amount and transaction_amount >= 100_000:
        reasons.append(f"Transaction amount ${transaction_amount:,.0f} warrants conditional review")
        logger.info(f"MEDIUM risk: ${transaction_amount:,.0f} transaction")
        return RiskLevel.MEDIUM, "; ".join(reasons)

    # MEDIUM: Analysis actions
    medium_risk_actions = {
        "earnings_analysis",
        "sector_comparison",
        "risk_assessment",
    }

    if action_type and action_type.lower().replace(" ", "_") in medium_risk_actions:
        reasons.append(f"Action type '{action_type}' suggests analytical review")
        logger.info(f"MEDIUM risk: {action_type}")
        return RiskLevel.MEDIUM, "; ".join(reasons)

    # LOW: Informational queries
    reasons.append("Informational query with minimal financial impact")
    logger.info("LOW risk: Informational query")
    return RiskLevel.LOW, "; ".join(reasons)


# ═══════════════════════════════════════════════════════════════════════════
# Routing Logic
# ═══════════════════════════════════════════════════════════════════════════

def route_to_reviewer(
    risk_level: RiskLevel,
    transaction_amount: Optional[float] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    Route query to appropriate reviewer based on risk level and expertise.

    Implements expertise-matched routing and time-aware workflows with
    SLA tracking to balance thoroughness with market timing requirements.

    Args:
        risk_level: Classified risk level
        transaction_amount: Transaction dollar amount
        domain: Financial domain (e.g., 'equity', 'fixed_income', 'credit')

    Returns:
        Dictionary with reviewer_role, sla_hours, requires_second_opinion,
        approval_committee_needed, and routing_reason
    """
    logger.info(f"Routing {risk_level} risk query")

    # CRITICAL risk routing
    if risk_level == RiskLevel.CRITICAL:
        return {
            "reviewer_role": "CFO",
            "sla_hours": 2,
            "requires_second_opinion": True,
            "approval_committee_needed": True,
            "escalation_path": ["Senior Analyst", "Head of Trading", "CFO", "Board Committee"],
            "routing_reason": "MNPI or $10M+ transaction requires executive review"
        }

    # HIGH risk routing
    if risk_level == RiskLevel.HIGH:
        sla_hours = 4

        # Large transactions need second opinion
        if transaction_amount and transaction_amount >= 10_000_000:
            return {
                "reviewer_role": "Senior Analyst",
                "sla_hours": sla_hours,
                "requires_second_opinion": True,
                "approval_committee_needed": False,
                "escalation_path": ["Senior Analyst", "Head of Trading"],
                "routing_reason": f"${transaction_amount:,.0f} transaction requires senior review with second opinion"
            }

        return {
            "reviewer_role": "Senior Analyst",
            "sla_hours": sla_hours,
            "requires_second_opinion": False,
            "approval_committee_needed": False,
            "escalation_path": ["Senior Analyst", "Head of Trading"],
            "routing_reason": "High-stakes decision requires senior analyst expertise"
        }

    # MEDIUM risk routing
    if risk_level == RiskLevel.MEDIUM:
        return {
            "reviewer_role": "Analyst",
            "sla_hours": 8,
            "requires_second_opinion": False,
            "approval_committee_needed": False,
            "escalation_path": ["Analyst", "Senior Analyst"],
            "routing_reason": "Conditional review by qualified analyst"
        }

    # LOW risk - minimal review needed
    return {
        "reviewer_role": "Junior Analyst",
        "sla_hours": 24,
        "requires_second_opinion": False,
        "approval_committee_needed": False,
        "escalation_path": ["Junior Analyst"],
        "routing_reason": "Informational query requires minimal oversight"
    }


# ═══════════════════════════════════════════════════════════════════════════
# Audit Trail Management
# ═══════════════════════════════════════════════════════════════════════════

def create_audit_entry(
    user_id: str,
    query_text: str,
    rag_response: Dict[str, Any],
    risk_classification: RiskLevel,
    reviewer_id: Optional[str] = None,
    decision_outcome: Optional[DecisionOutcome] = None,
    supporting_evidence: Optional[str] = None,
    previous_hash: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create tamper-proof audit trail entry with hash chain.

    Implements "audit-ready by default" principle for SOX Section 404
    compliance with cryptographic hash chains for tamper detection.

    Args:
        user_id: User who submitted the query
        query_text: Original query text
        rag_response: AI-generated response (JSONB structure)
        risk_classification: Assigned risk level
        reviewer_id: ID of human reviewer
        decision_outcome: Final decision (approved/rejected/modified)
        supporting_evidence: Analyst's reasoning and evidence
        previous_hash: Hash of previous audit entry (for chain)

    Returns:
        Complete audit entry with SHA-256 hash
    """
    logger.info(f"Creating audit entry for user {user_id}")

    timestamp = datetime.utcnow().isoformat()
    audit_id = hashlib.sha256(
        f"{user_id}{timestamp}{query_text}".encode()
    ).hexdigest()[:16]

    # Build audit entry
    audit_entry = {
        "audit_id": audit_id,
        "timestamp": timestamp,
        "user_id": user_id,
        "query_text": query_text,
        "rag_response": rag_response,
        "risk_classification": risk_classification.value,
        "reviewer_id": reviewer_id,
        "decision_outcome": decision_outcome.value if decision_outcome else None,
        "supporting_evidence": supporting_evidence,
        "previous_hash": previous_hash,
    }

    # Calculate hash chain
    entry_json = json.dumps(audit_entry, sort_keys=True)
    current_hash = hashlib.sha256(entry_json.encode()).hexdigest()
    audit_entry["current_hash"] = current_hash

    logger.info(f"Created audit entry {audit_id} with hash {current_hash[:16]}...")

    return audit_entry


def verify_hash_chain(audit_entries: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """
    Verify integrity of audit trail hash chain.

    Ensures tamper-proof audit trail by validating cryptographic hash
    chain across all entries.

    Args:
        audit_entries: List of audit entries in chronological order

    Returns:
        Tuple of (is_valid, error_message)
    """
    logger.info(f"Verifying hash chain for {len(audit_entries)} entries")

    if not audit_entries:
        return True, None

    for i, entry in enumerate(audit_entries):
        # Verify current hash
        entry_copy = {k: v for k, v in entry.items() if k != "current_hash"}
        entry_json = json.dumps(entry_copy, sort_keys=True)
        expected_hash = hashlib.sha256(entry_json.encode()).hexdigest()

        if entry.get("current_hash") != expected_hash:
            error_msg = f"Hash mismatch at entry {i} (audit_id: {entry.get('audit_id')})"
            logger.error(error_msg)
            return False, error_msg

        # Verify chain linkage
        if i > 0:
            previous_entry = audit_entries[i - 1]
            if entry.get("previous_hash") != previous_entry.get("current_hash"):
                error_msg = f"Chain break at entry {i} (audit_id: {entry.get('audit_id')})"
                logger.error(error_msg)
                return False, error_msg

    logger.info("✅ Hash chain verified successfully")
    return True, None


# ═══════════════════════════════════════════════════════════════════════════
# Approval Workflow
# ═══════════════════════════════════════════════════════════════════════════

def validate_approval_chain(
    decision_outcome: DecisionOutcome,
    reviewer_role: str,
    required_role: str,
    requires_second_opinion: bool = False,
    second_reviewer_role: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Validate that approval chain meets role-based access control requirements.

    Args:
        decision_outcome: Proposed decision
        reviewer_role: Role of primary reviewer
        required_role: Minimum required role for this decision
        requires_second_opinion: Whether second opinion is mandatory
        second_reviewer_role: Role of second reviewer (if applicable)

    Returns:
        Tuple of (is_valid, reason)
    """
    logger.info(f"Validating approval: {reviewer_role} -> {decision_outcome.value}")

    # Role hierarchy
    role_hierarchy = {
        "Junior Analyst": 1,
        "Analyst": 2,
        "Senior Analyst": 3,
        "Head of Trading": 4,
        "CFO": 5,
    }

    reviewer_level = role_hierarchy.get(reviewer_role, 0)
    required_level = role_hierarchy.get(required_role, 0)

    if reviewer_level < required_level:
        reason = f"Reviewer role '{reviewer_role}' insufficient for required role '{required_role}'"
        logger.warning(f"❌ {reason}")
        return False, reason

    if requires_second_opinion and not second_reviewer_role:
        reason = "Second opinion required but not provided"
        logger.warning(f"❌ {reason}")
        return False, reason

    if requires_second_opinion:
        second_level = role_hierarchy.get(second_reviewer_role, 0)
        if second_level < required_level:
            reason = f"Second reviewer role '{second_reviewer_role}' insufficient"
            logger.warning(f"❌ {reason}")
            return False, reason

    logger.info("✅ Approval chain validated")
    return True, "Approval chain meets requirements"


def check_sla_compliance(
    submission_time: datetime,
    review_time: Optional[datetime],
    sla_hours: int
) -> Dict[str, Any]:
    """
    Check if review meets SLA requirements.

    Implements time-aware workflows with SLA tracking to balance
    thoroughness with market timing requirements.

    Args:
        submission_time: When query was submitted
        review_time: When review was completed (None if pending)
        sla_hours: Required SLA in hours

    Returns:
        Dictionary with is_compliant, elapsed_hours, remaining_hours,
        and status message
    """
    logger.info(f"Checking SLA compliance (target: {sla_hours}h)")

    current_time = review_time or datetime.utcnow()
    elapsed = current_time - submission_time
    elapsed_hours = elapsed.total_seconds() / 3600

    sla_deadline = submission_time + timedelta(hours=sla_hours)
    remaining = sla_deadline - current_time
    remaining_hours = remaining.total_seconds() / 3600

    is_compliant = elapsed_hours <= sla_hours

    if review_time:
        # Completed review
        if is_compliant:
            status = f"✅ Review completed in {elapsed_hours:.1f}h (SLA: {sla_hours}h)"
            logger.info(status)
        else:
            status = f"❌ Review took {elapsed_hours:.1f}h, exceeded {sla_hours}h SLA by {elapsed_hours - sla_hours:.1f}h"
            logger.warning(status)
    else:
        # Pending review
        if remaining_hours > 0:
            status = f"⏳ Pending review: {remaining_hours:.1f}h remaining of {sla_hours}h SLA"
            logger.info(status)
        else:
            status = f"⚠️ SLA breach: {-remaining_hours:.1f}h overdue"
            logger.warning(status)

    return {
        "is_compliant": is_compliant,
        "elapsed_hours": round(elapsed_hours, 2),
        "remaining_hours": round(remaining_hours, 2),
        "sla_hours": sla_hours,
        "status": status,
    }


def escalate_decision(
    current_reviewer_role: str,
    escalation_path: List[str],
    reason: str
) -> Dict[str, Any]:
    """
    Escalate decision to next level in approval hierarchy.

    Implements fail-safe defaults and escalation hierarchies for
    urgent or complex decisions requiring higher authority.

    Args:
        current_reviewer_role: Current reviewer's role
        escalation_path: Ordered list of escalation roles
        reason: Reason for escalation

    Returns:
        Dictionary with next_reviewer_role, escalation_reason, and priority
    """
    logger.warning(f"Escalating from {current_reviewer_role}: {reason}")

    try:
        current_index = escalation_path.index(current_reviewer_role)

        # Check if can escalate further
        if current_index >= len(escalation_path) - 1:
            logger.error("Already at highest escalation level")
            return {
                "next_reviewer_role": current_reviewer_role,
                "escalation_reason": "Already at highest authority level",
                "priority": "CRITICAL",
                "requires_committee": True,
            }

        next_role = escalation_path[current_index + 1]
        logger.info(f"Escalating to {next_role}")

        return {
            "next_reviewer_role": next_role,
            "escalation_reason": reason,
            "priority": "HIGH",
            "requires_committee": next_role == "CFO",
        }

    except ValueError:
        logger.error(f"Role {current_reviewer_role} not in escalation path")
        # Fail-safe: escalate to highest level
        return {
            "next_reviewer_role": escalation_path[-1],
            "escalation_reason": f"Unknown role escalation: {reason}",
            "priority": "CRITICAL",
            "requires_committee": True,
        }


# ═══════════════════════════════════════════════════════════════════════════
# Main Workflow Class
# ═══════════════════════════════════════════════════════════════════════════

class HumanInTheLoopWorkflow:
    """
    Complete human-in-the-loop workflow orchestration.

    Coordinates risk classification, routing, approval, and audit trail
    creation for financial AI decisions requiring human oversight.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize HITL workflow.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.audit_trail: List[Dict[str, Any]] = []
        logger.info("Initialized HumanInTheLoopWorkflow")

    def process_query(
        self,
        user_id: str,
        query_text: str,
        transaction_amount: Optional[float] = None,
        action_type: Optional[str] = None,
        rag_response: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the complete HITL workflow.

        Args:
            user_id: User submitting the query
            query_text: Query text
            transaction_amount: Transaction dollar amount (if applicable)
            action_type: Type of financial action
            rag_response: AI-generated response to review

        Returns:
            Complete workflow result with routing and audit information
        """
        logger.info(f"Processing query from user {user_id}")

        # Step 1: Risk classification
        risk_level, risk_reason = classify_risk(
            query_text=query_text,
            transaction_amount=transaction_amount,
            action_type=action_type
        )

        # Step 2: Route to appropriate reviewer
        routing = route_to_reviewer(
            risk_level=risk_level,
            transaction_amount=transaction_amount
        )

        # Step 3: Create audit entry
        previous_hash = self.audit_trail[-1]["current_hash"] if self.audit_trail else None

        audit_entry = create_audit_entry(
            user_id=user_id,
            query_text=query_text,
            rag_response=rag_response or {},
            risk_classification=risk_level,
            previous_hash=previous_hash
        )

        self.audit_trail.append(audit_entry)

        # Step 4: Calculate SLA
        submission_time = datetime.fromisoformat(audit_entry["timestamp"])
        sla_check = check_sla_compliance(
            submission_time=submission_time,
            review_time=None,
            sla_hours=routing["sla_hours"]
        )

        return {
            "audit_id": audit_entry["audit_id"],
            "risk_level": risk_level.value,
            "risk_reason": risk_reason,
            "routing": routing,
            "sla_compliance": sla_check,
            "status": ReviewStatus.PENDING.value,
            "message": f"Query routed to {routing['reviewer_role']} with {routing['sla_hours']}h SLA"
        }

    def submit_review(
        self,
        audit_id: str,
        reviewer_id: str,
        reviewer_role: str,
        decision_outcome: DecisionOutcome,
        supporting_evidence: str
    ) -> Dict[str, Any]:
        """
        Submit human review decision.

        Args:
            audit_id: Audit entry ID being reviewed
            reviewer_id: ID of reviewer
            reviewer_role: Role of reviewer
            decision_outcome: Decision (approved/rejected/modified)
            supporting_evidence: Analyst's reasoning

        Returns:
            Review result with validation status
        """
        logger.info(f"Submitting review for audit {audit_id}")

        # Find audit entry
        audit_entry = next(
            (entry for entry in self.audit_trail if entry["audit_id"] == audit_id),
            None
        )

        if not audit_entry:
            logger.error(f"Audit entry {audit_id} not found")
            return {
                "status": "error",
                "message": f"Audit entry {audit_id} not found"
            }

        # Update audit entry
        audit_entry["reviewer_id"] = reviewer_id
        audit_entry["decision_outcome"] = decision_outcome.value
        audit_entry["supporting_evidence"] = supporting_evidence
        audit_entry["review_timestamp"] = datetime.utcnow().isoformat()

        # Recalculate hash with review data
        entry_copy = {k: v for k, v in audit_entry.items() if k != "current_hash"}
        entry_json = json.dumps(entry_copy, sort_keys=True)
        audit_entry["current_hash"] = hashlib.sha256(entry_json.encode()).hexdigest()

        logger.info(f"✅ Review submitted: {decision_outcome.value}")

        return {
            "status": "success",
            "audit_id": audit_id,
            "decision_outcome": decision_outcome.value,
            "message": f"Review submitted by {reviewer_role}"
        }

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get complete audit trail with hash verification."""
        is_valid, error = verify_hash_chain(self.audit_trail)

        return {
            "audit_trail": self.audit_trail,
            "total_entries": len(self.audit_trail),
            "hash_chain_valid": is_valid,
            "validation_error": error,
        }
