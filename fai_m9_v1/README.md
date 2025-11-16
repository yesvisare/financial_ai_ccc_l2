# L3 M9.1: Explainability & Citation Tracking

**Module:** Financial Compliance & Risk
**Section:** M9.1 - Explainability & Citation Tracking for Financial RAG Systems
**Services:** ANTHROPIC (Claude API), OPENAI (Embeddings), PINECONE (Vector Database)
**Level:** L3 SkillElevate

## Overview

This module implements citation-tracked financial RAG systems with explainability, audit trails, and verification for regulatory compliance. Financial RAG systems without explainability fail regulatory requirements including SEC Regulation S-P, SOX Section 404, and Investment Advisers Act fiduciary duties.

The system provides:
- **Source Attribution:** Inline citations [1], [2], [3] linking to specific SEC filings
- **Verifiable Citations:** Filing date, document section, direct quotes for audit verification
- **Retrieval Transparency:** Logs of retrieved documents, relevance scores, selection rationale
- **Audit Trail:** Immutable records meeting SOX Section 404 requirements
- **Conflict Detection:** Explicit disclosure when sources contradict
- **Citation Verification:** Post-generation validation catching LLM hallucinations

## Concepts Covered

This module covers comprehensive explainability for financial RAG systems:

1. **Three-Layer Explainability Framework**
   - Retrieval Explainability: Which documents were selected and why
   - Citation Attribution: Mapping response components to specific sources
   - Reasoning Transparency: How system concluded X given sources Y and Z

2. **Citation System Architecture**
   - Document retrieval with scoring
   - Citation marker assignment ([1], [2], [3])
   - LLM generation with citations
   - Citation map creation
   - Citation verification (hallucination detection)
   - Audit trail creation

3. **Conflict Detection Protocol**
   - Identifying contradictory sources
   - Explicit disclosure of conflicting signals
   - Prevention of cherry-picking favorable data

4. **Verification Engine (Hallucination Detection)**
   - Post-generation claim verification
   - Semantic similarity checking (threshold: >0.85)
   - Flagging unsupported claims for human review

5. **Audit Trail System**
   - SOX-compliant immutable logging
   - Complete pipeline tracking (query → retrieval → response → verification)
   - 7-year retention support
   - Tamper-evident hash chains

## Learning Outcomes

After completing this module, you will be able to:

1. Implement citation tracking assigning markers to retrieved documents
2. Create verifiable citation maps with structured metadata
3. Build retrieval transparency logging for audit compliance
4. Detect source conflicts and explicitly disclose them
5. Generate immutable SOX-compliant audit trails
6. Implement citation verification preventing hallucination-based fraud

## How It Works

### System Architecture

The system implements a five-component pipeline:

**Component 1: Citation-Aware Retrieval**
- Retrieves financial documents from vector database (Pinecone)
- Assigns relevance scores (0.0-1.0)
- Filters low-relevance documents (threshold: 0.70)
- Assigns citation markers [1], [2], [3]
- Logs retrieval decisions for audit trail

**Component 2: Citation Map Generation**
- Creates structured metadata for each citation
- Includes: source type, ticker, filing date, fiscal period, section, page number
- Adds direct quote, relevance score, document URL
- Computes SHA256 hash for tamper detection

**Component 3: LLM Prompting with Citations**
- Constructs prompt with citation instructions
- Embeds citation markers in context
- Instructs LLM to cite EVERY factual claim
- Requires explicit statement if information unavailable

**Component 4: Citation Verification**
- Extracts claims and citations from response
- Checks semantic similarity between claim and cited text
- Requires >85% similarity for verification
- Flags unsupported claims for human review

**Component 5: Audit Trail Logging**
- Logs complete pipeline to append-only database
- Captures: query, retrieval, response, citations, verification
- Creates immutable record for SEC examination
- Supports 7-year retention requirement

## Installation

### Prerequisites
- Python 3.9+
- ANTHROPIC API access (Claude API)
- OPENAI API access (for embeddings)
- PINECONE access (for vector database)

### Setup

1. Clone repository:
```bash
git clone <repository_url>
cd fai_m9_v1
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY
# - PINECONE_API_KEY
# - PINECONE_ENVIRONMENT
```

## Usage

### API Server

Start the FastAPI server:
```bash
# Windows PowerShell
.\scripts\run_api.ps1

# Linux/Mac
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

Interactive documentation: `http://localhost:8000/docs`

### Python Package

