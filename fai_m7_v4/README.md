# L3 M7.4: Audit Trail & Document Provenance

**Module:** Finance AI - Financial Data Ingestion & Compliance
**Video:** M7.4 - Audit Trail & Document Provenance
**Level:** L3 (Domain-Specific RAG Engineering)

## Overview

SOX-compliant audit trail and document provenance tracking for financial RAG systems. Provides immutable logging with hash-chained integrity (blockchain-inspired), chain-of-custody tracking for document transformations, and regulatory reporting capabilities for financial compliance.

## What This Module Does

**Capabilities:**
- **Immutable Audit Trail** - Hash-chained logging with SHA-256 integrity verification (blockchain-inspired design)
- **Document Provenance Tracking** - Complete lineage from SEC filing → chunks → embeddings → RAG answers
- **Chain-of-Custody** - Audit every data transformation in the pipeline
- **SOX Section 404 Compliant** - Logging meets regulatory requirements with 7-year retention
- **Regulatory Audit Reports** - Generate compliance reports for SEC reviews and external audits
- **Tamper Detection** - Verify hash chain integrity to detect any unauthorized modifications

**Key Features:**
- PostgreSQL-based event storage with append-only guarantees (immutability rules)
- SHA-256 hash chaining for cryptographic tamper detection
- Complete retrieval provenance (know exactly which chunks influenced which answers)
- User access auditing for insider trading prevention
- Performance metrics and anomaly detection
- Compliance report generation for quarterly reviews

## Learning Outcomes

After completing this module, you will be able to:

1. **Design SOX-compliant audit logs** - Implement immutable, tamper-proof logging systems that meet regulatory requirements for financial services
2. **Track retrieval provenance** - Know exactly which source documents and chunks influenced each RAG-generated answer
3. **Build chain-of-custody** - Document every transformation from PDF download → parsing → chunking → embedding → retrieval
4. **Generate audit reports** - Create compliance-ready reports for SEC reviews, external audits, and internal governance
5. **Implement retention policies** - Configure 7+ year minimum retention to meet SOX compliance mandates
6. **Verify audit integrity** - Detect tampering using hash chain verification (similar to blockchain)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Financial Audit Trail System                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Document Ingestion → [Log Event] → Hash Chain → PostgreSQL     │
│  Document Processing → [Log Event] → Hash Chain → PostgreSQL    │
│  User Query → [Log Event] → Hash Chain → PostgreSQL             │
│  Retrieval (Provenance) → [Log Event] → Hash Chain → PostgreSQL │
│  LLM Generation → [Log Event] → Hash Chain → PostgreSQL         │
│                                                                  │
│  Verification: Recompute all hashes → Compare → Detect tampering│
│  Reporting: Query events by date → Aggregate → Generate report  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Components:**

1. **AuditEvent Model (SQLAlchemy)**
   - `id`: Auto-incrementing primary key
   - `timestamp`: UTC datetime with timezone
   - `event_type`: Category (document_ingested, query_executed, etc.)
   - `event_data`: JSONB field for flexible event schemas
   - `previous_hash`: Links to previous event (chain formation)
   - `hash`: SHA-256 digest of this event (tamper detection)
   - `user_id`: User or system that triggered the event

2. **FinancialAuditTrail Class**
   - `log_event()`: Core logging function (all others call this)
   - `log_document_ingested()`: Log SEC filing ingestion
   - `log_document_processed()`: Log parsing/chunking completion
   - `log_query()`: Log user queries
   - `log_retrieval()`: Log retrieved chunks (provenance tracking)
   - `log_generation()`: Log LLM-generated answers with citations
   - `verify_integrity()`: Verify entire hash chain
   - `generate_compliance_report()`: Generate regulatory reports

3. **Hash Chain Mechanism**
   - Each event's hash includes previous event's hash
   - Forms cryptographic chain (like blockchain)
   - Any modification breaks the chain (tamper detection)
   - Deterministic JSON serialization (sorted keys)

4. **Compliance Reporting**
   - Query events by date range
   - Aggregate by event type and user
   - Verify chain integrity
   - Export for regulators (JSON/CSV)

## Installation

### Prerequisites
- Python 3.9+ (3.11+ recommended)
- PostgreSQL 12+ (14+ recommended for better JSONB performance)
- Virtual environment tool (venv or conda)

### Setup

1. **Clone repository:**
```bash
git clone <repo_url>
cd fai_m7_v4
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your PostgreSQL connection details
```

5. **Set up PostgreSQL database:**
```sql
-- Connect to PostgreSQL as admin user
CREATE DATABASE audit_db;
CREATE USER audit_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE audit_db TO audit_user;

-- Connect to audit_db
\c audit_db

-- Create immutability rules (critical for SOX compliance)
CREATE RULE no_update AS ON UPDATE TO audit_events DO INSTEAD NOTHING;
CREATE RULE no_delete AS ON DELETE TO audit_events DO INSTEAD NOTHING;
```

