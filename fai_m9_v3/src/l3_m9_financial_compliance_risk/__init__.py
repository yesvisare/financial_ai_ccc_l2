"""
L3 M9.3: Regulatory Constraints in LLM Outputs (MNPI, Disclaimers, Safe Harbor)

This module implements a three-layer compliance framework for financial LLM systems:
- Layer 1: MNPI Detection (Material Non-Public Information)
- Layer 2: Disclaimer Requirements (FINRA Rule 2210, Safe Harbor)
- Layer 3: Information Barriers (Chinese Walls for Regulation FD compliance)

The system filters LLM outputs to prevent securities law violations, ensure regulatory
compliance, and create audit trails for SEC investigations.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

__all__ = [
    "MNPIDetector",
    "DisclaimerManager",
    "InformationBarrier",
    "ComplianceFilter",
    "ViolationType",
    "filter_llm_output"
]


class ViolationType(Enum):
    """Types of regulatory violations that can be detected"""
    MNPI = "mnpi"
    MISSING_DISCLAIMER = "missing_disclaimer"
    INVESTMENT_ADVICE = "investment_advice"
    SELECTIVE_DISCLOSURE = "selective_disclosure"
    FORWARD_LOOKING_NO_SAFE_HARBOR = "forward_looking_no_safe_harbor"


class MNPIDetector:
    """
    Detects Material Non-Public Information in LLM outputs using three-layer approach:
    1. Source Validation: Identifies internal vs. public documents
    2. Materiality Indicator Matching: Detects material event keywords
    3. Temporal Check: Validates disclosure timing
    """

    # Internal document patterns (Layer 1)
    INTERNAL_SOURCE_PATTERNS = [
        r'\b(draft|confidential|internal|restricted)\b',
        r'\b(board minutes|executive memo|planning document)\b',
        r'\b(email|memo|forecast|projection)\b',
        r'\b(pre-announcement|embargo|not for distribution)\b'
    ]

    # Material event indicators (Layer 2)
    MATERIALITY_INDICATORS = {
        "earnings": {"severity": "HIGH", "patterns": [
            r'Q[1-4]\s+earnings',
            r'revenue\s+of\s+\$[\d.]+[BM]',
            r'profit\s+margin',
            r'EPS\s+of\s+\$[\d.]+'
        ]},
        "merger_acquisition": {"severity": "HIGH", "patterns": [
            r'\b(merger|acquisition|M&A)\b',
            r'\b(acquiring|purchase|buyout)\b',
            r'\b(deal|transaction)\s+valued\s+at'
        ]},
        "executive_change": {"severity": "MEDIUM", "patterns": [
            r'CEO\s+(resignation|appointment|departure)',
            r'executive\s+leadership\s+change',
            r'C-level\s+(hire|firing)'
        ]},
        "product_launch": {"severity": "MEDIUM", "patterns": [
            r'product\s+launch',
            r'new\s+(product|service)\s+announcement',
            r'patent\s+(approval|filing)'
        ]},
        "guidance": {"severity": "HIGH", "patterns": [
            r'guidance',
            r'forecast',
            r'expects?\s+to\s+(achieve|reach)',
            r'projected\s+(revenue|earnings)'
        ]}
    }

    # Forward-looking statement patterns (Layer 3)
    FORWARD_LOOKING_PATTERNS = [
        r'\b(will|expect|anticipate|project|forecast|estimate|believe)\b',
        r'\b(plan to|intend to|likely to)\b',
        r'Q[1-4]\s+\d{4}\s+(earnings|revenue)'
    ]

    def __init__(self, detection_threshold: float = 0.85):
        """
        Initialize MNPI detector.

        Args:
            detection_threshold: Confidence threshold for flagging violations (default 0.85)
        """
        self.detection_threshold = detection_threshold
        logger.info(f"MNPIDetector initialized with threshold={detection_threshold}")

    def validate_source(self, text: str, citations: List[Dict[str, Any]]) -> Tuple[bool, float]:
        """
        Layer 1: Validate if source is internal (non-public).

        Args:
            text: LLM output text
            citations: List of citation metadata from M9.1

        Returns:
            Tuple of (is_internal, confidence)
        """
        confidence = 0.0

        # Check citation metadata
        for citation in citations:
            source_type = citation.get("source_type", "").lower()
            document_url = citation.get("document_url", "").lower()

            # Public sources (SEC filings, press releases)
            if any(keyword in source_type for keyword in ["10-k", "10-q", "8-k", "press release", "public filing"]):
                continue

            # Internal document indicators
            if any(keyword in source_type for keyword in ["internal", "draft", "confidential", "memo", "email"]):
                confidence = max(confidence, 0.9)
                logger.warning(f"Internal source detected: {source_type}")

        # Check text content for internal markers
        for pattern in self.INTERNAL_SOURCE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                confidence = max(confidence, 0.7)
                logger.warning(f"Internal document pattern detected: {pattern}")

        return (confidence > 0.5, confidence)

    def detect_materiality_indicators(self, text: str) -> Tuple[List[str], float]:
        """
        Layer 2: Detect material event indicators.

        Args:
            text: LLM output text

        Returns:
            Tuple of (detected_indicators, confidence)
        """
        detected = []
        severity_weights = {"HIGH": 0.4, "MEDIUM": 0.25, "LOW": 0.1}
        total_confidence = 0.0

        for indicator_name, indicator_data in self.MATERIALITY_INDICATORS.items():
            severity = indicator_data["severity"]
            patterns = indicator_data["patterns"]

            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(indicator_name)
                    total_confidence += severity_weights[severity]
                    logger.info(f"Material indicator detected: {indicator_name} (severity={severity})")
                    break  # Only count each indicator once

        # Cap confidence at 1.0
        total_confidence = min(total_confidence, 1.0)

        return (detected, total_confidence)

    def check_temporal_disclosure(
        self,
        text: str,
        citations: List[Dict[str, Any]],
        public_disclosures: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[bool, float]:
        """
        Layer 3: Check if forward-looking statements were disclosed publicly.

        Args:
            text: LLM output text
            citations: Citation metadata
            public_disclosures: List of public disclosure records (optional)

        Returns:
            Tuple of (is_forward_looking_undisclosed, confidence)
        """
        # Detect forward-looking statements
        has_forward_looking = False
        for pattern in self.FORWARD_LOOKING_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                has_forward_looking = True
                logger.info(f"Forward-looking statement detected: {pattern}")
                break

        if not has_forward_looking:
            return (False, 0.0)

        # Check if disclosed publicly
        if public_disclosures:
            for citation in citations:
                filing_date = citation.get("filing_date")
                if filing_date:
                    # Check if this information was publicly disclosed
                    for disclosure in public_disclosures:
                        if disclosure.get("date") and disclosure["date"] <= filing_date:
                            logger.info("Forward-looking statement found in public disclosure")
                            return (False, 0.0)

        # Forward-looking statement without public disclosure
        logger.warning("Forward-looking statement without public disclosure detected")
        return (True, 0.8)

    def detect(
        self,
        text: str,
        citations: List[Dict[str, Any]],
        public_disclosures: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run three-layer MNPI detection.

        Args:
            text: LLM output text
            citations: Citation metadata from M9.1
            public_disclosures: Public disclosure records (optional)

        Returns:
            Detection results with violation flag and confidence breakdown
        """
        # Layer 1: Source validation
        is_internal, source_confidence = self.validate_source(text, citations)

        # Layer 2: Materiality indicators
        material_indicators, materiality_confidence = self.detect_materiality_indicators(text)

        # Layer 3: Temporal check
        is_undisclosed_forward, temporal_confidence = self.check_temporal_disclosure(
            text, citations, public_disclosures
        )

        # Decision logic: If ≥2 layers flag OR single high-confidence violation
        layers_flagged = sum([
            is_internal,
            materiality_confidence > 0.5,
            is_undisclosed_forward
        ])

        # Calculate overall confidence
        max_confidence = max(source_confidence, materiality_confidence, temporal_confidence)

        # Determine violation
        is_mnpi_violation = (
            layers_flagged >= 2 or
            max_confidence >= 0.9 or
            (is_internal and materiality_confidence > 0.5)
        )

        result = {
            "is_violation": is_mnpi_violation,
            "confidence": max_confidence,
            "layers_flagged": layers_flagged,
            "details": {
                "internal_source": is_internal,
                "source_confidence": source_confidence,
                "material_indicators": material_indicators,
                "materiality_confidence": materiality_confidence,
                "undisclosed_forward_looking": is_undisclosed_forward,
                "temporal_confidence": temporal_confidence
            }
        }

        if is_mnpi_violation:
            logger.error(f"MNPI VIOLATION DETECTED - Confidence: {max_confidence:.2f}, Layers: {layers_flagged}")

        return result


