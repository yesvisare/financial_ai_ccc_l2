"""
Tests for L3 M7.1: Financial Document Types & Regulatory Context

Comprehensive test suite covering:
- Document classification
- Regulatory mapping
- Sensitivity classification
- Retention policies
- PII detection
- Access control
- Material event detection
"""

import pytest
from datetime import datetime, timedelta

from src.l3_m7_financial_compliance_controls import (
    DocumentType,
    SensitivityLevel,
    RegulatoryFramework,
    DocumentClassifier,
    RegulatoryMapper,
    SensitivityClassifier,
    RetentionPolicyManager,
    PIIDetector,
    AuditLogger,
    AccessController,
    MaterialEventDetector,
    classify_document,
    get_retention_period,
    detect_pii,
    check_access_control,
)


# Document Classification Tests

def test_document_classifier_initialization():
    """Test document classifier initialization."""
    classifier = DocumentClassifier(offline=True)
    assert classifier.offline is True


def test_classify_10k_annual_report():
    """Test classification of 10-K annual report."""
    classifier = DocumentClassifier(offline=True)
    doc_text = """
    FORM 10-K
    ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934
    For the fiscal year ended December 31, 2023
    """
    result = classifier.classify(doc_text)
    assert result == DocumentType.FORM_10K


def test_classify_10q_quarterly_report():
    """Test classification of 10-Q quarterly report."""
    classifier = DocumentClassifier(offline=True)
    doc_text = """
    FORM 10-Q
    QUARTERLY REPORT PURSUANT TO SECTION 13 OR 15(d)
    For the quarterly period ended March 31, 2024
    (Unaudited)
    """
    result = classifier.classify(doc_text)
    assert result == DocumentType.FORM_10Q


def test_classify_8k_material_event():
    """Test classification of 8-K material event disclosure."""
    classifier = DocumentClassifier(offline=True)
    doc_text = """
    FORM 8-K
    CURRENT REPORT
    Date of Report (Date of earliest event reported): January 15, 2024
    Item 1.01 Entry into a Material Definitive Agreement
    """
    result = classifier.classify(doc_text)
    assert result == DocumentType.FORM_8K


def test_classify_earnings_transcript():
    """Test classification of earnings call transcript."""
    classifier = DocumentClassifier(offline=True)
    doc_text = """
    Q4 2023 Earnings Call Transcript
    Operator: Good morning and welcome to the fourth quarter earnings conference call.
    CFO: Thank you for joining us today for our prepared remarks and Q&A session.
    Analyst: Can you provide guidance for Q1 2024?
    """
    result = classifier.classify(doc_text)
    assert result == DocumentType.EARNINGS_TRANSCRIPT


def test_classify_credit_report():
    """Test classification of credit report."""
    classifier = DocumentClassifier(offline=True)
    doc_text = """
    CREDIT REPORT
    Credit Score: 720 (FICO)
    SSN: XXX-XX-1234
    Payment History: Current
    Accounts: Checking, Savings, Credit Card
    Source: Equifax
    """
    result = classifier.classify(doc_text)
    assert result == DocumentType.CREDIT_REPORT


def test_classify_loan_application():
    """Test classification of loan application."""
    classifier = DocumentClassifier(offline=True)
    doc_text = """
    MORTGAGE LOAN APPLICATION
    Income Verification: $85,000 annual
    Employment History: 5 years at current employer
    Debt-to-Income Ratio: 28%
    """
    result = classifier.classify(doc_text)
    assert result == DocumentType.LOAN_APPLICATION


def test_classify_internal_analysis():
    """Test classification of internal financial analysis."""
    classifier = DocumentClassifier(offline=True)
    doc_text = """
    INTERNAL USE ONLY - CONFIDENTIAL
    M&A Target Analysis - Budget Forecast
    Investment Committee Memo
    Variance Analysis Q3 2023
    """
    result = classifier.classify(doc_text)
    assert result == DocumentType.INTERNAL_ANALYSIS


def test_classify_prospectus():
    """Test classification of investment prospectus."""
    classifier = DocumentClassifier(offline=True)
    doc_text = """
    PROSPECTUS
    Offering Memorandum pursuant to the Securities Act of 1933
    Investment Objectives and Strategies
    Risk Factors
    """
    result = classifier.classify(doc_text)
    assert result == DocumentType.PROSPECTUS


def test_classify_unknown_document():
    """Test classification of unknown document type."""
    classifier = DocumentClassifier(offline=True)
    result = classifier.classify("Random text with no identifiable markers")
    assert result == DocumentType.UNKNOWN


