"""
FastAPI application for L3 M8.1: Financial Terminology & Concept Embeddings

Provides REST API endpoints for financial domain-aware embedding and query processing.
SERVICE: PINECONE (vector database) + SENTENCE_TRANSFORMERS (local embeddings)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, List, Optional
import os

from src.l3_m8_financial_domain_knowledge_injection import (
    FinancialAcronymExpander,
    embed_with_domain_context,
    validate_semantic_quality,
    process_financial_query
)
from config import CLIENTS, PINECONE_ENABLED, EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M8.1: Financial Domain Knowledge API",
    description="Domain-aware embeddings for financial RAG systems with acronym expansion and semantic validation",
    version="1.0.0"
)


# Request/Response Models
class ExpandRequest(BaseModel):
    """Request model for acronym expansion"""
    text: str = Field(..., description="Financial text containing acronyms")


class ExpandResponse(BaseModel):
    """Response model for acronym expansion"""
    original_text: str
    expanded_text: str
    stats: Dict[str, Any]
    ambiguous_terms: List[Dict[str, Any]]


class EmbedRequest(BaseModel):
    """Request model for embedding generation"""
    text: str = Field(..., description="Text to embed")
    context_type: Optional[str] = Field("financial_analysis", description="Context type")


class EmbedResponse(BaseModel):
    """Response model for embedding generation"""
    result: Dict[str, Any]


class QueryRequest(BaseModel):
    """Request model for financial query processing"""
    query: str = Field(..., description="Financial query")
    top_k: Optional[int] = Field(5, description="Number of results to return")


class QueryResponse(BaseModel):
    """Response model for query processing"""
    result: Dict[str, Any]


class ValidationRequest(BaseModel):
    """Request model for semantic validation"""
    test_pairs: List[List[Any]] = Field(
        ...,
        description="List of [text1, text2, expected_similarity] triplets"
    )


class ValidationResponse(BaseModel):
    """Response model for semantic validation"""
    result: Dict[str, Any]


# Endpoints
@app.get("/")
def root():
    """Health check and status endpoint"""
    return {
        "status": "healthy",
        "module": "L3_M8_Financial_Domain_Knowledge_Injection",
        "services": {
            "pinecone_enabled": PINECONE_ENABLED,
            "pinecone_connected": "pinecone" in CLIENTS,
            "embedding_model_loaded": EMBEDDING_MODEL is not None
        },
        "endpoints": [
            "/expand",
            "/embed",
            "/query",
            "/validate",
            "/stats"
        ]
    }


@app.post("/expand", response_model=ExpandResponse)
def expand_acronyms_endpoint(request: ExpandRequest):
    """
    Expand financial acronyms in text.

    Handles 100+ terms across valuation, profitability, analysis, accounting,
    market, regulatory, balance sheet, and temporal categories.
    """
    try:
        expander = FinancialAcronymExpander()

        expanded = expander.expand_acronyms(request.text)
        stats = expander.get_expansion_stats(request.text)
        ambiguous = expander.detect_ambiguous_terms(request.text)

        return ExpandResponse(
            original_text=request.text,
            expanded_text=expanded,
            stats=stats,
            ambiguous_terms=ambiguous
        )

    except Exception as e:
        logger.error(f"Acronym expansion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed", response_model=EmbedResponse)
def embed_endpoint(request: EmbedRequest):
    """
    Generate domain-aware financial embeddings.

    Pipeline:
    1. Acronym expansion (100+ terms)
    2. Domain contextualization
    3. 384-dimensional embedding generation

    Requires sentence-transformers library (local, no API key needed).
    """
    if EMBEDDING_MODEL is None:
        return EmbedResponse(result={
            "error": "Embedding model not loaded",
            "message": "Install sentence-transformers: pip install sentence-transformers"
        })

    try:
        expander = FinancialAcronymExpander()
        result = embed_with_domain_context(
            request.text,
            expander=expander,
            offline=False
        )

        return EmbedResponse(result=result)

    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """
    End-to-end financial query processing.

    Pipeline:
    1. Acronym expansion with ambiguity detection
    2. Domain contextualization
    3. Embedding generation
    4. Pinecone vector search (if enabled)
    5. Source-attributed results

    If PINECONE_ENABLED is not set, returns embedding without search.
    """
    try:
        result = process_financial_query(
            query=request.query,
            offline=False,
            pinecone_enabled=PINECONE_ENABLED
        )

        return QueryResponse(result=result)

    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate", response_model=ValidationResponse)
def validate_endpoint(request: ValidationRequest):
    """
    Validate embedding semantic quality against benchmark pairs.

    Expects test_pairs as list of [text1, text2, expected_similarity] triplets.
    Returns accuracy metrics and per-pair results.

    Target: 88-90% accuracy on financial domain benchmarks.
    """
    if EMBEDDING_MODEL is None:
        return ValidationResponse(result={
            "error": "Embedding model not loaded",
            "message": "Install sentence-transformers: pip install sentence-transformers"
        })

    try:
        # Convert to list of tuples
        test_pairs = [(t[0], t[1], t[2]) for t in request.test_pairs]

        expander = FinancialAcronymExpander()
        result = validate_semantic_quality(
            test_pairs=test_pairs,
            expander=expander,
            offline=False
        )

        return ValidationResponse(result=result)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def stats_endpoint():
    """
    Get system statistics and configuration.

    Returns acronym dictionary size, model info, and service status.
    """
    expander = FinancialAcronymExpander()

    return {
        "acronym_dictionary_size": len(expander.acronym_dict),
        "ambiguous_terms_count": len(expander.ambiguous_terms),
        "embedding_model": "all-MiniLM-L6-v2" if EMBEDDING_MODEL else None,
        "embedding_dimensions": 384 if EMBEDDING_MODEL else None,
        "services": {
            "pinecone_enabled": PINECONE_ENABLED,
            "pinecone_connected": "pinecone" in CLIENTS,
            "embedding_model_loaded": EMBEDDING_MODEL is not None
        },
        "performance_targets": {
            "semantic_accuracy": "88-90%",
            "latency_p95": "<100ms",
            "false_positive_rate": "<5%",
            "expansion_coverage": ">90%"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
