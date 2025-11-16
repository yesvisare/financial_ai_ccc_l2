# L3_M10.3: Managing Financial Knowledge Base Drift

**Track:** Finance AI
**Module:** M10 - Financial RAG in Production
**Video:** M10.3 (45 minutes)
**Services:** OpenAI (Embeddings API) + Pinecone (Vector DB) - auto-detected from script

## Overview

Production-ready implementation of drift detection and versioning for financial knowledge bases in RAG systems. This module addresses the critical challenge of maintaining accuracy and compliance as regulatory standards evolve (ASC 606, ASC 842, CECL updates).

Unlike generic RAG systems, financial knowledge bases require:
- **Semantic drift detection** when concept definitions change without terminology changes
- **Version control with regulatory effective dates** to support multi-year historical queries
- **Zero historical query breakage** for SOX compliance and audit trail requirements
- **Selective retraining** to minimize costs while maintaining accuracy

This implementation demonstrates how to detect and manage knowledge base drift in production financial RAG systems, ensuring citation accuracy above 95% while handling systematic regulatory changes.

## What You'll Learn

By completing this module, you will be able to:

1. **Detect semantic drift** using embedding similarity metrics between baseline and current concept definitions
2. **Implement versioning** for financial knowledge with regulatory effective dates and temporal query routing
3. **Handle systematic regulatory changes** (ASC 606, ASC 842, CECL) with automated monitoring and human-in-loop approval
4. **Build selective retraining pipelines** targeting only affected documents (e.g., 500 lease docs from 50K corpus)
5. **Create regression testing frameworks** validating updates don't break historical queries
6. **Generate audit trails** with cryptographic hashing for SOX 404 compliance (7+ year retention)

## Prerequisites

- **Generic CCC M1-M4:** RAG MVP fundamentals (chunking, embeddings, retrieval, generation)
- **Finance AI M10.1:** Secure Deployment (API key management, access control)
- **Finance AI M10.2:** Monitoring Performance (latency, accuracy metrics)
- **Understanding of regulatory compliance:** SOX 404, SEC requirements, GAAP standards
- **Python 3.11+:** Type hints, async/await, logging

## Key Concepts Covered

This module implements the following core concepts from the script:

### 1. Semantic Drift Detection
Uses cosine similarity between baseline and current concept embeddings to identify definition changes that don't involve terminology changes. Example: ASC 840 lease accounting vs. ASC 842 - same term ("lease") but fundamentally different accounting treatment.

**Severity thresholds:**
- **HIGH:** Similarity < 0.70 (major conceptual change)
- **MEDIUM:** 0.70-0.80 (moderate change)
- **LOW:** 0.80-0.85 (minor refinement)
- **No drift:** ≥ 0.85

### 2. Factual Obsolescence
Historical facts becoming superseded by newer information. Unlike semantic drift, this involves new data points rather than definition changes. Example: Effective dates, superseded standards (ASU updates).

### 3. Regulatory Effective Dates
Knowledge base versioning with "effective_from" and "effective_until" date ranges. Enables temporal query routing where queries are answered using the standards version applicable on the transaction date.

**Example:** Query about a 2018 lease uses ASC 840 (effective until 2019), while a 2020 lease uses ASC 842 (effective from 2019).

### 4. Version Control Strategy
Maintaining multiple concurrent standards rather than overwriting old knowledge. Critical for:
- Historical audit queries requiring outdated standards
- Transition period support (dual compliance)
- Regulatory lookback requirements

### 5. Selective Retraining
Re-embedding only documents affected by drifted concepts rather than full corpus reprocessing. Reduces costs from ~$10-50 (full corpus) to ~$1-2 (selective) for typical drift events.

**Implementation:**
1. Identify drifted concepts (e.g., "Right-of-Use Asset")
2. Search document corpus for concept mentions
3. Re-embed affected subset (500 docs vs. 50K total)
4. Update vector database with new embeddings

