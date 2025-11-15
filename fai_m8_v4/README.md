# L3 M8.4: Temporal Financial Information Handling

Production-ready workspace for fiscal year-aware temporal retrieval of financial documents. Handles conversion between fiscal periods and calendar dates, enabling accurate point-in-time queries and temporal consistency validation.

## Core Problem

**"When someone says 'Q3 2024,' they're referring to different calendar months"** depending on company fiscal year ends:
- **Apple** (FY ends Sept 30): Q3 FY2024 = April 1 - June 30, 2024
- **Microsoft** (FY ends June 30): Q3 FY2024 = January 1 - March 31, 2024
- **Walmart** (FY ends Jan 31): Q3 FY2024 = August 1 - October 31, 2023

This module solves fiscal period ambiguity by mapping company-specific fiscal quarters to calendar dates for accurate temporal retrieval.

---

## What You'll Learn

### Concepts Covered

1. **Fiscal Year vs Calendar Year**: Companies use non-standard fiscal years. Apple's Q3 FY2024 (April-June) differs from calendar Q3 (July-September).

2. **Point-in-Time Queries**: Reconstructing historical information states. Example: "What was Apple's revenue as of March 15, 2023?" requires filtering documents filed before that date.

3. **Temporal Consistency**: Mixing data from different fiscal periods (FY2023 revenue + FY2024 expenses) produces invalid financial ratios.

4. **Fiscal Quarter to Calendar Date Conversion**: Core temporal logic that works backward from fiscal year end to calculate quarter boundaries.

5. **Metadata Filtering in Vector Databases**: Using temporal filters (`filing_date BETWEEN start AND end`) to ensure accurate document retrieval.

6. **Forward-Looking Statement Decay**: Guidance from Q1 2024 may be invalid by Q4 2024 - requires confidence decay assessment.

### Learning Outcomes

1. Implement fiscal year end database mapping for 20+ companies
2. Convert fiscal quarter queries to calendar date ranges with 100% accuracy
3. Build point-in-time retrieval with temporal filters
4. Validate temporal consistency across search results
5. Handle forward-looking vs backward-looking statements
6. Integrate with entity linking (M8.3) for company resolution
7. Establish production compliance framework (SOX, GAAP, Reg FD)

---

## Prerequisites

**Generic CCC M1-M6**: Foundation in LLMs, prompt engineering, and RAG systems

**Prior Modules**:
- **M8.1**: Financial document types and regulatory context
- **M8.2**: Real-time financial data caching
- **M8.3**: Financial entity linking (company name → ticker resolution)

---

## Architecture Overview

```
User Query: "Apple Q3 FY2024 revenue"
           ↓
    [Entity Linking M8.3]
    "Apple" → ticker: AAPL
           ↓
 [FiscalCalendarManager]
 Q3 FY2024 → April 1 - June 30, 2024
           ↓
  [TemporalRetriever]
  Vector DB query with filters:
  - ticker = AAPL
  - filing_date BETWEEN 2024-04-01 AND 2024-06-30
           ↓
 [TemporalValidator]
 Check: All results from same fiscal period?
           ↓
    [LLM Generation]
    Generate response with temporal context
           ↓
    Return results with disclaimer:
    "Data from Apple Q3 FY2024 (April 1 - June 30, 2024)"
```

---

## How It Works

### Step 1: Fiscal Year Database Manager

**Core Function: `fiscal_quarter_to_dates()`**

Maps fiscal periods (e.g., 'Q3 FY2024') to actual calendar dates for vector database metadata filters.

**Example Usage:**
```python
from src.l3_m8_financial_domain_knowledge_injection import fiscal_quarter_to_dates

start, end = fiscal_quarter_to_dates('AAPL', 2024, 'Q3')
# Returns: ('2024-04-01', '2024-06-30')
```

**Core Logic**: Works backward from fiscal year end:
- Q4 ends on FY end date
- Q3 ends 3 months before Q4
- Q2 ends 6 months before Q4
- Q1 ends 9 months before Q4

### Step 2: Temporal Retrieval with Metadata Filtering