**Note:** The immutability rules prevent accidental or malicious modification/deletion of audit events.

## Usage

### Starting the API

**Windows PowerShell:**
```powershell
.\scripts\run_api.ps1
```

**Linux/Mac:**
```bash
# Set environment
export PYTHONPATH=$PWD
export DATABASE_URL="postgresql://audit_user:password@localhost:5432/audit_db"

# Start server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Interactive Notebook

```bash
jupyter notebook notebooks/L3_M7_Financial_Data_Ingestion_Compliance.ipynb
```

### Running Tests

**Windows PowerShell:**
```powershell
.\scripts\run_tests.ps1
```

**Linux/Mac:**
```bash
export PYTHONPATH=$PWD
pytest -v tests/
```

## API Endpoints

### Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "healthy",
  "module": "L3 M7.4: Audit Trail & Document Provenance",
  "database": "connected",
  "total_events": 15847
}
```

### Log Document Ingestion
```http
POST /log_document_ingested
Content-Type: application/json

{
  "document_id": "aapl_10k_2024",
  "source_url": "https://www.sec.gov/Archives/edgar/data/320193/...",
  "filing_date": "2024-03-15",
  "document_type": "10-K",
  "user_id": "data_pipeline@company.com"
}
```

**Response:**
```json
{
  "status": "logged",
  "event_hash": "a1b2c3d4e5f6...",
  "event_type": "document_ingested",
  "document_id": "aapl_10k_2024"
}
```

### Log Document Processing
```http
POST /log_document_processed
Content-Type: application/json

{
  "document_id": "aapl_10k_2024",
  "chunks_created": 487,
  "embeddings_created": 487,
  "processing_time_seconds": 12.5,
  "user_id": "data_pipeline@company.com"
}
```

### Log Query Execution
```http
POST /log_query
Content-Type: application/json

{
  "query_text": "What was Apple's revenue in Q4 2024?",
  "query_id": "q_20241115_001",
  "user_id": "analyst@company.com"
}
```

### Log Retrieval (Provenance Tracking)
```http
POST /log_retrieval
Content-Type: application/json

{
  "query_id": "q_20241115_001",
  "chunks_retrieved": [
    {
      "chunk_id": "aapl_10k_2024#chunk_127",
      "page_num": 28,
      "score": 0.87,
      "text_preview": "Revenue for Q4 2024 was $94.9B..."
    }
  ],
  "user_id": "analyst@company.com"
}
```

**Why This Matters:** This endpoint is CRITICAL for provenance. It records which chunks influenced the answer, enabling full traceability.

### Log Answer Generation
```http
POST /log_generation
Content-Type: application/json

{
  "query_id": "q_20241115_001",
  "answer": "According to Apple's 10-K filing...",
  "citations": ["[1] AAPL 10-K FY2024, p.28"],
  "model_used": "gpt-4",
  "user_id": "analyst@company.com"
}
```

### Verify Audit Trail Integrity
```http
GET /verify_integrity
```

**Response:**
```json
{
  "status": "verified",
  "chain_valid": true,
  "broken_events": [],
  "total_events": 15847
}
```

**If Tampering Detected:**
```json
{
  "status": "compromised",
  "chain_valid": false,
  "broken_events": [
    "Event 1234: hash mismatch",
    "Event 1235: previous_hash mismatch"
  ],
  "total_events": 15847
}
```

### Generate Compliance Report
```http
POST /compliance_report
Content-Type: application/json

{
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "report_period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z"
  },
  "total_events": 125643,
  "event_breakdown": {
    "document_ingested": 234,
    "document_processed": 234,
    "query_executed": 45123,
    "retrieval_completed": 45123,
    "generation_completed": 45123
  },
  "unique_users": 47,
  "chain_valid": true,
  "broken_events": [],
  "sample_events": [...]
}
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | `postgresql://user:password@localhost:5432/audit_db` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | `INFO` |
| `DEBUG` | Enable debug mode | No | `false` |

**Important:** This module does NOT use external API services (OpenAI, Anthropic, etc.). It only requires PostgreSQL database access.

### Database Configuration

**Production Settings (`configs/example.json`):**
```json
{
  "database": {
    "connection_pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30
  },
  "audit": {
    "retention_years": 7,
    "hash_algorithm": "sha256",
    "enable_verification": true
  }
}
```

## Common Failures & Solutions

This section documents failure modes from real-world deployments (extracted from script Section 8).