### 6. Embedding Similarity Metrics
Uses OpenAI text-embedding-3-small (1536 dimensions) with cosine similarity for drift detection. Baseline embeddings stored at initial deployment; current embeddings generated on monitoring cycles (daily/weekly).

### 7. Human-in-the-Loop Compliance
Automated drift detection with manual review for version creation. Ensures compliance officer validates regulatory interpretations before committing changes to production knowledge base.

### 8. Immutable Audit Trails
Cryptographic hashing (SHA-256) of all drift detections and version changes. Stored in PostgreSQL with 7+ year retention for SOX 404 compliance.

### 9. Regression Testing for Validation
Automated testing of historical queries after knowledge base updates. Ensures zero breakage by validating expected results still match after version changes.

## How It Works

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Drift Management Workflow                     │
└─────────────────────────────────────────────────────────────────┘

1. REGULATORY MONITORING (Automated - Daily)
   ┌──────────────────────────────────────┐
   │ • FASB website scraping              │
   │ • SEC EDGAR monitoring               │
   │ • AICPA guidance tracking            │
   │ → Detects new ASUs, effective dates  │
   └──────────────────────────────────────┘
                    ↓
2. DRIFT DETECTION (Automated - Weekly/On-Trigger)
   ┌──────────────────────────────────────┐
   │ • Generate current concept embeddings│
   │ • Compare to baseline (cosine sim)   │
   │ • Flag if similarity < 0.85          │
   │ • Classify severity (HIGH/MED/LOW)   │
   └──────────────────────────────────────┘
                    ↓
3. VERSION CONTROL CREATION (Human-in-Loop)
   ┌──────────────────────────────────────┐
   │ • Compliance officer reviews drift   │
   │ • Approves version creation          │
   │ • Sets effective_from/until dates    │
   │ • Logs to audit trail (immutable)    │
   └──────────────────────────────────────┘
                    ↓
4. SELECTIVE RETRAINING (Automated - Background)
   ┌──────────────────────────────────────┐
   │ • Identify affected documents        │
   │ • Re-embed in batches (50 docs/batch)│
   │ • Update Pinecone vector index       │
   │ • Cost: ~$1-2 vs. $10-50 full corpus │
   └──────────────────────────────────────┘
                    ↓
5. REGRESSION TESTING (Automated - Pre-Deployment)
   ┌──────────────────────────────────────┐
   │ • Run historical query test suite    │
   │ • Validate expected results match    │
   │ • Block deployment if failures exist │
   │ • Ensure zero historical breakage    │
   └──────────────────────────────────────┘
                    ↓
6. AUDIT TRAIL (Automated - Continuous)
   ┌──────────────────────────────────────┐
   │ • SHA-256 hashing of all changes     │
   │ • PostgreSQL storage (7+ years)      │
   │ • Immutable records for SOX 404      │
   │ • Timestamp, approver, data hash     │
   └──────────────────────────────────────┘
```

### Data Flow

**Baseline Establishment:**
```
Financial Concepts → OpenAI Embeddings API → Baseline Storage (Pinecone)
```

**Drift Detection:**
```
Current Concepts → OpenAI Embeddings API → Similarity Comparison → Drift Report
```

**Version Routing:**
```
Query (with date) → Version Manager → Appropriate KB Version → RAG Pipeline
```

## Installation

### 1. Clone and Setup
```bash
git clone <repository-url>
cd fai_m10_v3
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials:
# - OPENAI_API_KEY (required for embeddings)
# - PINECONE_API_KEY + PINECONE_ENVIRONMENT (required for vector storage)
# - PostgreSQL credentials (optional, for audit trails)
```

### 4. Verify Installation
```bash
# Run tests
pytest tests/ -v

# Start API server
uvicorn app:app --reload

# Check service status
curl http://localhost:8000/status
```

## Usage

### As Python Package

```python
from src.l3_m10_financial_rag_in_production import (
    FinancialKBDriftDetector,
    KnowledgeBaseVersionManager,
    detect_drift,
    create_version
)

