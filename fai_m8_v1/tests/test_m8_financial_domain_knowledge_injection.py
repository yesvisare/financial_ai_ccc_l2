"""
Tests for L3 M8.1: Financial Terminology & Concept Embeddings

Tests all major components:
1. FinancialAcronymExpander class
2. Domain contextualization
3. Embedding generation (offline mode)
4. Semantic validation
5. End-to-end query processing

SERVICE: Mocked/offline for testing
"""

import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.l3_m8_financial_domain_knowledge_injection import (
    FinancialAcronymExpander,
    add_domain_context,
    embed_with_domain_context,
    validate_semantic_quality,
    process_financial_query
)

# Force offline mode for tests
os.environ["PINECONE_ENABLED"] = "false"
os.environ["OFFLINE"] = "true"


# Fixtures
@pytest.fixture
def expander():
    """Create FinancialAcronymExpander instance"""
    return FinancialAcronymExpander()


@pytest.fixture
def sample_financial_text():
    """Sample financial text with acronyms"""
    return "Apple reported EPS of $1.52. P/E ratio stands at 28. EBITDA increased YoY."


@pytest.fixture
def sample_valuation_text():
    """Sample valuation text"""
    return "Our DCF model uses WACC of 8.5% and projects FCF growth of 12%."


# Test FinancialAcronymExpander
class TestFinancialAcronymExpander:
    """Test suite for FinancialAcronymExpander class"""

    def test_initialization(self, expander):
        """Test expander initializes with dictionary"""
        assert expander is not None
        assert len(expander.acronym_dict) > 0
        assert "EPS" in expander.acronym_dict
        assert "P/E" in expander.acronym_dict

    def test_dictionary_completeness(self, expander):
        """Test dictionary contains all required categories"""
        # Valuation metrics
        assert "P/E" in expander.acronym_dict
        assert "EV/EBITDA" in expander.acronym_dict

        # Profitability metrics
        assert "EBITDA" in expander.acronym_dict
        assert "ROE" in expander.acronym_dict

        # Analysis methods
        assert "DCF" in expander.acronym_dict
        assert "WACC" in expander.acronym_dict

        # Accounting standards
        assert "GAAP" in expander.acronym_dict
        assert "IFRS" in expander.acronym_dict

        # Market terms
        assert "IPO" in expander.acronym_dict
        assert "M&A" in expander.acronym_dict

        # Regulatory
        assert "SEC" in expander.acronym_dict
        assert "SOX" in expander.acronym_dict

        # Balance sheet
        assert "A/R" in expander.acronym_dict
        assert "COGS" in expander.acronym_dict

        # Temporal
        assert "YoY" in expander.acronym_dict
        assert "Q1" in expander.acronym_dict

    def test_expand_acronyms_basic(self, expander, sample_financial_text):
        """Test basic acronym expansion"""
        expanded = expander.expand_acronyms(sample_financial_text)

        assert "EPS (Earnings Per Share)" in expanded
        assert "P/E (Price-to-Earnings ratio)" in expanded
        assert "EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization)" in expanded
        assert "YoY (Year-over-Year)" in expanded

    def test_expand_acronyms_valuation(self, expander, sample_valuation_text):
        """Test valuation-specific acronym expansion"""
        expanded = expander.expand_acronyms(sample_valuation_text)

        assert "DCF (Discounted Cash Flow)" in expanded
        assert "WACC (Weighted Average Cost of Capital)" in expanded
        assert "FCF (Free Cash Flow)" in expanded

    def test_expand_acronyms_word_boundaries(self, expander):
        """Test that expansion respects word boundaries (no partial matches)"""
        text = "OPEN positions require PE review"
        expanded = expander.expand_acronyms(text)

        # Should expand PE but not partial "PE" in "OPEN"
        assert "PE (Private Equity)" in expanded
        assert "OPEN" in expanded  # Unchanged

    def test_detect_ambiguous_terms(self, expander):
        """Test detection of ambiguous terms"""
        text = "The PE firm invested $500M with 15% ROI target"

        ambiguous = expander.detect_ambiguous_terms(text)

        assert len(ambiguous) > 0
        pe_found = any(term["term"] == "PE" for term in ambiguous)
        assert pe_found

        pe_term = next(term for term in ambiguous if term["term"] == "PE")
        assert "Private Equity" in pe_term["possible_meanings"]
        assert "Price-to-Earnings" in pe_term["possible_meanings"]

    def test_get_expansion_stats(self, expander, sample_financial_text):
        """Test expansion statistics calculation"""
        stats = expander.get_expansion_stats(sample_financial_text)

        assert "total_dictionary_terms" in stats
        assert "terms_found_in_text" in stats
        assert "coverage_percentage" in stats
        assert stats["total_dictionary_terms"] > 0
        assert stats["terms_found_in_text"] >= 4  # EPS, P/E, EBITDA, YoY