```python
from src.l3_m9_financial_compliance_risk import (
    CitationAwareRetriever,
    CitationVerificationEngine,
    AuditTrailManager
)

# Initialize retriever
retriever = CitationAwareRetriever()

# Retrieve with citations
result = retriever.retrieve_with_citations(
    query="What was Tesla's Q2 2024 free cash flow?",
    k=5,
    filters={"ticker": "TSLA", "fiscal_period": "Q2 2024"}
)

print(result["citation_map"])
```

### Jupyter Notebook

```bash
jupyter notebook notebooks/L3_M9_Financial_Compliance_Risk.ipynb
```

The notebook provides an interactive walkthrough of all components with examples.

## API Endpoints

### GET /
Health check endpoint
- Returns service status and availability

### POST /query
Main query endpoint for citation-tracked financial RAG
- **Request:**
  - `query`: Financial question (required)
  - `ticker`: Stock ticker filter (optional)
  - `fiscal_period`: Fiscal period filter (optional)
  - `k`: Number of documents to retrieve (default: 5)
  - `user_id`: User identifier for audit trail (default: "default_user")
- **Response:**
  - `response`: LLM-generated answer with citations
  - `citations`: Complete citation map with metadata
  - `verification`: Verification results (supported/unsupported claims)
  - `retrieval_log`: Audit log of retrieval decisions
  - `service_status`: Current service availability

### POST /verify
Verify citations in a response against citation map
- **Request:**
  - `response_text`: LLM-generated response
  - `citation_map`: Citation metadata dictionary
- **Response:**
  - Verification results with fidelity score

### GET /audit/{query_id}
Retrieve audit log for a specific query
- **Response:**
  - Complete audit trail for the query

### GET /service-status
Get detailed service status and configuration
- **Response:**
  - Service availability
  - Configuration status
  - Capability matrix
  - Configuration recommendations

## Testing

Run tests:
```bash
# Windows PowerShell
.\scripts\run_tests.ps1

# Linux/Mac
pytest tests/ -v
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_ENABLED` | No | Enable/disable ANTHROPIC service (default: false) |
| `ANTHROPIC_API_KEY` | Yes (if enabled) | API key for Claude LLM |
| `OPENAI_ENABLED` | No | Enable/disable OPENAI service (default: false) |
| `OPENAI_API_KEY` | Yes (if enabled) | API key for embeddings |
| `PINECONE_ENABLED` | No | Enable/disable PINECONE service (default: false) |
| `PINECONE_API_KEY` | Yes (if enabled) | API key for vector database |
| `PINECONE_ENVIRONMENT` | Yes (if enabled) | Pinecone environment name |
| `PINECONE_INDEX_NAME` | No | Index name (default: "sec-filings") |
| `LOG_LEVEL` | No | Logging level (default: INFO) |
| `ENVIRONMENT` | No | Environment name (default: development) |

### Service Configuration

**Full Functionality (All Services Enabled):**
- ANTHROPIC: Claude API for LLM generation
- OPENAI: Text embeddings for vector search
- PINECONE: Vector database for document retrieval

**Offline Mode (All Services Disabled):**
- Uses mock data for testing
- No external API calls
- Limited functionality for development/testing

## Common Issues & Solutions

### 1. Citation Mismatch
**Symptom:** Response generates "[4]" but citation_map only has [1], [2], [3]

**Fix:** Validation before returning response catches this. System will regenerate or return error.

### 2. Hallucinated Citations
**Symptom:** "Apple revenue $500B [1]" but actual quote is "Apple revenue $81.8B"

**Fix:** Verification engine detects semantic mismatch (similarity <0.85) and flags for review.

### 3. Temporal Filtering Ignored
**Symptom:** Query asks for "Q1 2024 results" but response cites Q4 2023 10-K

**Fix:** Enforce fiscal_period filter in retrieval. System fails if no matching period found.

### 4. Conflicting Sources Not Disclosed
**Symptom:** System cites "Revenue up 5%" but omits "Margin declined 10%" from same period

**Fix:** Implement conflict detection to identify contradictory signals and force disclosure.

### 5. Audit Trail Incomplete
**Symptom:** Some queries logged, others missing

**Fix:** Transactional logging - entire request fails if audit logging fails.

### 6. Relevance Score Drift
**Symptom:** Same query retrieved different documents with different scores on different days

**Fix:** Quarterly threshold validation against manual audits. Monitor score distribution.

## Decision Card