### 1. Timezone Bugs in Timestamps
**Symptom:** Events logged with local time instead of UTC, causing confusion during audits
**Cause:** Using `datetime.now()` instead of `datetime.now(timezone.utc)`
**Fix:** Always use UTC timestamps:
```python
timestamp = datetime.now(timezone.utc)  # ✅ Correct
timestamp = datetime.now()              # ❌ Wrong (local time)
```

### 2. Non-Deterministic JSON Hashing
**Symptom:** Same event produces different hashes, breaking chain verification
**Cause:** Dictionary key ordering varies between Python runs
**Fix:** Use sorted keys in JSON serialization:
```python
json.dumps(data, sort_keys=True)  # ✅ Deterministic
json.dumps(data)                  # ❌ Non-deterministic
```

### 3. Hash Chain Breaks After Manual Edits
**Symptom:** `verify_integrity()` reports broken events
**Cause:** Event was modified directly in database (violates immutability)
**Fix:** Enforce SQL immutability rules:
```sql
CREATE RULE no_update AS ON UPDATE TO audit_events DO INSTEAD NOTHING;
CREATE RULE no_delete AS ON DELETE TO audit_events DO INSTEAD NOTHING;
```

### 4. Accidental Event Deletion
**Symptom:** Events missing from audit trail (SOX violation)
**Cause:** Missing database-level immutability constraints
**Fix:** Apply `CREATE RULE no_delete` at database level (see installation)

### 5. Lost Provenance Tracking
**Symptom:** Cannot trace which documents influenced an answer
**Cause:** Incomplete `event_data` in retrieval events (missing chunk IDs, page numbers)
**Fix:** Log ALL provenance details:
```python
log_retrieval(
    query_id="q_001",
    chunks_retrieved=[
        {
            "chunk_id": "doc#chunk_127",  # ✅ Required
            "page_num": 28,               # ✅ Required
            "score": 0.87,                # ✅ Recommended
            "text_preview": "..."         # ✅ Recommended
        }
    ]
)
```

### 6. Retention Policy Violations
**Symptom:** Data archived prematurely (< 7 years), failing SOX audits
**Cause:** No retention policy configured, default database settings used
**Fix:** Configure 7+ year minimum retention:
```json
{
  "audit": {
    "retention_years": 7  // SOX minimum, often 10 in practice
  }
}
```

### 7. Audit Trail Gaps (Logging Failures)
**Symptom:** Events missing for certain operations
**Cause:** Logging failures swallowed silently (try/except without re-raise)
**Fix:** NEVER swallow logging exceptions:
```python
try:
    event_hash = audit_trail.log_event(...)
except Exception as e:
    logger.error(f"Logging failed: {e}")
    raise  # ✅ Re-raise to prevent silent failures
```

### 8. Tamper Detection Failure
**Symptom:** Modified events not detected by `verify_integrity()`
**Cause:** Using weak hash algorithm (MD5, SHA-1)
**Fix:** Use only SHA-256:
```python
hashlib.sha256(data.encode('utf-8')).hexdigest()  # ✅ Secure
hashlib.md5(data.encode('utf-8')).hexdigest()     # ❌ Weak
```

## Decision Card

### When to Use This Module

**Use if:**
- ✅ Processing financial data (10-K, 10-Q, 8-K filings, earnings reports)
- ✅ Subject to SOX compliance (public companies, regulated financial firms)
- ✅ Need to answer: **"Prove which document influenced this RAG answer"**
- ✅ Require 7+ year retention with tamper evidence
- ✅ Executive liability for data accuracy (CEO/CFO certifications)
- ✅ Material event disclosure requirements (8-K filings)
- ✅ Insider trading prevention needed
- ✅ Multi-million dollar fines if audit trail incomplete

**Do NOT use if:**
- ❌ Early-stage startup (< $10M ARR, no regulatory oversight)
- ❌ Non-financial domain (e-commerce, social media, general content)
- ❌ No SOX requirements or similar regulations
- ❌ Lightweight logging sufficient (CloudWatch, application logs)
- ❌ Performance > compliance (high-frequency trading needs <1ms logging)
- ❌ Budget limited (< $500/month for PostgreSQL infrastructure)
- ❌ No compliance team oversight

### Cost Analysis

**Small Deployment (5,000 queries/month):**
- PostgreSQL database (managed): ₹2,000/month ($25/month)
- Storage (10GB): ₹150/month ($2/month)
- **Total: ₹2,150/month ($27/month)**

**Medium Deployment (50,000 queries/month):**
- PostgreSQL database (managed, HA): ₹8,000/month ($100/month)
- Storage (100GB): ₹1,500/month ($20/month)
- Backup storage (7-year retention): ₹800/month ($10/month)
- **Total: ₹10,300/month ($130/month)**

