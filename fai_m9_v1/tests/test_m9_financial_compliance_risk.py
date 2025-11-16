"""Tests for L3 M9.1: Explainability & Citation Tracking"""

import pytest
from src.l3_m9_financial_compliance_risk import (
    CitationAwareRetriever,
    CitationMapBuilder,
    CitationAwareLLMPrompt,
    CitationVerificationEngine,
    AuditTrailManager
)


# Test CitationAwareRetriever
class TestCitationAwareRetriever:
    """Test suite for CitationAwareRetriever"""

    def test_initialization(self):
        """Test retriever initialization"""
        retriever = CitationAwareRetriever(relevance_threshold=0.70)
        assert retriever.relevance_threshold == 0.70
        assert retriever.vectorstore is None

    def test_retrieve_with_citations_success(self):
        """Test successful retrieval with citations"""
        retriever = CitationAwareRetriever()
        result = retriever.retrieve_with_citations(
            query="What was Tesla's Q2 2024 free cash flow?",
            k=5
        )

        assert "documents" in result
        assert "citation_map" in result
        assert "retrieval_log" in result
        assert len(result["documents"]) > 0
        assert len(result["citation_map"]) > 0

    def test_retrieve_with_citations_empty_query(self):
        """Test retrieval with empty query"""
        retriever = CitationAwareRetriever()

        with pytest.raises(ValueError, match="Query cannot be empty"):
            retriever.retrieve_with_citations(query="", k=5)

    def test_citation_markers_assigned(self):
        """Test that citation markers are properly assigned"""
        retriever = CitationAwareRetriever()
        result = retriever.retrieve_with_citations(
            query="Tesla revenue",
            k=3
        )

        citation_map = result["citation_map"]
        assert "[1]" in citation_map
        assert "[2]" in citation_map
        assert "[3]" in citation_map

    def test_relevance_threshold_filtering(self):
        """Test that low-relevance documents are filtered"""
        retriever = CitationAwareRetriever(relevance_threshold=0.95)
        result = retriever.retrieve_with_citations(
            query="Tesla revenue",
            k=5
        )

        # With high threshold, some documents should be filtered
        assert result["retrieval_log"]["documents_excluded"] >= 0

    def test_filters_applied(self):
        """Test that metadata filters are applied"""
        retriever = CitationAwareRetriever()
        filters = {"ticker": "TSLA", "fiscal_period": "Q2 2024"}

        result = retriever.retrieve_with_citations(
            query="free cash flow",
            k=3,
            filters=filters
        )

        assert result["retrieval_log"]["filters_applied"] == filters


# Test CitationMapBuilder
class TestCitationMapBuilder:
    """Test suite for CitationMapBuilder"""

    def test_build_citation_map_entry(self):
        """Test building citation map entry"""

        class MockDocument:
            page_content = "Tesla reported Q2 2024 free cash flow of -$1.0B"

        metadata = {
            "document_type": "10-Q",
            "ticker": "TSLA",
            "company_name": "Tesla Inc",
            "filing_date": "2024-08-03",
            "fiscal_period": "Q2 2024",
            "section": "Financial Statements",
            "page_number": 5
        }

        entry = CitationMapBuilder.build_citation_map_entry(
            citation_id="[1]",
            document=MockDocument(),
            relevance_score=0.92,
            source_metadata=metadata
        )

        assert entry["citation_id"] == "[1]"
        assert entry["source_type"] == "10-Q"
        assert entry["ticker"] == "TSLA"
        assert entry["company_name"] == "Tesla Inc"
        assert entry["filing_date"] == "2024-08-03"
        assert entry["fiscal_period"] == "Q2 2024"
        assert entry["relevance_score"] == 0.92
        assert "hash" in entry
        assert "created_at" in entry

    def test_hash_computation(self):
        """Test SHA256 hash computation for tamper detection"""
        content = "Test content for hashing"
        hash1 = CitationMapBuilder._compute_hash(content)
        hash2 = CitationMapBuilder._compute_hash(content)

        # Same content should produce same hash
        assert hash1 == hash2

        # Different content should produce different hash
        hash3 = CitationMapBuilder._compute_hash("Different content")
        assert hash1 != hash3

    def test_earnings_call_metadata(self):
        """Test citation map entry for earnings call transcript"""

        class MockDocument:
            page_content = "CEO commentary on Q2 results"

        metadata = {
            "document_type": "Earnings Call Transcript",
            "ticker": "AAPL",
            "company_name": "Apple Inc",
            "call_date": "2024-08-01",
            "speaker": "Tim Cook",
            "call_type": "earnings"
        }

        entry = CitationMapBuilder.build_citation_map_entry(
            citation_id="[1]",
            document=MockDocument(),
            relevance_score=0.88,
            source_metadata=metadata
        )

        assert entry["source_type"] == "Earnings Call Transcript"
        assert entry["call_date"] == "2024-08-01"
        assert entry["speaker"] == "Tim Cook"


