"""
Tests for L3 M9.2: Financial Compliance Risk - Risk Assessment in Retrieval

Comprehensive test suite covering:
- Query risk classification (pattern-based)
- Multi-factor confidence scoring
- Compliance guardrails (RIA, MNPI, Safe Harbor, Form 8-K)
- User context adjustment
- Edge cases and adversarial queries

SERVICE: OFFLINE (no external API required)
"""

import pytest
import os
from datetime import datetime, timedelta

# Force offline mode for tests
os.environ["OFFLINE"] = "true"
os.environ["SEMANTIC_ANALYSIS_ENABLED"] = "false"

from src.l3_m9_financial_compliance_risk import (
    RiskLevel,
    SystemAction,
    FinancialQueryRiskClassifier,
    ConfidenceScorer,
    ComplianceGuardrails,
    classify_query_risk,
    compute_confidence_score,
    RiskClassificationResult
)


# ============================================================================
# RISK CLASSIFICATION TESTS
# ============================================================================

class TestRiskClassification:
    """Test suite for query risk classification."""

    def test_low_risk_educational_query(self):
        """Test classification of educational/factual queries."""
        queries = [
            "What is a 10-K filing?",
            "When does Apple's fiscal year end?",
            "Define EBITDA",
            "Explain what a balance sheet shows"
        ]

        for query in queries:
            result = classify_query_risk(query)
            assert result.risk_level == RiskLevel.LOW, f"Failed for: {query}"
            assert result.system_action == SystemAction.ANSWER_NORMALLY
            assert result.confidence >= 0.5

    def test_medium_risk_comparative_query(self):
        """Test classification of comparative analysis queries."""
        queries = [
            "Compare Apple and Microsoft's revenue growth",
            "What are Tesla's risk factors?",
            "How has Goldman Sachs stock performed?",
            "Is Tesla overvalued or undervalued?"
        ]

        for query in queries:
            result = classify_query_risk(query)
            assert result.risk_level == RiskLevel.MEDIUM, f"Failed for: {query}"
            assert result.system_action == SystemAction.ANSWER_WITH_DISCLAIMER
            assert result.confidence >= 0.5

    def test_high_risk_investment_advice_query(self):
        """Test classification of investment advice queries (requires RIA)."""
        queries = [
            "Should I buy Tesla stock?",
            "Is this a good time to invest in crypto?",
            "What's the best stock to buy right now?",
            "Would you recommend buying Apple or Microsoft?",
            "When should I sell my Amazon shares?"
        ]

        for query in queries:
            result = classify_query_risk(query)
            assert result.risk_level == RiskLevel.HIGH, f"Failed for: {query}"
            assert result.system_action == SystemAction.ESCALATE_TO_HUMAN_ADVISOR
            assert result.confidence >= 0.5
            assert result.regulatory_concern is not None
            assert "Investment Advisers Act" in result.regulatory_concern

    def test_pattern_matching_confidence(self):
        """Test that pattern matches have high confidence."""
        result = classify_query_risk("Should I buy Tesla stock?")
        assert result.confidence >= 0.85, "Pattern match should have high confidence"
        assert len(result.pattern_matches) > 0, "Should have pattern matches"

    def test_user_context_adjustment_escalation(self):
        """Test that repeated high-risk queries elevate risk level."""
        query = "Compare Apple and Microsoft revenue"  # Normally MEDIUM

        # Without high-risk history: MEDIUM
        result1 = classify_query_risk(query, user_context={"high_risk_query_count": 0})
        assert result1.risk_level == RiskLevel.MEDIUM

        # With high-risk history (≥3): Should elevate to HIGH
        result2 = classify_query_risk(query, user_context={"high_risk_query_count": 3})
        assert result2.risk_level == RiskLevel.HIGH, "Should elevate to HIGH with query history"
        assert result2.user_context_adjusted is True

    def test_edge_case_ambiguous_query(self):
        """Test handling of ambiguous queries."""
        query = "Tell me about Tesla"  # No clear pattern

        result = classify_query_risk(query)
        # Should default to MEDIUM for safety (conservative approach)
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]


# ============================================================================
# CONFIDENCE SCORING TESTS
# ============================================================================

