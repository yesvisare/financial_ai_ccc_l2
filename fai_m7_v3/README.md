# L3 M7.3: Financial Document Parsing & Chunking

Production-ready implementation of compliance-aware financial document parsing and chunking for SEC filings.

## Overview

This workspace implements a financial document parsing system that transforms SEC filings (10-K, 10-Q, 8-K) into searchable vector database chunks while preserving regulatory compliance boundaries and maintaining SOX Section 404 requirements.

**Key Features:**
- Parse structured SEC filings (Item 1, 1A, 7, 8)
- Extract XBRL financial data (200 core tags covering 90% of use cases)
- Compliance-aware chunking (SOX Section 404)
- Metadata tagging (fiscal period, ticker, filing type)
- Audit trail with hash chain integrity

## Architecture

```
SEC EDGAR API → Download Filing → Extract Sections → Parse XBRL → Chunk with Metadata → Vector DB
```

**Components:**
1. **EDGARDownloader**: Downloads SEC filings with rate limiting compliance (10 req/sec maximum)
2. **SECFilingParser**: Extracts regulatory sections (Item 1, 1A, 7, 8) while preserving boundaries
3. **XBRLParser**: Parses XBRL financial data from Item 8 (balance sheet, income statement)
4. **FinancialDocumentChunker**: Creates compliance-aware chunks with complete metadata

## Prerequisites

- Python 3.9+
- SEC User-Agent (company name + email - **required by SEC**)
- Basic understanding of SEC filings (10-K, 10-Q structure)
- Optional: OpenAI API key (for vector embeddings)
- Optional: Pinecone account (for vector database storage)

## Installation

1. **Clone and setup:**
```bash
git clone <repository>
cd fai_m7_v3
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your SEC User-Agent
```

3. **Environment Variables:**

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `EDGAR_ENABLED` | Enable EDGAR API access | Yes | `false` |
| `SEC_USER_AGENT` | Company name + email (SEC requirement) | Yes* | - |
| `SEC_RATE_LIMIT` | Requests per second (max 10) | No | `10` |
| `CHUNK_SIZE` | Characters per chunk | No | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | No | `200` |
| `OPENAI_ENABLED` | Enable OpenAI embeddings | No | `false` |
| `OPENAI_API_KEY` | OpenAI API key | No** | - |
| `PINECONE_ENABLED` | Enable Pinecone vector DB | No | `false` |
| `PINECONE_API_KEY` | Pinecone API key | No** | - |

\* Required if `EDGAR_ENABLED=true`
\** Required if respective service is enabled

**Important:** SEC requires a valid User-Agent with company name and email. Format: `"CompanyName product-team@company.com"`

## Usage

### Python Package

```python
from src.l3_m7_financial_data_ingestion_compliance import FinancialDocumentChunker

# Initialize chunker
chunker = FinancialDocumentChunker(chunk_size=1000, chunk_overlap=200)

# Download and chunk SEC filing
chunks = chunker.chunk_filing(
    ticker='MSFT',
    filing_type='10-K',
    user_agent='YourCompany yourteam@company.com'
)

# Each chunk includes metadata
for chunk in chunks[:3]:  # Show first 3 chunks
    print(f"Section: {chunk['metadata']['section']}")
    print(f"Fiscal Period: {chunk['metadata'].get('fiscal_period', 'N/A')}")
    print(f"Text: {chunk['text'][:100]}...")
    print()
```

### FastAPI Server

```bash
# Start server (Windows PowerShell)
.\scripts\run_api.ps1

# Or manually
export PYTHONPATH=$PWD  # On Windows: $env:PYTHONPATH = $PWD
export EDGAR_ENABLED=true
export SEC_USER_AGENT="YourCompany yourteam@company.com"
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**API Endpoints:**
- `GET /` - Health check
- `GET /health` - Detailed health check with service status
- `GET /capabilities` - List available capabilities based on enabled services
- `POST /chunk` - Download and chunk SEC filing
- `POST /extract-sections` - Extract regulatory sections from HTML

**Example API Usage:**
```bash
# Chunk a filing
curl -X POST "http://localhost:8000/chunk" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "MSFT", "filing_type": "10-K", "fiscal_year": 2023}'

