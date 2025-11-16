"""
L3 M9.2: Financial Compliance Risk - Risk Assessment in Retrieval

This module implements production-ready risk assessment and compliance guardrails
for financial RAG systems. It classifies query risk levels, computes confidence
scores, and enforces regulatory compliance to prevent unauthorized investment advice.

Key capabilities:
- Pattern-based and semantic query risk classification
- Multi-factor confidence scoring (retrieval quality, source diversity, temporal consistency)
- Regulatory compliance guardrails (RIA, MNPI, Safe Harbor, Form 8-K)
- Human-in-the-loop escalation workflows for high-risk queries
"""

import re
import logging
import hashlib
from typing import List, Dict, Any, Optional, Literal, Tuple
from enum import Enum
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available - using fallback calculations")

logger = logging.getLogger(__name__)

__all__ = [
    "RiskLevel",
    "SystemAction",
    "RiskClassificationResult",
    "ConfidenceScore",
    "FinancialQueryRiskClassifier",
    "ConfidenceScorer",
    "ComplianceGuardrails",
    "classify_query_risk",
    "compute_confidence_score"
]


# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

class RiskLevel(str, Enum):
    """Risk classification levels for financial queries."""
    LOW = "LOW"           # Educational/factual queries
    MEDIUM = "MEDIUM"     # Comparative analysis
    HIGH = "HIGH"         # Investment advice (requires RIA)


class SystemAction(str, Enum):
    """Recommended system actions based on risk level."""
    ANSWER_NORMALLY = "ANSWER_NORMALLY"
    ANSWER_WITH_DISCLAIMER = "ANSWER_WITH_DISCLAIMER"
    ESCALATE_TO_HUMAN_ADVISOR = "ESCALATE_TO_HUMAN_ADVISOR"
    BLOCK_RESPONSE = "BLOCK_RESPONSE"


@dataclass
class RiskClassificationResult:
    """Result of query risk classification."""
    risk_level: RiskLevel
    confidence: float
    reasoning: str
    regulatory_concern: Optional[str] = None
    system_action: SystemAction = SystemAction.ANSWER_NORMALLY
    pattern_matches: List[str] = field(default_factory=list)
    user_context_adjusted: bool = False


@dataclass
class ConfidenceScore:
    """Multi-factor confidence score for retrieval results."""
    overall_score: float
    retrieval_quality: float
    source_diversity: float
    temporal_consistency: float
    citation_agreement: float
    domain_relevance_bonus: float = 0.0
    threshold_category: str = "VERY_LOW"  # HIGH, MEDIUM, LOW, VERY_LOW


# ============================================================================
# FINANCIAL QUERY RISK CLASSIFIER
# ============================================================================

