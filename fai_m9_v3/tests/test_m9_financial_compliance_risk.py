"""
Tests for L3 M9.3: Regulatory Constraints in LLM Outputs
"""

import pytest
from src.l3_m9_financial_compliance_risk import (
    MNPIDetector,
    DisclaimerManager,
    InformationBarrier,
    ComplianceFilter,
    ViolationType,
    filter_llm_output
)


# ============================================================================
# MNPI Detection Tests
# ============================================================================

class TestMNPIDetector:
    """Test suite for MNPI detection functionality"""

    def test_source_validation_internal_document(self):
        """Test detection of internal source patterns"""
        detector = MNPIDetector()

        text = "According to the confidential board minutes..."
        citations = [
            {"source_type": "internal memo", "source_id": "board_2024_01"}
        ]

        is_internal, confidence = detector.validate_source(text, citations)

        assert is_internal is True
        assert confidence > 0.5

    def test_source_validation_public_document(self):
        """Test that public sources pass validation"""
        detector = MNPIDetector()

        text = "According to the 10-Q filing..."
        citations = [
            {"source_type": "10-Q", "source_id": "sec_filing_2024"}
        ]

        is_internal, confidence = detector.validate_source(text, citations)

        assert is_internal is False
        assert confidence <= 0.5

    def test_materiality_indicators_earnings(self):
        """Test detection of earnings-related material indicators"""
        detector = MNPIDetector()

        text = "Q4 earnings are projected at $3.5 billion with EPS of $2.10"

        indicators, confidence = detector.detect_materiality_indicators(text)

        assert "earnings" in indicators
        assert confidence > 0.3  # HIGH severity = 0.4

    def test_materiality_indicators_merger(self):
        """Test detection of M&A material indicators"""
        detector = MNPIDetector()

        text = "The company is acquiring TechCorp in a deal valued at $500M"

        indicators, confidence = detector.detect_materiality_indicators(text)

        assert "merger_acquisition" in indicators
        assert confidence > 0.3

    def test_materiality_indicators_executive_change(self):
        """Test detection of executive change indicators"""
        detector = MNPIDetector()

        text = "CEO resignation expected next quarter"

        indicators, confidence = detector.detect_materiality_indicators(text)

        assert "executive_change" in indicators
        assert confidence > 0.2  # MEDIUM severity

    def test_temporal_check_forward_looking(self):
        """Test detection of undisclosed forward-looking statements"""
        detector = MNPIDetector()

        text = "Q4 2024 revenue will exceed $5 billion"
        citations = []

        is_undisclosed, confidence = detector.check_temporal_disclosure(text, citations)

        assert is_undisclosed is True
        assert confidence > 0.7

    def test_temporal_check_no_forward_looking(self):
        """Test that historical statements don't trigger temporal check"""
        detector = MNPIDetector()

        text = "Q3 2023 revenue was $4.5 billion"
        citations = []

        is_undisclosed, confidence = detector.check_temporal_disclosure(text, citations)

        assert is_undisclosed is False
        assert confidence == 0.0

    def test_mnpi_detection_violation_multi_layer(self):
        """Test MNPI detection with multiple layers flagged"""
        detector = MNPIDetector()

        text = "Based on internal forecasts, Q4 earnings will be $3B"
        citations = [
            {"source_type": "internal forecast", "source_id": "budget_2024"}
        ]

        result = detector.detect(text, citations)

        assert result["is_violation"] is True
        assert result["layers_flagged"] >= 2
        assert result["confidence"] > 0.5

    def test_mnpi_detection_no_violation_public_info(self):
        """Test that public information doesn't trigger MNPI violation"""
        detector = MNPIDetector()

        text = "Q3 earnings were $2.5B according to the 10-Q filing"
        citations = [
            {"source_type": "10-Q", "source_id": "sec_20231115"}
        ]

        result = detector.detect(text, citations)

        assert result["is_violation"] is False

    def test_mnpi_detection_high_confidence_violation(self):
        """Test that single high-confidence violation triggers blocking"""
        detector = MNPIDetector(detection_threshold=0.85)

        # Strong MNPI signal: internal source + material indicator
        text = "Confidential: Merger announcement next week, deal value $2B"
        citations = [
            {"source_type": "confidential memo", "source_id": "exec_2024"}
        ]

        result = detector.detect(text, citations)

        assert result["is_violation"] is True
        assert result["confidence"] >= 0.85


# ============================================================================
# Disclaimer Manager Tests
# ============================================================================