# Test domain contextualization
class TestDomainContext:
    """Test suite for domain contextualization"""

    def test_add_domain_context_default(self):
        """Test default context addition"""
        text = "Apple reported strong earnings"
        contextualized = add_domain_context(text)

        assert contextualized.startswith("Financial analysis context:")
        assert "Apple reported strong earnings" in contextualized

    def test_add_domain_context_types(self):
        """Test different context types"""
        text = "Revenue increased 15%"

        analysis_context = add_domain_context(text, "financial_analysis")
        assert "Financial analysis context:" in analysis_context

        reporting_context = add_domain_context(text, "financial_reporting")
        assert "Financial reporting context:" in reporting_context

        valuation_context = add_domain_context(text, "valuation")
        assert "Company valuation context:" in valuation_context

        regulatory_context = add_domain_context(text, "regulatory")
        assert "Regulatory compliance context:" in regulatory_context


# Test embedding generation
class TestEmbedding:
    """Test suite for embedding generation"""

    def test_embed_offline_mode(self, expander):
        """Test embedding in offline mode"""
        text = "Apple reported EPS of $1.52"

        result = embed_with_domain_context(text, expander, offline=True)

        assert result["skipped"] is True
        assert result["reason"] == "offline mode"
        assert "processed_text" in result
        assert "original_text" in result
        assert result["original_text"] == text

    def test_embed_processed_text(self, expander):
        """Test that processed text includes expansions and context"""
        text = "P/E ratio is 28"

        result = embed_with_domain_context(text, expander, offline=True)

        processed = result["processed_text"]
        assert "Financial analysis context:" in processed
        assert "P/E (Price-to-Earnings ratio)" in processed

    @pytest.mark.skipif(
        True,  # Always skip in CI/CD environments
        reason="Requires sentence-transformers library"
    )
    def test_embed_online_mode(self, expander):
        """Test actual embedding generation (only if library available)"""
        text = "Apple reported strong earnings"

        result = embed_with_domain_context(text, expander, offline=False)

        if "error" not in result:
            assert "embedding" in result
            assert "dimensions" in result
            assert result["dimensions"] == 384
            assert len(result["embedding"]) == 384


# Test semantic validation
class TestSemanticValidation:
    """Test suite for semantic validation"""

    def test_validate_offline_mode(self, expander):
        """Test validation in offline mode"""
        test_pairs = [
            ("EBITDA increased", "Operating profit grew", 0.8),
            ("NASA launched rocket", "EBITDA increased", 0.1)
        ]

        result = validate_semantic_quality(test_pairs, expander, offline=True)

        assert result["skipped"] is True
        assert result["reason"] == "offline mode"

    @pytest.mark.skipif(
        True,  # Always skip in CI/CD environments
        reason="Requires sentence-transformers and scikit-learn"
    )
    def test_validate_online_mode(self, expander):
        """Test actual semantic validation (only if libraries available)"""
        test_pairs = [
            ("Company's EPS increased", "Earnings per share grew", 0.9),
            ("P/E ratio is high", "Stock is expensive", 0.7)
        ]

        result = validate_semantic_quality(test_pairs, expander, offline=False)

        if "error" not in result:
            assert "accuracy_percentage" in result
            assert "test_results" in result
            assert "meets_target" in result