# Initialize drift detector
detector = FinancialKBDriftDetector(threshold=0.85)

# Establish baseline
baseline_concepts = {
    "Lease Accounting": "ASC 840: Operating leases off-balance sheet...",
    "Revenue Recognition": "ASC 605: Revenue recognized when earned..."
}
detector.establish_baseline(baseline_concepts)

# Detect drift
current_concepts = {
    "Lease Accounting": "ASC 842: All leases on-balance sheet with ROU asset...",
    "Revenue Recognition": "ASC 606: Five-step model for revenue..."
}
drift_report = detector.detect_drift(current_concepts)

print(f"Drift detected: {drift_report['summary']['total_drift_count']} concepts")
print(f"High severity: {drift_report['summary']['high_severity']}")

# Create version for drifted concepts
version_manager = KnowledgeBaseVersionManager()
version = version_manager.create_version(
    standard_name="ASC 842",
    effective_from="2019-01-01",
    effective_until=None,  # Current standard
    concept_definitions=current_concepts
)

# Query version for specific date
version_2018 = version_manager.get_version_for_date(
    query_date="2018-06-15",
    standard_name="ASC 840"  # Returns old standard
)
```

### Via API

```bash
# Start server
uvicorn app:app --reload --port 8000

# Establish baseline
curl -X POST http://localhost:8000/baseline/establish \
  -H "Content-Type: application/json" \
  -d '{
    "financial_concepts": {
      "Lease Accounting": "ASC 842 requires lessees to recognize...",
      "Revenue Recognition": "ASC 606 establishes five-step model..."
    }
  }'

# Detect drift
curl -X POST http://localhost:8000/drift/detect \
  -H "Content-Type: application/json" \
  -d '{
    "current_concepts": {
      "Lease Accounting": "Updated definition with clarifications..."
    }
  }'

# Create version
curl -X POST http://localhost:8000/version/create \
  -H "Content-Type: application/json" \
  -d '{
    "standard_name": "ASC 842",
    "effective_from": "2019-01-01",
    "effective_until": null
  }'

# Check regulatory updates
curl -X POST http://localhost:8000/regulatory/check

# Get audit trail
curl http://localhost:8000/audit/trail
```

### Via Jupyter Notebook

```bash
# Launch Jupyter
jupyter notebook notebooks/L3_M10_Financial_RAG_In_Production.ipynb

# Or use JupyterLab
jupyter lab notebooks/
```

The notebook provides an interactive walkthrough of all concepts with code examples and explanations.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| **OpenAI Configuration** | | | |
| `OPENAI_ENABLED` | No | `false` | Enable OpenAI embeddings service |
| `OPENAI_API_KEY` | If enabled | - | OpenAI API key for embeddings |
| **Pinecone Configuration** | | | |
| `PINECONE_ENABLED` | No | `false` | Enable Pinecone vector database |
| `PINECONE_API_KEY` | If enabled | - | Pinecone API key |
| `PINECONE_ENVIRONMENT` | If enabled | - | Pinecone environment (e.g., us-west1-gcp) |
| `PINECONE_INDEX_NAME` | No | `financial-kb-drift` | Pinecone index name |
| **PostgreSQL Configuration** | | | |
| `POSTGRES_HOST` | No | `localhost` | PostgreSQL host for audit trails |
| `POSTGRES_PORT` | No | `5432` | PostgreSQL port |
| `POSTGRES_DB` | No | `financial_kb_drift` | Database name |
| `POSTGRES_USER` | If using PG | - | PostgreSQL username |
| `POSTGRES_PASSWORD` | If using PG | - | PostgreSQL password |
| **Application Settings** | | | |
| `DRIFT_THRESHOLD` | No | `0.85` | Similarity threshold for drift detection |
| `RETRAINING_BATCH_SIZE` | No | `50` | Batch size for re-embedding documents |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `AUDIT_RETENTION_DAYS` | No | `2555` | Audit trail retention (7 years for SOX 404) |
| `CITATION_ACCURACY_THRESHOLD` | No | `95` | Minimum citation accuracy (%) |

## API Endpoints

### Core Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and service info |
| `/status` | GET | Service availability and configuration |
| `/config` | GET | Current configuration settings |

### Baseline Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/baseline/establish` | POST | Establish baseline embeddings for concepts |