class TestDisclaimerManager:
    """Test suite for disclaimer injection functionality"""

    def test_investment_advice_pattern_detection(self):
        """Test detection of investment advice patterns"""
        manager = DisclaimerManager()

        text = "We recommend buying XYZ stock at current prices"

        requires_disclaimer = manager.requires_investment_disclaimer(text)

        assert requires_disclaimer is True

    def test_forward_looking_pattern_detection(self):
        """Test detection of forward-looking statement patterns"""
        manager = DisclaimerManager()

        text = "The company expects revenue growth of 20% next year"

        requires_disclaimer = manager.requires_forward_looking_disclaimer(text)

        assert requires_disclaimer is True

    def test_add_investment_disclaimer(self):
        """Test injection of investment advice disclaimer"""
        manager = DisclaimerManager()

        text = "This stock is undervalued and should be purchased"

        filtered_text, added = manager.add_disclaimers(text)

        assert "investment_advice" in added
        assert "FINRA Rule 2210" in filtered_text
        assert "Not Investment Advice" in filtered_text or "educational purposes" in filtered_text

    def test_add_forward_looking_disclaimer(self):
        """Test injection of Safe Harbor disclaimer"""
        manager = DisclaimerManager()

        text = "Q4 earnings will likely exceed analyst expectations"

        filtered_text, added = manager.add_disclaimers(text)

        assert "forward_looking" in added
        assert "SAFE HARBOR" in filtered_text
        assert "Private Securities Litigation Reform Act" in filtered_text

    def test_add_multiple_disclaimers(self):
        """Test that both disclaimers can be added"""
        manager = DisclaimerManager()

        text = "We recommend buying this stock. The company will grow 30% next year."

        filtered_text, added = manager.add_disclaimers(text)

        assert "investment_advice" in added
        assert "forward_looking" in added
        assert len(added) == 2

    def test_general_disclaimer_fallback(self):
        """Test that general disclaimer is added when no specific patterns match"""
        manager = DisclaimerManager()

        text = "Historical stock prices from 2020-2023"

        filtered_text, added = manager.add_disclaimers(text)

        assert "general" in added
        assert "DISCLAIMER" in filtered_text


# ============================================================================
# Information Barrier Tests
# ============================================================================

class TestInformationBarrier:
    """Test suite for information barrier (Chinese Walls) functionality"""

    def test_public_access_always_allowed(self):
        """Test that public data is always accessible"""
        barrier = InformationBarrier()

        has_access = barrier.check_access("any_user", "public")

        assert has_access is True

    def test_restricted_access_denied_without_permission(self):
        """Test that restricted data is blocked without permission"""
        permissions = {
            "analyst_external": ["public"]
        }
        barrier = InformationBarrier(user_permissions=permissions)

        has_access = barrier.check_access("analyst_external", "internal")

        assert has_access is False

    def test_restricted_access_granted_with_permission(self):
        """Test that authorized users can access restricted data"""
        permissions = {
            "analyst_internal": ["public", "internal", "restricted"]
        }
        barrier = InformationBarrier(user_permissions=permissions)

        has_access = barrier.check_access("analyst_internal", "restricted")

        assert has_access is True

    def test_filter_citations_by_permission(self):
        """Test citation filtering based on user permissions"""
        permissions = {
            "analyst_external": ["public"]
        }
        barrier = InformationBarrier(user_permissions=permissions)

        citations = [
            {"source_id": "public_1", "data_namespace": "public"},
            {"source_id": "internal_1", "data_namespace": "internal"},
            {"source_id": "public_2", "data_namespace": "public"}
        ]

        filtered = barrier.filter_citations(citations, "analyst_external")

        assert len(filtered) == 2
        assert all(c["data_namespace"] == "public" for c in filtered)

    def test_default_permissions_public_only(self):
        """Test that users without explicit permissions default to public access"""
        barrier = InformationBarrier()

        has_access_public = barrier.check_access("unknown_user", "public")
        has_access_internal = barrier.check_access("unknown_user", "internal")

        assert has_access_public is True
        assert has_access_internal is False


# ============================================================================
# Compliance Filter Integration Tests
# ============================================================================