class TestConfidenceScoring:
    """Test suite for multi-factor confidence scoring."""

    def test_high_confidence_scenario(self):
        """Test scenario with high retrieval quality and source agreement."""
        retrieval_results = [
            {"score": 0.92, "source_type": "10-K", "fiscal_period": "2024-Q4", "numerical_claim": "94.9B"},
            {"score": 0.89, "source_type": "8-K", "fiscal_period": "2024-Q4", "numerical_claim": "94.9B"},
            {"score": 0.91, "source_type": "earnings_call", "fiscal_period": "2024-Q4", "numerical_claim": "94.9B"},
            {"score": 0.85, "source_type": "analyst_report", "fiscal_period": "2024-Q4", "numerical_claim": "94.9B"}
        ]

        score = compute_confidence_score(retrieval_results, query="What was Apple's Q4 2024 revenue?")

        assert score.overall_score >= 0.85, f"Expected HIGH confidence, got {score.overall_score:.2f}"
        assert score.threshold_category == "HIGH"
        assert score.retrieval_quality >= 0.85
        assert score.source_diversity >= 0.75  # 4 unique types
        assert score.temporal_consistency >= 0.90  # All same period
        assert score.citation_agreement >= 0.90  # All agree on claim

    def test_low_confidence_scenario(self):
        """Test scenario with poor retrieval quality and inconsistency."""
        retrieval_results = [
            {"score": 0.55, "source_type": "unknown", "fiscal_period": "2024-Q4", "numerical_claim": "100B"},
            {"score": 0.52, "source_type": "unknown", "fiscal_period": "2024-Q3", "numerical_claim": "95B"},
            {"score": 0.48, "source_type": "unknown", "fiscal_period": "2023-Q4", "numerical_claim": "90B"}
        ]

        score = compute_confidence_score(retrieval_results)

        assert score.overall_score < 0.70, f"Expected LOW confidence, got {score.overall_score:.2f}"
        assert score.threshold_category in ["LOW", "VERY_LOW"]
        assert score.retrieval_quality < 0.60
        assert score.temporal_consistency < 0.50  # Different periods

    def test_empty_retrieval_results(self):
        """Test handling of empty retrieval results."""
        score = compute_confidence_score([])

        assert score.overall_score == 0.0
        assert score.threshold_category == "VERY_LOW"
        assert score.retrieval_quality == 0.0

    def test_domain_relevance_bonus(self):
        """Test that financial keywords boost confidence."""
        retrieval_results = [
            {"score": 0.80, "source_type": "10-K", "fiscal_period": "2024-Q4"}
        ]

        query_with_keywords = "What was the revenue in the 10-K SEC filing?"
        query_without_keywords = "What was it?"

        score_with = compute_confidence_score(retrieval_results, query_with_keywords)
        score_without = compute_confidence_score(retrieval_results, query_without_keywords)

        # With keywords should have slightly higher score (bonus)
        assert score_with.domain_relevance_bonus > 0
        assert score_with.overall_score >= score_without.overall_score

    def test_confidence_thresholds(self):
        """Test that threshold categorization is correct."""
        scorer = ConfidenceScorer()

        assert scorer._categorize_confidence(0.95) == "HIGH"
        assert scorer._categorize_confidence(0.85) == "HIGH"
        assert scorer._categorize_confidence(0.78) == "MEDIUM"
        assert scorer._categorize_confidence(0.70) == "MEDIUM"
        assert scorer._categorize_confidence(0.60) == "LOW"
        assert scorer._categorize_confidence(0.50) == "LOW"
        assert scorer._categorize_confidence(0.40) == "VERY_LOW"


# ============================================================================
# COMPLIANCE GUARDRAILS TESTS
# ============================================================================