**System Flow:**
1. Extract entity (e.g., "Apple" → AAPL)
2. Lookup fiscal year end from database
3. Convert Q3 FY2024 to calendar dates (April 1 - June 30, 2024)
4. Vector search with metadata filter: `ticker=AAPL AND filing_date BETWEEN 2024-04-01 AND 2024-06-30`
5. Validate temporal consistency
6. Return temporally-verified results

### Step 3: Point-in-Time Retrieval

**Example**: "What was Apple's revenue as of March 15, 2023?"

Filters documents filed before the specified date to reconstruct historical information state:
```python
from src.l3_m8_financial_domain_knowledge_injection import point_in_time_query

result = point_in_time_query(
    ticker='AAPL',
    as_of_date='2023-03-15',
    query_text='revenue'
)
```

### Step 4: Temporal Consistency Validation

Detects issues like:
- Mixing data from different fiscal periods
- Comparing documents from different companies
- Large date ranges indicating stale data

```python
from src.l3_m8_financial_domain_knowledge_injection import validate_temporal_consistency

validation = validate_temporal_consistency(
    documents=[
        {"ticker": "AAPL", "filing_date": "2024-04-01", "fiscal_period": "Q3 FY2024"},
        {"ticker": "AAPL", "filing_date": "2024-05-15", "fiscal_period": "Q3 FY2024"}
    ],
    strict=True
)
```

### Step 5: Integration with Entity Linking (M8.3)

Entity linking from M8.3 feeds company name → ticker resolution into fiscal calendar lookups:
```
User: "What was Microsoft's Q2 revenue?"
     ↓
[M8.3 Entity Linking]: "Microsoft" → ticker: MSFT
     ↓
[M8.4 Fiscal Mapping]: MSFT Q2 FY2024 → Oct 1, 2023 - Dec 31, 2023
```

---

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd fai_m8_v4
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and configure:
# - PINECONE_API_KEY (required for vector queries)
# - PINECONE_ENVIRONMENT (required for Pinecone)
# - ANTHROPIC_API_KEY (optional for LLM generation)
```

### 4. Populate Fiscal Year Database
The `data/fiscal_year_ends.json` file contains fiscal year end dates for 20+ companies. Customize as needed.

---

## Usage

### Python Package

```python
from src.l3_m8_financial_domain_knowledge_injection import (
    FiscalCalendarManager,
    TemporalRetriever,
    fiscal_quarter_to_dates
)

# Convert fiscal period to calendar dates
start, end = fiscal_quarter_to_dates('AAPL', 2024, 'Q3')
print(f"Apple Q3 FY2024: {start} to {end}")
# Output: Apple Q3 FY2024: 2024-04-01 to 2024-06-30

# Initialize fiscal manager
manager = FiscalCalendarManager()
company_data = manager.get_fiscal_year_end('MSFT')
print(f"Microsoft FY ends: {company_data['fiscal_year_end']}")
# Output: Microsoft FY ends: 06-30
```

### API Server

```bash
# Windows PowerShell
.\scripts\run_api.ps1

# Manual start (set environment variables first)
$env:PINECONE_ENABLED = "True"
$env:PINECONE_API_KEY = "your_key_here"
uvicorn app:app --reload
```

**Access API**: http://localhost:8000

**API Documentation**: http://localhost:8000/docs

### Jupyter Notebook

```bash
jupyter notebook notebooks/L3_M8_Financial_Domain_Knowledge_Injection.ipynb
```

---

## API Endpoints

### GET /
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "L3 M8.4: Temporal Financial Information Handling",
  "pinecone_enabled": true,
  "fiscal_companies": 25
}
```

### POST /convert-fiscal-period
Convert fiscal quarter to calendar date range.

**Request:**
```json
{
  "ticker": "AAPL",
  "fiscal_year": 2024,
  "quarter": "Q3"
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "fiscal_period": "Q3 FY2024",
  "calendar_start": "2024-04-01",
  "calendar_end": "2024-06-30",
  "fiscal_year_end": "09-30"
}
```

### POST /query-fiscal-period
Query documents for a specific fiscal period.

**Request:**
```json
{
  "ticker": "AAPL",
  "fiscal_year": 2024,
  "quarter": "Q3",
  "query_text": "revenue growth",
  "top_k": 5
}
```