# Extract sections from HTML
curl -X POST "http://localhost:8000/extract-sections" \
  -H "Content-Type: application/json" \
  -d '{"html_content": "<html>...</html>", "filing_type": "10-K"}'
```

### Jupyter Notebook

```bash
jupyter notebook notebooks/L3_M7_Financial_Data_Ingestion_Compliance.ipynb
```

## Decision Card

**📋 DECISION CARD: Financial Document Parsing & Chunking**

### ✅ USE WHEN:
- Analyzing 10+ companies' financial filings (batch processing saves time)
- Building financial research platform (enable analyst queries across companies)
- Need audit-ready lineage (SOX Section 404 compliance requirement)
- Budget allows $50K-100K legal review + $70-100/month operational costs
- Analyzing US public companies (SEC EDGAR coverage)

### ❌ AVOID WHEN:
- Analyzing <5 companies (manual extraction is faster due to setup overhead)
- Need 100% accuracy (edge cases exist: 5-15% require manual intervention)
- Global coverage required (non-US companies not in SEC EDGAR)
- Only need financial metrics (XBRL-only parsing is 2x faster)
- No compliance requirement (Generic CCC semantic chunking is simpler)

### 💰 COST:

**Small Investment Firm (20 analysts, 50 companies, 5K filings):**
- Monthly: ₹8,500 ($105 USD)
  - OpenAI embeddings: ₹2,500 ($30)
  - Pinecone storage: ₹6,000 ($75) - 500K vectors
- Per analyst: ₹425/month ($5.25)
- Setup: ₹40L-80L ($50K-100K) one-time SEC counsel review

**Medium Asset Manager (100 analysts, 200 companies, 50K filings):**
- Monthly: ₹45,000 ($550 USD)
  - OpenAI embeddings: ₹25,000 ($300) - batch processing
  - Pinecone storage: ₹20,000 ($250) - 5M vectors
- Per analyst: ₹450/month ($5.50)
- Setup: ₹80L-1.2Cr ($100K-150K) comprehensive legal review

**Large Hedge Fund (500 analysts, 500 companies, 200K filings):**
- Monthly: ₹1,50,000 ($1,850 USD)
  - OpenAI embeddings: ₹1,00,000 ($1,250) - high volume
  - Pinecone storage: ₹50,000 ($600) - 20M vectors, dedicated
- Per analyst: ₹300/month ($3.70) - economies of scale
- Setup: ₹1.2Cr-2Cr ($150K-250K) - enterprise legal review + ongoing compliance

### ⚖️ TRADE-OFFS:
- **Benefit:** 95% accuracy, 2-3 min processing vs. 2 hours manual (40x faster)
- **Limitation:** 5-15% edge cases require manual intervention (images, foreign issuers)
- **Complexity:** Medium (requires legal review, SOX compliance understanding)

### 📊 PERFORMANCE:
- Latency: 2-3 minutes per 10-K (150-page filing)
- Throughput: 20 filings/hour (single process), 200 filings/hour (parallel 10 processes)
- Accuracy: 95% table extraction, 90% XBRL tag coverage (200 core tags)

### ⚖️ REGULATORY:
- Compliance: SOX Section 404, Regulation FD, Securities Exchange Act 1934
- Disclaimer: "Not Investment Advice" (required on every response)
- Review: SEC counsel ($50K-100K initial), CFO sign-off, SOX auditor annual review

### 📏 ALTERNATIVES:
- **Use XBRL-only** if: Only need financial metrics (40% faster, but misses qualitative)
- **Use Bloomberg** if: Budget >$24K/year per user, need global coverage
- **Use Manual extraction** if: Analyzing <5 companies (faster with setup overhead)
- **Use Generic CCC** if: No compliance requirement (simpler, no SOX overhead)

## Common Failures

### Failure #1: Split Financial Table (Broken SOX Compliance)

**What happens:**
- Chunker splits balance sheet table mid-content
- Assets (first half) go in Chunk 45
- Liabilities (second half) go in Chunk 46
- CFO queries "What are Microsoft's total liabilities?" → Gets partial answer (only current liabilities, missing long-term)
- Auditor flags during SOX 404 review: "Financial statement integrity violated"

**Why it happens:**
- Used semantic chunking (Generic CCC M2 approach) instead of table-aware chunking
- Chunk size set too small (500 chars) - balance sheet is 2,000+ chars
- No boundary detection for `<table>` tags

**How to fix:**
- Treat each financial table as atomic unit (one table = one chunk)
- Never apply chunk_size limit to tables - compliance overrides size limits
- Implement `_chunk_financial_statements()` method that preserves table integrity

**Impact:** CFO gets wrong answer (missing half the liabilities), auditor fails SOX 404 review, $1M+ remediation cost.

---

### Failure #2: Misidentified XBRL Tag (Wrong Financial Metric)

**What happens:**
- User queries "What was Microsoft's net income in FY2023?"
- System retrieves chunk with `us-gaap:ProfitLoss` tag instead of `us-gaap:NetIncomeLoss`
- Answer: $72B (operating income) instead of $50B (net income)
- CFO makes investment decision based on wrong number
- $10M+ loss due to incorrect analysis

**Why it happens:**
- XBRL taxonomy has multiple similar tags:
  - `us-gaap:OperatingIncomeLoss` (operating income, before taxes)
  - `us-gaap:IncomeLossFromContinuingOperations` (after taxes, before discontinued ops)
  - `us-gaap:NetIncomeLoss` (final bottom line)
  - `us-gaap:ProfitLoss` (IFRS equivalent, slightly different)
- Chunker maps user query "net income" to wrong tag
- No validation against company's actual tag usage

**How to fix:**
- Validate that company actually uses the XBRL tag in their filing
- Implement tag hierarchy fallback (try alternates if primary tag not found)
- Map common tags to their alternates: `NetIncomeLoss` → `[ProfitLoss, IncomeLossFromContinuingOperations]`

**Impact:** $72B instead of $50B = 44% error. CFO makes wrong decision, $10M+ loss.

---

### Failure #3: Missing Fiscal Period Context (Wrong Year Comparison)

**What happens:**
- User queries "Compare Microsoft and Apple revenue growth"
- System retrieves:
  - Microsoft FY2023 revenue (fiscal year ends June 30, 2023)
  - Apple FY2024 revenue (fiscal year ends September 30, 2024)
- Comparing June 2023 to September 2024 = 15-month period (not apples-to-apples)
- Revenue "growth" includes 3 extra months → misleading

**Why it happens:**
- Didn't store fiscal year end date in metadata
- Assumed "FY2023" means same period for all companies
- No validation of fiscal period alignment

**How to fix:**
- Store fiscal year end date in chunk metadata (`fiscal_year_end: "June 30"`)
- Normalize fiscal periods to calendar quarters for cross-company comparison
- Validate fiscal period alignment before comparison queries
- Example normalization:
  - Microsoft FY2023 (June 30) → Calendar Q4 2022 + Q1/Q2 2023
  - Apple FY2023 (Sept 30) → Calendar Q4 2022 + Q1/Q2/Q3 2023

**Impact:** 15-month comparison instead of 12-month = 25% inflation of growth rate. Investor makes wrong decision.

---

### Failure #4: Ignored Section Boundaries (Compliance Violation)

**What happens:**
- Chunker splits Item 7 (MD&A) and Item 8 (Financial Statements) boundary
- Last paragraph of MD&A (management's revenue forecast) ends up in same chunk as first table of Item 8 (actual revenue)
- Auditor flags: "Management's forward-looking statements mixed with GAAP financial statements"
- SEC review: "Did you inadvertently create misleading disclosure?"
- $500K+ SEC investigation costs

**Why it happens:**
- Used fixed chunk size (1000 chars) without section awareness
- Didn't detect Item 7 → Item 8 boundary
- Treated filing as continuous text (like a blog post)

**How to fix:**
- Extract sections FIRST, then chunk within sections (never across section boundaries)
- Implement strict boundary detection:
  ```python
  # Find section boundaries
  section_boundaries = []
  for section_name, pattern in patterns.items():
      match = re.search(pattern, html_content)
      section_boundaries.append({'name': section_name, 'start': match.start()})

  # Sort by position and set end positions
  section_boundaries.sort(key=lambda x: x['start'])
  for i in range(len(section_boundaries) - 1):
      section_boundaries[i]['end'] = section_boundaries[i+1]['start']
  ```
- Validate no section overlap (compliance validation)

**Impact:** SEC investigation ($500K+ legal fees), potential enforcement action, reputational damage.

---

### Failure #5: No Chunk Overlap (Lost Context)

**What happens:**
- User queries "What are Microsoft's revenue recognition policies?"
- Revenue recognition policy spans two paragraphs:
  - Paragraph 1 (end of Chunk 42): "We recognize revenue when control transfers..."
  - Paragraph 2 (start of Chunk 43): "...which is typically upon delivery for software licenses."
- Query matches Chunk 43 (keyword "software licenses") but misses Chunk 42 context
- Answer incomplete: System says "revenue recognized upon delivery" without mentioning "when control transfers" (critical GAAP requirement)
- CFO misunderstands policy → wrong accounting decision

**Why it happens:**
- No chunk overlap (`chunk_overlap=0`)
- Paragraph boundary fell exactly at chunk boundary
- Context lost between chunks

**How to fix:**
- Set chunk overlap to 15-20% of chunk size minimum
- Recommended: `chunk_overlap=200` for `chunk_size=1000`
- When creating new chunk, include last `chunk_overlap` characters from previous chunk
- Example:
  ```python
  if len(current_chunk) > chunk_size:
      # Save current chunk
      chunks.append(current_chunk)

      # Start new chunk with overlap
      overlap_text = current_chunk[-chunk_overlap:]
      current_chunk = overlap_text + "\n\n" + next_paragraph
  ```

**Impact:** Incomplete answer leads to wrong accounting decision. Loss of critical GAAP context.

---

## Testing

```bash
# Run tests (Windows PowerShell)
.\scripts\run_tests.ps1