class TestComplianceGuardrails:
    """Test suite for regulatory compliance guardrails."""

    def test_ria_guardrail_blocks_high_risk(self):
        """Test that RIA guardrail blocks high-risk queries."""
        guardrails = ComplianceGuardrails()

        # Create HIGH risk classification
        classification = RiskClassificationResult(
            risk_level=RiskLevel.HIGH,
            confidence=0.95,
            reasoning="Investment advice detected",
            regulatory_concern="Investment Advisers Act of 1940",
            system_action=SystemAction.ESCALATE_TO_HUMAN_ADVISOR,
            pattern_matches=["should.*buy"],
            user_context_adjusted=False
        )

        result = guardrails.check_ria_compliance(classification)

        assert result["compliant"] is False
        assert result["violation"] == "UNAUTHORIZED_INVESTMENT_ADVICE"
        assert "Investment Advisers Act" in result["regulation"]
        assert result["required_action"] == "ESCALATE_TO_RIA"

    def test_ria_guardrail_allows_low_risk(self):
        """Test that RIA guardrail allows low/medium risk queries."""
        guardrails = ComplianceGuardrails()

        for risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            classification = RiskClassificationResult(
                risk_level=risk_level,
                confidence=0.90,
                reasoning="Educational query",
                system_action=SystemAction.ANSWER_NORMALLY,
                pattern_matches=[],
                user_context_adjusted=False
            )

            result = guardrails.check_ria_compliance(classification)
            assert result["compliant"] is True

    def test_mnpi_guardrail_blocks_early_document(self):
        """Test that MNPI guardrail blocks documents predating public disclosure."""
        guardrails = ComplianceGuardrails()

        # Document created before public disclosure (MNPI violation)
        documents = [
            {
                "document_timestamp": datetime(2024, 10, 1),
                "public_disclosure_date": datetime(2024, 10, 5)  # Disclosed later
            }
        ]

        result = guardrails.check_mnpi_disclosure(documents)

        assert result["compliant"] is False
        assert result["violation"] == "MATERIAL_NON_PUBLIC_INFORMATION"
        assert "Reg FD" in result["regulation"]
        assert result["required_action"] == "BLOCK_DOCUMENT"

    def test_mnpi_guardrail_allows_public_documents(self):
        """Test that MNPI guardrail allows properly disclosed documents."""
        guardrails = ComplianceGuardrails()

        documents = [
            {
                "document_timestamp": datetime(2024, 10, 5),
                "public_disclosure_date": datetime(2024, 10, 5)  # Same day = OK
            },
            {
                "document_timestamp": datetime(2024, 10, 6),
                "public_disclosure_date": datetime(2024, 10, 5)  # After disclosure = OK
            }
        ]

        result = guardrails.check_mnpi_disclosure(documents)
        assert result["compliant"] is True

    def test_safe_harbor_injection(self):
        """Test that Safe Harbor warnings are injected for forward-looking statements."""
        guardrails = ComplianceGuardrails()

        response = "Apple expects revenue to grow 15% next quarter."

        # Should inject Safe Harbor warning
        enhanced = guardrails.inject_safe_harbor_warning(response, contains_forward_looking=True)

        assert "FORWARD-LOOKING STATEMENT DISCLAIMER" in enhanced
        assert "risks and uncertainties" in enhanced
        assert response in enhanced  # Original response preserved

    def test_safe_harbor_not_injected_for_factual(self):
        """Test that Safe Harbor warnings are NOT injected for factual statements."""
        guardrails = ComplianceGuardrails()

        response = "Apple's Q4 2024 revenue was $94.9B."

        enhanced = guardrails.inject_safe_harbor_warning(response, contains_forward_looking=False)

        assert enhanced == response  # No modification
        assert "FORWARD-LOOKING" not in enhanced

    def test_form_8k_validation_late_filing(self):
        """Test that late Form 8-K filings are flagged."""
        guardrails = ComplianceGuardrails()

        # Material event filed 10 days late (max 4 business days)
        filing_date = datetime.now() - timedelta(days=10)

        result = guardrails.validate_form_8k_disclosure("ceo_resignation", filing_date)

        assert result["compliant"] is False
        assert result["violation"] == "LATE_8K_DISCLOSURE"
        assert "Rule 8-K" in result["regulation"]

    def test_form_8k_validation_timely_filing(self):
        """Test that timely Form 8-K filings pass validation."""
        guardrails = ComplianceGuardrails()

        # Filed 2 days ago (within 4-day window)
        filing_date = datetime.now() - timedelta(days=2)

        result = guardrails.validate_form_8k_disclosure("major_acquisition", filing_date)
        assert result["compliant"] is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """End-to-end integration tests."""

    def test_full_pipeline_high_risk_query(self):
        """Test complete pipeline for high-risk query."""
        query = "Should I invest in Tesla stock right now?"

        # Step 1: Classify risk
        classification = classify_query_risk(query, user_context={"account_type": "retail"})

        assert classification.risk_level == RiskLevel.HIGH
        assert classification.system_action == SystemAction.ESCALATE_TO_HUMAN_ADVISOR

        # Step 2: Check compliance
        guardrails = ComplianceGuardrails()
        compliance = guardrails.check_ria_compliance(classification)

        assert compliance["compliant"] is False
        assert compliance["required_action"] == "ESCALATE_TO_RIA"

    def test_full_pipeline_low_risk_query(self):
        """Test complete pipeline for low-risk query with good retrieval."""
        query = "What was Apple's Q4 2024 revenue?"

        # Step 1: Classify risk
        classification = classify_query_risk(query)

        assert classification.risk_level == RiskLevel.LOW
        assert classification.system_action == SystemAction.ANSWER_NORMALLY

        # Step 2: Compute confidence
        retrieval_results = [
            {"score": 0.92, "source_type": "10-K", "fiscal_period": "2024-Q4", "numerical_claim": "94.9B"},
            {"score": 0.89, "source_type": "8-K", "fiscal_period": "2024-Q4", "numerical_claim": "94.9B"}
        ]

        confidence = compute_confidence_score(retrieval_results, query)

        assert confidence.overall_score >= 0.70
        assert confidence.threshold_category in ["MEDIUM", "HIGH"]

        # Step 3: Check compliance
        guardrails = ComplianceGuardrails()
        compliance = guardrails.check_ria_compliance(classification)

        assert compliance["compliant"] is True


# ============================================================================
# EDGE CASES AND ADVERSARIAL TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and adversarial inputs."""

    def test_empty_query(self):
        """Test handling of empty query."""
        # Should not crash
        result = classify_query_risk("")
        assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]

    def test_very_long_query(self):
        """Test handling of extremely long query."""
        long_query = "What is EBITDA? " * 1000

        result = classify_query_risk(long_query)
        assert result.risk_level == RiskLevel.LOW  # Educational pattern
        assert result.confidence > 0

    def test_special_characters_query(self):
        """Test query with special characters."""
        query = "What's Apple's Q4 revenue? (10-K filing)"

        result = classify_query_risk(query)
        assert result.risk_level == RiskLevel.LOW

    def test_adversarial_query_obfuscation(self):
        """Test that obfuscated advice queries are still caught."""
        # Trying to hide "should I buy" with extra words
        query = "In your opinion, considering all factors, should I perhaps buy Tesla?"

        result = classify_query_risk(query)
        assert result.risk_level == RiskLevel.HIGH, "Should catch obfuscated advice"


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