**Response:**
```json
{
  "status": "success",
  "ticker": "AAPL",
  "fiscal_period": "Q3 FY2024",
  "calendar_period": "2024-04-01 to 2024-06-30",
  "results": [...],
  "metadata": {
    "filter_applied": "ticker=AAPL AND filing_date BETWEEN 2024-04-01 AND 2024-06-30"
  }
}
```

### POST /point-in-time-query
Execute point-in-time query (documents filed before specific date).

**Request:**
```json
{
  "ticker": "AAPL",
  "as_of_date": "2023-03-15",
  "query_text": "What was Apple's revenue?",
  "top_k": 5
}
```

**Response:**
```json
{
  "status": "success",
  "ticker": "AAPL",
  "as_of_date": "2023-03-15",
  "results": [...],
  "metadata": {
    "filter_applied": "ticker=AAPL AND filing_date <= 2023-03-15"
  }
}
```

### POST /validate-temporal-consistency
Validate temporal consistency across documents.

**Request:**
```json
{
  "documents": [
    {"ticker": "AAPL", "filing_date": "2024-04-01", "fiscal_period": "Q3 FY2024"},
    {"ticker": "AAPL", "filing_date": "2024-05-15", "fiscal_period": "Q3 FY2024"}
  ],
  "strict": true
}
```

**Response:**
```json
{
  "status": "valid",
  "issues": [],
  "summary": {
    "tickers": ["AAPL"],
    "fiscal_periods": ["Q3 FY2024"],
    "document_count": 2
  }
}
```

### POST /fiscal-year-end
Get fiscal year end information for a company.

**Request:**
```json
{
  "ticker": "AAPL"
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "fiscal_year_end": "09-30",
  "company_name": "Apple Inc.",
  "source": "SEC 10-K"
}
```

### GET /companies
List all companies in fiscal year database.

**Response:**
```json
{
  "count": 25,
  "tickers": ["AAPL", "MSFT", "WMT", ...]
}
```

### GET /health
Extended health check with component status.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "fiscal_manager": {
      "status": "operational",
      "companies_loaded": 25
    },
    "pinecone": {
      "status": "enabled",
      "client_initialized": true
    }
  },
  "version": "1.0.0"
}
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PINECONE_ENABLED` | No | `false` | Enable Pinecone vector database |
| `PINECONE_API_KEY` | Yes (if enabled) | - | Pinecone API key |
| `PINECONE_ENVIRONMENT` | Yes (if enabled) | - | Pinecone environment (e.g., `us-west1-gcp`) |
| `PINECONE_INDEX_NAME` | No | `financial-documents` | Pinecone index name |
| `ANTHROPIC_ENABLED` | No | `false` | Enable Anthropic Claude for LLM generation |
| `ANTHROPIC_API_KEY` | Yes (if enabled) | - | Anthropic API key |
| `REDIS_ENABLED` | No | `false` | Enable Redis caching |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection URL |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

---

## Testing

```bash
# Windows PowerShell
.\scripts\run_tests.ps1

# Manual
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

**Test Coverage Target**: ≥95%

---

## Common Issues & Solutions

### Failure #1: Fiscal Year Database Out of Date

**Problem**: Companies occasionally change fiscal year ends (e.g., fiscal year transition periods)

**Solution**:
- Update `data/fiscal_year_ends.json` annually
- Version control fiscal year database
- Add "last_updated" field to track data freshness
- Subscribe to SEC Edgar RSS feeds for fiscal year changes

**Detection**: Query returns unexpected date ranges

### Failure #2: Transition Period Confusion

**Problem**: Fiscal year changes create overlap periods (e.g., company moved FY end from Dec 31 to June 30)

**Solution**:
- Flag documents during transition periods
- Require explicit verification for transition years
- Add "transition_period" metadata to affected documents
- Document historical fiscal year changes in database

**Detection**: Documents show 5 quarters in a single fiscal year

### Failure #3: Forward-Looking Statement Becomes Outdated

**Problem**: Guidance from Q1 2024 may be invalid by Q4 2024

**Solution**:
- Add "confidence decay" metadata to forward-looking statements
- Flag statements > 6 months old as "potentially outdated"
- Implement `check_forward_looking_statements()` validation
- Include staleness warnings in API responses

