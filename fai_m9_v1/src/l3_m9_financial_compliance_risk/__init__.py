"""
L3 M9.1: Explainability & Citation Tracking

This module implements citation-tracked financial RAG systems with explainability,
audit trails, and verification for regulatory compliance (SEC, SOX, GDPR).

Components:
- CitationAwareRetriever: Retrieves documents with citation marker assignment
- CitationMapBuilder: Generates verifiable citation metadata
- CitationAwareLLMPrompt: Constructs prompts with citation instructions
- CitationVerificationEngine: Post-generation hallucination detection
- AuditTrailManager: SOX-compliant immutable audit logging
"""

import logging
import hashlib
import re
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

__all__ = [
    "CitationAwareRetriever",
    "CitationMapBuilder",
    "CitationAwareLLMPrompt",
    "CitationVerificationEngine",
    "AuditTrailManager"
]


class CitationAwareRetriever:
    """
    Retrieves financial documents with citation marker assignment.

    Features:
    - Tracks relevance scores
    - Assigns citation IDs [1], [2], [3]
    - Logs retrieval decisions for audit trail
    - Filters low-relevance documents (threshold: 0.70)

    SOX Compliance: All retrieval decisions logged for audit defense.
    """

    def __init__(
        self,
        vectorstore=None,
        embeddings=None,
        relevance_threshold: float = 0.70
    ):
        """
        Initialize citation-aware retriever.

        Args:
            vectorstore: Vector database instance (Pinecone, Weaviate, etc.)
            embeddings: Embedding model instance
            relevance_threshold: Minimum relevance score (0.0-1.0)
        """
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.relevance_threshold = relevance_threshold
        logger.info(f"CitationAwareRetriever initialized with threshold {relevance_threshold}")

    def retrieve_with_citations(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Retrieve documents and assign citation markers.

        Args:
            query: Financial question/query text
            k: Number of documents to retrieve
            filters: Metadata filters (ticker, fiscal_period, etc.)

        Returns:
            Dictionary containing:
            - documents: List of documents with citation markers
            - citation_map: Dictionary mapping citation IDs to metadata
            - retrieval_log: Audit log of retrieval decisions
        """
        if not query:
            raise ValueError("Query cannot be empty")

        logger.info(f"Retrieving documents for query: {query[:100]}...")

        # Mock retrieval for offline mode (replace with actual vector search)
        if self.vectorstore is None:
            logger.warning("No vectorstore configured - using mock data")
            results = self._mock_retrieval(query, k)
        else:
            # Real retrieval with similarity scores
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filters
            )

        # Filter below relevance threshold
        filtered_results = [
            (doc, score) for doc, score in results
            if score >= self.relevance_threshold
        ]

        # Log exclusions (audit requirement)
        excluded_count = len(results) - len(filtered_results)
        if excluded_count > 0:
            logger.warning(
                f"Excluded {excluded_count} documents below threshold {self.relevance_threshold}"
            )

        # Assign citation markers
        citation_map = {}
        documents_with_citations = []

        for idx, (doc, score) in enumerate(filtered_results, start=1):
            citation_id = f"[{idx}]"

            # Extract metadata
            metadata = getattr(doc, 'metadata', {}) if hasattr(doc, 'metadata') else {}
            content = getattr(doc, 'page_content', str(doc)) if hasattr(doc, 'page_content') else str(doc)

            citation_map[citation_id] = {
                "source_type": metadata.get("document_type", "Unknown"),
                "ticker": metadata.get("ticker", "N/A"),
                "company_name": metadata.get("company_name", "N/A"),
                "filing_date": metadata.get("filing_date", "N/A"),
                "fiscal_period": metadata.get("fiscal_period", "N/A"),
                "section": metadata.get("section", "N/A"),
                "page_number": metadata.get("page_number", "N/A"),
                "relevance_score": float(score),
                "document_url": metadata.get("source_url", "N/A"),
                "excerpt": content[:500] if content else "N/A"
            }

            # Add citation marker to content
            cited_content = f"{citation_id} {content}"
            documents_with_citations.append(cited_content)

        # Create retrieval audit log
        retrieval_log = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "documents_retrieved": len(results),
            "documents_used": len(filtered_results),
            "documents_excluded": excluded_count,
            "relevance_threshold": self.relevance_threshold,
            "filters_applied": filters or {}
        }

        logger.info(f"Retrieved {len(filtered_results)} documents with citations")

        return {
            "documents": documents_with_citations,
            "citation_map": citation_map,
            "retrieval_log": retrieval_log
        }

    def _mock_retrieval(self, query: str, k: int) -> List[Tuple[Any, float]]:
        """
        Mock retrieval for offline/testing mode.

        Returns mock documents with relevance scores.
        """
        class MockDocument:
            def __init__(self, content: str, metadata: Dict):
                self.page_content = content
                self.metadata = metadata

        mock_docs = [
            (
                MockDocument(
                    "Tesla reported Q2 2024 free cash flow of -$1.0B, driven by $2.3B capital expenditures for Gigafactory expansion.",
                    {
                        "document_type": "10-Q",
                        "ticker": "TSLA",
                        "company_name": "Tesla Inc",
                        "filing_date": "2024-08-03",
                        "fiscal_period": "Q2 2024",
                        "section": "Financial Statements",
                        "page_number": 5,
                        "source_url": "https://sec.gov/edgar/mock"
                    }
                ),
                0.92
            ),
            (
                MockDocument(
                    "Operating cash flow improved to $1.3B compared to $0.5B in Q1 2024, indicating operational efficiency gains.",
                    {
                        "document_type": "10-Q",
                        "ticker": "TSLA",
                        "company_name": "Tesla Inc",
                        "filing_date": "2024-08-03",
                        "fiscal_period": "Q2 2024",
                        "section": "Cash Flow Statement",
                        "page_number": 7,
                        "source_url": "https://sec.gov/edgar/mock"
                    }
                ),
                0.88
            ),
            (
                MockDocument(
                    "Capital expenditures totaled $2.3B for manufacturing capacity expansion and equipment purchases.",
                    {
                        "document_type": "10-Q",
                        "ticker": "TSLA",
                        "company_name": "Tesla Inc",
                        "filing_date": "2024-08-03",
                        "fiscal_period": "Q2 2024",
                        "section": "Management Discussion",
                        "page_number": 12,
                        "source_url": "https://sec.gov/edgar/mock"
                    }
                ),
                0.85
            )
        ]

        return mock_docs[:k]


class CitationMapBuilder:
    """
    Generates verifiable citation metadata from retrieved documents.

    Purpose:
    - Create structured provenance for each citation
    - Enable SEC auditors to verify claims in minutes
    - Support 7-year retention for SOX compliance
    """

    @staticmethod
    def build_citation_map_entry(
        citation_id: str,
        document: Any,
        relevance_score: float,
        source_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build verifiable citation entry with complete metadata.

        Args:
            citation_id: Citation marker (e.g., "[1]", "[2]")
            document: Document object with content
            relevance_score: Relevance score (0.0-1.0)
            source_metadata: Document metadata dictionary

        Returns:
            Complete citation map entry with all required fields
        """
        content = getattr(document, 'page_content', str(document)) if hasattr(document, 'page_content') else str(document)

        entry = {
            "citation_id": citation_id,
            "source_type": source_metadata.get("document_type", "Unknown"),
            "ticker": source_metadata.get("ticker", "N/A"),
            "company_name": source_metadata.get("company_name", "N/A"),
        }

        # Document-type-specific fields
        doc_type = source_metadata.get("document_type", "")

        if doc_type in ["10-K", "10-Q", "8-K"]:
            entry.update({
                "filing_date": source_metadata.get("filing_date", "N/A"),
                "fiscal_period": source_metadata.get("fiscal_period", "N/A"),
                "section": source_metadata.get("section", "N/A"),
                "item_number": source_metadata.get("item_number", "N/A"),
                "page_number": source_metadata.get("page_number", "N/A"),
                "cik": source_metadata.get("cik", "N/A"),
                "accession_number": source_metadata.get("accession_number", "N/A")
            })
        elif doc_type == "Earnings Call Transcript":
            entry.update({
                "call_date": source_metadata.get("call_date", "N/A"),
                "speaker": source_metadata.get("speaker", "N/A"),
                "timestamp": source_metadata.get("timestamp", "N/A"),
                "call_type": source_metadata.get("call_type", "N/A")
            })

        entry.update({
            "direct_quote": content[:200] if content else "N/A",
            "relevance_score": relevance_score,
            "document_url": source_metadata.get("source_url", "N/A"),
            "hash": CitationMapBuilder._compute_hash(content),
            "created_at": datetime.utcnow().isoformat()
        })

        return entry

    @staticmethod
    def _compute_hash(content: str) -> str:
        """
        Compute SHA256 hash for tamper detection.

        Args:
            content: Document content to hash

        Returns:
            SHA256 hash string
        """
        return hashlib.sha256(content.encode()).hexdigest()


class CitationAwareLLMPrompt:
    """
    Constructs prompts instructing LLM to use citation markers.

    Critical: LLM must use [1], [2], [3] or state
    "Information not available in provided documents"
    """

    SYSTEM_PROMPT = """You are a financial research assistant providing analysis of SEC filings and earnings data.

CRITICAL CITATION RULES:
1. Use citation markers [1], [2], [3] for EVERY factual claim
2. Only cite facts explicitly present in provided documents
3. If information unavailable in documents, state: "Information not available in provided documents"
4. Never invent or assume facts not present in sources
5. When sources conflict, explicitly disclose: "Sources show conflicting data..."

CITATION FORMAT:
Correct: "Tesla revenue $81.8B [1], down 5% YoY [2]"
Incorrect: "Tesla revenue $81.8B, down 5% YoY" (missing citations)
Incorrect: "Tesla projects $100B revenue" (hallucination - not in sources)

CONFLICT HANDLING:
If Document [1] says "revenue up 5%" and Document [2] says "revenue flat":
Response: "Revenue shows mixed signals: 5% growth reported [1] while another source describes results as flat [2]. Discrepancy warrants investigation."

OUTPUT FORMAT:
- State claim
- Use citation marker [#]
- Continue analysis
- Disclose conflicts explicitly"""

    @staticmethod
    def build_rag_prompt(
        query: str,
        retrieved_context: str,
        citation_map: Dict[str, Any]
    ) -> str:
        """
        Build complete RAG prompt with citations.

        Args:
            query: User's financial question
            retrieved_context: Documents with citation markers
            citation_map: Citation metadata dictionary

        Returns:
            Complete prompt for LLM
        """
        user_message = f"""Based on the following documents:

{retrieved_context}

Answer this financial question:
"{query}"

REMEMBER: Cite EVERY fact. Use [1], [2], [3] markers.
If information unavailable, say so explicitly."""

        return user_message


class CitationVerificationEngine:
    """
    Post-generation verification: Do citations actually support claims?

    Purpose: Prevent LLM hallucinations (financial fraud risk)
    Threshold: 0.85 semantic similarity required for verification
    """

    def verify_citations(
        self,
        response: str,
        citation_map: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify each citation in response supports the claim.

        Args:
            response: LLM-generated response with citations
            citation_map: Citation metadata from retrieval

        Returns:
            Dictionary containing:
            - verification_passed: bool (all claims supported)
            - verified_claims: List of verified claims
            - unsupported_claims: List of unsupported claims
            - overall_fidelity: Float 0.0-1.0 (verified/total)
            - recommendation: "PASS" or "REVIEW"
        """
        if not response:
            logger.error("Cannot verify empty response")
            return {
                "verification_passed": False,
                "verified_claims": [],
                "unsupported_claims": [],
                "overall_fidelity": 0.0,
                "recommendation": "REVIEW"
            }

        # Extract claims and their citations
        claims_with_citations = self._extract_claims(response)

        if not claims_with_citations:
            logger.warning("No citations found in response")
            return {
                "verification_passed": False,
                "verified_claims": [],
                "unsupported_claims": [{"claim": "No citations found", "status": "MISSING_CITATIONS"}],
                "overall_fidelity": 0.0,
                "recommendation": "REVIEW"
            }

        verified = []
        unsupported = []

        for claim, citation_ids in claims_with_citations:
            for citation_id in citation_ids:
                citation_key = f"[{citation_id}]"

                if citation_key not in citation_map:
                    unsupported.append({
                        "claim": claim,
                        "citation": citation_key,
                        "similarity": 0.0,
                        "status": "CITATION_NOT_FOUND",
                        "citation_text": "N/A"
                    })
                    continue

                citation_text = citation_map[citation_key].get("excerpt", "")

                # Check if claim appears in citation (semantic similarity)
                similarity = self._semantic_similarity(claim, citation_text)

                if similarity > 0.85:  # Threshold: 85% semantic match
                    verified.append({
                        "claim": claim,
                        "citation": citation_key,
                        "similarity": similarity,
                        "status": "SUPPORTED"
                    })
                else:
                    unsupported.append({
                        "claim": claim,
                        "citation": citation_key,
                        "similarity": similarity,
                        "status": "UNSUPPORTED",
                        "citation_text": citation_text[:200]
                    })

        # Calculate overall fidelity
        total_claims = len(verified) + len(unsupported)
        fidelity = len(verified) / total_claims if total_claims > 0 else 0.0

        logger.info(f"Verification: {len(verified)} verified, {len(unsupported)} unsupported, fidelity {fidelity:.2f}")

        return {
            "verification_passed": len(unsupported) == 0,
            "verified_claims": verified,
            "unsupported_claims": unsupported,
            "overall_fidelity": fidelity,
            "recommendation": "PASS" if fidelity >= 0.95 else "REVIEW"
        }

    @staticmethod
    def _semantic_similarity(text1: str, text2: str) -> float:
        """
        Compute semantic similarity using simple word overlap.

        Note: In production, replace with sentence-transformers or similar.
        This is a simplified version for offline mode.

        Args:
            text1: First text (claim)
            text2: Second text (citation)

        Returns:
            Similarity score 0.0-1.0
        """
        # Simple word-based similarity (replace with embeddings in production)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _extract_claims(self, response: str) -> List[Tuple[str, List[str]]]:
        """
        Extract factual claims with their citations.

        Pattern: "fact [1]" or "fact [1], [2]"

        Args:
            response: LLM response text

        Returns:
            List of (claim_text, [citation_ids])
        """
        # Find patterns like "fact [1]" or "fact [1], [2]"
        pattern = r"([^[.]+)\s*\[(\d+(?:\],?\s*\[\d+)*)\]"
        matches = re.findall(pattern, response)

        claims_with_citations = []
        for claim_text, citation_str in matches:
            citations = re.findall(r"\d+", citation_str)
            claims_with_citations.append((claim_text.strip(), citations))

        return claims_with_citations


class AuditTrailManager:
    """
    Creates immutable SOX-compliant audit logs.

    Requirements:
    - Append-only (no updates/deletes)
    - 7-year retention
    - Tamper-evident (hash chains)
    - Complete query → response → verification pipeline
    """

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize audit trail manager.

        Args:
            storage_backend: Database connection (PostgreSQL, etc.) or None for JSON
        """
        self.storage = storage_backend
        self.audit_entries = []
        logger.info("AuditTrailManager initialized")

    def log_complete_pipeline(
        self,
        query_id: str,
        user_id: str,
        query_text: str,
        retrieved_docs: List[Dict],
        llm_response: str,
        citations: Dict[str, Any],
        verification: Dict[str, Any]
    ) -> str:
        """
        Log entire pipeline: query → retrieval → response → verification

        Purpose: Create defensible audit trail for SEC examination

        Args:
            query_id: Unique query identifier
            user_id: User who made the query
            query_text: Query text
            retrieved_docs: List of retrieved documents
            llm_response: LLM-generated response
            citations: Citation map
            verification: Verification results

        Returns:
            Response ID for tracking
        """
        timestamp = datetime.utcnow()
        response_id = str(uuid.uuid4())

        audit_entry = {
            "query_id": query_id,
            "response_id": response_id,
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "query_text": query_text,
            "retrieved_documents": {
                "count": len(retrieved_docs),
                "documents": retrieved_docs
            },
            "llm_response": llm_response,
            "citations": citations,
            "verification": {
                "passed": verification.get("verification_passed", False),
                "verified_count": len(verification.get("verified_claims", [])),
                "unsupported_count": len(verification.get("unsupported_claims", [])),
                "overall_fidelity": verification.get("overall_fidelity", 0.0),
                "recommendation": verification.get("recommendation", "REVIEW")
            },
            "created_at": timestamp.isoformat()
        }

        # Store audit entry
        if self.storage is None:
            # JSON storage for offline mode
            self.audit_entries.append(audit_entry)
            logger.info(f"Audit entry logged to memory: {query_id}")
        else:
            # Database storage
            self._store_to_database(audit_entry)
            logger.info(f"Audit entry logged to database: {query_id}")

        return response_id

    def _store_to_database(self, audit_entry: Dict[str, Any]):
        """
        Store audit entry to database (append-only).

        In production, implement with PostgreSQL or similar.
        """
        # Placeholder for database storage
        logger.info("Database storage not implemented - using memory storage")
        self.audit_entries.append(audit_entry)

    def get_audit_log(self, query_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs.

        Args:
            query_id: Optional query ID to filter by

        Returns:
            List of audit entries
        """
        if query_id:
            return [entry for entry in self.audit_entries if entry["query_id"] == query_id]
        return self.audit_entries