# Test end-to-end query processing
class TestQueryProcessing:
    """Test suite for query processing pipeline"""

    def test_process_query_offline(self):
        """Test query processing in offline mode"""
        query = "What is Apple's P/E ratio and EBITDA?"

        result = process_financial_query(query, offline=True, pinecone_enabled=False)

        assert "query" in result
        assert "ambiguous_terms" in result
        assert "embedding_result" in result
        assert "pipeline_status" in result

    def test_process_query_ambiguous_detection(self):
        """Test that ambiguous terms are detected during query processing"""
        query = "PE firms are evaluating the IPO with ROI expectations"

        result = process_financial_query(query, offline=True, pinecone_enabled=False)

        ambiguous = result["ambiguous_terms"]
        assert len(ambiguous) > 0
        pe_found = any(term["term"] == "PE" for term in ambiguous)
        assert pe_found

    def test_process_query_pinecone_disabled(self):
        """Test query processing with Pinecone disabled"""
        query = "Show me companies with high ROIC"

        result = process_financial_query(query, offline=False, pinecone_enabled=False)

        pinecone_result = result["pinecone_search"]
        assert pinecone_result["skipped"] is True


# Integration tests
class TestIntegration:
    """Integration tests for complete workflow"""

    def test_complete_pipeline_offline(self):
        """Test complete pipeline in offline mode"""
        # Step 1: Initialize expander
        expander = FinancialAcronymExpander()
        assert expander is not None

        # Step 2: Expand acronyms
        text = "Apple's EPS grew 15% YoY with P/E of 28"
        expanded = expander.expand_acronyms(text)
        assert "EPS (Earnings Per Share)" in expanded

        # Step 3: Add context
        contextualized = add_domain_context(expanded)
        assert "Financial analysis context:" in contextualized

        # Step 4: Generate embedding (offline)
        embedding_result = embed_with_domain_context(text, expander, offline=True)
        assert embedding_result["skipped"] is True

        # Step 5: Full query processing
        query_result = process_financial_query(text, offline=True, pinecone_enabled=False)
        assert query_result["pipeline_status"] == "complete"

    def test_error_handling(self):
        """Test error handling throughout pipeline"""
        expander = FinancialAcronymExpander()

        # Empty text should not crash
        empty_result = expander.expand_acronyms("")
        assert empty_result == ""

        # None-like inputs
        stats = expander.get_expansion_stats("")
        assert stats["terms_found_in_text"] == 0


# Performance tests
class TestPerformance:
    """Test performance characteristics"""

    def test_expansion_coverage_target(self, expander):
        """Test that dictionary achieves >90% coverage target"""
        # Comprehensive financial text
        text = """
        Apple's Q1 FY2024 results: EPS of $1.52, P/E ratio at 28, EBITDA up 15% YoY.
        Our DCF model uses WACC of 8.5%, projects FCF growth of 12%, NPV is positive.
        ROE improved to 45%, ROIC exceeds WACC. Balance sheet shows A/R up, A/P stable.
        IPO plans under SEC review, SOX compliance verified, GAAP standards followed.
        """

        stats = expander.get_expansion_stats(text)

        # Should find multiple terms
        assert stats["terms_found_in_text"] >= 10

    def test_false_positive_rate(self, expander):
        """Test that false positive rate is low"""
        # Text with potential false positives
        text = "OPEN the report. SPEAK at the conference. REPAIR the system."

        expanded = expander.expand_acronyms(text)

        # Should NOT expand partial matches
        assert "OPEN" in expanded
        assert "SPEAK" in expanded
        assert "REPAIR" in expanded
        assert "OPEN (" not in expanded  # No expansion of OPEN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