**Detection**: Forward-looking statements used in analysis after 6+ months

### Failure #4: Cross-Company Fiscal Period Mismatch

**Problem**: Comparing Apple Q3 to Microsoft Q3 from different calendar periods

**Solution**:
- Validate all results from same fiscal period before comparison
- Use `validate_temporal_consistency()` with `strict=True`
- Normalize to calendar quarters for cross-company analysis
- Add warnings when comparing different fiscal periods

**Detection**: TemporalValidator returns "mixed_fiscal_periods" error

### Failure #5: Missing Fiscal Period Metadata in Documents

**Problem**: Documents ingested without `filing_date` metadata

**Solution**:
- OCR extraction of filing dates from SEC headers
- Fallback to document creation date if filing date unavailable
- Validate metadata completeness during ingestion
- Add required metadata schema validation

**Detection**: Vector queries return no results despite existing documents

---

## Decision Card

### When to Use Temporal Financial Retrieval

| Scenario | Decision |
|----------|----------|
| Single calendar-year company | ❌ Skip temporal complexity |
| 2-5 companies, mix of fiscal years | ✅ Use automatic mapping |
| 10+ companies, regulated industry | ✅ Full deployment with audit trails |
| Real-time market data | ✅ Combine with M8.2 caching |
| Ad-hoc financial research | ✅ Use for accuracy |
| High-frequency trading | ❌ Too slow; use direct data feeds |

### When to Use

- **Multi-company financial analysis** with different fiscal years
- **Regulatory compliance** (SOX, GAAP, Reg FD) requiring temporal accuracy
- **Point-in-time queries** reconstructing historical information state
- **Financial statement comparisons** requiring consistent fiscal periods
- **Audit trail requirements** tracking data-as-of-date
- **Cross-company benchmarking** with fiscal period normalization

### When NOT to Use

**Anti-Pattern #1**: Applying fiscal periods to non-financial queries (e.g., "Apple product history")

**Anti-Pattern #2**: Using historical data for real-time decisions without disclaimer on data freshness

**Anti-Pattern #3**: Cross-industry comparisons with different fiscal calendars without normalization

**Anti-Pattern #4**: Over-engineering for small-scale systems (< 5 companies with same fiscal year)

**Decision Checklist**:
- ✅ Need temporal accuracy in financial analysis?
- ✅ Multiple companies with different fiscal years?
- ✅ Regulatory compliance requirements (SOX)?
- ❌ Single calendar-year company? Skip temporal complexity.

### Cost Estimates

**Small Deployment (10 companies, 1,000 queries/month)**:
- Fiscal calendar: Spreadsheet (free)
- Vector DB (Pinecone): ~$50/month
- Audit infrastructure: Not needed
- **Total Annual Cost: $600**

**Medium Deployment (100 companies, 10,000 queries/month)**:
- Fiscal calendar: JSON database + annual updates (~$200/year)
- Vector DB (Pinecone): ~$150/month
- Redis caching: ~$20/month
- **Total Annual Cost: $2,200**

**Large Deployment (Fortune 500 portfolio, 100,000 queries/month)**:
- Fiscal calendar: 500 companies × $0.10/lookup/year = $50/year
- Vector DB (Pinecone): ~$400/month
- Redis caching: ~$50/month
- Audit infrastructure: $500 one-time
- **Total Annual Cost: $5,900**