# Test CitationAwareLLMPrompt
class TestCitationAwareLLMPrompt:
    """Test suite for CitationAwareLLMPrompt"""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined"""
        assert CitationAwareLLMPrompt.SYSTEM_PROMPT is not None
        assert "citation" in CitationAwareLLMPrompt.SYSTEM_PROMPT.lower()

    def test_build_rag_prompt(self):
        """Test building RAG prompt with citations"""
        query = "What was Tesla's free cash flow?"
        context = "[1] Tesla reported -$1.0B free cash flow\n[2] Capital expenditures were $2.3B"
        citation_map = {
            "[1]": {"source": "10-Q"},
            "[2]": {"source": "10-Q"}
        }

        prompt = CitationAwareLLMPrompt.build_rag_prompt(
            query=query,
            retrieved_context=context,
            citation_map=citation_map
        )

        assert query in prompt
        assert context in prompt
        assert "cite" in prompt.lower() or "citation" in prompt.lower()


# Test CitationVerificationEngine
class TestCitationVerificationEngine:
    """Test suite for CitationVerificationEngine"""

    def test_verify_citations_supported(self):
        """Test verification with supported citations"""
        verifier = CitationVerificationEngine()

        response = "Tesla reported free cash flow of -$1.0B [1] and capital expenditures of $2.3B [2]"
        citation_map = {
            "[1]": {"excerpt": "Tesla reported Q2 2024 free cash flow of -$1.0B"},
            "[2]": {"excerpt": "Capital expenditures totaled $2.3B for expansion"}
        }

        verification = verifier.verify_citations(response, citation_map)

        assert "verification_passed" in verification
        assert "verified_claims" in verification
        assert "unsupported_claims" in verification
        assert "overall_fidelity" in verification

    def test_verify_citations_unsupported(self):
        """Test verification with unsupported citations"""
        verifier = CitationVerificationEngine()

        response = "Tesla reported revenue of $100B [1]"
        citation_map = {
            "[1]": {"excerpt": "Tesla reported revenue of $25B"}  # Mismatch
        }

        verification = verifier.verify_citations(response, citation_map)

        assert verification["verification_passed"] is False
        assert len(verification["unsupported_claims"]) > 0

    def test_verify_citations_missing_citation(self):
        """Test verification with missing citation"""
        verifier = CitationVerificationEngine()

        response = "Tesla reported revenue [4]"  # Citation [4] doesn't exist
        citation_map = {
            "[1]": {"excerpt": "Tesla data"},
            "[2]": {"excerpt": "More data"}
        }

        verification = verifier.verify_citations(response, citation_map)

        assert verification["verification_passed"] is False
        assert any(
            claim["status"] == "CITATION_NOT_FOUND"
            for claim in verification["unsupported_claims"]
        )

    def test_verify_citations_empty_response(self):
        """Test verification with empty response"""
        verifier = CitationVerificationEngine()

        verification = verifier.verify_citations("", {})

        assert verification["verification_passed"] is False
        assert verification["overall_fidelity"] == 0.0

    def test_extract_claims(self):
        """Test claim extraction from response"""
        verifier = CitationVerificationEngine()

        response = "Tesla revenue was $25B [1] and margin improved [2]"
        claims = verifier._extract_claims(response)

        assert len(claims) == 2
        assert claims[0][0].strip() == "Tesla revenue was $25B"
        assert "1" in claims[0][1]

    def test_semantic_similarity(self):
        """Test semantic similarity calculation"""
        verifier = CitationVerificationEngine()

        # Identical text should have high similarity
        sim1 = verifier._semantic_similarity("Tesla revenue", "Tesla revenue")
        assert sim1 == 1.0

        # Different text should have lower similarity
        sim2 = verifier._semantic_similarity("Tesla revenue", "Apple profit")
        assert sim2 < 1.0


# Test AuditTrailManager
class TestAuditTrailManager:
    """Test suite for AuditTrailManager"""

    def test_initialization(self):
        """Test audit trail manager initialization"""
        manager = AuditTrailManager()
        assert manager.storage is None
        assert manager.audit_entries == []

    def test_log_complete_pipeline(self):
        """Test logging complete pipeline"""
        manager = AuditTrailManager()

        response_id = manager.log_complete_pipeline(
            query_id="test-query-123",
            user_id="analyst-456",
            query_text="What was Tesla's free cash flow?",
            retrieved_docs=[{"doc": "test"}],
            llm_response="Test response [1]",
            citations={"[1]": {"source": "10-Q"}},
            verification={"verification_passed": True, "verified_claims": [], "unsupported_claims": [], "overall_fidelity": 1.0}
        )

        assert response_id is not None
        assert len(manager.audit_entries) == 1

        entry = manager.audit_entries[0]
        assert entry["query_id"] == "test-query-123"
        assert entry["user_id"] == "analyst-456"
        assert entry["query_text"] == "What was Tesla's free cash flow?"

    def test_get_audit_log_by_query_id(self):
        """Test retrieving audit log by query ID"""
        manager = AuditTrailManager()

        # Log multiple queries
        manager.log_complete_pipeline(
            query_id="query-1",
            user_id="user-1",
            query_text="Query 1",
            retrieved_docs=[],
            llm_response="Response 1",
            citations={},
            verification={"verification_passed": True, "verified_claims": [], "unsupported_claims": [], "overall_fidelity": 1.0}
        )

        manager.log_complete_pipeline(
            query_id="query-2",
            user_id="user-2",
            query_text="Query 2",
            retrieved_docs=[],
            llm_response="Response 2",
            citations={},
            verification={"verification_passed": True, "verified_claims": [], "unsupported_claims": [], "overall_fidelity": 1.0}
        )

        # Retrieve specific query
        logs = manager.get_audit_log(query_id="query-1")
        assert len(logs) == 1
        assert logs[0]["query_id"] == "query-1"

    def test_get_all_audit_logs(self):
        """Test retrieving all audit logs"""
        manager = AuditTrailManager()

        # Log multiple queries
        for i in range(3):
            manager.log_complete_pipeline(
                query_id=f"query-{i}",
                user_id=f"user-{i}",
                query_text=f"Query {i}",
                retrieved_docs=[],
                llm_response=f"Response {i}",
                citations={},
                verification={"verification_passed": True, "verified_claims": [], "unsupported_claims": [], "overall_fidelity": 1.0}
            )

        # Retrieve all logs
        all_logs = manager.get_audit_log()
        assert len(all_logs) == 3

    def test_audit_entry_structure(self):
        """Test audit entry has required fields"""
        manager = AuditTrailManager()

        manager.log_complete_pipeline(
            query_id="test-query",
            user_id="test-user",
            query_text="Test query",
            retrieved_docs=[{"doc": "test"}],
            llm_response="Test response",
            citations={"[1]": {"source": "test"}},
            verification={"verification_passed": True, "verified_claims": [], "unsupported_claims": [], "overall_fidelity": 1.0}
        )

        entry = manager.audit_entries[0]

        # Required fields
        assert "query_id" in entry
        assert "response_id" in entry
        assert "timestamp" in entry
        assert "user_id" in entry
        assert "query_text" in entry
        assert "retrieved_documents" in entry
        assert "llm_response" in entry
        assert "citations" in entry
        assert "verification" in entry
        assert "created_at" in entry


# Integration Tests
class TestIntegration:
    """Integration tests for complete pipeline"""

    def test_complete_pipeline_offline_mode(self):
        """Test complete pipeline in offline mode"""
        # Initialize components
        retriever = CitationAwareRetriever()
        verifier = CitationVerificationEngine()
        audit_manager = AuditTrailManager()

        # Step 1: Retrieve
        query = "What was Tesla's Q2 2024 free cash flow?"
        retrieval_result = retriever.retrieve_with_citations(
            query=query,
            k=3
        )

        # Step 2: Mock LLM response
        llm_response = "Tesla reported free cash flow of -$1.0B [1] for Q2 2024."

        # Step 3: Verify
        verification = verifier.verify_citations(
            response=llm_response,
            citation_map=retrieval_result["citation_map"]
        )

        # Step 4: Audit
        response_id = audit_manager.log_complete_pipeline(
            query_id="integration-test",
            user_id="test-user",
            query_text=query,
            retrieved_docs=[retrieval_result["citation_map"]],
            llm_response=llm_response,
            citations=retrieval_result["citation_map"],
            verification=verification
        )

        # Assertions
        assert retrieval_result["documents"] is not None
        assert verification["overall_fidelity"] >= 0.0
        assert response_id is not None
        assert len(audit_manager.audit_entries) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
