"""FastAPI application for L3 M9.1: Explainability & Citation Tracking"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uuid

from src.l3_m9_financial_compliance_risk import (
    CitationAwareRetriever,
    CitationMapBuilder,
    CitationAwareLLMPrompt,
    CitationVerificationEngine,
    AuditTrailManager
)
from config import (
    validate_config,
    get_anthropic_client,
    get_openai_embeddings,
    get_pinecone_vectorstore,
    get_service_status,
    ANTHROPIC_ENABLED,
    OPENAI_ENABLED,
    PINECONE_ENABLED
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M9.1: Explainability & Citation Tracking",
    description="Production API for financial RAG with explainability, citation tracking, and audit trails",
    version="1.0.0"
)

# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str
    ticker: Optional[str] = None
    fiscal_period: Optional[str] = None
    k: int = 5
    user_id: str = "default_user"

class CitationInfo(BaseModel):
    """Citation metadata model"""
    citation_id: str
    source_type: str
    ticker: str
    company_name: str
    filing_date: str
    fiscal_period: str
    section: str
    relevance_score: float
    excerpt: str

class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    status: str
    query_id: str
    response: str
    citations: Dict[str, Any]
    verification: Dict[str, Any]
    retrieval_log: Dict[str, Any]
    service_status: Dict[str, Any]

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    module: str
    services: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    logger.info("Starting L3 M9.1: Explainability & Citation Tracking API")

    # Validate configuration
    if not validate_config():
        logger.warning("⚠️ Configuration validation failed - running in limited mode")
    else:
        logger.info("✅ Configuration validated successfully")

    # Log service status
    status = get_service_status()
    logger.info(f"Service status: {status}")

    if not any([status['anthropic_configured'], status['openai_configured'], status['pinecone_configured']]):
        logger.warning("⚠️ No services configured - API will run in offline/mock mode")


@app.get("/", response_model=HealthResponse)
async def root():
    """
    Health check endpoint

    Returns service status and availability information
    """
    service_status = get_service_status()

    return HealthResponse(
        status="online",
        module="L3_M9.1_Explainability_Citation_Tracking",
        services=service_status
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Main query endpoint for citation-tracked financial RAG

    This endpoint:
    1. Retrieves relevant documents with citation markers
    2. Generates LLM response with citations
    3. Verifies citations against source documents
    4. Logs complete audit trail

    Args:
        request: Query request with question and filters

    Returns:
        Query response with citations, verification, and audit trail
    """
    try:
        query_id = str(uuid.uuid4())
        logger.info(f"Processing query {query_id}: {request.query[:100]}...")

        # Initialize components
        vectorstore = get_pinecone_vectorstore() if PINECONE_ENABLED else None
        embeddings = get_openai_embeddings() if OPENAI_ENABLED else None
        anthropic_client = get_anthropic_client() if ANTHROPIC_ENABLED else None

        retriever = CitationAwareRetriever(
            vectorstore=vectorstore,
            embeddings=embeddings,
            relevance_threshold=0.70
        )

        prompter = CitationAwareLLMPrompt()
        verifier = CitationVerificationEngine()
        audit_manager = AuditTrailManager()

        # Build filters
        filters = {}
        if request.ticker:
            filters["ticker"] = request.ticker
        if request.fiscal_period:
            filters["fiscal_period"] = request.fiscal_period

        # Step 1: Retrieve documents with citations
        retrieval_result = retriever.retrieve_with_citations(
            query=request.query,
            k=request.k,
            filters=filters if filters else None
        )

        documents = retrieval_result["documents"]
        citation_map = retrieval_result["citation_map"]
        retrieval_log = retrieval_result["retrieval_log"]

        # Step 2: Build LLM prompt
        llm_prompt = prompter.build_rag_prompt(
            query=request.query,
            retrieved_context="\n\n".join(documents),
            citation_map=citation_map
        )

        # Step 3: Generate response
        if anthropic_client:
            try:
                response = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    system=prompter.SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": llm_prompt}
                    ]
                )
                llm_response = response.content[0].text
                logger.info("✅ LLM response generated successfully")
            except Exception as e:
                logger.error(f"LLM generation failed: {str(e)}")
                llm_response = f"⚠️ LLM generation unavailable. Retrieved documents: {len(documents)}. Please configure ANTHROPIC_API_KEY to enable full functionality."
        else:
            # Offline mode - generate mock response
            llm_response = f"""⚠️ Running in offline mode (ANTHROPIC disabled).

Retrieved {len(documents)} documents for query: "{request.query}"

Citations available:
{', '.join(citation_map.keys())}

To enable full LLM functionality:
1. Set ANTHROPIC_ENABLED=true in .env
2. Add ANTHROPIC_API_KEY to .env
3. Restart the API server

Mock response: Based on retrieved documents, the information shows financial data from {citation_map.get('[1]', {}).get('ticker', 'N/A')} for {citation_map.get('[1]', {}).get('fiscal_period', 'N/A')} [1]."""

        # Step 4: Verify citations
        verification = verifier.verify_citations(
            response=llm_response,
            citation_map=citation_map
        )

        # Step 5: Log audit trail
        response_id = audit_manager.log_complete_pipeline(
            query_id=query_id,
            user_id=request.user_id,
            query_text=request.query,
            retrieved_docs=[citation_map],
            llm_response=llm_response,
            citations=citation_map,
            verification=verification
        )

        logger.info(f"✅ Query {query_id} processed successfully")

        return QueryResponse(
            status="success",
            query_id=query_id,
            response=llm_response,
            citations=citation_map,
            verification=verification,
            retrieval_log=retrieval_log,
            service_status=get_service_status()
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/verify")
async def verify_citations(
    response_text: str,
    citation_map: Dict[str, Any]
):
    """
    Verify citations in a response against citation map

    Args:
        response_text: LLM-generated response with citations
        citation_map: Citation metadata dictionary

    Returns:
        Verification results with supported/unsupported claims
    """
    try:
        verifier = CitationVerificationEngine()
        verification = verifier.verify_citations(
            response=response_text,
            citation_map=citation_map
        )

        return {
            "status": "success",
            "verification": verification
        }
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit/{query_id}")
async def get_audit_log(query_id: str):
    """
    Retrieve audit log for a specific query

    Args:
        query_id: Query identifier

    Returns:
        Audit log entries for the query
    """
    try:
        audit_manager = AuditTrailManager()
        logs = audit_manager.get_audit_log(query_id=query_id)

        if not logs:
            raise HTTPException(status_code=404, detail=f"No audit log found for query {query_id}")

        return {
            "status": "success",
            "query_id": query_id,
            "audit_logs": logs
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audit log retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/service-status")
async def service_status():
    """
    Get detailed service status and configuration

    Returns:
        Service availability and configuration status
    """
    status = get_service_status()

    return {
        "status": "online",
        "services": status,
        "capabilities": {
            "llm_generation": status["anthropic_configured"],
            "embeddings": status["openai_configured"],
            "vector_search": status["pinecone_configured"],
            "offline_mode": not any([
                status["anthropic_configured"],
                status["openai_configured"],
                status["pinecone_configured"]
            ])
        },
        "recommendations": _get_configuration_recommendations(status)
    }


def _get_configuration_recommendations(status: Dict[str, Any]) -> List[str]:
    """Generate configuration recommendations based on service status"""
    recommendations = []

    if not status["anthropic_configured"]:
        recommendations.append("Configure ANTHROPIC_API_KEY to enable LLM generation")

    if not status["openai_configured"]:
        recommendations.append("Configure OPENAI_API_KEY to enable embeddings and vector search")

    if not status["pinecone_configured"]:
        recommendations.append("Configure PINECONE settings (API_KEY, ENVIRONMENT) to enable vector search")

    if not recommendations:
        recommendations.append("All services configured - full functionality available")

    return recommendations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