class DisclaimerManager:
    """
    Manages disclaimer injection for FINRA Rule 2210 and Safe Harbor compliance.
    """

    # Standard disclaimer templates
    DISCLAIMERS = {
        "investment_advice": (
            "\n\n⚠️ DISCLAIMER: This information is for educational purposes only and does not "
            "constitute investment advice. Consult a registered financial advisor before making "
            "investment decisions. (FINRA Rule 2210)"
        ),
        "forward_looking": (
            "\n\n⚠️ SAFE HARBOR STATEMENT: This response contains forward-looking statements that "
            "involve risks and uncertainties. Actual results may differ materially. See our SEC "
            "filings for risk factors. (Private Securities Litigation Reform Act of 1995)"
        ),
        "general": (
            "\n\n⚠️ DISCLAIMER: This information is provided as-is without warranties. "
            "Verify all information independently before making decisions."
        )
    }

    # Patterns requiring investment advice disclaimer
    INVESTMENT_ADVICE_PATTERNS = [
        r'\b(recommend|suggests?|advise|should\s+(buy|sell))\b',
        r'\b(undervalued|overvalued|good\s+investment)\b',
        r'\b(target\s+price|price\s+target)\b',
        r'\b(buy|sell|hold)\s+rating'
    ]

    def __init__(self, auto_inject: bool = True):
        """
        Initialize disclaimer manager.

        Args:
            auto_inject: Automatically inject disclaimers when patterns detected
        """
        self.auto_inject = auto_inject
        logger.info(f"DisclaimerManager initialized (auto_inject={auto_inject})")

    def requires_investment_disclaimer(self, text: str) -> bool:
        """Check if text requires investment advice disclaimer."""
        for pattern in self.INVESTMENT_ADVICE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.info(f"Investment advice pattern detected: {pattern}")
                return True
        return False

    def requires_forward_looking_disclaimer(self, text: str) -> bool:
        """Check if text requires Safe Harbor disclaimer."""
        forward_patterns = [
            r'\b(will|expect|anticipate|project|forecast)\b',
            r'\b(future|upcoming|planned)\b',
            r'Q[1-4]\s+\d{4}'
        ]
        for pattern in forward_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.info(f"Forward-looking pattern detected: {pattern}")
                return True
        return False

    def add_disclaimers(self, text: str) -> Tuple[str, List[str]]:
        """
        Add required disclaimers to text.

        Args:
            text: Original LLM output

        Returns:
            Tuple of (text_with_disclaimers, list_of_added_disclaimers)
        """
        added = []
        result = text

        # Check investment advice
        if self.requires_investment_disclaimer(text):
            result += self.DISCLAIMERS["investment_advice"]
            added.append("investment_advice")
            logger.info("Added investment advice disclaimer")

        # Check forward-looking statements
        if self.requires_forward_looking_disclaimer(text):
            result += self.DISCLAIMERS["forward_looking"]
            added.append("forward_looking")
            logger.info("Added Safe Harbor disclaimer")

        # Add general disclaimer if no specific ones
        if not added:
            result += self.DISCLAIMERS["general"]
            added.append("general")

        return (result, added)


