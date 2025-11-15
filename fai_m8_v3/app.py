"""
FastAPI application for L3 M8.3: Financial Entity Recognition & Linking

API endpoints:
- POST /extract: Extract entities from text
- POST /link: Link entities to knowledge bases
- POST /enrich: Enrich entities with metadata
- POST /process: Complete pipeline (extract + link + enrich)
- GET /health: Health check
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
import time

from src.l3_m8_financial_domain_knowledge_injection import (
    FinancialEntityRecognizer,
    EntityLinker,
    EntityEnricher,
    EntityAwareRAG,
    process_query as process_query_func
)
from config import get_config, FINBERT_MODEL_PATH, SEC_EDGAR_USER_AGENT

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# FASTAPI APP INITIALIZATION
# =============================================================================

app = FastAPI(
    title="Financial Entity Recognition & Linking API",
    description="FinBERT-based entity recognition and linking for financial RAG systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (configure as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ExtractRequest(BaseModel):
    """Request model for entity extraction."""
    text: str = Field(..., min_length=1, description="Text to extract entities from")
    use_context: bool = Field(True, description="Apply context-aware filtering")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Apple CEO Tim Cook announced Q3 2024 earnings with 15% revenue growth",
                "use_context": True
            }
        }


class LinkRequest(BaseModel):
    """Request model for entity linking."""
    entity_text: str = Field(..., min_length=1, description="Entity name to link")
    context: str = Field("", description="Surrounding context for disambiguation")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_text": "Apple",
                "context": "Apple CEO Tim Cook discussed supply chain challenges"
            }
        }


class EnrichRequest(BaseModel):
    """Request model for entity enrichment."""
    entity: Dict[str, Any] = Field(..., description="Entity dictionary with ticker field")

    class Config:
        json_schema_extra = {
            "example": {
                "entity": {
                    "text": "Apple Inc.",
                    "ticker": "AAPL",
                    "type": "ORGANIZATION"
                }
            }
        }


class ProcessRequest(BaseModel):
    """Request model for complete pipeline processing."""
    query: str = Field(..., min_length=1, description="User query to process")
    enrich_metadata: bool = Field(True, description="Enable metadata enrichment")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What did Apple say about supply chains?",
                "enrich_metadata": True
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    service: str
    version: str
    finbert_model: str
    timestamp: float


class ExtractResponse(BaseModel):
    """Response model for entity extraction."""
    text: str
    entities: List[Dict[str, Any]]
    entity_count: int
    processing_time_ms: float


class LinkResponse(BaseModel):
    """Response model for entity linking."""
    entity_text: str
    linked_entity: Optional[Dict[str, Any]]
    processing_time_ms: float


class EnrichResponse(BaseModel):
    """Response model for entity enrichment."""
    enriched_entity: Dict[str, Any]
    processing_time_ms: float


class ProcessResponse(BaseModel):
    """Response model for complete pipeline."""
    query: str
    enhanced_query: str
    entities: List[Dict[str, Any]]
    entity_count: int
    processing_time_ms: float


# =============================================================================
# GLOBAL INSTANCES (lazy initialization)
# =============================================================================

_recognizer: Optional[FinancialEntityRecognizer] = None
_linker: Optional[EntityLinker] = None
_enricher: Optional[EntityEnricher] = None
_pipeline: Optional[EntityAwareRAG] = None


def get_recognizer() -> FinancialEntityRecognizer:
    """Get or initialize FinancialEntityRecognizer."""
    global _recognizer
    if _recognizer is None:
        logger.info("Initializing FinancialEntityRecognizer...")
        _recognizer = FinancialEntityRecognizer(model_path=FINBERT_MODEL_PATH)
    return _recognizer


def get_linker() -> EntityLinker:
    """Get or initialize EntityLinker."""
    global _linker
    if _linker is None:
        logger.info("Initializing EntityLinker...")
        _linker = EntityLinker(user_agent=SEC_EDGAR_USER_AGENT)
    return _linker


def get_enricher() -> EntityEnricher:
    """Get or initialize EntityEnricher."""
    global _enricher
    if _enricher is None:
        logger.info("Initializing EntityEnricher...")
        _enricher = EntityEnricher()
    return _enricher


def get_pipeline() -> EntityAwareRAG:
    """Get or initialize EntityAwareRAG pipeline."""
    global _pipeline
    if _pipeline is None:
        logger.info("Initializing EntityAwareRAG pipeline...")
        _pipeline = EntityAwareRAG(
            model_path=FINBERT_MODEL_PATH,
            user_agent=SEC_EDGAR_USER_AGENT
        )
    return _pipeline


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Financial Entity Recognition & Linking API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns service status and configuration.
    """
    return HealthResponse(
        status="healthy",
        service="Financial Entity Recognition & Linking",
        version="1.0.0",
        finbert_model=FINBERT_MODEL_PATH,
        timestamp=time.time()
    )