### Drift Detection

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/drift/detect` | POST | Detect drift by comparing current to baseline |

### Version Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/version/create` | POST | Create new KB version with effective dates |
| `/version/query` | POST | Get version for specific date |
| `/version/list` | GET | List all versions |

### Regulatory Monitoring

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/regulatory/check` | POST | Check FASB/SEC/AICPA for updates |

### Retraining Pipeline

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/retrain/execute` | POST | Execute selective retraining for affected docs |

### Regression Testing

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/regression/validate` | POST | Run regression tests on historical queries |

### Audit Trail

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/audit/trail` | GET | Retrieve audit trail (filterable by event type) |

## Common Failures & Solutions

### 1. False Positive Drift Alerts
**Symptom:** Drift detected for editorial-only changes (typo fixes, formatting)
**Cause:** Threshold too sensitive (0.90+) or minor wording changes triggering alerts
**Fix:**
```python
# Lower threshold to 0.85 or implement severity assessment
detector = FinancialKBDriftDetector(threshold=0.85)

# Or add editorial change filter
if drift_severity == "LOW" and edit_distance < 10:
    log_as_editorial_change()  # Don't trigger version update
```

### 2. Missed Regulatory Updates
**Symptom:** Knowledge base outdated despite monitoring running
**Cause:** FASB RSS feed parsing failure, website structure changes
**Fix:**
```python
# Add fallback to manual check + email notifications
try:
    updates = scrape_fasb_website()
except ParseError:
    send_notification_to_compliance_team()
    fallback_to_manual_review()

# Implement multiple data sources
sources = [FASB_API, SEC_EDGAR, AICPA_ALERTS]
```

### 3. Version Conflicts in Queries
**Symptom:** Queries returning mixed old/new standards (ASC 840 + ASC 842 content)
**Cause:** Effective date logic incorrect or metadata missing from queries
**Fix:**
```python
# Ensure temporal query routing based on transaction date
def route_query(query_text, transaction_date):
    version = version_manager.get_version_for_date(
        query_date=transaction_date,
        standard_name=extract_standard(query_text)
    )
    return query_with_version_filter(query_text, version)
```

### 4. Retraining Cost Overruns
**Symptom:** Monthly embedding costs exceed budget ($50+ vs. $6-10 expected)
**Cause:** Full corpus re-embedding instead of selective targeting
**Fix:**
```python
# Implement selective retraining
affected_docs = identify_affected_documents(drift_concepts)  # 500 docs
retrain_documents(affected_docs)  # $1-2 cost

# Instead of:
# retrain_all_documents(full_corpus)  # $10-50 cost
```

### 5. Historical Query Breakage
**Symptom:** Regression tests failing after knowledge base updates
**Cause:** Overwriting baseline instead of versioning
**Fix:**
```python
# Maintain multiple concurrent versions
version_manager.create_version(
    standard_name="ASC 842",
    effective_from="2019-01-01",
    effective_until=None  # Don't delete ASC 840
)

# Validate before deployment
regression_results = validate_regression(historical_queries)
if regression_results['failed'] > 0:
    rollback_changes()
```

### 6. Audit Trail Storage Overflow
**Symptom:** PostgreSQL storage filling up rapidly
**Cause:** Logging full document content in audit trail instead of hashes
**Fix:**
```python
# Store hashes instead of full content
audit_entry = {
    "data_hash": hashlib.sha256(content.encode()).hexdigest(),
    # NOT: "full_content": content  # ❌ Don't store full content
}

# Implement retention policy (7 years for SOX)
archive_entries_older_than(days=2555)
```

