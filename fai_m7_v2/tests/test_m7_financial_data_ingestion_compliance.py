"""
Tests for M7.2: PII Detection & Financial Data Redaction

Test Coverage:
- Validation functions (Luhn, ABA checksum)
- Custom recognizers (Tax ID, Routing, Account)
- FinancialPIIRedactor class
- Audit trail functionality
- End-to-end redaction scenarios
"""

import pytest
from src.l3_m7_financial_data_ingestion_compliance import (
    validate_luhn,
    validate_aba_checksum,
    FinancialPIIRedactor,
    create_audit_entry,
    redact_document
)


# ============================================================================
# VALIDATION FUNCTION TESTS
# ============================================================================

class TestValidationFunctions:
    """Test validation algorithms."""

    def test_luhn_valid_cards(self):
        """Test Luhn algorithm with valid credit card numbers."""
        valid_cards = [
            "4111111111111111",  # Visa test card
            "5500000000000004",  # Mastercard test card
            "340000000000009",   # Amex test card
        ]
        for card in valid_cards:
            assert validate_luhn(card), f"Failed to validate {card}"

    def test_luhn_invalid_cards(self):
        """Test Luhn algorithm with invalid credit card numbers."""
        invalid_cards = [
            "4111111111111112",  # Wrong checksum
            "1234567890123456",  # Random digits
            "0000000000000000",  # All zeros
        ]
        for card in invalid_cards:
            assert not validate_luhn(card), f"Incorrectly validated {card}"

    def test_aba_valid_routing(self):
        """Test ABA checksum with valid routing numbers."""
        valid_routing = [
            "021000021",  # JPMorgan Chase
            "026009593",  # Bank of America
            "011401533",  # Wells Fargo
        ]
        for routing in valid_routing:
            assert validate_aba_checksum(routing), f"Failed to validate {routing}"

    def test_aba_invalid_routing(self):
        """Test ABA checksum with invalid routing numbers."""
        invalid_routing = [
            "123456789",  # Wrong checksum
            "000000000",  # All zeros
            "111111111",  # Repetitive
        ]
        for routing in invalid_routing:
            assert not validate_aba_checksum(routing), f"Incorrectly validated {routing}"


# ============================================================================
# AUDIT TRAIL TESTS
# ============================================================================

class TestAuditTrail:
    """Test audit trail functionality."""

    def test_create_audit_entry(self):
        """Test audit entry creation."""
        # Mock entity class
        class MockEntity:
            def __init__(self, entity_type):
                self.entity_type = entity_type

        entities = [
            MockEntity("SSN"),
            MockEntity("SSN"),
            MockEntity("CREDIT_CARD")
        ]

        audit = create_audit_entry(
            doc_id="TEST001",
            text="Test document",
            entities_detected=entities,
            user_id="test_user"
        )

        assert audit["doc_id"] == "TEST001"
        assert audit["user_id"] == "test_user"
        assert audit["entities_detected"] == 3
        assert audit["entity_breakdown"]["SSN"] == 2
        assert audit["entity_breakdown"]["CREDIT_CARD"] == 1
        assert "doc_hash" in audit
        assert "timestamp" in audit


# ============================================================================
# REDACTOR TESTS
# ============================================================================

class TestFinancialPIIRedactor:
    """Test FinancialPIIRedactor class."""

    @pytest.fixture
    def redactor(self):
        """Create redactor instance for testing."""
        return FinancialPIIRedactor(confidence_threshold=0.5)

    def test_redactor_initialization(self, redactor):
        """Test redactor initializes correctly."""
        assert redactor.confidence_threshold == 0.5
        assert isinstance(redactor.audit_trail, list)
        assert len(redactor.audit_trail) == 0

    def test_redact_ssn(self, redactor):
        """Test SSN redaction."""
        text = "The applicant's SSN is 123-45-6789."
        result = redactor.redact_document(text, doc_id="TEST_SSN")

        if result.get("error"):
            # Presidio not available - skip test
            pytest.skip("Presidio not available")

        assert "<SSN>" in result["redacted_text"] or "123-45-6789" not in result["redacted_text"]
        assert result["entities_redacted"] >= 0

    def test_redact_multiple_entities(self, redactor):
        """Test redaction of multiple PII types."""
        text = """
        Applicant Information:
        SSN: 123-45-6789
        Phone: 555-123-4567
        Email: john.doe@email.com
        Account: 98765432
        """
        result = redactor.redact_document(text, doc_id="TEST_MULTI", user_id="analyst")

        if result.get("error"):
            pytest.skip("Presidio not available")

        # Check audit trail was created
        assert len(redactor.audit_trail) > 0
        assert redactor.audit_trail[-1]["doc_id"] == "TEST_MULTI"
        assert redactor.audit_trail[-1]["user_id"] == "analyst"

    def test_get_audit_trail(self, redactor):
        """Test audit trail retrieval."""
        text1 = "SSN: 123-45-6789"
        text2 = "Account: 98765432"

        redactor.redact_document(text1, doc_id="DOC1")
        redactor.redact_document(text2, doc_id="DOC2")

        trail = redactor.get_audit_trail()

        if not trail:
            pytest.skip("Presidio not available")

        assert len(trail) == 2
        assert trail[0]["doc_id"] == "DOC1"
        assert trail[1]["doc_id"] == "DOC2"

    def test_export_audit_trail(self, redactor, tmp_path):
        """Test audit trail export to JSON."""
        text = "SSN: 123-45-6789"
        redactor.redact_document(text, doc_id="EXPORT_TEST")

        if not redactor.audit_trail:
            pytest.skip("Presidio not available")

        # Export to temporary file
        output_file = tmp_path / "audit_trail.json"
        redactor.export_audit_trail(str(output_file))

        # Verify file exists and contains data
        assert output_file.exists()

        import json
        with open(output_file) as f:
            data = json.load(f)

        assert len(data) > 0
        assert data[0]["doc_id"] == "EXPORT_TEST"