**Cost Optimization**:
- Cache fiscal year ends in Redis (lookup latency: 1ms vs 50ms)
- Batch fiscal period conversions (convert Q1-Q4 upfront)
- Use metadata-only filtering (don't retrieve full documents)
- Shared fiscal calendar across teams

**ROI Calculation**:
- Cost of one erroneous investment decision: $1M+
- Temporal accuracy preventing even 1 error/year: **ROI = 100-200x**

### Alternatives

**Alternative #1: Semantic Search Only**
- **Pro**: Simple implementation, no fiscal database needed
- **Con**: No temporal accuracy; "Q3 2024" might retrieve Q2 or Q4 documents
- **Production Fit**: ❌ Unreliable for financial analysis

**Alternative #2: Require User to Specify Explicit Calendar Dates**
- **Pro**: User controls exact date ranges
- **Con**: User burden; error-prone; poor UX (users think in fiscal quarters)
- **Production Fit**: ❌ Bad UX for financial professionals

**Alternative #3: Automatic Fiscal Period Mapping (Our Approach)**
- **Pro**: Accurate + user-friendly + production-ready
- **Con**: Requires fiscal database maintenance (annual updates)
- **Production Fit**: ✅ Best for production financial systems

**Alternative #4: LLM-Based Fiscal Period Extraction**
- **Pro**: Can handle natural language ("Apple's Q3 earnings")
- **Con**: LLM hallucination risk on fiscal dates
- **Production Fit**: ⚠️ Better combined with explicit validation (use LLM + validate against fiscal database)

**Decision Framework**: Use automatic mapping for structured queries; supplement with LLM extraction for natural language inputs, but ALWAYS validate against fiscal database.

---

## Financial Domain Compliance

### Regulatory Requirements

**1. SOX Section 302**: CEO/CFO must certify financial reports based on information "as of" specific dates
- **Implementation**: All API responses include `as_of_date` and `fiscal_period`
- **Audit Trail**: Log all fiscal period conversions

**2. SOX Section 404**: Internal controls over financial reporting—audit trails must show which data was current at decision time
- **Implementation**: Point-in-time queries filter by `filing_date <= as_of_date`
- **Audit Trail**: Store query metadata (ticker, date, fiscal period)

**3. GAAP Temporal Requirements**: Financial statements require consistent fiscal periods for comparisons
- **Implementation**: `validate_temporal_consistency()` enforces same fiscal period
- **Warning**: Flag cross-period comparisons as invalid

**4. Regulation FD (Fair Disclosure)**: Material information must be disclosed uniformly to all investors on same date
- **Implementation**: Filter documents by `filing_date` (public disclosure date)
- **Compliance**: No pre-disclosure data retrieval

### Production Deployment Checklist

- [ ] Fiscal year database covers 95%+ of portfolio companies
- [ ] All documents tagged with `filing_date` and `report_date`
- [ ] Temporal validation tests pass 100% accuracy
- [ ] Audit trail logs all fiscal period conversions
- [ ] Disclaimers included in all API responses

### Required Disclaimers

All API responses include:
```
"Data retrieved from [Company] [Fiscal Period] ([Calendar Dates]).
Historical data; not real-time. See original filings for authoritative information."
```

---

## License

MIT License - see LICENSE file for details

---

## Resources

### Documentation
- **SEC EDGAR**: https://www.sec.gov/cgi-bin/browse-edgar (authoritative fiscal year sources)
- **XBRL Instance Documents**: Machine-readable fiscal period metadata
- **Company Investor Relations**: Fiscal calendar documentation

### Related Modules
- **M8.1**: Financial document types and regulatory context
- **M8.2**: Real-time financial data caching
- **M8.3**: Financial entity linking (company name → ticker)
- **M9.1**: Multi-source financial data fusion (next module)

### External Tools
- **Pinecone**: https://www.pinecone.io/docs/ (vector database)
- **Anthropic Claude**: https://docs.anthropic.com/ (LLM generation)
- **Python dateutil**: https://dateutil.readthedocs.io/ (fiscal period calculations)

---

## What's Next: Finance AI M9.1

**Multi-source financial data fusion**: Combine SEC filings + earnings calls + market data

**Before Next Video**:
- Extend your fiscal calendar to 50+ companies
- Add historical fiscal year changes (companies occasionally change FY ends)
- Integrate with real filing data from SEC EDGAR

---

## Summary

**Key Takeaways**:
- ✅ Fiscal periods are company-specific; never assume calendar year
- ✅ Explicit metadata filtering beats semantic search for temporal accuracy
- ✅ Point-in-time queries require document `filing_date` tracking
- ✅ Forward-looking statements have built-in expiration dates
- ✅ Financial systems demand 100% accuracy; test every date conversion

**What You Accomplished**:
- Built fiscal calendar system mapping companies to fiscal year ends
- Implemented fiscal → calendar date conversion (core temporal logic)
- Integrated with entity linking (M8.3) for company resolution
- Validated temporal consistency across retrieval results
- Established production compliance framework (SOX, GAAP, Reg FD)