def test_classify_empty_document():
    """Test classification of empty document."""
    classifier = DocumentClassifier(offline=True)
    result = classifier.classify("")
    assert result == DocumentType.UNKNOWN


# Regulatory Mapping Tests

def test_regulatory_mapper_initialization():
    """Test regulatory mapper initialization."""
    mapper = RegulatoryMapper()
    assert mapper is not None


def test_map_10k_regulations():
    """Test regulatory mapping for 10-K."""
    mapper = RegulatoryMapper()
    regulations = mapper.get_applicable_regulations(DocumentType.FORM_10K)
    assert RegulatoryFramework.SOX_302 in regulations
    assert RegulatoryFramework.SOX_404 in regulations


def test_map_credit_report_regulations():
    """Test regulatory mapping for credit reports."""
    mapper = RegulatoryMapper()
    regulations = mapper.get_applicable_regulations(DocumentType.CREDIT_REPORT)
    assert RegulatoryFramework.FCRA in regulations
    assert RegulatoryFramework.GLBA in regulations
    assert RegulatoryFramework.GDPR_ARTICLE_25 in regulations


def test_map_earnings_transcript_regulations():
    """Test regulatory mapping for earnings transcripts."""
    mapper = RegulatoryMapper()
    regulations = mapper.get_applicable_regulations(DocumentType.EARNINGS_TRANSCRIPT)
    assert RegulatoryFramework.REG_FD in regulations


def test_compliance_summary_10k():
    """Test compliance summary for 10-K."""
    mapper = RegulatoryMapper()
    summary = mapper.get_compliance_summary(DocumentType.FORM_10K)
    assert summary["requires_cfo_approval"] is True
    assert summary["requires_external_audit"] is True


def test_compliance_summary_prospectus():
    """Test compliance summary for prospectus."""
    mapper = RegulatoryMapper()
    summary = mapper.get_compliance_summary(DocumentType.PROSPECTUS)
    assert summary["requires_legal_review"] is True


# Sensitivity Classification Tests

def test_sensitivity_classifier_initialization():
    """Test sensitivity classifier initialization."""
    classifier = SensitivityClassifier()
    assert classifier is not None


def test_classify_credit_report_sensitivity():
    """Test sensitivity classification for credit report (always PII)."""
    classifier = SensitivityClassifier()
    sensitivity = classifier.classify_sensitivity(DocumentType.CREDIT_REPORT, is_filed=False)
    assert sensitivity == SensitivityLevel.PII


def test_classify_10k_unfiled_sensitivity():
    """Test sensitivity classification for unfiled 10-K (MNPI)."""
    classifier = SensitivityClassifier()
    sensitivity = classifier.classify_sensitivity(DocumentType.FORM_10K, is_filed=False)
    assert sensitivity == SensitivityLevel.MNPI


def test_classify_10k_filed_sensitivity():
    """Test sensitivity classification for filed 10-K (Public)."""
    classifier = SensitivityClassifier()
    sensitivity = classifier.classify_sensitivity(DocumentType.FORM_10K, is_filed=True)
    assert sensitivity == SensitivityLevel.PUBLIC


def test_classify_internal_analysis_sensitivity():
    """Test sensitivity classification for internal analysis (always MNPI)."""
    classifier = SensitivityClassifier()
    sensitivity = classifier.classify_sensitivity(DocumentType.INTERNAL_ANALYSIS, is_filed=False)
    assert sensitivity == SensitivityLevel.MNPI


def test_classify_earnings_transcript_sensitivity():
    """Test sensitivity classification for earnings transcript."""
    classifier = SensitivityClassifier()
    # During call (MNPI)
    sensitivity_during = classifier.classify_sensitivity(DocumentType.EARNINGS_TRANSCRIPT, is_filed=False)
    assert sensitivity_during == SensitivityLevel.MNPI

    # After call (Public)
    sensitivity_after = classifier.classify_sensitivity(DocumentType.EARNINGS_TRANSCRIPT, is_filed=True)
    assert sensitivity_after == SensitivityLevel.PUBLIC


# Retention Policy Tests

def test_retention_policy_manager_initialization():
    """Test retention policy manager initialization."""
    manager = RetentionPolicyManager()
    assert manager is not None


def test_retention_period_10k():
    """Test retention period for 10-K (7 years)."""
    manager = RetentionPolicyManager()
    period = manager.get_retention_period(DocumentType.FORM_10K)
    assert period == 7


def test_retention_period_prospectus():
    """Test retention period for prospectus (permanent)."""
    manager = RetentionPolicyManager()
    period = manager.get_retention_period(DocumentType.PROSPECTUS)
    assert period is None