class TestComplianceFilter:
    """Test suite for complete compliance filtering pipeline"""

    def test_compliance_filter_blocks_mnpi(self):
        """Test that MNPI violations result in blocked responses"""
        compliance = ComplianceFilter()

        result = compliance.filter_output(
            llm_output="Based on internal forecasts, Q4 earnings will be $3B",
            citations=[
                {"source_type": "internal forecast", "source_id": "budget_2024"}
            ],
            user_id="analyst_123"
        )

        assert result["allowed"] is False
        assert result["blocked_reason"] == "MNPI_VIOLATION"
        assert result["audit_logged"] is True

    def test_compliance_filter_allows_public_info(self):
        """Test that public information passes compliance checks"""
        compliance = ComplianceFilter()

        result = compliance.filter_output(
            llm_output="Q3 earnings were $2.5B according to SEC filings",
            citations=[
                {"source_type": "10-Q", "source_id": "sec_20231115", "data_namespace": "public"}
            ],
            user_id="analyst_123"
        )

        assert result["allowed"] is True
        assert result["filtered_text"] is not None
        assert len(result["disclaimers_added"]) > 0

    def test_compliance_filter_adds_disclaimers(self):
        """Test that appropriate disclaimers are added to allowed responses"""
        compliance = ComplianceFilter()

        result = compliance.filter_output(
            llm_output="This stock may be a good investment opportunity",
            citations=[
                {"source_type": "market analysis", "source_id": "report_2024", "data_namespace": "public"}
            ],
            user_id="investor_456"
        )

        assert result["allowed"] is True
        assert "investment_advice" in result["disclaimers_added"]

    def test_compliance_filter_citation_filtering(self):
        """Test that citations are filtered by information barriers"""
        permissions = {
            "analyst_external": ["public"]
        }
        compliance = ComplianceFilter(
            information_barrier=InformationBarrier(user_permissions=permissions)
        )

        citations = [
            {"source_id": "pub_1", "data_namespace": "public"},
            {"source_id": "int_1", "data_namespace": "internal"}
        ]

        result = compliance.filter_output(
            llm_output="General market commentary",
            citations=citations,
            user_id="analyst_external"
        )

        assert result["citations_filtered"] == 1

    def test_compliance_audit_logging(self):
        """Test that violations are logged to audit trail"""
        compliance = ComplianceFilter(enable_audit_logging=True)

        # Trigger MNPI violation
        compliance.filter_output(
            llm_output="Confidential merger plans",
            citations=[
                {"source_type": "confidential", "source_id": "board_minutes"}
            ],
            user_id="user_789"
        )

        # Check audit log
        logs = compliance.get_audit_log()

        assert len(logs) > 0
        assert logs[-1]["user_id"] == "user_789"
        assert logs[-1]["violation_type"] == ViolationType.MNPI.value

    def test_compliance_audit_log_filtering(self):
        """Test audit log retrieval filtered by user"""
        compliance = ComplianceFilter(enable_audit_logging=True)

        # Create violations for different users
        compliance.filter_output(
            "MNPI content",
            [{"source_type": "internal"}],
            "user_A"
        )
        compliance.filter_output(
            "MNPI content",
            [{"source_type": "internal"}],
            "user_B"
        )

        # Filter logs
        user_a_logs = compliance.get_audit_log(user_id="user_A")

        assert len(user_a_logs) == 1
        assert user_a_logs[0]["user_id"] == "user_A"


# ============================================================================
# Convenience Function Tests
# ============================================================================

class TestConvenienceFunction:
    """Test suite for filter_llm_output convenience function"""

    def test_filter_llm_output_basic(self):
        """Test basic filtering with convenience function"""
        result = filter_llm_output(
            llm_output="Q3 earnings were $2.5B",
            citations=[
                {"source_type": "10-Q", "source_id": "sec_filing"}
            ]
        )

        assert "allowed" in result
        assert "filtered_text" in result

    def test_filter_llm_output_with_risk_score(self):
        """Test filtering with risk score from M9.2"""
        result = filter_llm_output(
            llm_output="Market analysis commentary",
            citations=[],
            user_id="analyst_001",
            risk_score=0.65
        )

        assert result["allowed"] is not None


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and error handling"""

    def test_empty_citations(self):
        """Test handling of empty citation list"""
        detector = MNPIDetector()

        result = detector.detect("Some text", citations=[])

        # Should not crash
        assert "is_violation" in result

    def test_null_metadata_fields(self):
        """Test handling of null/missing metadata fields"""
        detector = MNPIDetector()

        citations = [
            {"source_type": None, "source_id": "test"}
        ]

        # Should not crash
        is_internal, confidence = detector.validate_source("text", citations)

        assert isinstance(is_internal, bool)

    def test_threshold_boundary_conditions(self):
        """Test threshold at exact boundary values"""
        detector_low = MNPIDetector(detection_threshold=0.0)
        detector_high = MNPIDetector(detection_threshold=1.0)

        text = "Test text"
        citations = []

        result_low = detector_low.detect(text, citations)
        result_high = detector_high.detect(text, citations)

        # Should handle extreme thresholds without errors
        assert "is_violation" in result_low
        assert "is_violation" in result_high

    def test_very_long_text(self):
        """Test handling of very long text inputs"""
        manager = DisclaimerManager()

        long_text = "A" * 10000 + " recommend buying stock"

        filtered, added = manager.add_disclaimers(long_text)

        # Should handle long text without performance issues
        assert len(filtered) > len(long_text)
        assert "investment_advice" in added


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