# ============================================================================
# CONVENIENCE FUNCTION TESTS
# ============================================================================

class TestConvenienceFunctions:
    """Test convenience wrapper functions."""

    def test_redact_document_function(self):
        """Test standalone redact_document function."""
        result = redact_document(
            text="SSN: 123-45-6789",
            doc_id="CONVENIENCE_TEST"
        )

        if result.get("error"):
            pytest.skip("Presidio not available")

        assert "redacted_text" in result
        assert "entities_redacted" in result
        assert "audit_id" in result


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEnd:
    """End-to-end integration tests."""

    def test_credit_report_redaction(self):
        """Test redaction of synthetic credit report."""
        credit_report = """
        CREDIT REPORT

        Personal Information:
        Name: John Smith
        SSN: 123-45-6789
        DOB: 01/15/1980
        Phone: 555-123-4567

        Credit Accounts:
        Account #: 4111-1111-1111-1111 (Visa)
        Account #: 9876543210 (Checking)

        Credit Score: 720
        """

        redactor = FinancialPIIRedactor()
        result = redactor.redact_document(credit_report, doc_id="CREDIT_001")

        if result.get("error"):
            pytest.skip("Presidio not available")

        # Verify sensitive data is redacted
        redacted = result["redacted_text"]
        assert "123-45-6789" not in redacted
        assert result["entities_redacted"] > 0

    def test_loan_application_redaction(self):
        """Test redaction of loan application."""
        loan_app = """
        LOAN APPLICATION

        Applicant: Jane Doe
        SSN: 987-65-4321
        Email: jane.doe@email.com

        Banking Information:
        Bank: ABC Bank
        Routing: 021000021
        Account: 1234567890

        Employment:
        Annual Salary: $85,000
        """

        redactor = FinancialPIIRedactor()
        result = redactor.redact_document(loan_app, doc_id="LOAN_001")

        if result.get("error"):
            pytest.skip("Presidio not available")

        # Verify multiple entity types detected
        assert result["entities_redacted"] > 0

        # Check audit trail
        assert len(redactor.audit_trail) == 1
        assert redactor.audit_trail[0]["doc_id"] == "LOAN_001"

    def test_batch_processing(self):
        """Test batch processing of multiple documents."""
        documents = [
            ("SSN: 123-45-6789", "DOC001"),
            ("Account: 98765432, Routing: 021000021", "DOC002"),
            ("Email: test@email.com, Phone: 555-1234", "DOC003"),
        ]

        redactor = FinancialPIIRedactor()
        results = []

        for text, doc_id in documents:
            result = redactor.redact_document(text, doc_id)
            results.append(result)

        if results[0].get("error"):
            pytest.skip("Presidio not available")

        # Verify all processed
        assert len(results) == 3

        # Verify audit trail contains all
        assert len(redactor.audit_trail) == 3


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_document(self):
        """Test redaction of empty document."""
        redactor = FinancialPIIRedactor()
        result = redactor.redact_document("", doc_id="EMPTY")

        if result.get("error"):
            pytest.skip("Presidio not available")

        assert result["entities_redacted"] == 0

    def test_no_pii_document(self):
        """Test document with no PII."""
        text = "This is a simple document with no sensitive information."
        redactor = FinancialPIIRedactor()
        result = redactor.redact_document(text, doc_id="NO_PII")

        if result.get("error"):
            pytest.skip("Presidio not available")

        assert result["entities_redacted"] == 0
        assert result["redacted_text"] == text

    def test_partially_redacted_input(self):
        """Test document that's already partially redacted."""
        text = "SSN: XXX-XX-6789"  # Partially masked
        redactor = FinancialPIIRedactor()
        result = redactor.redact_document(text, doc_id="PARTIAL")

        if result.get("error"):
            pytest.skip("Presidio not available")

        # Should handle gracefully
        assert "redacted_text" in result


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