def test_retention_period_loan_application():
    """Test retention period for loan application (3 years)."""
    manager = RetentionPolicyManager()
    period = manager.get_retention_period(DocumentType.LOAN_APPLICATION)
    assert period == 3


def test_calculate_deletion_date():
    """Test deletion date calculation."""
    manager = RetentionPolicyManager()
    creation_date = datetime(2020, 1, 1)
    deletion_date = manager.calculate_deletion_date(DocumentType.FORM_10K, creation_date)

    # Should be 7 years later
    expected_date = creation_date + timedelta(days=7*365)
    assert deletion_date == expected_date


def test_calculate_deletion_date_permanent():
    """Test deletion date calculation for permanent retention."""
    manager = RetentionPolicyManager()
    creation_date = datetime(2020, 1, 1)
    deletion_date = manager.calculate_deletion_date(DocumentType.PROSPECTUS, creation_date)

    # Should be None for permanent retention
    assert deletion_date is None


# PII Detection Tests

def test_pii_detector_initialization():
    """Test PII detector initialization."""
    detector = PIIDetector()
    assert detector.recall_threshold == 0.999


def test_detect_ssn():
    """Test SSN detection."""
    detector = PIIDetector()
    text = "Customer SSN: 123-45-6789"
    detections = detector.detect_pii(text)

    assert len(detections) == 1
    assert detections[0]["type"] == "SSN"
    assert detections[0]["severity"] == "CRITICAL"


def test_detect_phone():
    """Test phone number detection."""
    detector = PIIDetector()
    text = "Contact: 555-123-4567"
    detections = detector.detect_pii(text)

    assert len(detections) == 1
    assert detections[0]["type"] == "PHONE"


def test_detect_email():
    """Test email address detection."""
    detector = PIIDetector()
    text = "Email: john.doe@example.com"
    detections = detector.detect_pii(text)

    assert len(detections) == 1
    assert detections[0]["type"] == "EMAIL"


def test_detect_multiple_pii():
    """Test detection of multiple PII types."""
    detector = PIIDetector()
    text = """
    Customer Information:
    SSN: 123-45-6789
    Phone: 555-123-4567
    Email: customer@example.com
    """
    detections = detector.detect_pii(text)

    assert len(detections) == 3
    types = {d["type"] for d in detections}
    assert types == {"SSN", "PHONE", "EMAIL"}


def test_redact_pii():
    """Test PII redaction."""
    detector = PIIDetector()
    text = "Customer SSN: 123-45-6789 and email: test@example.com"
    redacted_text, detections = detector.redact_pii(text)

    assert "[REDACTED_SSN]" in redacted_text
    assert "[REDACTED_EMAIL]" in redacted_text
    assert "123-45-6789" not in redacted_text
    assert "test@example.com" not in redacted_text
    assert len(detections) == 2


# Audit Logger Tests

def test_audit_logger_initialization():
    """Test audit logger initialization."""
    logger = AuditLogger()
    assert logger.audit_log == []


def test_log_access():
    """Test logging document access."""
    logger = AuditLogger()
    entry = logger.log_access(
        user_id="user123",
        doc_type=DocumentType.FORM_10K,
        action="view",
        doc_id="doc456"
    )

    assert entry["user_id"] == "user123"
    assert entry["document_type"] == DocumentType.FORM_10K.value
    assert entry["action"] == "view"
    assert entry["doc_id"] == "doc456"


def test_get_audit_trail():
    """Test retrieving audit trail."""
    logger = AuditLogger()

    logger.log_access("user1", DocumentType.FORM_10K, "view", "doc1")
    logger.log_access("user2", DocumentType.FORM_10Q, "edit", "doc2")
    logger.log_access("user1", DocumentType.FORM_8K, "download", "doc3")

    # Get all for user1
    trail = logger.get_audit_trail(user_id="user1")
    assert len(trail) == 2

    # Get all for doc2
    trail = logger.get_audit_trail(doc_id="doc2")
    assert len(trail) == 1


# Access Control Tests

def test_access_controller_initialization():
    """Test access controller initialization."""
    controller = AccessController()
    assert controller is not None


def test_executive_access_mnpi():
    """Test executive access to MNPI documents."""
    controller = AccessController()
    has_access = controller.check_access("executive", SensitivityLevel.MNPI)
    assert has_access is True


def test_executive_access_pii():
    """Test executive access to PII documents."""
    controller = AccessController()
    has_access = controller.check_access("executive", SensitivityLevel.PII)
    assert has_access is True


def test_analyst_no_access_pii():
    """Test analyst denied access to PII documents."""
    controller = AccessController()
    has_access = controller.check_access("analyst", SensitivityLevel.PII)
    assert has_access is False