### Use This Approach When:
- Portfolio size: $50M+ (economics justify implementation cost)
- User type: Professional analysts, investment advisors (not retail)
- Question type: Strategic analysis, metric comparisons (not real-time trades)
- Compliance culture: Mature (CFO/general counsel engaged)
- Budget: $5K-20K/month available
- Team: At least one person dedicated to compliance/audit
- Use case: Client-facing advice requiring regulatory defense

### Don't Use When:
- Portfolio size: <$10M (cost exceeds benefit)
- Use case: Real-time algorithmic trading (sub-second decisions needed)
- Compliance maturity: Startup (no compliance officer)
- Budget: <$1K/month
- Question type: Narrow metric extraction (use rule-based system instead)
- No audit capacity to maintain/interpret logs

### Alternatives:
- **Knowledge Graph Approach:** Better for multi-company analysis, requires 6-12 months to build
- **Human-in-the-Loop Only:** Guaranteed accuracy but non-scalable
- **Deterministic Rule-Based System:** Fast for specific metrics but brittle to format changes

## Cost Considerations

### Free Tier (Small Investment Firm)
- SEC EDGAR: $0
- Vector Database (Pinecone Starter): $70/month
- ANTHROPIC API: $200-500/month (50K queries)
- OPENAI API: $50/month (embeddings)
- **Total: $320-620/month**

### Paid Tier (Mid-Sized Asset Manager)
- Capital IQ Transcripts: $1,000/month
- Vector Database (Pinecone Standard): $300/month
- ANTHROPIC API: $2,000/month (500K queries)
- OPENAI API: $200/month
- **Total: $3,500-5,000/month**

### Enterprise Tier (Large Bank)
- Bloomberg + Reuters: $3,333/month
- Vector Database (Pinecone Enterprise): $2,000/month
- ANTHROPIC API: $10,000/month (5M queries)
- OPENAI API: $500/month
- Compliance Tooling: $5,000/month
- **Total: $20,000-25,000/month**

## Production Checklist

**Pre-Launch:**
- [ ] Compliance review completed
- [ ] Legal review completed
- [ ] Citation verification tested on 100+ real SEC filings (>95% accuracy)
- [ ] Audit logging implemented (all 5 components)
- [ ] Database backup strategy documented
- [ ] Monitoring alerts configured
- [ ] Staff training completed
- [ ] SOX 404 control documentation completed
- [ ] 2-week shadow period with human validation

**Ongoing Operations:**
- [ ] Weekly audit log review
- [ ] Monthly citation accuracy sampling (50 random responses)
- [ ] Quarterly threshold recalibration
- [ ] Verification metrics dashboard (target: >90% hallucination detection)
- [ ] Monthly compliance reporting
- [ ] Quarterly staff retraining
- [ ] Maintain organized audit logs for SEC examination

**Crisis Response:**
- [ ] Halt production queries immediately
- [ ] Preserve audit logs (no modifications)
- [ ] Alert compliance and legal teams
- [ ] Conduct root cause analysis
- [ ] Notify SEC if material customer harm occurred
- [ ] Implement remediation
- [ ] Resume with human review period

## Regulatory Framework

This system addresses requirements from:

- **SEC Regulation S-P:** Requires explainability for automated investment advice
- **SOX Section 404:** Requires audit trails proving data accuracy (7-year retention)
- **Investment Advisers Act Section 206(4):** Fiduciary duty to act in client best interest
- **GDPR Article 22:** Right to explanation of automated decisions (EU clients)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Make changes
4. Run tests (`pytest tests/`)
5. Commit changes (`git commit -m 'Add AmazingFeature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

- **Documentation:** This README and inline code documentation
- **Issues:** Create an issue in the repository
- **Community:** TechVoyageHub L3 SkillElevate community

## Credits

Created as part of TechVoyageHub L3 SkillElevate curriculum - Finance AI M9.1: Explainability & Citation Tracking.

## Disclaimers

**For End Users:**
This system provides analysis based on SEC filings and market data. All responses cite sources; verify citations before making investment decisions. System may misinterpret data or hallucinate citations. Investment decisions require human judgment and financial advisor consultation.

**For Compliance Officers:**
This system generates audit trails but does not guarantee compliance. Human oversight remains required. System failures may create regulatory liability. Test thoroughly before client-facing deployment.

**For Executives/CEOs:**
This system reduces decision time and increases documentation for audit purposes. However, you remain personally liable for financial statement accuracy under SOX Section 302. Do not rely on system outputs without human verification.