### 7. Slow Drift Detection on Large Corpora
**Symptom:** Drift detection taking hours for 50K+ document corpus
**Cause:** Generating embeddings for all concepts on every check
**Fix:**
```python
# Cache baseline embeddings (generate once)
baseline_cache = load_from_pinecone(namespace="baseline")

# Only generate current embeddings for changed concepts
changed_concepts = detect_changed_definitions()  # Track via git
current_embeddings = generate_embeddings(changed_concepts)
```

### 8. Human Approval Bottlenecks
**Symptom:** Drift detected but version updates delayed for weeks
**Cause:** Manual approval process without notifications
**Fix:**
```python
# Implement automated notifications
if drift_detected:
    send_slack_notification(compliance_team, drift_report)
    create_jira_ticket(priority="HIGH")
    set_approval_deadline(days=5)

# Track approval SLAs
monitor_approval_time()
```

## Decision Card

### When to Use This Approach

**✅ USE when:**
- **Financial RAG systems with evolving standards** - GAAP, IFRS, tax code requiring ongoing updates
- **Multi-year data requiring historical accuracy** - Queries about past transactions need period-appropriate standards
- **SOX compliance requirements** - Public companies needing audit trails and 95%+ citation accuracy
- **High citation accuracy requirements** - Legal, regulatory, compliance use cases (95%+ accuracy)
- **Moderate update frequency** - Standards change quarterly/annually (not daily)
- **Defined effective dates** - Regulatory changes have clear effective_from dates

**❌ DO NOT USE when:**
- **Static knowledge bases** - No regulatory changes expected (e.g., historical analysis only)
- **Short-lived projects** - <1 year lifecycle doesn't justify versioning overhead
- **Non-regulated domains** - Marketing content, blog posts, general Q&A (no compliance requirements)
- **High-velocity updates** - Daily/hourly changes make versioning impractical
- **Low accuracy tolerance** - Use cases where 80-90% accuracy is acceptable
- **No temporal requirements** - Queries always use current knowledge (no historical lookback)

### Cost Considerations

**Tier 1: Small Deployment (5K documents, monthly checks)**
- Baseline embedding: $0.50 one-time
- Monthly drift detection: $0.20
- Selective retraining (avg 100 docs/month): $0.50
- **Total: ~₹100-150/month ($1-2 USD)**

**Tier 2: Medium Deployment (50K documents, weekly checks)**
- Baseline embedding: $5 one-time
- Monthly drift detection (4 checks): $4
- Selective retraining (avg 500 docs/month): $2
- **Total: ~₹500-800/month ($6-10 USD)** ← Script baseline

**Tier 3: Large Deployment (500K documents, daily checks)**
- Baseline embedding: $50 one-time
- Monthly drift detection (30 checks): $60
- Selective retraining (avg 2K docs/month): $10
- **Total: ~₹5,000-8,000/month ($60-100 USD)**

**Additional costs:**
- PostgreSQL hosting: $10-50/month (cloud managed)
- Pinecone: Free tier (1 index) or $70/month (production)
- Monitoring/alerting: $5-20/month (optional)

### Alternative Approaches

**If budget constrained:** Skip Pinecone, use local SQLite for baseline storage
**If no compliance requirements:** Skip audit trails, simplify to basic drift detection
**If high update frequency:** Consider full corpus re-embedding instead of versioning
**If no historical queries:** Overwrite baseline instead of creating versions

## Production Deployment

### Security Checklist

- [ ] API keys stored in environment (not code)
- [ ] HTTPS enabled for API endpoints
- [ ] Rate limiting configured (prevent abuse)
- [ ] Audit logging enabled with 7+ year retention
- [ ] SOX compliance validated (immutable records, approver tracking)
- [ ] Access control implemented (role-based permissions)
- [ ] Secrets rotation policy established (90-day key rotation)

### Monitoring Metrics

**Drift Detection:**
- Drift detection frequency (daily/weekly)
- False positive rate (target: <5%)
- High severity drift alerts (requires immediate action)
- Time to version approval (SLA: 5 days)

