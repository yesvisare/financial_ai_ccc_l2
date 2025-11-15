"""
L3 M7.1: Financial Document Types & Regulatory Context

This module implements compliance-aware document classification systems for financial services,
covering 8+ financial document types with regulatory implications, mapping to compliance frameworks,
and managing document lifecycle workflows with retention policies and audit trails.

Core capabilities:
- Document type classification (10-K, 10-Q, 8-K, earnings transcripts, credit reports, etc.)
- Regulatory framework mapping (SOX, Reg FD, GLBA, FCRA, GDPR, Securities Act)
- Sensitivity level classification (Public, MNPI, PII)
- Retention policy enforcement
- PII detection and redaction
- Audit trail logging
- Access control validation
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "DocumentType",
    "SensitivityLevel",
    "RegulatoryFramework",
    "DocumentClassifier",
    "RegulatoryMapper",
    "SensitivityClassifier",
    "RetentionPolicyManager",
    "PIIDetector",
    "AuditLogger",
    "AccessController",
    "MaterialEventDetector",
    "classify_document",
    "get_retention_period",
    "detect_pii",
    "check_access_control",
]


class DocumentType(Enum):
    """Financial document types with regulatory implications."""
    FORM_10K = "10-K Annual Report"
    FORM_10Q = "10-Q Quarterly Report"
    FORM_8K = "8-K Material Event Disclosure"
    EARNINGS_TRANSCRIPT = "Earnings Call Transcript"
    CREDIT_REPORT = "Credit Report"
    LOAN_APPLICATION = "Loan Application"
    INTERNAL_ANALYSIS = "Internal Financial Analysis"
    PROSPECTUS = "Investment Prospectus"
    UNKNOWN = "Unknown"


class SensitivityLevel(Enum):
    """Document sensitivity classification levels."""
    PUBLIC = "Public Information"
    MNPI = "Material Non-Public Information"
    PII = "Personally Identifiable Information"
    MIXED = "Mixed Sensitivity"


class RegulatoryFramework(Enum):
    """Compliance frameworks applicable to financial documents."""
    SOX_302 = "SOX Section 302 - CEO/CFO Certification"
    SOX_404 = "SOX Section 404 - Internal Controls"
    REG_FD = "Regulation FD - Fair Disclosure"
    GLBA = "Gramm-Leach-Bliley Act"
    FCRA = "Fair Credit Reporting Act"
    GDPR_ARTICLE_25 = "GDPR Article 25 - Data Protection by Design"
    SECURITIES_ACT_1933 = "Securities Act of 1933"
    ECOA = "Equal Credit Opportunity Act"
    FAIR_HOUSING_ACT = "Fair Housing Act"


class DocumentClassifier:
    """Classifies financial documents by type using pattern matching and heuristics."""

    def __init__(self, offline: bool = False):
        """
        Initialize document classifier.

        Args:
            offline: If True, skip external API calls
        """
        self.offline = offline
        logger.info("Initialized DocumentClassifier")

    def classify(self, document_text: str, metadata: Optional[Dict[str, Any]] = None) -> DocumentType:
        """
        Classify document type from content and metadata.

        Args:
            document_text: Document content to analyze
            metadata: Optional metadata (filename, source, etc.)

        Returns:
            DocumentType enum value
        """
        logger.info("Classifying document...")

        if not document_text:
            logger.warning("Empty document provided")
            return DocumentType.UNKNOWN

        text_lower = document_text.lower()

        # Pattern matching for SEC forms
        if re.search(r'\b10-?k\b', text_lower) or 'annual report' in text_lower:
            if 'pursuant to section' in text_lower or 'securities exchange act' in text_lower:
                logger.info("Classified as 10-K Annual Report")
                return DocumentType.FORM_10K

        if re.search(r'\b10-?q\b', text_lower) or 'quarterly report' in text_lower:
            if 'unaudited' in text_lower or 'fiscal quarter' in text_lower:
                logger.info("Classified as 10-Q Quarterly Report")
                return DocumentType.FORM_10Q

        if re.search(r'\b8-?k\b', text_lower) or 'current report' in text_lower:
            if 'material event' in text_lower or 'item 1.01' in text_lower:
                logger.info("Classified as 8-K Material Event Disclosure")
                return DocumentType.FORM_8K

        # Earnings call indicators
        if 'earnings call' in text_lower or 'conference call' in text_lower:
            if any(term in text_lower for term in ['operator:', 'q&a', 'analyst:', 'prepared remarks']):
                logger.info("Classified as Earnings Call Transcript")
                return DocumentType.EARNINGS_TRANSCRIPT

        # Credit report indicators
        if any(term in text_lower for term in ['credit score', 'fico', 'experian', 'equifax', 'transunion']):
            if 'ssn' in text_lower or 'social security' in text_lower or 'payment history' in text_lower:
                logger.info("Classified as Credit Report")
                return DocumentType.CREDIT_REPORT

        # Loan application indicators
        if 'loan application' in text_lower or 'mortgage application' in text_lower:
            if any(term in text_lower for term in ['income verification', 'employment history', 'debt-to-income']):
                logger.info("Classified as Loan Application")
                return DocumentType.LOAN_APPLICATION

        # Internal analysis indicators
        if any(term in text_lower for term in ['internal use only', 'confidential', 'budget forecast', 'variance analysis']):
            if any(term in text_lower for term in ['m&a', 'merger', 'acquisition', 'investment committee']):
                logger.info("Classified as Internal Financial Analysis")
                return DocumentType.INTERNAL_ANALYSIS

        # Prospectus indicators
        if 'prospectus' in text_lower or 'offering memorandum' in text_lower:
            if 'securities act' in text_lower or 'investment objectives' in text_lower:
                logger.info("Classified as Investment Prospectus")
                return DocumentType.PROSPECTUS

        logger.warning("Could not classify document type")
        return DocumentType.UNKNOWN


class RegulatoryMapper:
    """Maps document types to applicable regulatory frameworks."""

    # Regulatory mapping for each document type
    DOCUMENT_REGULATIONS = {
        DocumentType.FORM_10K: [
            RegulatoryFramework.SOX_302,
            RegulatoryFramework.SOX_404,
        ],
        DocumentType.FORM_10Q: [
            RegulatoryFramework.SOX_302,
            RegulatoryFramework.SOX_404,
        ],
        DocumentType.FORM_8K: [
            RegulatoryFramework.REG_FD,
        ],
        DocumentType.EARNINGS_TRANSCRIPT: [
            RegulatoryFramework.REG_FD,
        ],
        DocumentType.CREDIT_REPORT: [
            RegulatoryFramework.FCRA,
            RegulatoryFramework.GLBA,
            RegulatoryFramework.GDPR_ARTICLE_25,
        ],
        DocumentType.LOAN_APPLICATION: [
            RegulatoryFramework.GLBA,
            RegulatoryFramework.ECOA,
            RegulatoryFramework.FAIR_HOUSING_ACT,
        ],
        DocumentType.INTERNAL_ANALYSIS: [
            RegulatoryFramework.SOX_404,
        ],
        DocumentType.PROSPECTUS: [
            RegulatoryFramework.SECURITIES_ACT_1933,
        ],
    }

    def __init__(self):
        """Initialize regulatory mapper."""
        logger.info("Initialized RegulatoryMapper")

    def get_applicable_regulations(self, doc_type: DocumentType) -> List[RegulatoryFramework]:
        """
        Get all applicable regulatory frameworks for a document type.

        Args:
            doc_type: Document type to map

        Returns:
            List of applicable regulatory frameworks
        """
        regulations = self.DOCUMENT_REGULATIONS.get(doc_type, [])
        logger.info(f"Mapped {doc_type.value} to {len(regulations)} regulations")
        return regulations

    def get_compliance_summary(self, doc_type: DocumentType) -> Dict[str, Any]:
        """
        Get detailed compliance requirements for a document type.

        Args:
            doc_type: Document type

        Returns:
            Dict with compliance details
        """
        regulations = self.get_applicable_regulations(doc_type)

        return {
            "document_type": doc_type.value,
            "regulatory_frameworks": [reg.value for reg in regulations],
            "framework_count": len(regulations),
            "requires_cfo_approval": doc_type in [DocumentType.FORM_10K, DocumentType.FORM_10Q],
            "requires_legal_review": doc_type in [DocumentType.FORM_8K, DocumentType.PROSPECTUS],
            "requires_external_audit": doc_type in [DocumentType.FORM_10K],
        }


class SensitivityClassifier:
    """Classifies document sensitivity levels."""

    def __init__(self):
        """Initialize sensitivity classifier."""
        logger.info("Initialized SensitivityClassifier")

    def classify_sensitivity(self, doc_type: DocumentType, is_filed: bool = False) -> SensitivityLevel:
        """
        Classify document sensitivity level.

        Args:
            doc_type: Document type
            is_filed: Whether document has been publicly filed

        Returns:
            SensitivityLevel enum value
        """
        # PII-containing documents
        if doc_type in [DocumentType.CREDIT_REPORT, DocumentType.LOAN_APPLICATION]:
            logger.info(f"Classified {doc_type.value} as PII")
            return SensitivityLevel.PII

        # MNPI documents (before filing)
        if doc_type in [DocumentType.FORM_10K, DocumentType.FORM_10Q, DocumentType.FORM_8K]:
            if not is_filed:
                logger.info(f"Classified {doc_type.value} as MNPI (not filed)")
                return SensitivityLevel.MNPI
            else:
                logger.info(f"Classified {doc_type.value} as PUBLIC (filed)")
                return SensitivityLevel.PUBLIC

        # Earnings transcripts
        if doc_type == DocumentType.EARNINGS_TRANSCRIPT:
            if not is_filed:
                logger.info("Classified earnings transcript as MNPI (during call)")
                return SensitivityLevel.MNPI
            else:
                logger.info("Classified earnings transcript as PUBLIC (after call)")
                return SensitivityLevel.PUBLIC

        # Internal analysis - always MNPI
        if doc_type == DocumentType.INTERNAL_ANALYSIS:
            logger.info("Classified internal analysis as MNPI")
            return SensitivityLevel.MNPI

        # Prospectus - public after filing
        if doc_type == DocumentType.PROSPECTUS:
            if not is_filed:
                return SensitivityLevel.MNPI
            return SensitivityLevel.PUBLIC

        return SensitivityLevel.PUBLIC


class RetentionPolicyManager:
    """Manages document retention policies and calculates retention periods."""

    # Retention periods in years for each document type
    RETENTION_PERIODS = {
        DocumentType.FORM_10K: 7,  # SOX 404
        DocumentType.FORM_10Q: 7,  # SOX 404
        DocumentType.FORM_8K: 7,   # SOX compliance
        DocumentType.EARNINGS_TRANSCRIPT: 7,  # Reg FD compliance
        DocumentType.CREDIT_REPORT: 7,  # FCRA
        DocumentType.LOAN_APPLICATION: 3,  # ECOA minimum 25 months, rounded up
        DocumentType.INTERNAL_ANALYSIS: 7,  # SOX 404
        DocumentType.PROSPECTUS: None,  # Permanent retention
    }

    def __init__(self):
        """Initialize retention policy manager."""
        logger.info("Initialized RetentionPolicyManager")

    def get_retention_period(self, doc_type: DocumentType) -> Optional[int]:
        """
        Get retention period in years for a document type.

        Args:
            doc_type: Document type

        Returns:
            Retention period in years, or None for permanent retention
        """
        period = self.RETENTION_PERIODS.get(doc_type)
        logger.info(f"Retention period for {doc_type.value}: {period if period else 'Permanent'}")
        return period

    def calculate_deletion_date(self, doc_type: DocumentType, creation_date: datetime) -> Optional[datetime]:
        """
        Calculate when a document can be deleted.

        Args:
            doc_type: Document type
            creation_date: When document was created

        Returns:
            Deletion date, or None for permanent retention
        """
        period = self.get_retention_period(doc_type)

        if period is None:
            logger.info("Document has permanent retention - no deletion date")
            return None

        deletion_date = creation_date + timedelta(days=period * 365)
        logger.info(f"Deletion date calculated: {deletion_date.isoformat()}")
        return deletion_date


class PIIDetector:
    """Detects and redacts personally identifiable information."""

    # PII patterns (simplified for demonstration)
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    PHONE_PATTERN = r'\b\d{3}-\d{3}-\d{4}\b'
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    def __init__(self, recall_threshold: float = 0.999):
        """
        Initialize PII detector.

        Args:
            recall_threshold: Minimum recall threshold (default 99.9%)
        """
        self.recall_threshold = recall_threshold
        logger.info(f"Initialized PIIDetector with recall threshold: {recall_threshold}")

    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII instances in text.

        Args:
            text: Text to scan for PII

        Returns:
            List of detected PII instances with type and location
        """
        detections = []

        # Detect SSNs
        for match in re.finditer(self.SSN_PATTERN, text):
            detections.append({
                "type": "SSN",
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "severity": "CRITICAL"
            })

        # Detect phone numbers
        for match in re.finditer(self.PHONE_PATTERN, text):
            detections.append({
                "type": "PHONE",
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "severity": "HIGH"
            })

        # Detect email addresses
        for match in re.finditer(self.EMAIL_PATTERN, text):
            detections.append({
                "type": "EMAIL",
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "severity": "MEDIUM"
            })

        logger.info(f"Detected {len(detections)} PII instances")
        return detections

    def redact_pii(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Redact PII from text.

        Args:
            text: Text to redact

        Returns:
            Tuple of (redacted_text, detection_log)
        """
        detections = self.detect_pii(text)
        redacted_text = text

        # Sort by position in reverse to maintain correct indices
        for detection in sorted(detections, key=lambda x: x['start'], reverse=True):
            redacted_text = (
                redacted_text[:detection['start']] +
                f"[REDACTED_{detection['type']}]" +
                redacted_text[detection['end']:]
            )

        logger.info(f"Redacted {len(detections)} PII instances")
        return redacted_text, detections


class AuditLogger:
    """Logs all document access and operations for audit trails."""

    def __init__(self):
        """Initialize audit logger."""
        self.audit_log = []
        logger.info("Initialized AuditLogger")

    def log_access(
        self,
        user_id: str,
        doc_type: DocumentType,
        action: str,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log document access event.

        Args:
            user_id: User accessing document
            doc_type: Document type
            action: Action performed (view, edit, download, etc.)
            doc_id: Optional document identifier
            metadata: Optional additional metadata

        Returns:
            Audit log entry
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "document_type": doc_type.value,
            "action": action,
            "doc_id": doc_id,
            "metadata": metadata or {}
        }

        self.audit_log.append(entry)
        logger.info(f"Logged audit entry: {user_id} {action} {doc_type.value}")

        return entry

    def get_audit_trail(self, user_id: Optional[str] = None, doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve audit trail with optional filtering.

        Args:
            user_id: Filter by user
            doc_id: Filter by document

        Returns:
            List of matching audit entries
        """
        results = self.audit_log

        if user_id:
            results = [e for e in results if e['user_id'] == user_id]

        if doc_id:
            results = [e for e in results if e['doc_id'] == doc_id]

        logger.info(f"Retrieved {len(results)} audit entries")
        return results


class AccessController:
    """Enforces role-based access controls for sensitive documents."""

    # Role permissions (simplified for demonstration)
    ROLE_PERMISSIONS = {
        "executive": {
            SensitivityLevel.PUBLIC,
            SensitivityLevel.MNPI,
            SensitivityLevel.PII,
        },
        "compliance_officer": {
            SensitivityLevel.PUBLIC,
            SensitivityLevel.MNPI,
            SensitivityLevel.PII,
        },
        "analyst": {
            SensitivityLevel.PUBLIC,
            SensitivityLevel.MNPI,
        },
        "auditor": {
            SensitivityLevel.PUBLIC,
            SensitivityLevel.MNPI,
        },
        "credit_officer": {
            SensitivityLevel.PUBLIC,
            SensitivityLevel.PII,
        },
        "employee": {
            SensitivityLevel.PUBLIC,
        },
    }

    def __init__(self):
        """Initialize access controller."""
        logger.info("Initialized AccessController")

    def check_access(self, user_role: str, sensitivity: SensitivityLevel) -> bool:
        """
        Check if user role has access to document sensitivity level.

        Args:
            user_role: User's role
            sensitivity: Document sensitivity level

        Returns:
            True if access allowed, False otherwise
        """
        allowed_levels = self.ROLE_PERMISSIONS.get(user_role, set())
        has_access = sensitivity in allowed_levels

        logger.info(f"Access check: role={user_role}, sensitivity={sensitivity.value}, allowed={has_access}")
        return has_access

    def get_accessible_document_types(self, user_role: str) -> List[DocumentType]:
        """
        Get list of document types accessible to a role.

        Args:
            user_role: User's role

        Returns:
            List of accessible document types
        """
        allowed_levels = self.ROLE_PERMISSIONS.get(user_role, set())

        accessible_types = []
        for doc_type in DocumentType:
            # Simplified: assume unfiled for conservative check
            classifier = SensitivityClassifier()
            sensitivity = classifier.classify_sensitivity(doc_type, is_filed=False)

            if sensitivity in allowed_levels:
                accessible_types.append(doc_type)

        logger.info(f"User role '{user_role}' can access {len(accessible_types)} document types")
        return accessible_types


class MaterialEventDetector:
    """Detects material events requiring Form 8-K filing."""

    # Material event keywords (simplified)
    MATERIAL_EVENT_KEYWORDS = [
        'bankruptcy',
        'chapter 11',
        'asset sale',
        'acquisition',
        'merger',
        'management change',
        'ceo resign',
        'cfo resign',
        'accounting restatement',
        'material impairment',
        'regulatory investigation',
        'sec inquiry',
    ]

    def __init__(self):
        """Initialize material event detector."""
        logger.info("Initialized MaterialEventDetector")

    def detect_material_events(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect potential material events in text.

        Args:
            text: Text to analyze

        Returns:
            List of detected material events
        """
        text_lower = text.lower()
        events = []

        for keyword in self.MATERIAL_EVENT_KEYWORDS:
            if keyword in text_lower:
                events.append({
                    "event_type": keyword.upper().replace(' ', '_'),
                    "keyword": keyword,
                    "requires_8k": True,
                    "filing_deadline": "4 business days",
                    "severity": "CRITICAL"
                })

        logger.info(f"Detected {len(events)} potential material events")

        if events:
            logger.warning(f"⚠️ Material events detected - legal review required")

        return events


# Convenience functions

def classify_document(
    document_text: str,
    metadata: Optional[Dict[str, Any]] = None,
    offline: bool = False
) -> Dict[str, Any]:
    """
    Classify a document and return complete analysis.

    Args:
        document_text: Document content
        metadata: Optional metadata
        offline: Skip external API calls if True

    Returns:
        Dict with complete classification results
    """
    logger.info("Starting document classification")

    if offline:
        logger.warning("⚠️ Offline mode - skipping external service calls")

    # Initialize components
    classifier = DocumentClassifier(offline=offline)
    reg_mapper = RegulatoryMapper()
    sens_classifier = SensitivityClassifier()
    retention_mgr = RetentionPolicyManager()
    pii_detector = PIIDetector()
    event_detector = MaterialEventDetector()

    # Classify document type
    doc_type = classifier.classify(document_text, metadata)

    # Get regulatory mapping
    regulations = reg_mapper.get_applicable_regulations(doc_type)
    compliance_summary = reg_mapper.get_compliance_summary(doc_type)

    # Classify sensitivity
    is_filed = metadata.get('is_filed', False) if metadata else False
    sensitivity = sens_classifier.classify_sensitivity(doc_type, is_filed)

    # Get retention period
    retention_period = retention_mgr.get_retention_period(doc_type)

    # Detect PII
    pii_detections = pii_detector.detect_pii(document_text)

    # Detect material events
    material_events = event_detector.detect_material_events(document_text)

    result = {
        "document_type": doc_type.value,
        "sensitivity_level": sensitivity.value,
        "regulatory_frameworks": [reg.value for reg in regulations],
        "retention_period_years": retention_period if retention_period else "Permanent",
        "compliance_summary": compliance_summary,
        "pii_detected": len(pii_detections) > 0,
        "pii_count": len(pii_detections),
        "material_events_detected": len(material_events) > 0,
        "material_events": material_events,
        "requires_legal_review": len(material_events) > 0 or doc_type in [DocumentType.FORM_8K, DocumentType.PROSPECTUS],
        "offline_mode": offline,
    }

    logger.info("Document classification completed")
    return result


def get_retention_period(doc_type: DocumentType) -> Optional[int]:
    """
    Get retention period for a document type.

    Args:
        doc_type: Document type

    Returns:
        Retention period in years, or None for permanent
    """
    mgr = RetentionPolicyManager()
    return mgr.get_retention_period(doc_type)


def detect_pii(text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Detect and redact PII from text.

    Args:
        text: Text to process

    Returns:
        Tuple of (redacted_text, detections)
    """
    detector = PIIDetector()
    return detector.redact_pii(text)


def check_access_control(user_role: str, doc_type: DocumentType, is_filed: bool = False) -> bool:
    """
    Check if user role can access document type.

    Args:
        user_role: User's role
        doc_type: Document type
        is_filed: Whether document is filed

    Returns:
        True if access allowed
    """
    controller = AccessController()
    classifier = SensitivityClassifier()

    sensitivity = classifier.classify_sensitivity(doc_type, is_filed)
    return controller.check_access(user_role, sensitivity)