def test_employee_access_public_only():
    """Test employee access to public documents only."""
    controller = AccessController()
    assert controller.check_access("employee", SensitivityLevel.PUBLIC) is True
    assert controller.check_access("employee", SensitivityLevel.MNPI) is False
    assert controller.check_access("employee", SensitivityLevel.PII) is False


def test_credit_officer_access_pii():
    """Test credit officer access to PII documents."""
    controller = AccessController()
    has_access = controller.check_access("credit_officer", SensitivityLevel.PII)
    assert has_access is True


def test_get_accessible_document_types():
    """Test getting accessible document types for role."""
    controller = AccessController()
    accessible = controller.get_accessible_document_types("analyst")

    # Analysts should have access to MNPI and Public documents
    assert len(accessible) > 0


# Material Event Detection Tests

def test_material_event_detector_initialization():
    """Test material event detector initialization."""
    detector = MaterialEventDetector()
    assert detector is not None


def test_detect_bankruptcy():
    """Test detection of bankruptcy event."""
    detector = MaterialEventDetector()
    text = "The company filed for Chapter 11 bankruptcy protection."
    events = detector.detect_material_events(text)

    assert len(events) > 0
    assert any(e["event_type"] == "CHAPTER_11" for e in events)
    assert all(e["requires_8k"] is True for e in events)


def test_detect_acquisition():
    """Test detection of acquisition event."""
    detector = MaterialEventDetector()
    text = "We are pleased to announce the acquisition of CompanyX."
    events = detector.detect_material_events(text)

    assert len(events) > 0
    assert any(e["event_type"] == "ACQUISITION" for e in events)


def test_detect_management_change():
    """Test detection of management change event."""
    detector = MaterialEventDetector()
    text = "The CEO has resigned effective immediately."
    events = detector.detect_material_events(text)

    assert len(events) > 0
    assert any("CEO" in e["event_type"] for e in events)


def test_no_material_events():
    """Test text with no material events."""
    detector = MaterialEventDetector()
    text = "The company continues normal operations."
    events = detector.detect_material_events(text)

    assert len(events) == 0


# Integration Tests

def test_classify_document_offline():
    """Test complete document classification in offline mode."""
    doc_text = """
    FORM 10-K
    ANNUAL REPORT
    For the fiscal year ended December 31, 2023
    """

    result = classify_document(doc_text, offline=True)

    assert result["document_type"] == DocumentType.FORM_10K.value
    assert result["offline_mode"] is True
    assert "retention_period_years" in result
    assert "regulatory_frameworks" in result


def test_get_retention_period_function():
    """Test convenience function for retention period."""
    period = get_retention_period(DocumentType.FORM_10K)
    assert period == 7


def test_detect_pii_function():
    """Test convenience function for PII detection."""
    redacted, detections = detect_pii("SSN: 123-45-6789")
    assert "[REDACTED_SSN]" in redacted
    assert len(detections) == 1


def test_check_access_control_function():
    """Test convenience function for access control."""
    has_access = check_access_control("executive", DocumentType.FORM_10K, is_filed=False)
    assert has_access is True

    has_access = check_access_control("employee", DocumentType.FORM_10K, is_filed=False)
    assert has_access is False


def test_classify_with_pii_detection():
    """Test document classification with PII detection."""
    doc_text = """
    CREDIT REPORT
    Credit Score: 720
    SSN: 123-45-6789
    Email: customer@example.com
    """

    result = classify_document(doc_text, offline=True)

    assert result["document_type"] == DocumentType.CREDIT_REPORT.value
    assert result["pii_detected"] is True
    assert result["pii_count"] > 0


def test_classify_with_material_events():
    """Test document classification with material event detection."""
    doc_text = """
    FORM 8-K
    CURRENT REPORT
    The company announces the acquisition of CompanyX for $500 million.
    """

    result = classify_document(doc_text, offline=True)

    assert result["document_type"] == DocumentType.FORM_8K.value
    assert result["material_events_detected"] is True
    assert result["requires_legal_review"] is True


# Error Handling Tests

def test_invalid_document_type_string():
    """Test handling of invalid document type string."""
    # This test ensures graceful handling of invalid input
    mapper = RegulatoryMapper()
    regulations = mapper.get_applicable_regulations(DocumentType.UNKNOWN)
    assert regulations == []


def test_pii_detector_custom_threshold():
    """Test PII detector with custom recall threshold."""
    detector = PIIDetector(recall_threshold=0.95)
    assert detector.recall_threshold == 0.95