**Retraining Pipeline:**
- Affected document count per drift event
- Retraining cost per event (target: <$5)
- Batch processing time (target: <1 hour)
- Re-embedding success rate (target: 100%)

**Regression Testing:**
- Historical query validation pass rate (target: 100%)
- Test suite coverage (target: 95%+ of queries)
- Validation time (target: <10 minutes)

**Audit Trail:**
- Event logging rate (all drift/version events)
- Storage growth rate (monitor PostgreSQL size)
- Retention compliance (7+ years maintained)

### Deployment Steps

1. **Infrastructure Setup**
   - Provision PostgreSQL 15+ for audit trails
   - Create Pinecone index (1536 dimensions, cosine metric)
   - Configure OpenAI API access with rate limits

2. **Initial Baseline**
   - Generate baseline embeddings for all current concepts
   - Store in Pinecone with "baseline" namespace
   - Validate storage and retrieval

3. **Monitoring Configuration**
   - Schedule daily regulatory source checks
   - Schedule weekly drift detection runs
   - Configure Slack/email notifications for alerts

4. **Regression Test Suite**
   - Build test suite from historical queries (200+ examples)
   - Document expected results with source citations
   - Automate execution in CI/CD pipeline

5. **Human Approval Workflow**
   - Define compliance officer approval process
   - Set SLA for version approval (5 days)
   - Implement notification escalation

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/test_m10_financial_rag_in_production.py::TestDriftDetection -v

# Run with coverage report
pytest --cov=src --cov-report=html tests/

# Run tests in offline mode (no API calls)
OPENAI_ENABLED=false pytest tests/
```

## Development

### Project Structure

```
fai_m10_v3/
├── app.py                              # FastAPI entrypoint (thin wrapper)
├── config.py                           # Environment & client management
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # API key template
├── .gitignore                          # Python defaults + .ipynb_checkpoints
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample JSON data
├── example_data.txt                    # Sample text data
│
├── src/                                # Source code package
│   └── l3_m10_financial_rag_in_production/
│       └── __init__.py                 # Core business logic (importable)
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M10_Financial_RAG_In_Production.ipynb
│
├── tests/                              # Test suite
│   └── test_m10_financial_rag_in_production.py
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API
    └── run_tests.ps1                   # Windows: Run tests
```

### Adding New Features

1. **New drift detection algorithm:**
   - Implement in `src/l3_m10_financial_rag_in_production/__init__.py`
   - Add tests in `tests/test_m10_financial_rag_in_production.py`
   - Update API endpoint in `app.py`

2. **New regulatory source:**
   - Add to `RegulatoryMonitor` class sources dict
   - Implement scraping logic
   - Add tests for parsing

3. **New version routing logic:**
   - Extend `KnowledgeBaseVersionManager`
   - Update temporal query routing
   - Add regression tests

## Resources

- **Augmented Script:** [Managing Financial Knowledge Base Drift](https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_FinanceAI_M10_3_Managing_Financial_Knowledge_Base_Drift.md)
- **FASB Standards:** https://www.fasb.org/
- **SEC EDGAR Database:** https://www.sec.gov/edgar
- **AICPA Guidance:** https://www.aicpa.org/
- **OpenAI Embeddings API:** https://platform.openai.com/docs/guides/embeddings
- **Pinecone Documentation:** https://docs.pinecone.io/
- **SOX 404 Compliance:** https://www.soxlaw.com/

## Support

For issues or questions:
- **Open an issue** on GitHub with detailed description
- **Check documentation** in `notebooks/` for detailed walkthrough
- **Review script** for conceptual explanations and trade-offs
- **Run tests** with `-v` flag for detailed error messages

## License

MIT License - See [LICENSE](LICENSE) file for details

---

**Built with:** Python 3.11+, FastAPI, OpenAI API, Pinecone, PostgreSQL, scikit-learn
**Compliant with:** SOX 404, SEC requirements, GAAP standards
**Cost:** ~₹500-800/month ($6-10 USD) for 50K document corpus with weekly drift checks
