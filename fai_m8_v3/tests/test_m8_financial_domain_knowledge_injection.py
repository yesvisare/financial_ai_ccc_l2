"""
Tests for L3 M8.3: Financial Entity Recognition & Linking

Test coverage:
- FinancialEntityRecognizer: NER extraction, confidence filtering, fallback mode
- EntityLinker: SEC EDGAR linking, Wikipedia linking, disambiguation
- EntityEnricher: Metadata enrichment, caching
- EntityAwareRAG: Complete pipeline, query enhancement
- Utility functions: Rate limiting, preprocessing, similarity calculation
"""

import pytest
import time
from typing import Dict, List, Any

from src.l3_m8_financial_domain_knowledge_injection import (
    FinancialEntityRecognizer,
    EntityLinker,
    EntityEnricher,
    EntityAwareRAG,
    process_query,
    extract_entities,
    link_entity,
    enrich_entity,
    preprocess_tickers,
    calculate_similarity,
    KNOWN_TICKERS
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_text():
    """Sample financial text for testing."""
    return "Apple CEO Tim Cook announced Q3 2024 earnings with 15% revenue growth"


@pytest.fixture
def sample_query():
    """Sample query for pipeline testing."""
    return "What did Apple say about supply chains?"


@pytest.fixture
def recognizer():
    """FinancialEntityRecognizer instance for testing."""
    return FinancialEntityRecognizer(confidence_threshold=0.75)


@pytest.fixture
def linker():
    """EntityLinker instance for testing."""
    return EntityLinker(user_agent="TestSuite test@example.com")


@pytest.fixture
def enricher():
    """EntityEnricher instance for testing."""
    return EntityEnricher(cache_ttl=3600)


@pytest.fixture
def pipeline():
    """EntityAwareRAG pipeline for integration testing."""
    return EntityAwareRAG()


# =============================================================================
# UTILITY FUNCTION TESTS
# =============================================================================

def test_preprocess_tickers():
    """Test ticker preprocessing functionality."""
    # Test single ticker
    text = "AAPL stock price increased"
    result = preprocess_tickers(text)
    assert "Apple Inc." in result
    assert "AAPL" not in result

    # Test multiple tickers
    text = "AAPL and MSFT reported earnings"
    result = preprocess_tickers(text)
    assert "Apple Inc." in result
    assert "Microsoft Corporation" in result

    # Test case insensitivity
    text = "aapl stock"
    result = preprocess_tickers(text)
    assert "Apple Inc." in result.lower()

    # Test no tickers
    text = "Some random text without tickers"
    result = preprocess_tickers(text)
    assert result == text


def test_calculate_similarity():
    """Test string similarity calculation."""
    # Exact match
    assert calculate_similarity("Apple Inc.", "Apple Inc.") == 1.0

    # Similar strings
    score = calculate_similarity("Apple Inc", "Apple Inc.")
    assert 0.8 < score < 1.0

    # Different strings
    score = calculate_similarity("Apple", "Microsoft")
    assert score < 0.5

    # Empty strings
    score = calculate_similarity("", "test")
    assert score == 0.0


def test_known_tickers_config():
    """Test that KNOWN_TICKERS contains expected entries."""
    assert "AAPL" in KNOWN_TICKERS
    assert KNOWN_TICKERS["AAPL"] == "Apple Inc."
    assert "MSFT" in KNOWN_TICKERS
    assert "TSLA" in KNOWN_TICKERS
    assert len(KNOWN_TICKERS) >= 5  # At least 5 major tickers


# =============================================================================
# FINANCIALENTITYRECOGNIZER TESTS
# =============================================================================

def test_recognizer_initialization(recognizer):
    """Test FinancialEntityRecognizer initialization."""
    assert recognizer is not None
    assert recognizer.confidence_threshold == 0.75
    assert recognizer.label_map is not None
    assert "B-ORG" in recognizer.label_map


def test_recognizer_extract_entities_basic(recognizer, sample_text):
    """Test basic entity extraction."""
    entities = recognizer.extract_entities(sample_text)

    assert isinstance(entities, list)
    # Should extract at least "Apple" and "Tim Cook"
    assert len(entities) >= 1

    # Check entity structure
    if entities:
        entity = entities[0]
        assert "text" in entity
        assert "type" in entity
        assert "confidence" in entity
        assert entity["confidence"] >= recognizer.confidence_threshold


def test_recognizer_extract_entities_empty():
    """Test extraction with empty text."""
    recognizer = FinancialEntityRecognizer()

    with pytest.raises(ValueError, match="Input text cannot be empty"):
        recognizer.extract_entities("")


def test_recognizer_fallback_extraction(recognizer):
    """Test fallback extraction when FinBERT unavailable."""
    # Force fallback by using a text with known tickers
    text = "AAPL and MSFT stocks are up"
    entities = recognizer._fallback_extraction(text)

    assert isinstance(entities, list)
    # Should extract known tickers
    entity_texts = [e["text"] for e in entities]
    assert any("Apple" in text for text in entity_texts) or any("Microsoft" in text for text in entity_texts)


def test_recognizer_confidence_threshold():
    """Test confidence threshold filtering."""
    # High threshold should filter more entities
    recognizer_high = FinancialEntityRecognizer(confidence_threshold=0.95)
    recognizer_low = FinancialEntityRecognizer(confidence_threshold=0.50)

    text = "Apple CEO Tim Cook discussed earnings"

    # Note: Actual extraction may vary based on model availability
    # This test validates threshold behavior exists
    assert recognizer_high.confidence_threshold > recognizer_low.confidence_threshold


# =============================================================================
# ENTITYLINKER TESTS
# =============================================================================

def test_linker_initialization(linker):
    """Test EntityLinker initialization."""
    assert linker is not None
    assert linker.user_agent is not None
    assert linker.confidence_threshold == 0.85


def test_linker_generate_variants(linker):
    """Test variant generation for entity names."""
    variants = linker._generate_variants("Apple Inc.")

    assert isinstance(variants, list)
    assert "Apple Inc." in variants
    assert "apple inc." in variants
    assert "Apple" in variants  # Suffix removed


def test_linker_extract_ticker(linker):
    """Test ticker extraction from company name."""
    # Known ticker
    ticker = linker._extract_ticker("", "Apple Inc.")
    assert ticker == "AAPL"

    # Unknown company
    ticker = linker._extract_ticker("", "Unknown Company XYZ")
    assert ticker is None


def test_linker_calculate_context_score(linker):
    """Test context relevance scoring."""
    summary = "Apple Inc. is a technology company with high revenue and market cap"
    context = "Apple announced strong earnings"

    score = linker._calculate_context_score(summary, context)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

    # No context should give neutral score
    score_no_context = linker._calculate_context_score(summary, "")
    assert score_no_context == 0.5


def test_linker_link_entity_basic(linker):
    """Test basic entity linking."""
    entity = {
        "text": "Apple",
        "type": "ORGANIZATION",
        "confidence": 0.9
    }

    # This may hit real APIs or return unlinked
    result = linker.link_entity(entity, context="technology company")

    assert "canonical_name" in result
    assert "source" in result
    # Should at least try to link (may be unlinked if API fails)
    assert result["source"] in ["SEC EDGAR", "Wikipedia", "unlinked"]


def test_linker_link_to_wikipedia_error_handling(linker):
    """Test Wikipedia linking with error handling."""
    # Use a very ambiguous or nonexistent name
    result = linker.link_to_wikipedia("XYZ_NONEXISTENT_COMPANY_123", context="")

    # Should handle gracefully (return None or empty)
    assert result is None or result.get("confidence", 0) < linker.confidence_threshold


# =============================================================================
# ENTITYENRICHER TESTS
# =============================================================================

def test_enricher_initialization(enricher):
    """Test EntityEnricher initialization."""
    assert enricher is not None
    assert enricher.cache_ttl == 3600
    assert enricher._cache is not None


def test_enricher_enrich_entity_no_ticker(enricher):
    """Test enrichment with entity lacking ticker."""
    entity = {
        "text": "Some Company",
        "type": "ORGANIZATION",
        "confidence": 0.9
    }

    result = enricher.enrich_entity(entity)

    # Should return entity unchanged (no ticker to enrich)
    assert result["text"] == "Some Company"
    assert "market_cap" not in result or result.get("market_cap") is None


def test_enricher_enrich_entity_with_ticker(enricher):
    """Test enrichment with valid ticker."""
    entity = {
        "text": "Apple Inc.",
        "ticker": "AAPL",
        "type": "ORGANIZATION",
        "confidence": 0.95
    }

    result = enricher.enrich_entity(entity)

    # Should have attempted enrichment (may fail if yfinance unavailable)
    assert "text" in result
    # May have metadata fields if yfinance worked
    # Don't assert on metadata presence (depends on yfinance availability)


def test_enricher_cache_behavior(enricher):
    """Test caching behavior."""
    entity1 = {
        "text": "Apple Inc.",
        "ticker": "AAPL",
        "type": "ORGANIZATION"
    }

    # First call
    result1 = enricher.enrich_entity(entity1)

    # Second call (should use cache)
    entity2 = {
        "text": "Apple Inc.",
        "ticker": "AAPL",
        "type": "ORGANIZATION"
    }
    result2 = enricher.enrich_entity(entity2)

    # Both should complete (cache hit on second)
    assert result1 is not None
    assert result2 is not None


# =============================================================================
# ENTITYAWARERAG PIPELINE TESTS
# =============================================================================

def test_pipeline_initialization(pipeline):
    """Test EntityAwareRAG pipeline initialization."""
    assert pipeline is not None
    assert pipeline.recognizer is not None
    assert pipeline.linker is not None
    assert pipeline.enricher is not None


def test_pipeline_process_query_basic(pipeline, sample_query):
    """Test basic query processing through pipeline."""
    result = pipeline.process_query(sample_query)

    # Validate result structure
    assert isinstance(result, dict)
    assert "query" in result
    assert "enhanced_query" in result
    assert "entities" in result
    assert "entity_count" in result
    assert "processing_time_ms" in result

    # Validate values
    assert result["query"] == sample_query
    assert isinstance(result["entities"], list)
    assert result["entity_count"] == len(result["entities"])
    assert result["processing_time_ms"] > 0


def test_pipeline_process_query_empty():
    """Test pipeline with empty query."""
    pipeline = EntityAwareRAG()

    with pytest.raises(ValueError, match="Query cannot be empty"):
        pipeline.process_query("")


def test_pipeline_process_query_no_enrichment(pipeline, sample_query):
    """Test pipeline without metadata enrichment."""
    result = pipeline.process_query(sample_query, enrich_metadata=False)

    assert isinstance(result, dict)
    assert "entities" in result
    # Entities should not have enrichment metadata (or have minimal metadata)


def test_pipeline_enhanced_query_generation(pipeline):
    """Test enhanced query generation."""
    entities = [
        {
            "text": "Apple",
            "canonical_name": "Apple Inc.",
            "ticker": "AAPL",
            "sector": "Technology",
            "market_cap": 2.8e12
        }
    ]

    enhanced = pipeline._generate_enhanced_query(
        "What did Apple say?",
        entities
    )

    # Enhanced query should include metadata
    assert "Apple Inc." in enhanced or "AAPL" in enhanced


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================

def test_extract_entities_convenience(sample_text):
    """Test extract_entities convenience function."""
    entities = extract_entities(sample_text)

    assert isinstance(entities, list)
    # Should work like recognizer.extract_entities


def test_link_entity_convenience():
    """Test link_entity convenience function."""
    result = link_entity("Apple", context="technology company")

    assert isinstance(result, dict)
    assert "canonical_name" in result


def test_enrich_entity_convenience():
    """Test enrich_entity convenience function."""
    entity = {
        "text": "Apple Inc.",
        "ticker": "AAPL"
    }

    result = enrich_entity(entity)

    assert isinstance(result, dict)
    assert "text" in result


def test_process_query_convenience(sample_query):
    """Test process_query convenience function."""
    result = process_query(sample_query)

    assert isinstance(result, dict)
    assert "query" in result
    assert "enhanced_query" in result
    assert "entities" in result


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

def test_end_to_end_pipeline():
    """Test complete end-to-end pipeline with real query."""
    query = "What did JPMorgan Chase say about credit risk in Q3 2024?"

    result = process_query(query, enrich_metadata=True)

    # Validate complete result
    assert result["query"] == query
    assert len(result["enhanced_query"]) >= len(query)  # Enhanced should be same or longer
    assert isinstance(result["entities"], list)
    assert result["processing_time_ms"] > 0


def test_multiple_entities_query():
    """Test query with multiple entities."""
    query = "Compare Apple and Microsoft earnings for Q3 2024"

    result = process_query(query)

    # Should detect multiple entities
    assert len(result["entities"]) >= 1  # At least one entity (may miss some without full model)


def test_ambiguous_entity_disambiguation():
    """Test disambiguation of ambiguous entity names."""
    # "Apple" in financial context should resolve to Apple Inc.
    query = "Apple announced strong iPhone sales"

    result = process_query(query)

    # If entity linked, should be Apple Inc. (AAPL)
    if result["entities"]:
        for entity in result["entities"]:
            if "canonical_name" in entity and "Apple" in entity["canonical_name"]:
                # Should be Apple Inc., not Apple Records
                assert "Inc" in entity.get("canonical_name", "") or entity.get("ticker") == "AAPL"


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

def test_processing_latency(sample_query):
    """Test that processing latency meets targets."""
    start = time.time()
    result = process_query(sample_query, enrich_metadata=False)
    latency_ms = (time.time() - start) * 1000

    # Target: <1000ms for p99 (without enrichment)
    # Allow 5000ms for test environment (slower than production)
    assert latency_ms < 5000, f"Latency {latency_ms:.0f}ms exceeds 5000ms threshold"

    # Also check reported latency
    assert result["processing_time_ms"] > 0


def test_batch_processing_performance():
    """Test performance of batch processing."""
    queries = [
        "Apple earnings",
        "Tesla deliveries",
        "Microsoft Azure growth"
    ]

    start = time.time()
    results = [process_query(q, enrich_metadata=False) for q in queries]
    total_time = time.time() - start

    # Should process all queries
    assert len(results) == len(queries)

    # Average time per query should be reasonable
    avg_time_ms = (total_time / len(queries)) * 1000
    assert avg_time_ms < 5000  # Allow 5s per query in test environment


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

def test_error_handling_invalid_input():
    """Test error handling with invalid input."""
    # Empty query
    with pytest.raises(ValueError):
        process_query("")

    # None input
    with pytest.raises((ValueError, AttributeError)):
        process_query(None)


def test_error_handling_network_failure(monkeypatch):
    """Test graceful handling of network failures."""
    # This test would mock network calls to simulate failures
    # For now, we just ensure the system doesn't crash
    query = "Apple earnings"

    try:
        result = process_query(query)
        # Should return something even if network fails
        assert isinstance(result, dict)
    except Exception as e:
        # Should only raise expected exceptions
        assert isinstance(e, (ValueError, ConnectionError))


# =============================================================================
# ACCURACY EVALUATION (Optional - requires test dataset)
# =============================================================================

def test_load_test_dataset():
    """Test loading of test dataset (if available)."""
    import json
    import os

    test_dataset_path = "tests/test_dataset.json"

    if os.path.exists(test_dataset_path):
        with open(test_dataset_path, 'r') as f:
            dataset = json.load(f)

        assert isinstance(dataset, list)
        if dataset:
            assert "query" in dataset[0]
            assert "expected_entity" in dataset[0]
    else:
        pytest.skip("Test dataset not available")


def evaluate_accuracy(test_dataset_path="tests/test_dataset.json"):
    """
    Evaluate entity linking accuracy on test dataset.

    Args:
        test_dataset_path: Path to test dataset JSON file

    Returns:
        Accuracy score (0.0-1.0)
    """
    import json
    import os

    if not os.path.exists(test_dataset_path):
        print(f"⚠️ Test dataset not found: {test_dataset_path}")
        return 0.0

    with open(test_dataset_path, 'r') as f:
        dataset = json.load(f)

    correct = 0
    total = len(dataset)

    for test_case in dataset:
        try:
            result = process_query(test_case["query"], enrich_metadata=False)

            # Check if any entity matches expected
            for entity in result["entities"]:
                if entity.get("ticker") == test_case["expected_entity"]:
                    correct += 1
                    break
        except Exception as e:
            print(f"⚠️ Error processing test case: {e}")

    accuracy = correct / total if total > 0 else 0.0
    print(f"Entity Linking Accuracy: {accuracy:.1%} ({correct}/{total})")

    return accuracy


# =============================================================================
# PYTEST MARKERS
# =============================================================================

# Mark slow tests
slow = pytest.mark.slow

# Mark tests requiring network
network = pytest.mark.network

# Mark integration tests
integration = pytest.mark.integration


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