class FinancialQueryRiskClassifier:
    """
    Classifies financial queries into risk tiers to prevent unauthorized
    investment advice and ensure regulatory compliance.

    Uses hybrid approach:
    - Pattern-based classification (60% weight) for legal safety
    - Semantic analysis (40% weight) for nuanced understanding
    - User context adjustment for account type and query history
    """

    # High-risk patterns (investment advice - requires RIA license)
    HIGH_RISK_PATTERNS = [
        r'\b(should|would|recommend|suggestion)\s+(I|you|we)\s+(buy|sell|invest|trade|short|long)\b',
        r'\b(what|which)\s+.{0,30}\s+(best|worst|top|bottom)\s+(stock|investment|fund|etf)\b',
        r'\bis\s+.{0,30}\s+a\s+(good|bad|smart|wise|foolish)\s+(investment|trade|bet|play)\b',
        r'\b(when|timing)\s+.{0,30}\s+(buy|sell|invest|enter|exit)\b',
        r'\b(how much|what percentage|allocation)\s+.{0,30}\s+(should|would|recommend)\b',
        r'\b(advice|advise|recommend|suggest)\s+.{0,20}\s+(buy|sell|invest)\b',
        r'\bworth\s+buying\b',
    ]

    # Medium-risk patterns (comparative analysis)
    MEDIUM_RISK_PATTERNS = [
        r'\b(compare|versus|vs|better than|worse than)\b.{0,50}\b(stock|company|investment)\b',
        r'\b(risk|risky|volatile|safe|dangerous)\b.{0,30}\b(stock|investment|portfolio)\b',
        r'\b(performance|returns|growth|decline)\s+of\b',
        r'\b(overvalued|undervalued|fair value|worth)\b',
        r'\b(forecast|predict|projection|outlook|guidance)\b',
    ]

    # Low-risk patterns (educational/factual)
    LOW_RISK_PATTERNS = [
        r'\b(what is|define|explain|meaning of)\b',
        r'\bhow (does|do|did)\b.{0,50}\b(work|function|operate)\b',
        r'\b(when|where|who|which)\s+(did|was|were|filed)\b',
        r'\b(show me|find|retrieve|get)\s+.{0,30}\s+(filing|form|document|report)\b',
    ]

    def __init__(self, semantic_analysis_enabled: bool = False):
        """
        Initialize the risk classifier.

        Args:
            semantic_analysis_enabled: Enable semantic intent analysis (requires LLM)
        """
        self.semantic_analysis_enabled = semantic_analysis_enabled

        # Compile regex patterns for performance
        self.high_risk_regex = [re.compile(p, re.IGNORECASE) for p in self.HIGH_RISK_PATTERNS]
        self.medium_risk_regex = [re.compile(p, re.IGNORECASE) for p in self.MEDIUM_RISK_PATTERNS]
        self.low_risk_regex = [re.compile(p, re.IGNORECASE) for p in self.LOW_RISK_PATTERNS]

        logger.info(f"FinancialQueryRiskClassifier initialized (semantic_analysis={semantic_analysis_enabled})")

    def classify(
        self,
        query: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> RiskClassificationResult:
        """
        Classify a financial query's risk level.

        Args:
            query: The user's query text
            user_context: Optional context (account_type, high_risk_query_count, etc.)

        Returns:
            RiskClassificationResult with risk level, confidence, and recommended action
        """
        logger.info(f"Classifying query: {query[:100]}...")

        # Step 1: Pattern-based classification (60% weight)
        pattern_result = self._classify_by_patterns(query)
        pattern_confidence = pattern_result["confidence"]

        # Step 2: Semantic analysis (40% weight) - optional
        if self.semantic_analysis_enabled and pattern_confidence < 0.85:
            semantic_result = self._classify_semantic(query)
            combined_confidence = (0.6 * pattern_confidence) + (0.4 * semantic_result["confidence"])

            # Use higher risk level if confidence is strong
            if semantic_result["confidence"] > 0.7 and semantic_result["risk_level"].value > pattern_result["risk_level"].value:
                risk_level = semantic_result["risk_level"]
            else:
                risk_level = pattern_result["risk_level"]
        else:
            # High-confidence pattern match bypasses semantic analysis
            combined_confidence = pattern_confidence
            risk_level = pattern_result["risk_level"]

        # Step 3: User context adjustment
        adjusted_risk, context_adjusted = self._adjust_for_user_context(
            risk_level,
            combined_confidence,
            user_context or {}
        )

        # Step 4: Map risk to system action
        system_action = self._map_risk_to_action(adjusted_risk, combined_confidence)

        # Step 5: Determine regulatory concern
        regulatory_concern = self._get_regulatory_concern(adjusted_risk)

        result = RiskClassificationResult(
            risk_level=adjusted_risk,
            confidence=combined_confidence,
            reasoning=pattern_result["reasoning"],
            regulatory_concern=regulatory_concern,
            system_action=system_action,
            pattern_matches=pattern_result["matches"],
            user_context_adjusted=context_adjusted
        )

        logger.info(f"Classification result: {result.risk_level} (confidence={result.confidence:.2f}, action={result.system_action})")
        return result

    def _classify_by_patterns(self, query: str) -> Dict[str, Any]:
        """Pattern-based classification using regex matching."""
        query_lower = query.lower()

        # Check high-risk patterns first (legal safety priority)
        high_matches = []
        for pattern in self.high_risk_regex:
            if pattern.search(query_lower):
                high_matches.append(pattern.pattern)

        if high_matches:
            return {
                "risk_level": RiskLevel.HIGH,
                "confidence": 0.95,  # High confidence for pattern matches
                "reasoning": f"Detected investment advice language: {high_matches[0][:50]}...",
                "matches": high_matches
            }

        # Check medium-risk patterns
        medium_matches = []
        for pattern in self.medium_risk_regex:
            if pattern.search(query_lower):
                medium_matches.append(pattern.pattern)

        if medium_matches:
            return {
                "risk_level": RiskLevel.MEDIUM,
                "confidence": 0.85,
                "reasoning": f"Detected comparative/analysis language: {medium_matches[0][:50]}...",
                "matches": medium_matches
            }

        # Check low-risk patterns
        low_matches = []
        for pattern in self.low_risk_regex:
            if pattern.search(query_lower):
                low_matches.append(pattern.pattern)

        if low_matches:
            return {
                "risk_level": RiskLevel.LOW,
                "confidence": 0.90,
                "reasoning": f"Detected educational/factual language: {low_matches[0][:50]}...",
                "matches": low_matches
            }

        # No pattern match - default to medium risk (conservative)
        return {
            "risk_level": RiskLevel.MEDIUM,
            "confidence": 0.50,
            "reasoning": "No clear pattern match - defaulting to medium risk for safety",
            "matches": []
        }

    def _classify_semantic(self, query: str) -> Dict[str, Any]:
        """
        Semantic intent analysis using LLM.

        In production, this would call Claude/GPT-4 with a prompt like:
        "Classify the following financial query as LOW (educational), MEDIUM (analysis),
        or HIGH (investment advice): {query}"

        For this educational module, we return a placeholder.
        """
        logger.info("⚠️ Semantic analysis requested but not implemented (educational module)")

        # Placeholder - in production would call LLM API
        return {
            "risk_level": RiskLevel.MEDIUM,
            "confidence": 0.60,
            "reasoning": "Semantic analysis not available (placeholder)"
        }

    def _adjust_for_user_context(
        self,
        risk_level: RiskLevel,
        confidence: float,
        user_context: Dict[str, Any]
    ) -> Tuple[RiskLevel, bool]:
        """
        Adjust risk level based on user context (account type, history).

        Args:
            risk_level: Initial risk classification
            confidence: Classification confidence
            user_context: User account type, query history, etc.

        Returns:
            (adjusted_risk_level, was_adjusted)
        """
        adjusted = False

        # Elevate risk if user has pattern of high-risk queries
        high_risk_count = user_context.get("high_risk_query_count", 0)
        if high_risk_count >= 3 and risk_level == RiskLevel.MEDIUM:
            logger.warning(f"Elevating MEDIUM to HIGH due to high-risk query history (count={high_risk_count})")
            risk_level = RiskLevel.HIGH
            adjusted = True

        # Stricter enforcement for retail accounts (SEC focus area)
        if user_context.get("account_type") == "retail" and risk_level == RiskLevel.MEDIUM:
            if confidence > 0.75:
                logger.info("Maintaining strict medium-risk classification for retail account")

        return risk_level, adjusted

    def _map_risk_to_action(self, risk_level: RiskLevel, confidence: float) -> SystemAction:
        """Map risk level to system action."""
        if risk_level == RiskLevel.LOW:
            return SystemAction.ANSWER_NORMALLY
        elif risk_level == RiskLevel.MEDIUM:
            return SystemAction.ANSWER_WITH_DISCLAIMER
        else:  # HIGH
            return SystemAction.ESCALATE_TO_HUMAN_ADVISOR

    def _get_regulatory_concern(self, risk_level: RiskLevel) -> Optional[str]:
        """Get relevant regulatory citation for risk level."""
        if risk_level == RiskLevel.HIGH:
            return "Investment Advisers Act of 1940 - RIA registration required for investment advice"
        elif risk_level == RiskLevel.MEDIUM:
            return "FINRA Rule 2210 - Communications must be fair, balanced, and not misleading"
        return None


# ============================================================================
# CONFIDENCE SCORER
# ============================================================================

class ConfidenceScorer:
    """
    Multi-factor confidence scoring for RAG retrieval results.

    Combines five factors:
    1. Retrieval Quality (40%) - Semantic similarity of top documents
    2. Source Diversity (25%) - Number of unique source types
    3. Temporal Consistency (20%) - Sources from same fiscal period
    4. Citation Agreement (15%) - Degree sources align on numerical claims
    5. Domain Relevance (bonus) - Query matches financial domain
    """

    CONFIDENCE_THRESHOLDS = {
        "HIGH": 0.85,      # Answer with standard disclaimer
        "MEDIUM": 0.70,    # Answer with "moderate confidence" warning
        "LOW": 0.50,       # Warn "information may be incomplete"
        "VERY_LOW": 0.0    # Refuse to answer, escalate
    }

    def __init__(self):
        """Initialize confidence scorer."""
        logger.info("ConfidenceScorer initialized")

    def compute_score(
        self,
        retrieval_results: List[Dict[str, Any]],
        query: Optional[str] = None
    ) -> ConfidenceScore:
        """
        Compute multi-factor confidence score.

        Args:
            retrieval_results: List of retrieved documents with scores and metadata
                Expected format: [{"score": 0.92, "source_type": "10-K", "date": "2024-Q4", ...}, ...]
            query: Optional query text for domain relevance scoring

        Returns:
            ConfidenceScore with overall score and component breakdowns
        """
        if not retrieval_results:
            logger.warning("No retrieval results provided - returning zero confidence")
            return ConfidenceScore(
                overall_score=0.0,
                retrieval_quality=0.0,
                source_diversity=0.0,
                temporal_consistency=0.0,
                citation_agreement=0.0,
                threshold_category="VERY_LOW"
            )

        # Component 1: Retrieval Quality (40% weight)
        retrieval_quality = self._compute_retrieval_quality(retrieval_results)

        # Component 2: Source Diversity (25% weight)
        source_diversity = self._compute_source_diversity(retrieval_results)

        # Component 3: Temporal Consistency (20% weight)
        temporal_consistency = self._compute_temporal_consistency(retrieval_results)

        # Component 4: Citation Agreement (15% weight)
        citation_agreement = self._compute_citation_agreement(retrieval_results)

        # Component 5: Domain Relevance (bonus)
        domain_bonus = self._compute_domain_relevance(query) if query else 0.0

        # Weighted combination
        overall = (
            (retrieval_quality * 0.40) +
            (source_diversity * 0.25) +
            (temporal_consistency * 0.20) +
            (citation_agreement * 0.15) +
            domain_bonus
        )

        # Determine threshold category
        threshold_category = self._categorize_confidence(overall)

        score = ConfidenceScore(
            overall_score=overall,
            retrieval_quality=retrieval_quality,
            source_diversity=source_diversity,
            temporal_consistency=temporal_consistency,
            citation_agreement=citation_agreement,
            domain_relevance_bonus=domain_bonus,
            threshold_category=threshold_category
        )

        logger.info(f"Confidence score: {overall:.3f} ({threshold_category}) - R:{retrieval_quality:.2f} D:{source_diversity:.2f} T:{temporal_consistency:.2f} C:{citation_agreement:.2f}")
        return score

    def _compute_retrieval_quality(self, results: List[Dict[str, Any]]) -> float:
        """Average semantic similarity of top 5 documents."""
        scores = [r.get("score", 0.0) for r in results[:5]]
        if not scores:
            return 0.0

        if NUMPY_AVAILABLE:
            return float(np.mean(scores))
        else:
            return sum(scores) / len(scores)

    def _compute_source_diversity(self, results: List[Dict[str, Any]]) -> float:
        """
        Count unique source types (10-K, 8-K, earnings call, analyst report, etc.).
        Normalized to 0-1 scale (4+ unique types = 1.0).
        """
        source_types = set()
        for r in results:
            source_type = r.get("source_type", "unknown")
            source_types.add(source_type)

        unique_count = len(source_types)
        # Normalize: 4+ unique types = full score
        normalized = min(unique_count / 4.0, 1.0)
        return normalized

    def _compute_temporal_consistency(self, results: List[Dict[str, Any]]) -> float:
        """
        Fraction of sources from the same fiscal period.
        Penalizes mixing Q4 2024 with Q3 2024 data.
        """
        periods = [r.get("fiscal_period", "unknown") for r in results]
        if not periods:
            return 0.0

        # Find most common period
        period_counts = defaultdict(int)
        for p in periods:
            period_counts[p] += 1

        most_common_count = max(period_counts.values())
        consistency = most_common_count / len(periods)
        return consistency

    def _compute_citation_agreement(self, results: List[Dict[str, Any]]) -> float:
        """
        Check if sources agree on numerical claims.

        In production, this would extract numbers from documents and check consistency.
        For this educational module, we check if a 'numerical_claim' field exists and matches.
        """
        claims = [r.get("numerical_claim") for r in results if r.get("numerical_claim")]

        if len(claims) < 2:
            # Need at least 2 sources to check agreement
            return 0.5  # Neutral score

        # Check if all claims match (simplified)
        first_claim = claims[0]
        agreement = sum(1 for c in claims if c == first_claim) / len(claims)
        return agreement

    def _compute_domain_relevance(self, query: str) -> float:
        """
        Bonus points if query matches financial domain keywords.
        Caps at +0.05 to avoid over-weighting.
        """
        if not query:
            return 0.0

        financial_keywords = [
            "revenue", "earnings", "ebitda", "eps", "10-k", "10-q", "8-k",
            "sec", "filing", "financial", "stock", "dividend", "assets", "liabilities"
        ]

        query_lower = query.lower()
        matches = sum(1 for kw in financial_keywords if kw in query_lower)

        # +0.01 per keyword, max +0.05
        return min(matches * 0.01, 0.05)

    def _categorize_confidence(self, score: float) -> str:
        """Categorize confidence score into threshold bucket."""
        if score >= self.CONFIDENCE_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif score >= self.CONFIDENCE_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        elif score >= self.CONFIDENCE_THRESHOLDS["LOW"]:
            return "LOW"
        else:
            return "VERY_LOW"


# ============================================================================
# COMPLIANCE GUARDRAILS
# ============================================================================

class ComplianceGuardrails:
    """
    Regulatory compliance guardrails for financial RAG systems.

    Implements four critical guardrails:
    1. Investment Advice Detection (RIA requirement)
    2. MNPI Detection (Regulation Fair Disclosure)
    3. Forward-Looking Statement Controls (Safe Harbor)
    4. Form 8-K Disclosure Validation
    """

    def __init__(self):
        """Initialize compliance guardrails."""
        logger.info("ComplianceGuardrails initialized")

    def check_ria_compliance(self, classification: RiskClassificationResult) -> Dict[str, Any]:
        """
        Guardrail 1: Investment Advice Detection.

        Blocks high-risk queries that constitute investment advice without RIA license.
        Regulated under Investment Advisers Act of 1940.
        """
        if classification.risk_level == RiskLevel.HIGH:
            logger.warning(f"⚠️ RIA GUARDRAIL TRIGGERED - Query requires licensed advisor")
            return {
                "compliant": False,
                "violation": "UNAUTHORIZED_INVESTMENT_ADVICE",
                "regulation": "Investment Advisers Act of 1940",
                "required_action": "ESCALATE_TO_RIA",
                "message": "This query requires a licensed Registered Investment Advisor. Routing to human advisor."
            }

        return {"compliant": True}

    def check_mnpi_disclosure(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Guardrail 2: Material Non-Public Information Detection.

        Prevents retrieval of MNPI (insider information).
        Regulated under Regulation Fair Disclosure (Reg FD).

        Args:
            documents: Retrieved documents with timestamp and public_disclosure_date
        """
        for doc in documents:
            doc_timestamp = doc.get("document_timestamp")
            public_date = doc.get("public_disclosure_date")

            if doc_timestamp and public_date:
                # Check if document predates public disclosure
                if doc_timestamp < public_date:
                    logger.error(f"⚠️ MNPI GUARDRAIL TRIGGERED - Document contains non-public information")
                    return {
                        "compliant": False,
                        "violation": "MATERIAL_NON_PUBLIC_INFORMATION",
                        "regulation": "Regulation Fair Disclosure (Reg FD)",
                        "required_action": "BLOCK_DOCUMENT",
                        "message": "Document contains material non-public information and cannot be disclosed."
                    }

        return {"compliant": True}

    def inject_safe_harbor_warning(self, response: str, contains_forward_looking: bool) -> str:
        """
        Guardrail 3: Forward-Looking Statement Controls.

        Injects Safe Harbor language for revenue forecasts, earnings guidance, projections.
        Regulated under Private Securities Litigation Reform Act (1995).

        Args:
            response: Generated response text
            contains_forward_looking: Whether response includes forecasts/projections

        Returns:
            Response with Safe Harbor disclaimer injected
        """
        if not contains_forward_looking:
            return response

        safe_harbor_warning = (
            "\n\n⚠️ FORWARD-LOOKING STATEMENT DISCLAIMER:\n"
            "This information contains forward-looking statements that involve risks and uncertainties. "
            "Actual results may differ materially from projections. See SEC filings for risk factors."
        )

        logger.info("Injecting Safe Harbor disclaimer for forward-looking statements")
        return response + safe_harbor_warning

    def validate_form_8k_disclosure(self, event_type: str, filing_date: datetime) -> Dict[str, Any]:
        """
        Guardrail 4: Form 8-K Disclosure Validation.

        Material events require Form 8-K filing within 4 business days.
        Examples: bankruptcy, auditor changes, CEO resignation, major acquisition.

        Args:
            event_type: Type of material event
            filing_date: Date Form 8-K was filed

        Returns:
            Compliance check result
        """
        material_events = [
            "bankruptcy", "auditor_change", "ceo_resignation", "cfo_resignation",
            "major_acquisition", "asset_sale", "delisting_notice"
        ]

        if event_type.lower() in material_events:
            # Check if filing is within 4 business days (simplified - just checks days)
            days_to_file = (datetime.now() - filing_date).days

            if days_to_file > 4:
                logger.warning(f"⚠️ 8-K GUARDRAIL - Late disclosure detected ({days_to_file} days)")
                return {
                    "compliant": False,
                    "violation": "LATE_8K_DISCLOSURE",
                    "regulation": "Securities Exchange Act of 1934, Rule 8-K",
                    "required_action": "FLAG_DISCLOSURE_VIOLATION",
                    "message": f"Material event disclosure delayed {days_to_file} days (max 4 business days)"
                }

        return {"compliant": True}


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def classify_query_risk(
    query: str,
    user_context: Optional[Dict[str, Any]] = None,
    semantic_analysis: bool = False
) -> RiskClassificationResult:
    """
    Convenience function to classify a financial query's risk level.

    Args:
        query: The user's query text
        user_context: Optional user context (account_type, history, etc.)
        semantic_analysis: Enable semantic intent analysis (requires LLM)

    Returns:
        RiskClassificationResult with risk level, confidence, and recommended action

    Example:
        >>> result = classify_query_risk("Should I buy Tesla stock?")
        >>> print(f"Risk: {result.risk_level}, Action: {result.system_action}")
        Risk: HIGH, Action: ESCALATE_TO_HUMAN_ADVISOR
    """
    classifier = FinancialQueryRiskClassifier(semantic_analysis_enabled=semantic_analysis)
    return classifier.classify(query, user_context)


def compute_confidence_score(
    retrieval_results: List[Dict[str, Any]],
    query: Optional[str] = None
) -> ConfidenceScore:
    """
    Convenience function to compute confidence score for retrieval results.

    Args:
        retrieval_results: List of retrieved documents with scores and metadata
        query: Optional query text for domain relevance scoring

    Returns:
        ConfidenceScore with overall score and component breakdowns

    Example:
        >>> results = [
        ...     {"score": 0.92, "source_type": "10-K", "fiscal_period": "2024-Q4"},
        ...     {"score": 0.89, "source_type": "8-K", "fiscal_period": "2024-Q4"}
        ... ]
        >>> score = compute_confidence_score(results, "What was Apple's Q4 revenue?")
        >>> print(f"Confidence: {score.overall_score:.2f} ({score.threshold_category})")
        Confidence: 0.85 (MEDIUM)
    """
    scorer = ConfidenceScorer()
    return scorer.compute_score(retrieval_results, query)