**Large Deployment (500,000 queries/month):**
- PostgreSQL (managed, high availability): ₹32,000/month ($400/month)
- Storage (1TB active): ₹15,000/month ($200/month)
- Backup + archival (S3 + Glacier): ₹8,000/month ($100/month)
- Monitoring tools (CloudWatch, DataDog): ₹4,000/month ($50/month)
- **Total: ₹59,000/month ($750/month)**

**Trade-offs:**
- Storage grows **linearly** with events (~5KB per event average)
- Retention = cost multiplier (7-year SOX requirement = 7× storage)
- Hash verification adds 10-20ms per write operation
- BUT prevents ₹5-66 crore fines (SOX violation penalties range $1M-$10M USD)

**Hidden Costs:**
- Database migration complexity when scaling to 10M+ events/year
- Compliance audit labor (reviewing 7 years of logs costs ₹8-40 lakhs in consultant fees)
- Storage growth requires planning (partition by month, archive old events)
- Verification computation (checking all hashes takes time at scale)

## Project Structure

```
fai_m7_v4/
├── app.py                              # FastAPI application (thin wrapper)
├── config.py                           # Environment configuration (database only)
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # Environment template
├── .gitignore                          # Python defaults + notebooks
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample audit events
├── example_data.txt                    # Sample queries and use cases
├── src/
│   └── l3_m7_financial_data_ingestion_compliance/
│       └── __init__.py                 # Core audit trail logic
├── notebooks/
│   └── L3_M7_Financial_Data_Ingestion_Compliance.ipynb
├── tests/
│   └── test_m7_financial_data_ingestion_compliance.py
├── configs/
│   └── example.json                    # Configuration template
└── scripts/
    ├── run_api.ps1                     # Start API (Windows)
    └── run_tests.ps1                   # Run tests (Windows)
```

## Testing

The test suite validates ALL core functionality and failure scenarios.

**Test Coverage:**
- Hash computation and determinism
- Event logging (all event types)
- Hash chain formation and integrity
- Chain verification (valid and broken chains)
- Compliance report generation
- Timezone handling (UTC enforcement)
- JSON key ordering (determinism)
- Storage efficiency (text truncation)
- Bulk event logging (performance)
- Error handling (database failures)

**Run tests:**
```bash
pytest -v tests/
```

**Expected output:**
```
tests/test_m7_financial_data_ingestion_compliance.py::test_hash_event_determinism PASSED
tests/test_m7_financial_data_ingestion_compliance.py::test_hash_chain_formation PASSED
tests/test_m7_financial_data_ingestion_compliance.py::test_verify_integrity_empty_trail PASSED
...
===================== 20 passed in 2.34s =====================
```

## Compliance & Regulatory Notes

### SOX Section 404 Requirements

**Internal Controls Over Financial Reporting:**
- Immutable audit trail (append-only, no deletions)
- 7-year minimum retention (often 10 years in practice)
- Tamper detection mechanisms (hash chain verification)
- Executive certification of controls (CEO/CFO sign off)

**This Module Provides:**
- ✅ Hash-chained events (tamper detection via cryptography)
- ✅ PostgreSQL with append-only design (CREATE RULE no_update/no_delete)
- ✅ Configurable retention (default 7 years)
- ✅ Audit report generation for quarterly reviews
- ✅ Provenance tracking for data accuracy certification

### Disclaimers

**⚠️ IMPORTANT LEGAL NOTICES:**

1. **Not a Certified Solution:** This is educational software, NOT a certified SOX compliance solution
2. **Legal Review Required:** Must be reviewed by compliance officer and legal counsel before production use
3. **Executive Certification:** CFO/CCO must certify controls before relying on this system
4. **Criminal Liability:** SOX Section 302 violations carry criminal penalties (up to 20 years prison)
5. **No Warranty:** Provided "as is" without warranties (see LICENSE)

**Recommendation:** Use this as a foundation, then engage compliance consultants for certification.

## Support & Resources

**Script Reference:**
`https://github.com/yesvisare/financial_ai_ccc_l2/blob/main/Augmented_Finance_AI_M7_4_Audit_Trail_Document_Provenance.md`

**Documentation:**
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
- FastAPI: https://fastapi.tiangolo.com/
- SOX Section 404: https://www.sec.gov/spotlight/sarbanes-oxley.htm

**Community:**
- TechVoyageHub Discord: [Link]
- Course Forum: [Link]
- GitHub Issues: [Link]

## License

MIT License - See LICENSE file for details

Copyright (c) 2024 TechVoyageHub

---

**Module:** L3 M7.4 - Audit Trail & Document Provenance
**Track:** Finance AI
**Level:** Domain-Specific RAG Engineering
**Prerequisites:** Generic CCC M1-M6, Finance AI M7.1-M7.3