class InformationBarrier:
    """
    Implements Chinese Walls to prevent selective disclosure (Regulation FD).
    """

    def __init__(self, user_permissions: Optional[Dict[str, List[str]]] = None):
        """
        Initialize information barrier.

        Args:
            user_permissions: Mapping of user_id to allowed data namespaces
        """
        self.user_permissions = user_permissions or {}
        logger.info("InformationBarrier initialized")

    def check_access(self, user_id: str, data_namespace: str) -> bool:
        """
        Check if user has access to data namespace.

        Args:
            user_id: User identifier
            data_namespace: Data classification (e.g., "public", "internal", "restricted")

        Returns:
            True if access allowed, False otherwise
        """
        # Public data always accessible
        if data_namespace == "public":
            return True

        # Check user permissions
        allowed_namespaces = self.user_permissions.get(user_id, ["public"])
        has_access = data_namespace in allowed_namespaces

        if not has_access:
            logger.warning(f"Access denied: user={user_id}, namespace={data_namespace}")

        return has_access

    def filter_citations(
        self,
        citations: List[Dict[str, Any]],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Filter citations based on user permissions.

        Args:
            citations: List of citation metadata
            user_id: User identifier

        Returns:
            Filtered citations list
        """
        filtered = []
        for citation in citations:
            namespace = citation.get("data_namespace", "public")
            if self.check_access(user_id, namespace):
                filtered.append(citation)
            else:
                logger.info(f"Citation filtered: {citation.get('source_id', 'unknown')}")

        return filtered


class ComplianceFilter:
    """
    Main orchestrator for regulatory compliance filtering.
    Integrates MNPI detection, disclaimer management, and information barriers.
    """

    def __init__(
        self,
        mnpi_detector: Optional[MNPIDetector] = None,
        disclaimer_manager: Optional[DisclaimerManager] = None,
        information_barrier: Optional[InformationBarrier] = None,
        enable_audit_logging: bool = True
    ):
        """
        Initialize compliance filter.

        Args:
            mnpi_detector: MNPI detector instance
            disclaimer_manager: Disclaimer manager instance
            information_barrier: Information barrier instance
            enable_audit_logging: Enable compliance audit trail
        """
        self.mnpi_detector = mnpi_detector or MNPIDetector()
        self.disclaimer_manager = disclaimer_manager or DisclaimerManager()
        self.information_barrier = information_barrier or InformationBarrier()
        self.enable_audit_logging = enable_audit_logging
        self.audit_log: List[Dict[str, Any]] = []

        logger.info("ComplianceFilter initialized")

    def _log_violation(
        self,
        violation_type: ViolationType,
        user_id: str,
        text: str,
        details: Dict[str, Any],
        action_taken: str
    ):
        """Log compliance violation for audit trail."""
        if not self.enable_audit_logging:
            return

        violation_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "violation_type": violation_type.value,
            "user_id": user_id,
            "text_snippet": text[:200],  # First 200 chars
            "details": details,
            "action_taken": action_taken
        }

        self.audit_log.append(violation_record)
        logger.error(f"VIOLATION LOGGED: {violation_type.value} - {action_taken}")

    def filter_output(
        self,
        llm_output: str,
        citations: List[Dict[str, Any]],
        user_id: str,
        risk_score: Optional[float] = None,
        public_disclosures: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Filter LLM output through compliance pipeline.

        Args:
            llm_output: Raw LLM response text
            citations: Citation metadata from M9.1
            user_id: User identifier
            risk_score: Risk score from M9.2 (optional)
            public_disclosures: Public disclosure records (optional)

        Returns:
            Filtered response with compliance metadata
        """
        logger.info(f"Processing compliance filter for user={user_id}")

        # Step 1: Filter citations by information barrier
        filtered_citations = self.information_barrier.filter_citations(citations, user_id)

        if len(filtered_citations) < len(citations):
            self._log_violation(
                ViolationType.SELECTIVE_DISCLOSURE,
                user_id,
                llm_output,
                {"original_citations": len(citations), "filtered": len(filtered_citations)},
                "Citations filtered by information barrier"
            )

        # Step 2: MNPI detection
        mnpi_result = self.mnpi_detector.detect(llm_output, filtered_citations, public_disclosures)

        if mnpi_result["is_violation"]:
            self._log_violation(
                ViolationType.MNPI,
                user_id,
                llm_output,
                mnpi_result["details"],
                "Response blocked - MNPI detected"
            )

            return {
                "allowed": False,
                "blocked_reason": "MNPI_VIOLATION",
                "filtered_text": None,
                "violation_details": mnpi_result,
                "audit_logged": True
            }

        # Step 3: Add disclaimers
        filtered_text, added_disclaimers = self.disclaimer_manager.add_disclaimers(llm_output)

        # Log if investment advice detected
        if "investment_advice" in added_disclaimers:
            self._log_violation(
                ViolationType.INVESTMENT_ADVICE,
                user_id,
                llm_output,
                {"disclaimers_added": added_disclaimers},
                "Investment advice disclaimer added"
            )

        # Step 4: Final compliance check
        logger.info("✅ Compliance check passed - Response allowed")

        return {
            "allowed": True,
            "filtered_text": filtered_text,
            "disclaimers_added": added_disclaimers,
            "mnpi_check": mnpi_result,
            "citations_filtered": len(citations) - len(filtered_citations),
            "audit_logged": self.enable_audit_logging
        }

    def get_audit_log(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve compliance audit log.

        Args:
            user_id: Filter by specific user (optional)

        Returns:
            List of violation records
        """
        if user_id:
            return [log for log in self.audit_log if log["user_id"] == user_id]
        return self.audit_log


def filter_llm_output(
    llm_output: str,
    citations: List[Dict[str, Any]],
    user_id: str = "anonymous",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for filtering LLM outputs with default compliance settings.

    Args:
        llm_output: Raw LLM response text
        citations: Citation metadata
        user_id: User identifier
        **kwargs: Additional options (risk_score, public_disclosures, etc.)

    Returns:
        Compliance filtering result
    """
    compliance_filter = ComplianceFilter()
    return compliance_filter.filter_output(
        llm_output,
        citations,
        user_id,
        risk_score=kwargs.get("risk_score"),
        public_disclosures=kwargs.get("public_disclosures")
    )