# Or manually
export PYTHONPATH=$PWD  # On Windows: $env:PYTHONPATH = $PWD
pytest -v tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test
pytest tests/test_m7_financial_data_ingestion_compliance.py::TestEDGARDownloader -v
```

## Performance

- **Processing Time:** 2-3 minutes per 10-K (150 pages)
- **XBRL Parsing:** 200 core tags = 90% coverage in 30 seconds
- **Chunk Generation:** ~68 chunks per 10-K with metadata
- **Rate Limiting:** 10 requests/second (SEC enforced - exceeding this results in IP ban)

## Compliance Notes

**SOX Section 404 Requirements:**
- Financial statements (Item 8) must maintain integrity (no table splitting)
- Audit trail required for all transformations (SHA-256 hash for each chunk)
- Hash chain prevents tampering detection
- Metadata enables compliance reporting
- 7-year retention requirement for audit trails

**SEC EDGAR API Rules:**
- User-Agent with company name + email **required** (not optional)
- Rate limit: 10 requests/second **maximum** (enforced by IP blocking)
- IP ban if limits exceeded (no warning - immediate block)
- Respect for SEC resources (cache filings locally, don't repeatedly download)

## Project Structure

```
fai_m7_v3/
├── app.py                              # FastAPI entrypoint
├── config.py                           # Environment & client management
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # API key template
├── .gitignore                          # Python defaults
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample JSON data
├── example_data.txt                    # Sample text data
│
├── src/                                # Source code package
│   └── l3_m7_financial_data_ingestion_compliance/
│       └── __init__.py                 # Core business logic
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M7_Financial_Data_Ingestion_Compliance.ipynb
│
├── tests/                              # Test suite
│   └── test_m7_financial_data_ingestion_compliance.py
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API
    └── run_tests.ps1                   # Windows: Run tests
```

## Contributing

Pull requests welcome. Please ensure:
- All tests pass (`pytest tests/`)
- Code follows PEP 8 style
- Docstrings on public functions (Google style)
- Update README with new features
- SOX compliance maintained (don't break section boundaries!)

## License

MIT License - see LICENSE file

## Support

- **Documentation:** See notebooks for examples
- **Issues:** GitHub Issues
- **SEC EDGAR API Docs:** https://www.sec.gov/edgar/sec-api-documentation
- **XBRL Resources:** https://www.sec.gov/structureddata/osd-inline-xbrl.html

## Acknowledgments

- Built following TechVoyageHub L3 baseline structure
- Implements PractaThon™ standards for production readiness
- Compliance guidance from SOX Section 404 requirements
- SEC EDGAR API documentation