@app.post("/extract", response_model=ExtractResponse, tags=["Entity Extraction"])
async def extract_entities(request: ExtractRequest):
    """
    Extract financial entities from text using FinBERT.

    Returns:
        List of extracted entities with type, confidence, and position
    """
    try:
        start_time = time.time()

        recognizer = get_recognizer()
        entities = recognizer.extract_entities(
            text=request.text,
            use_context=request.use_context
        )

        processing_time = (time.time() - start_time) * 1000

        return ExtractResponse(
            text=request.text,
            entities=entities,
            entity_count=len(entities),
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.post("/link", response_model=LinkResponse, tags=["Entity Linking"])
async def link_entity(request: LinkRequest):
    """
    Link entity to knowledge bases (SEC EDGAR + Wikipedia).

    Returns:
        Linked entity with canonical name, ticker, CIK, and metadata
    """
    try:
        start_time = time.time()

        linker = get_linker()
        entity = {
            "text": request.entity_text,
            "type": "ORGANIZATION",
            "confidence": 1.0
        }

        linked = linker.link_entity(entity, context=request.context)

        processing_time = (time.time() - start_time) * 1000

        return LinkResponse(
            entity_text=request.entity_text,
            linked_entity=linked if linked.get("source") != "unlinked" else None,
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        logger.error(f"Entity linking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Linking failed: {str(e)}")


@app.post("/enrich", response_model=EnrichResponse, tags=["Entity Enrichment"])
async def enrich_entity(request: EnrichRequest):
    """
    Enrich entity with financial metadata (market cap, industry, ratios).

    Requires entity to have 'ticker' field.

    Returns:
        Enriched entity with market data
    """
    try:
        start_time = time.time()

        enricher = get_enricher()
        enriched = enricher.enrich_entity(request.entity)

        processing_time = (time.time() - start_time) * 1000

        return EnrichResponse(
            enriched_entity=enriched,
            processing_time_ms=round(processing_time, 2)
        )

    except Exception as e:
        logger.error(f"Entity enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@app.post("/process", response_model=ProcessResponse, tags=["Complete Pipeline"])
async def process_query(request: ProcessRequest):
    """
    Process query through complete entity recognition pipeline.

    Pipeline stages:
    1. Extract entities (FinBERT NER)
    2. Link entities (SEC EDGAR + Wikipedia)
    3. Enrich metadata (market data)
    4. Generate enhanced query for RAG

    Returns:
        Complete processing result with enhanced query and entity metadata
    """
    try:
        pipeline = get_pipeline()
        result = pipeline.process_query(
            query=request.query,
            enrich_metadata=request.enrich_metadata
        )

        return ProcessResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/stats", tags=["Statistics"])
async def get_stats():
    """
    Get API statistics and usage metrics.

    Returns:
        Service statistics
    """
    return {
        "service": "Financial Entity Recognition & Linking",
        "model": FINBERT_MODEL_PATH,
        "recognizer_initialized": _recognizer is not None,
        "linker_initialized": _linker is not None,
        "enricher_initialized": _enricher is not None,
        "pipeline_initialized": _pipeline is not None,
        "config": get_config()
    }


# =============================================================================
# STARTUP/SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("="*60)
    logger.info("Financial Entity Recognition & Linking API Starting")
    logger.info("="*60)
    logger.info(f"FinBERT Model: {FINBERT_MODEL_PATH}")
    logger.info(f"SEC EDGAR User-Agent: {SEC_EDGAR_USER_AGENT}")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Financial Entity Recognition & Linking API Shutting Down")


# =============================================================================
# MAIN (for direct execution)
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
